import logging
import logging.handlers as handlers

LOG_FILE = "/var/log/heating/heating.log"


def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    try:
        fh = handlers.RotatingFileHandler(LOG_FILE, maxBytes=2000000, backupCount=2)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except:
        pass

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
