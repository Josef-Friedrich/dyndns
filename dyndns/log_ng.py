"""Bundle the logging functionality."""

from __future__ import annotations

import logging
from enum import Enum

from typing_extensions import TypedDict

from dyndns.types import RecordType


class Update(TypedDict):
    update_time: str
    updated: bool
    fqdn: str
    record_type: str
    ip: str


class LogLevel(Enum):
    CONFIGURATION_ERROR = 51

    DNS_SERVER_ERROR = 51

    CRITICAL = 50
    """Python default"""

    DNS_NAME_ERROR = 41

    PARAMETER_ERROR = 41

    ERROR = 40
    """Python default"""

    WARNING = 30
    """Python default"""

    UPDATED = 21

    INFO = 20
    """Python default"""

    UNCHANGED = 11

    DEBUG = 10
    """Python default"""

    NOTSET = 0
    """Python default"""


class Logger:
    __logger: logging.Logger

    def __init__(self) -> None:
        for log_level in LogLevel:
            logging.addLevelName(log_level.value, log_level.name)

        self.__logger = logging.getLogger("dyndns-ng")
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.__logger.addHandler(stream_handler)
        self.__logger.setLevel(logging.DEBUG)

    def log(self, log_level: LogLevel, message: object) -> None:
        self.__logger.log(log_level.value, message)

    def log_update(
        self, updated: bool, fqdn: str, record_type: RecordType, ip: str
    ) -> None:
        level: LogLevel
        if updated:
            level = LogLevel.UPDATED
        else:
            level = LogLevel.UNCHANGED
        self.log(level, f"{fqdn} {record_type} {ip}")

    def set_level(self, level: int | LogLevel) -> None:
        if isinstance(level, LogLevel):
            self.__logger.setLevel(level.value)
        else:
            self.__logger.setLevel(level)


logger = Logger()
