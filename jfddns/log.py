"""Bundles the logging functionality."""

import logging

logger = logging.getLogger('jfddns')
handler = logging.FileHandler('jfddns.log')
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def msg(text, level='info'):
    log_message = getattr(logger, level)
    log_message(text)
    return text


def message(text, level='info'):
    log_message = getattr(logger, level)
    log_message(text)
    return text


CONFIGURATION_ERROR = 51
logging.addLevelName(CONFIGURATION_ERROR, 'CONFIGURATION_ERROR')

PARAMETER_ERROR = 41
logging.addLevelName(PARAMETER_ERROR, 'PARAMETER_ERROR')

DNS_SERVER_ERROR = 31
logging.addLevelName(DNS_SERVER_ERROR, 'DNS_SERVER_ERROR')

UPDATED = 21
logging.addLevelName(UPDATED, 'UPDATED')

UNCHANGED = 11
logging.addLevelName(UNCHANGED, 'UNCHANGED')
