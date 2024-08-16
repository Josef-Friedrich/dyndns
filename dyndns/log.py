"""Bundle the logging functionality."""

from __future__ import annotations

import logging
import typing
from enum import Enum

from typing_extensions import TypedDict

if typing.TYPE_CHECKING:
    from dyndns.dns import DnsChangeMessage
    from dyndns.types import RecordType


class Update(TypedDict):
    update_time: str
    updated: bool
    fqdn: str
    record_type: str
    ip: str


class LogLevel(Enum):
    CONFIGURATION_ERROR = 53

    DNS_SERVER_ERROR = 52

    IP_ADDRESS_ERROR = 51

    CRITICAL = 50
    """Python default"""

    DNS_NAME_ERROR = 43

    PARAMETER_ERROR = 42

    CHECK_ERROR = 41

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

    @classmethod
    def get_name(cls, value: int) -> str:
        for log_level in cls:
            if log_level.value == value:
                return log_level.name
        raise ValueError(f"No LogLevel with value {value}")

    def log(self, message: str) -> str:
        return logger.log(self.value, message)


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

    def log(self, log_level: LogLevel | int, message: object) -> str:
        level: int
        name: str
        if isinstance(log_level, LogLevel):
            level = log_level.value
            name = log_level.name
        else:
            level = log_level
            name = LogLevel.get_name(level)
        self.__logger.log(level, message)
        return f"{name}: {message}\n"

    def log_change(self, message: "DnsChangeMessage") -> str:
        if message.old == message.new:
            return self.log(
                LogLevel.UNCHANGED,
                f"{message.fqdn} {message.record_type} {message.new}",
            )
        else:
            return self.log(
                LogLevel.UPDATED,
                f"{message.fqdn} {message.record_type} {message.old} -> {message.new}",
            )

    def log_update(
        self, updated: bool, fqdn: str, record_type: "RecordType", ip: str
    ) -> str:
        level: LogLevel
        if updated:
            level = LogLevel.UPDATED
        else:
            level = LogLevel.UNCHANGED
        return self.log(level, f"{fqdn} {record_type} {ip}")

    def set_level(self, level: int | LogLevel) -> None:
        if isinstance(level, LogLevel):
            self.__logger.setLevel(level.value)
        else:
            self.__logger.setLevel(level)


logger = Logger()
