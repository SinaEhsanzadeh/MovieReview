import logging
import sys
from logging.config import dictConfig

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": sys.stdout
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "movie_rating.log",
            "mode": "a"
        }
    },
    "loggers": {
        "movie_rating": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO"
    }
}

def setup_logging():
    dictConfig(LOG_CONFIG)
    logger = logging.getLogger("movie_rating")
    logger.info("Logging configured successfully")