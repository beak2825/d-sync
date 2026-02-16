"""Logging utilities for d-sync"""

import logging
from pathlib import Path
from datetime import datetime
from .config import LOG_FILE, LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)


class Logger:
    """Custom logger for d-sync"""

    _loggers = {}

    def __new__(cls, name: str):
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)

            # File handler
            fh = logging.FileHandler(LOG_FILE)
            fh.setLevel(logging.DEBUG)

            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            logger.addHandler(fh)
            logger.addHandler(ch)

            cls._loggers[name] = logger

        return cls._loggers[name]

    def __init__(self, name: str):
        pass
