"""Define log levels and initialize logger"""

import logging
from datetime import datetime
from enum import IntEnum
from py.utils.directories import FileData


class LogLevel(IntEnum):
    """Valid log levels"""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40

    @classmethod
    def assert_log_level(cls, level: str):
        """Assert that `level` is a valid log level"""
        assert level in list(cls.__members__), f"{level} is not a valid log level"


def initialize_logger(log_level: str):
    """Initialize Logger"""

    # Validate log level input
    log_level = log_level.upper()
    LogLevel.assert_log_level(log_level)
    level: LogLevel = LogLevel[log_level]  # type: ignore

    # Get loggger
    logger = logging.getLogger()

    # Define log outout dir
    log_file = FileData.log_dir / f"{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.log"

    # Define log formatter
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler(FileData.log_dir / log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Set log level
    logger.setLevel(level.value)
