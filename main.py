import asyncio

from tsmd.logging_loader import logger
from tsmd.config_loader import config

from tsmd.collection import Collection
from tsmd.torrent_file_sync import TorrentFileSync
from tsmd.dht_swarm_monitor import DHTSwarmMonitor
from tsmd.udp_tracker_swarm_monitor import UDPTrackerSwarmMonitor
from tsmd.output_generator import OutputGenerator

__version__ = "v0.0.1"
__banner__ = f"Starting up [:TSMD:]torrent_swarm_monitoring_daemon {__version__}"


async def example_run_one(collection_name):
    collection = Collection(collection_name)
    TorrentFileSync(collection)

    #### DHT crawl all infohash
    dht_swarm_monitor = DHTSwarmMonitor()
    await dht_swarm_monitor.async_init()
    await dht_swarm_monitor.run(collection)

    #### UDP scrape tracker for all infohash
    monitor = UDPTrackerSwarmMonitor()
    monitor.run(collection)

    ogen = OutputGenerator()


async def example_run_all():

    #### load and syn torrent collections
    TorrentFileSync()

    #### DHT crawl all infohash
    dht_swarm_monitor = DHTSwarmMonitor()
    await dht_swarm_monitor.async_init()
    await dht_swarm_monitor.run()

    #### UDP srape tracker for all infohash
    monitor = UDPTrackerSwarmMonitor()
    monitor.run()

    ogen = OutputGenerator()


def main():
    #asyncio.run(example_run_one("aa-ia"))
    #asyncio.run(example_run_one("libgen_r"))
    asyncio.run(example_run_all())

if __name__ == "__main__":
    logger.info(__banner__)
    main()
