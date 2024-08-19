"""Bundle the logging functionality."""

from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from dyndns.dns import DnsChangeMessage


class Update(TypedDict):
    update_time: str
    updated: bool
    fqdn: str
    record_type: str
    ip: str


class LogLevel(Enum):
    """
    Define more log levels than the default Pythons levels in order to control
    more precisely what is logged and what is not.

    https://docs.python.org/3/library/logging.html#logging-levels"""

    CRITICAL = 50
    """The Python default log level value for an critical message."""

    CONFIGURATION_ERROR = 49
    """
    If ``dyndns`` has been configured incorrectly.
    This mainly affects the configuration file in YAML format
    (``/etc/dyndns.yml`` oder ``~/.dyndns.yml``).

    :see: :exc:`dyndns.exceptions.ConfigurationError`
    """

    DNS_SERVER_ERROR = 48
    """
    :see: :exc:`dyndns.exceptions.DNSServerError`
    """

    IP_ADDRESS_ERROR = 47
    """
    :see: :exc:`dyndns.exceptions.IpAddressesError`
    """

    DNS_NAME_ERROR = 43
    """
    :see: :exc:`dyndns.exceptions.DnsNameError`
    """

    PARAMETER_ERROR = 42
    """
    :see: :exc:`dyndns.exceptions.ParameterError`
    """

    CHECK_ERROR = 41
    """
    :see: :exc:`dyndns.exceptions.CheckError`
    """

    ERROR = 40
    """The Python default log level value for an error."""

    WARNING = 30
    """The Python default log level value for an warning."""

    UPDATED = 21

    INFO = 20
    """The Python default log level value for an information message."""

    UNCHANGED = 11

    DEBUG = 10
    """The Python default log level value for a debug message."""

    NOTSET = 0
    """The Python default log level value for an not set log level."""

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

    def set_level(self, level: int | LogLevel) -> None:
        if isinstance(level, LogLevel):
            self.__logger.setLevel(level.value)
        else:
            self.__logger.setLevel(level)


logger = Logger()
