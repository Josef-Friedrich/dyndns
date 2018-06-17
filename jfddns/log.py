"""Bundles the logging functionality."""

import logging
import os
import sqlite3


log_file = os.path.join(os.getcwd(), 'jfddns.log')


class UpdatesDB(object):

    def __init__(self):
        self.db_file = os.path.join(os.getcwd(), 'jfddns.db')
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS updates (
                update_time DATETIME,
                fqdn TEXT,
                record_type VARCHAR(4),
                ip TEXT
        );""")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fqdn (
                fqdn TEXT
        );""")


class Message(object):

    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0

    log_levels = {
        'CONFIGURATION_ERROR': 51,
        'DNS_SERVER_ERROR': 51,
        'PARAMETER_ERROR': 41,
        'UPDATED': 21,
        'UNCHANGED': 11,
    }

    def __init__(self):
        self._setup_logging()

    def _log_level_num(self, log_level):
        return self.log_levels[log_level]

    def _setup_logging(self):
        for log_level, log_level_num in self.log_levels.items():
            logging.addLevelName(log_level_num, log_level)

        self.logger = logging.getLogger('jfddns')
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def message(self, msg, log_level):
        self.logger.log(self._log_level_num(log_level), msg)
        return '{}: {}'.format(log_level, msg)


message = Message()
msg = message.message
