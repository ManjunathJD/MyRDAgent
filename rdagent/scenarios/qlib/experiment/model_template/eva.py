import logging
import sys
from typing import Optional

class LogFormatter(logging.Formatter):
    """Custom log formatter."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        """
        Init LogFormatter.

        Args:
            fmt (str): format string.
            datefmt (str): date format string.
        """
        if fmt is None:
            fmt = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"

        logging.Formatter.__init__(self, fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format record."""
        return logging.Formatter.format(self, record)

def get_stream_logger(name: str = "default", level: int = logging.INFO, formatter: Optional[logging.Formatter] = None) -> logging.Logger:
    """
    Get stream logger.

    Args:
        name (str): name of logger.
        level (int): log level.
        formatter (logging.Formatter): formatter.

    Returns:
        logging.Logger: logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if formatter is None:
        formatter = LogFormatter()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger