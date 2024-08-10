"""Bundle the logging functionality."""

from __future__ import annotations

import datetime
import logging
import os
from enum import Enum

from typing_extensions import TypedDict

from dyndns.types import LogLevel, RecordType

log_file: str = os.path.join(os.getcwd(), "dyndns.log")


class DateTime:
    def __init__(self, date_time_string: str | None = None) -> None:
        if not date_time_string:
            self.datetime = datetime.datetime.now()
        else:
            self.datetime = datetime.datetime.strptime(
                date_time_string, "%Y-%m-%d %H:%M:%S.%f"
            )

    def iso8601(self) -> str:
        return self.datetime.isoformat(" ")

    def iso8601_short(self) -> str:
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")


class Update(TypedDict):
    update_time: str
    updated: bool
    fqdn: str
    record_type: str
    ip: str


class LogLevelEnum(Enum):
    CONFIGURATION_ERROR = 51
    DNS_SERVER_ERROR = 51
    PARAMETER_ERROR = 41
    UPDATED = 21
    UNCHANGED = 11


class Logger:
    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0

    __logger: logging.Logger

    log_levels: dict[str, int] = {
        "CONFIGURATION_ERROR": 51,
        "DNS_SERVER_ERROR": 51,
        "PARAMETER_ERROR": 41,
        "UPDATED": 21,
        "UNCHANGED": 11,
    }

    def __init__(self) -> None:
        for log_level, log_level_num in self.log_levels.items():
            logging.addLevelName(log_level_num, log_level)

        self.__logger = logging.getLogger("dyndns")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.__logger.addHandler(stream_handler)
        self.__logger.setLevel(logging.DEBUG)

    def _log_level_num(self, log_level: LogLevel) -> int:
        return self.log_levels[log_level]

    def log(self, msg: str, log_level: LogLevel) -> str:
        self.__logger.log(self._log_level_num(log_level), msg)
        return "{}: {}\n".format(log_level, msg)

    def log_update(
        self, updated: bool, fqdn: str, record_type: RecordType, ip: str
    ) -> None:
        message = f"{fqdn} {record_type} {ip}"
        if updated:
            self.log(message, "UPDATED")
        else:
            self.log(message, "UNCHANGED")


logger = Logger()
