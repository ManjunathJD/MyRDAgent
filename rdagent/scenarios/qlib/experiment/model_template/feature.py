import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

from rdagent.core.conf import get_config_path
from rdagent.core.exception import RDException
from rdagent.log.base import BaseLogHandler, LogFormatter
from rdagent.utils import fmt


class Logger:
    _instances = {}
    _default_logger_name = "RDAGENT"
    _log_level = logging.INFO

    def __new__(cls, name=None, level=None):
        if name is None:
            name = cls._default_logger_name
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._init(name, level)
            cls._instances[name] = instance
        return cls._instances[name]

    def _init(self, name, level):
        self._logger = logging.getLogger(name)
        if level is not None:
            self._log_level = level
        self._logger.setLevel(self._log_level)
        self._set_default_handler()

    @classmethod
    def set_default_logger_name(cls, name):
        cls._default_logger_name = name

    @classmethod
    def set_default_log_level(cls, level):
        cls._log_level = level

    def _set_default_handler(self):
        if not self._logger.hasHandlers():
            self.add_stream_handler(self._log_level)

    def add_file_handler(
        self,
        level: int = logging.INFO,
        filename: Optional[str] = None,
        fmt_str: Optional[str] = None,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 5,
    ):
        if fmt_str is None:
            fmt_str = LogFormatter.default_fmt_str()
        formatter = LogFormatter.get_formatter(fmt_str)

        if filename is None:
            log_file_path = get_config_path() / "log"
            if not log_file_path.exists():
                os.makedirs(log_file_path)
            filename = str(log_file_path / f"{self._logger.name}.log")
        else:
            filename = str(Path(filename))

        file_handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

        self._logger.addHandler(file_handler)

    def add_stream_handler(
        self, level: int = logging.INFO, fmt_str: Optional[str] = None
    ):
        if fmt_str is None:
            fmt_str = LogFormatter.default_fmt_str()
        formatter = LogFormatter.get_formatter(fmt_str)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)

        self._logger.addHandler(stream_handler)

    def add_handler(self, handler: BaseLogHandler):
        self._logger.addHandler(handler)

    def remove_handler(self, handler):
        self._logger.removeHandler(handler)

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self._logger.log(level, msg, *args, **kwargs)


def _set_default_logger(name, level):
    Logger.set_default_logger_name(name)
    Logger.set_default_log_level(level)


def _get_logger(name):
    return Logger(name)


def set_logger(name="rdagent", level="info"):
    level_dict = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING}
    if level not in level_dict:
        raise RDException(f"logger level only support {level_dict.keys()}")
    _set_default_logger(name, level_dict[level])
    return _get_logger(name)


def get_logger(name=None):
    if name is None:
        name = Logger._default_logger_name
    return Logger(name)