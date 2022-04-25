import logging
import logging.handlers as handlers

LOG_FILE = "/var/log/heating/heating.log"
BACKUP_LOG_FILE = "heating.log"


def get_logger(name=__name__, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s"
    )

    try:
        fh = handlers.RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=2)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except PermissionError:
        fh = handlers.RotatingFileHandler(
            BACKUP_LOG_FILE, maxBytes=2000000, backupCount=2
        )
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass

    ch = logging.StreamHandler()
    ch.setLevel(level)

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


if __name__ == "__main__":
    l = get_logger('test')
    l.info("hello\n\t\t  hello")
