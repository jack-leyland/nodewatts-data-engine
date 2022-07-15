import logging

def setup_logger(verbose, name):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    if verbose:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s::%(levelname)s::%(name)s::%(module)s %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger