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
