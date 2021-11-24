import logging
import logging.handlers as handlers


def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    fh = handlers.RotatingFileHandler('heating2.log', maxBytes=500, backupCount=2)
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "[%(levelname)s] [%(asctime)s] %(message)s (%(name)s)"
    )

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
