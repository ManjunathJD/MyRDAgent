import logging
import os
import sys
from typing import Any, Dict, Optional, TextIO, Union

from rdagent.log.base import BaseLogger

_logger_initialized = False
_default_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s:%(lineno)d: %(message)s",
    "%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str, level: Optional[int] = None, format_: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the given name and level.
    """
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    if format_ is not None:
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter(format_, "%Y-%m-%d %H:%M:%S"))
    return logger


def init_logger(
    level: int = logging.INFO,
    log_file: Optional[Union[str, os.PathLike]] = None,
    format_: Optional[str] = None,
    stream: Optional[TextIO] = None,
    file_level: Optional[int] = logging.DEBUG,
):
    """
    Initialize the logger.
    """
    global _logger_initialized
    if _logger_initialized:
        return
    _logger_initialized = True

    if format_ is None:
        formatter = _default_formatter
    else:
        formatter = logging.Formatter(format_, "%Y-%m-%d %H:%M:%S")

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if stream is None:
        stream = sys.stdout

    stream_handler = logging.StreamHandler(stream)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_log_record_dict(record: logging.LogRecord) -> Dict[str, Any]:
    """
    Get a dictionary representation of a log record.
    """
    return {
        "name": record.name,
        "levelno": record.levelno,
        "levelname": record.levelname,
        "pathname": record.pathname,
        "filename": record.filename,
        "module": record.module,
        "lineno": record.lineno,
        "funcName": record.funcName,
        "asctime": record.asctime,
        "message": record.getMessage(),
    }


class RDLogger(BaseLogger):
    """
    RDLogger is a wrapper around the standard Python logger.
    """

    def __init__(self, name: str, level: int = logging.INFO, format_: Optional[str] = None):
        self.logger = get_logger(name, level, format_)

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args, exc_info=True, **kwargs):
        self.logger.exception(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)