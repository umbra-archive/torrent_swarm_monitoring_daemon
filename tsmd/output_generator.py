# import redis
import json

from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template
from peewee import OperationalError

# from cache_cfg import redis_client, int_to_ip_port
from .collection import Collection
from .logging_loader import logger
from .schema import db, create_dynamic_table_model
from .config_loader import config
from .torrent import Torrent, ByteValueJSONEncoder

def max_none(a, b):
    """ like python max(), but accepts None"""
    return max(a or 0, b or 0)


class OutputGenerator:
    """ optional arg: collection_list = [selected list of collections]
                      defaults to all collections
    """
    def __init__(self, collection_list=None):
        if collection_list is None:
            self.collection_list = [Collection(k) for k in config["collection_enabled"].keys()]
        else:
            self.collection_list = collection_list

        logger.debug(f"OutputGenerator loaded with collections: {self.collection_list}")

        self.template_dir = config["output"]["template_dir"]
        self.torrent_html_template_file = config["output"]["torrent_html_template_file"]
        self.stats_html_template_file = config["output"]["stats_html_template_file"]
        self.path_json_out = config["output"]["json_path"]
        self.path_html_out = config["output"]["html_path"]
        self.path_stats_out = config["output"]["stats_path"]

        self.data_html, self.data_json = self._process_collection()

        file_loader = FileSystemLoader(self.template_dir)
        self.template_env = Environment(loader=file_loader)

        self.generate_html()
        self.generate_json()
        self.generate_stats()


    def refresh(self):
        self.data_html, self.data_json = self._process_collection()

    def _process_collection(self):
        data_html = []
        data_json = []

        for collection in self.collection_list:
            logger.debug(f"Loading collection {collection.name}")
            tmp_html, tmp_json = self._read_data(collection)
            data_html.extend(tmp_html)
            data_json.extend(tmp_json)

        return data_html, data_json


    def _read_data(self, collection):
        Torrent_file = create_dynamic_table_model(collection.name)
        data_html = []
        data_json = []

        if not Torrent_file.table_exists():
            logger.warning(f"Table {collection.name} does not exist yet, skipping")
            return [],[]

        for row in Torrent_file.select():

            html_dict = {
                "infohash": row.infohash,
                "link": row.src_url,
                "type": collection.name,
                "size_bytes": row.size,
                "seeders": row.tracker_seeder,
                "leechers": row.tracker_leecher,
                "dht_peers": row.dht_peers,
                "tracker_scraped": row.tracker_scraped,
                "dht_scraped": row.dht_scraped,
                "last_updated": max_none(row.tracker_scraped, row.dht_scraped)
            }
            json_dict = {
                "name": row.tf_comment,
                "link": row.src_url,
                "created_unix": row.tf_creation_date,
                "size_bytes": row.size,
                "type": collection.name,
                "infohash": row.infohash,
                "seeders": row.tracker_seeder,
                "leechers": row.tracker_leecher,
                "completed": row.tracker_compleeted,
                "scraped_date": row.tracker_scraped,
                "dht_peers": row.dht_peers,
                "dht_scraped": row.dht_scraped,
            }

            data_html.append(html_dict)
            data_json.append(json_dict)

        return data_html, data_json

    def generate_json(self):
        json_out = json.dumps(self.data_json, cls=ByteValueJSONEncoder)
        with open(self.path_json_out, "w") as fd:
            fd.write(json_out)
        logger.info(f"JSON written to {self.path_json_out}")


    def fill_html_template(self, data, template_file, out_file, name="HTML"):
        template = self.template_env.get_template(template_file)
        output = template.render(data=data, update_time=datetime.utcnow())
        with open(out_file, "w") as fd:
            fd.write(output)
        logger.info(f"{name} written to {template_file}")

    def generate_stats(self):
        stats = {}
        for collection in self.collection_list:
            try:
                count = create_dynamic_table_model(collection.name).select().count()
            except OperationalError:
                count = "n/a"
            stats[collection.name]=count

        self.fill_html_template(stats, self.stats_html_template_file, self.path_stats_out, name="Stats")

    def generate_html(self):
        self.fill_html_template(self.data_html, self.torrent_html_template_file, self.path_html_out, name="HTML")



if __name__ == "__main__":
    #ogen = OutputGenerator([libgen_r])
    ogen = OutputGenerator()
    #ogen.generate_json()
    #ogen.generate_html()
    #ogen.generate_stats()
    #ogen.refresh(s)
