import logging
import logging.config
import os


def setup_logging():
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
    )
