import time
import requests
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
    RequestException,
    ChunkedEncodingError,
)

from bs4 import BeautifulSoup
from peewee import SqliteDatabase, Model, BlobField, CharField
from urllib.parse import urljoin, urlunparse, urlparse

from .collection import Collection, sanitize_url, get_scheme_and_hostname
from .schema import db, create_dynamic_table_model
from .config_loader import config
from .torrent import Torrent
from .logging_loader import logger


## we should add a santey check to make sure info hashes are uniq
## could, but should not be done as a SQL constraint,
## as we need to handle such case propperly

### TBD TBD TBD
### TBD TBD TBD
### TBD TBD TBD
## we still need to protect from SSRF and SSRF-rebind attacks
## right now we just protect against HTTP redirect based SSRFs
## ssrfs are blind, at least. Could leak IP/allow nat/localhost enum
## and blind-GET-sploitation against local network/local host



def http_get_with_retry(url, max_retries=3, sleep=1, allow_redirects=False):
    ## returns: file, success, error_msg
    ## allow_redirects=False prevents redirect based ssrf
    success = False
    attempts = 0
    caught_exceptions = []

    while attempts < max_retries:
        logger.debug(
            f"Attempting to fetch torrent file form url: {url}. Retry: {attempts}"
        )
        try:
            file_response = requests.get(url, allow_redirects=allow_redirects)
            break
        except (
            ConnectionError,
            Timeout,
            HTTPError,
            RequestException,
            ChunkedEncodingError,
        ) as e:
            attempts += 1
            caught_exceptions.append(e.__class__.__name__)
            if attempts == max_retries:
                return None, False, f"max caught exceptions: {str(caught_exceptions)}"
            time.sleep(sleep * attempts)

    if file_response.status_code != 200:
        logger.warning(f"Failed to download: {file_name}")
        return (
            file_response,
            False,
            f"non 200 HTTP status code {file_response.status_code}",
        )

    if file_response.content == "":
        logger.warning("File content empty, skipping")
        return file_response, False, "file is empty"

    return file_response, True, "success"


class TorrentFileSync:
    """ take a single collection, or a list of collections, optional: stop_after_n """

    def __init__(self, collection=None, stop_after_n=-1):
        if collection is None:
            collection = [Collection(d) for d in config["collection_enabled"].keys()]

        if isinstance(collection, list):
            self.children = [TorrentFileSync(c) for c in collection]
            return

        self.collection = collection
        self.torrent_file_table = create_dynamic_table_model(self.collection.name)
        self.create_table_if_nonexist()
        self.stop_after_n = stop_after_n
        self.sleep = 1
        self.max_retries = 3
        self.save_torrent_content_to_db = False

        self.sync()

    def create_table_if_nonexist(self):
        if db.table_exists(self.torrent_file_table):
            logger.debug(f"DB table {self.collection.name} found")
        else:
            logger.info(f"DB table {self.collection.name} does not exist, creating")
            db.create_tables([self.torrent_file_table])

    def is_irrelevant(self, url):
        if not url.endswith(".torrent"):
            logger.info(
               f"URL {url} is not relevent. Skipping. File name must end on '.torrent'"
            )
            return True

        ## this only checks for base url match..
        if not get_scheme_and_hostname(url) == get_scheme_and_hostname(self.collection.url):
            logger.warning(
               f"URL {url} is not relevent. Skipping, href points to other base url"
            )
            return True

        if self.collection.required_substring:
            if not self.collection.required_substring in url:
                logger.info(
                    f"URL {url} is not relevent. Skipping, href missing required_substring"
                )
                return True

        return None

    def sync(self):
        ### allow_redirects=False else potential SSRF
        response = requests.get(self.collection.url, allow_redirects=False)
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a"):
            file_name = link.get("href")
            remote_file_url = urljoin(self.collection.url, file_name)
            logger.info(f"Processing link: {file_name}")

            if error_msg := self.is_irrelevant(remote_file_url):
                continue

            exists = (
                self.torrent_file_table.select()
                .where(self.torrent_file_table.src_url == remote_file_url)
                .exists()
            )
            if exists:
                logger.info(f"Skipped (already in DB): {file_name}")
                continue

            file_response, success, error_msg = http_get_with_retry(
                remote_file_url, max_retries=self.max_retries, sleep=self.sleep
            )

            if not success:
                logger.error(
                    f"HTTP get torrent file failed: {remote_file_url} error: {error_msg}"
                )
                continue
            logger.info("Successfuly fetched torrent file")

            with db:
                ### TBD: check if infohash is uniq...
                file, created = self.torrent_file_table.get_or_create(name=file_name)

                logger.info(f"Adding torrent to collection: {remote_file_url}")

                if self.save_torrent_content_to_db:
                    file.content = file_response.content

                torrent = Torrent(file_response.content)

                file.infohash = torrent.infohash
                file.size = torrent.size
                file.src_url = remote_file_url

                file.tf_created_by = torrent.created_by
                file.tf_creation_date = torrent.creation_date
                file.tf_comment = torrent.comment
                file.tf_comment_utf8 = torrent.comment_utf8

                file.save()

            # Debug feature: stop_after_n defaults to -1, will run untill end
            if not self.stop_after_n:
                break
            self.stop_after_n -= 1

    def count(self):
        print(self.torrent_file_table.select().count())

    def info(self):
        for t in self.torrent_file_table.select():
            print(t, t.name, t.infohash)


if __name__ == "__main__":

    collection = Collection("libgen_r")
    tfs = TorrentFileSync(collection, stop_after_n=-1)
