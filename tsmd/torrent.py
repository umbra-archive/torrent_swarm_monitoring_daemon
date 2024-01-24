import bencodepy
import humanize
import urllib
import sys
import json
import hashlib
from datetime import datetime


class ByteValueJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return o.decode("utf-8")
        return json.JSONEncoder.default(self, o)


class Torrent:
    def __init__(self, blob, link=""):
        self.blob = blob
        self.decoded_data = bencodepy.bdecode(self.blob)
        self.link = link
        self.info = self.decoded_data[b"info"]

        try:
            self.url_list = self.decoded_data[b"url-list"]
        except:
            self.url_list = "N/A"

        try:
            self.announce = self.decoded_data[b"announce"]
        except:
            self.announce = "N/A"

        try:
            self.announce_list = self.decoded_data[b"announce-list"]
        except:
            self.announce_list = "N/A"

        try:
            self.comment = self.decoded_data[b"comment"]
        except KeyError:
            self.comment = "N/A"

        try:
            self.comment_utf8 = self.decoded_data[b"comment.utf-8"]
        except KeyError:
            self.comment_utf8 = "N/A"

        try:
            self.created_by = self.decoded_data[b"created by"]
        except KeyError:
            self.created_by = "N/A"

        try:
            self.creation_date = int(self.decoded_data[b"creation date"])
            self.creation_human = datetime.fromtimestamp(self.creation_date).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except KeyError:
            self.creation_date = 0
            self.creation_human = "N/A"

        self.size = self._calculate_size()
        self.size_human = humanize.naturalsize(self.size, binary=True)
        self.infohash = self._calculate_infohash()

    def _calculate_size(self):
        if b"files" in self.info:  # Multi-file torrent
            return sum(file[b"length"] for file in self.info[b"files"])
        else:
            return self.info[b"length"]

    def _calculate_infohash(self):
        return hashlib.sha1(bencodepy.bencode(self.info)).hexdigest()

    def print_info(self):
        print(f"firs level keys:        {self.decoded_data.keys()}")
        print(f"announce:               {self.announce}")
        print(f"announce-list:          {self.announce_list}")
        print(f"creation_date:          {self.creation_date}")
        print(f"creation_date (human):  {self.creation_human}")
        print(f"comment:                {self.comment}")
        print(f"comment.utf-8:          {self.comment_utf8}")
        print(f"created by:             {self.created_by}")
        print(f"size (calculated):      {self.size}")
        print(f"size (human):           {self.size_human}")
        print(f"infohash (calculated):  {self.infohash}")
        print(f"url-list (webseed):     {str(self.url_list)[:80]+'[...]'}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python torrent_file_decoder.py <torrent_file>")
        sys.exit()

    file_path = sys.argv[1]
    with open(file_path, "rb") as file:
        torrent_data = file.read()
    test_torrent = Torrent(torrent_data)
    test_torrent.print_info()
