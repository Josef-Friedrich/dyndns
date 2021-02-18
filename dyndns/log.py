"""Bundle the logging functionality."""

import datetime
import logging
import os
import sqlite3


log_file = os.path.join(os.getcwd(), 'dyndns.log')


class DateTime:

    def __init__(self, date_time_string=None):
        if not date_time_string:
            self.datetime = datetime.datetime.now()
        else:
            self.datetime = datetime.datetime.strptime(date_time_string,
                                                       '%Y-%m-%d %H:%M:%S.%f')

    def iso8601(self):
        return self.datetime.isoformat(' ')

    def iso8601_short(self):
        return self.datetime.strftime('%Y-%m-%d %H:%M:%S')


class UpdatesDB:

    def __init__(self):
        self.db_file = os.path.join(os.getcwd(), 'dyndns.db')
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS updates (
                update_time TEXT,
                updated INTEGER,
                fqdn TEXT,
                record_type TEXT,
                ip TEXT
        );""")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fqdns (
                fqdn TEXT
        );""")

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS update_time ON
            updates(update_time);
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS fqdn_updated ON updates(fqdn, updated);
        """)

    def get_fqdns(self):
        self.cursor.execute('SELECT fqdn FROM fqdns;')
        fqdns = self.cursor.fetchall()
        out = []
        for fqdn in fqdns:
            out.append(fqdn[0])
        out.sort()
        return out

    @staticmethod
    def normalize_row(row):
        return {
            'update_time': DateTime(row[0]).iso8601_short(),
            'updated': bool(row[1]),
            'fqdn': row[2],
            'record_type': row[3],
            'ip': row[4],
        }

    def get_updates_by_fqdn(self, fqdn):
        self.cursor.execute('SELECT * FROM updates WHERE updated = 1 AND'
                            ' fqdn = ?;',
                            (fqdn,))
        rows = self.cursor.fetchall()
        out = []
        for row in rows:
            row_dict = self.normalize_row(row)
            out.append(row_dict)
        return out

    def _is_fqdn_stored(self, fqdn):
        self.cursor.execute(
            'SELECT fqdn FROM fqdns WHERE fqdn = ?;',
            (fqdn,)
        )
        return bool(self.cursor.fetchone())

    def log_update(self, updated, fqdn, record_type, ip):
        if not self._is_fqdn_stored(fqdn):
            self.cursor.execute(
                'INSERT INTO fqdns VALUES (?);',
                (fqdn,)
            )

        self.cursor.execute(
            'INSERT INTO updates VALUES (?, ?, ?, ?, ?);',
            (DateTime().iso8601(), int(updated), fqdn, record_type, ip),
        )
        self.cursor.execute(
            "DELETE FROM updates WHERE update_time < "
            "DATETIME('NOW', '-30 day');"
        )
        self.connection.commit()


class Message:

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

        self.logger = logging.getLogger('dyndns')
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
