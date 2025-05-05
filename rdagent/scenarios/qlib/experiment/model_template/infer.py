import logging
import sys
from typing import Optional

class LogFormatter(logging.Formatter):
    """
    Custom log formatter with color support for console output.
    """

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_format = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: grey + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    """
    Singleton logger for logging messages.
    """

    _instance = None

    def __new__(cls, name: str = "RD-Agent", level: Optional[int] = None):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.name = name
            cls._instance.logger = logging.getLogger(name)
            if level is None:
                level = logging.INFO
            cls._instance.logger.setLevel(level)

            # Console handler
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(level)
            ch.setFormatter(LogFormatter())
            cls._instance.logger.addHandler(ch)

        return cls._instance

    def get_logger(self):
        """
        Returns the internal logger object.
        """
        return self.logger

    @staticmethod
    def debug(msg, *args, **kwargs):
        """
        Log a debug message.
        """
        Logger().logger.debug(msg, *args, **kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        """
        Log an info message.
        """
        Logger().logger.info(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        """
        Log a warning message.
        """
        Logger().logger.warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        """
        Log an error message.
        """
        Logger().logger.error(msg, *args, **kwargs)

    @staticmethod
    def critical(msg, *args, **kwargs):
        """
        Log a critical message.
        """
        Logger().logger.critical(msg, *args, **kwargs)