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

    This class provides methods for logging messages at different levels, including
    debug, info, warning, error, and critical. It also supports logging to both the
    console and a file.

    """

    _logger = None
    _log_level = logging.INFO
    _log_path = ""
    _log_file = ""

    @classmethod
    def set_level(cls, level: Union[str, int]):
        """Set the logging level."""
        if isinstance(level, str):
            level = logging._nameToLevel.get(level, logging.INFO)
        cls._log_level = level
        if cls._logger:
            cls._logger.setLevel(cls._log_level)

    @classmethod
    def set_path(cls, path: str):
        """Set the log path."""
        cls._log_path = path
        cls._setup_logger()

    @classmethod
    def set_log_file(cls, file: str):
        """Set the log file."""
        cls._log_file = file
        cls._setup_logger()

    @classmethod
    def _setup_logger(cls):
        """Setup the logger."""
        if cls._logger is not None:
            return

        # Create logger
        cls._logger = logging.getLogger(Config.get("app.name"))
        cls._logger.setLevel(cls._log_level)

        # Create console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(cls._log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        ch.setFormatter(formatter)
        cls._logger.addHandler(ch)

        # Create file handler
        if cls._log_path and cls._log_file:
            if not os.path.exists(cls._log_path):
                os.makedirs(cls._log_path)
            fh = logging.FileHandler(
                os.path.join(cls._log_path, cls._log_file), encoding="utf-8"
            )
            fh.setLevel(cls._log_level)
            fh.setFormatter(formatter)
            cls._logger.addHandler(fh)

    @classmethod
    def get_logger(cls):
        """Get the logger."""
        if cls._logger is None:
            cls._setup_logger()
        return cls._logger

    @classmethod
    def debug(cls, msg: Any, *args: Any, **kwargs: Any):
        """Log a debug message."""
        if Env.is_debug() or Env.is_test():
            cls.get_logger().debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg: Any, *args: Any, **kwargs: Any):
        """Log an info message."""
        cls.get_logger().info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg: Any, *args: Any, **kwargs: Any):
        """Log a warning message."""
        cls.get_logger().warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg: Any, *args: Any, **kwargs: Any):
        """Log an error message."""
        cls.get_logger().error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg: Any, *args: Any, **kwargs: Any):
        """Log a critical message."""
        cls.get_logger().critical(msg, *args, **kwargs)

    @classmethod
    def log_df(cls, df: pd.DataFrame, msg: Optional[str] = None):
        """Log a DataFrame."""
        if msg:
            cls.info(msg)
        cls.info(df.to_markdown(index=False))