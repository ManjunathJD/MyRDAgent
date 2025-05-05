import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from rdagent.core.conf import Config
from rdagent.utils.env import Env


class Logger:
    """
    Wrapper class for logging.

    This class provides methods for logging messages at different levels, and supports writing
    logs to both console and file.

    """

    def __init__(
        self,
        log_name: str = None,
        log_path: Optional[str] = None,
        log_level: Union[str, int] = "INFO",
        log_to_file: bool = True,
        log_to_console: bool = True,
        file_mode: str = "a",
    ):
        """
        Initialize the Logger.

        Args:
            log_name (str): The name of the logger.
            log_path (Optional[str]): The path to the log file.
            log_level (Union[str, int]): The log level.
            log_to_file (bool): Whether to write logs to a file.
            log_to_console (bool): Whether to write logs to the console.
            file_mode(str): file mode for log, default is 'a'
        """
        self.log_name = log_name or Env.get_task_id() or "rdagent"
        self.log_level = log_level
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        self.file_mode = file_mode

        self.logger = logging.getLogger(self.log_name)
        self.logger.propagate = False
        self.logger.setLevel(self.log_level)

        self.log_path = log_path or Config.get_log_path()
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path, exist_ok=True)

        self.formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        if self.log_to_file:
            self._add_file_handler()

        if self.log_to_console:
            self._add_stream_handler()

    def _add_file_handler(self):
        """Add a file handler to the logger."""
        file_name = os.path.join(self.log_path, f"{self.log_name}.log")
        file_handler = logging.FileHandler(file_name, mode=self.file_mode, encoding="utf-8")
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def _add_stream_handler(self):
        """Add a stream handler to the logger."""
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(stream_handler)

    def debug(self, msg: str, *args, **kwargs):
        """Log a message with severity 'DEBUG'."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log a message with severity 'INFO'."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log a message with severity 'WARNING'."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log a message with severity 'ERROR'."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log a message with severity 'CRITICAL'."""
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, exc_info=True, **kwargs):
        """Log a message with severity 'ERROR' and exception information."""
        self.logger.error(msg, *args, exc_info=exc_info, **kwargs)

    def log(self, level: int, msg: str, *args, **kwargs):
        """Log a message with the given severity."""
        self.logger.log(level, msg, *args, **kwargs)


def get_logger(
    log_name: Optional[str] = None,
    log_path: Optional[str] = None,
    log_level: Union[str, int] = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    file_mode: str = "a",
) -> logging.Logger:
    """Get a logger instance."""
    return Logger(log_name, log_path, log_level, log_to_file, log_to_console, file_mode).logger