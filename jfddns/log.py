"""Bundles the logging functionality."""

import datetime
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
                update_time TEXT,
                fqdn TEXT,
                record_type TEXT,
                ip TEXT
        );""")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fqdns (
                fqdn TEXT
        );""")

    @staticmethod
    def _now_to_iso8601():
        return datetime.datetime.now().isoformat(' ')

    @staticmethod
    def _iso8601_to_datetime(iso8601):
        return datetime.datetime.strptime(iso8601, "%Y-%m-%d %H:%M:%S.%f")

    def get_fqdns(self):
        self.cursor.execute('SELECT fqdn FROM fqdns;')
        fqdns = self.cursor.fetchall()
        out = []
        for fqdn in fqdns:
                out.append(fqdn[0])
        out.sort()
        return out

    def get_updates_by_fqdn(self, fqdn):
        self.cursor.execute('SELECT * FROM updates where fqdn = ?;',
                            (fqdn,))
        return self.cursor.fetchall()

    def _is_fqdn_stored(self, fqdn):
        self.cursor.execute(
            'SELECT fqdn FROM fqdns WHERE fqdn = ?;',
            (fqdn,)
        )
        return bool(self.cursor.fetchone())

    def log_update(self, fqdn, record_type, ip):
        if not self._is_fqdn_stored(fqdn):
            self.cursor.execute(
                'INSERT INTO fqdns VALUES (?);',
                (fqdn,)
            )

        update_time = self._now_to_iso8601()
        self.cursor.execute(
            'INSERT INTO updates VALUES (?, ?, ?, ?);',
            (update_time, fqdn, record_type, ip),
        )
        self.connection.commit()


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
        return '{}: {}\n'.format(log_level, msg)


message = Message()
msg = message.message
