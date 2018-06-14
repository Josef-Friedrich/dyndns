"""Bundles the logging functionality."""

import logging


class Message(object):

    # CRITICAL 	50
    # ERROR 	40
    # WARNING 	30
    # INFO 	20
    # DEBUG 	10
    # NOTSET 	0

    log_levels = {
        'CONFIGURATION_ERROR': 49,
        'DNS_SERVER_ERROR': 48,
        'PARAMETER_ERROR': 39,
        'UPDATED': 19,
        'UNCHANGED': 9,
    }

    def _log_level_num(self, log_level):
        return self.log_levels[log_level]

    def __init__(self):
        self._setup_logging()

    def _setup_logging(self):
        for log_level, log_level_num in self.log_levels.items():
            logging.addLevelName(log_level_num, log_level)

        self.logger = logging.getLogger('jfddns')
        handler = logging.FileHandler('jfddns.log')
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def message(self, msg, log_level):
        self.logger.log(self._log_level_num(log_level), msg)
        return '{}: {}'.format(log_level, msg)


message = Message()
msg = message.message
