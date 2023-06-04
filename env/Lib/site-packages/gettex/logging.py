import logging


def get_logger(verbose):
    logger = logging.getLogger("gettex")
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger
