"""Bundle the logging functionality."""

from __future__ import annotations

import logging

from typing_extensions import TypedDict

from dyndns.types import LogLevel, RecordType


class Update(TypedDict):
    update_time: str
    updated: bool
    fqdn: str
    record_type: str
    ip: str


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

    def log(self, log_level: LogLevel, message: object) -> str:
        self.__logger.log(log_level.value, message)
        return f"{log_level.name}: {message}\n"

    def log_update(
        self, updated: bool, fqdn: str, record_type: RecordType, ip: str
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
