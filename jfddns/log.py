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
        'CONFIGURATION_ERROR': 52,
        'DNS_SERVER_ERROR': 51,
        'PARAMETER_ERROR': 41,
        'UPDATED': 22,
        'UNCHANGED': 21,
    }

    def __init__(self):
        self._setup_logging()

    def _setup_logging():
        for log_level, log_level_num in self.log_levels:
            logging.addLevelName(log_level_num, log_level)

        self.logger = logging.getLogger('jfddns')
        handler = logging.FileHandler('jfddns.log')
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def message(text, level='info'):
        log_message = getattr(logger, level)
        log_message(text)
        return text
