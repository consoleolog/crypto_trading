import time
import logging
import os

fmt = "[%(levelname)s] %(asctime)s : %(filename)s : %(module)s : %(lineno)d - %(message)s"

datefmt = '%Y-%m-%d %H:%M:%S'

filefmt = '%Y%m%d%H%M'

def get_logger(logging_service="undefined"):
    logger = logging.getLogger(f"{logging_service}_logger")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    file_formatter = logging.Formatter(
        fmt=fmt,
        datefmt=datefmt)
    fh = logging.FileHandler(f"{log_dir}/{logging_service}.log", encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(file_formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    return logger


class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    green = '\x1b[38;5;46m'
    bold_green = '\x1b[32;1m'

    def __init__(self):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.bold_green + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=datefmt)
        return formatter.format(record)

log = get_logger(f"crypto")