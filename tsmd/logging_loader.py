import logging.config
from .config_loader import config

logging_config = config.get("logging", {})
logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)

def main():
    logger.debug("This is an debug message")
    logger.info("This is an info message")
    logger.error("This is an error message")
    logger.warning("This is a warning message")
    logger.critical("This is a critical message")


if "__main__" == __name__:
    main()
