import logging
import logging.handlers as handlers

LOG_FILE = "/var/log/heating/heating.log"
BACKUP_LOG_FILE = "heating.log"


def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(levelname)s:\t  %(message)s [%(asctime)s] (%(name)s)")

    try:
        fh = handlers.RotatingFileHandler(LOG_FILE, maxBytes=2000000, backupCount=2)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except PermissionError:
        fh = handlers.RotatingFileHandler(BACKUP_LOG_FILE, maxBytes=2000000, backupCount=2)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
