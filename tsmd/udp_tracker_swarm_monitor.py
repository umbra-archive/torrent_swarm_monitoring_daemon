import time

from tracker_scraper import scrape
from .schema import create_dynamic_table_model, db
from .config_loader import config
from .collection import Collection
from .logging_loader import logger


class UDPTrackerSwarmMonitor:
    def __init__(self):
        self.UDP_max_retry = 3
        self.UDP_max_infohash = 70  # max 73 infohash fit in a UDP package..
        self.UDP_retry_sleep = 3

    def run(self, collection=None, tracker=None):
        if collection is None:
            collection = [Collection(d) for d in config["collection_enabled"].keys()]

        if isinstance(collection, list):
            for c in collection:
                self.run(c)
            return

        if not tracker:
            tracker = config["tracker"]["udp_uri"]
        logger.info(f"Running UDP tracker scaper. Querying URL: {tracker}")

        model = create_dynamic_table_model(collection.name)
        query = model.select(model.infohash)
        infohash_list = [item.infohash for item in query]

        logger.debug(
            f"Searching peers for {len(infohash_list)} infohash from collection: {collection.name}"
        )
        slice_size = self.UDP_max_infohash
        for i in range(0, len(infohash_list), slice_size):
            data = {}
            current_slice = infohash_list[i : i + slice_size]

            for r in range(self.UDP_max_retry):
                try:
                    data = scrape(tracker=tracker, hashes=current_slice)
                    break
                except TimeoutError:
                    logger.warning(f"Failed UDP tracker scrape attempt, retry: [{r+1}/{self.UDP_max_retry}]")
                    time.sleep(self.UDP_retry_sleep)

            else:
                logger.error(f"UDP tracker scrape failed for slice. Max retries reached {self.UDP_max_retry}")
                time.sleep(self.UDP_retry_sleep * 5)

            logger.debug(f"Result from {tracker}: {data}")
            self._save(data, model)

    def _save(self, data, model):
        logger.debug(f"Saving {len(data)} results from udp tracker")
        timestamp = int(time.time())

        for infohash, v in data.items():
            query = model.update(
                tracker_seeder=v["seeds"],
                tracker_leecher=v["peers"],
                tracker_scraped=timestamp,
                tracker_compleeted=v["complete"],
            ).where(model.infohash == infohash)
            query.execute()


def main():
    monitor = UDPTrackerSwarmMonitor()
    monitor.run(Collection("libgen_r"))


if __name__ == "__main__":
    main()
