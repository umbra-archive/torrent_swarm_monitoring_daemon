import time
import itertools
import requests

# import redis
import secrets
from aiobtdht import DHT
from aioudp import UDPServer
import asyncio

from .collection import Collection
from .schema import create_dynamic_table_model, db
from .logging_loader import logger
from .cache_cfg import redis_client, ip_port_to_int, int_to_ip_port
from .config_loader import config

### DHT will only tell use what peers exist for a given infohash
### no info about the compleetness of the torrent is included
### for this info we need to make use of the bittorent protocol


class DHTSwarmMonitor:
    def __init__(self, udp_port=None, bind_address=None, lookup_parallelism=30):
        # only read from config if not provided as arguments
        if udp_port:
            self.udp_port = udp_port
        else:
            self.udp_port = config["dht"]["listening_port_udp"]

        if bind_address:
            self.bind_address = bind_address
        else:
            self.bind_address = config["dht"]["listening_ip"]

        if lookup_parallelism:
            self.lookup_parallelism = lookup_parallelism
        else:
            self.lookup_parallelism = config["dht"]["lookup_parallelism"]

        self.loop = asyncio.get_event_loop()
        self.dht = None
        self.semaphore = asyncio.Semaphore(self.lookup_parallelism)
        ## too big and sqlite will freeze for a while..
        self.db_batch_update_size = 70
        ### redis is not currently used
        ### only needed for deduplicating peers from DHT and peers from tracker
        self.save_to_redis = False

    async def async_init(self):
        initial_nodes = [
            ("67.215.246.10", 6881),  # router.bittorrent.com
            ("87.98.162.88", 6881),  # dht.transmissionbt.com
            ("82.221.103.244", 6881),  # router.utorrent.com
        ]

        udp = UDPServer()
        udp.run(self.bind_address, self.udp_port, loop=self.loop)

        local_node_identifier = secrets.randbits(16 * 8)
        self.dht = DHT(local_node_identifier, server=udp, loop=self.loop)

        logger.info(
            f"Bootstrapping DHT node on interface:port {self.bind_address}:{self.udp_port}"
        )
        await self.dht.bootstrap(initial_nodes)
        logger.debug("DHT Bootstrap done")

    async def _find_torrent(self, infohash):
        # note that iobtdht is deigned in a way that dht lookups are invoked via
        # dht (<class 'aiobtdht.dht.DHT'>) as a 'list read' ( __getitem__)
        logger.debug(f"Searching for torrent with infohash: {infohash.hex()}")
        result = await self.dht[infohash]
        return infohash, result

    async def _limited_find_torrent(self, infohash):
        async with self.semaphore:
            return await self._find_torrent(infohash)

    async def run(self, collection=None):
        if collection == None:
            collection = [Collection(d) for d in config["collection_enabled"].keys()]

        if isinstance(collection, list):
            for c in collection:
                self.run(c)
            return
        table_name = collection.name
        model = create_dynamic_table_model(table_name)
        query = model.select(model.infohash)
        infohash_list = [bytes.fromhex(item.infohash) for item in query]

        completed_tasks = set()
        tasks = set(
            asyncio.create_task(self._limited_find_torrent(infohash))
            for infohash in infohash_list
        )

        logger.info(f"Starting DHT crawl for {len(tasks)} infohash")
        while tasks:
            done_tmp, tasks = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )
            completed_tasks.update(done_tmp)
            logger.debug(f"DHT lookup status {len(completed_tasks)} / {len(tasks)}")

            if len(completed_tasks) > self.db_batch_update_size:
                ## the underlying lib, aiodht has some bugs,
                ## Not To Self:
                ## next line would be and okay place for exception handeling
                ## (and again further down)
                ## unroll expression and try/except Exception as e:
                results = [await task for task in completed_tasks]

                self._save_data(table_name, results, model)
                completed_tasks = set()

        results = [await task for task in completed_tasks]

        self._save_data(table_name, results, model)
        logger.info("DHT crawl complete")

    def _save_data(self, table_name, results, model):
        logger.debug(f"Saving {len(results)} DHT results to sqlite:{table_name}")

        for r in results:
            dht_count = len(r[1])
            infohash_hex = r[0].hex()
            logger.debug("Found: {dht_count} peers for infohash: {infohash_hex}")
            query = model.update(dht_peers=dht_count, dht_scraped=int(time.time())).where(
                model.infohash == infohash_hex
            )
            query.execute()

        if self.save_to_redis:
            logger.info("Saving DHT peer to redis")
            self._save_data_redis()

    def _save_data_redis(table_name, results):
        ## WIP
        with redis_client[table_name].pipeline() as pipeline:
            for r in results:
                key = r[0].hex()
                value_set = [ip_port_to_int(ip, port) for (ip, port) in r[1]]
                pipeline.sadd(key, *value_set)
            pipeline.execute()


async def main():
    monitor = DHTSwarmMonitor(
        lookup_parallelism=40, udp_port=12345, bind_address="0.0.0.0"
    )
    # monitor = DHTSwarmMonitor(DEBUG_stop_after_N=10)
    await monitor.async_init()
    await monitor.run(Collection("libgen_r"))

if __name__ == "__main__":
    asyncio.run(main())
