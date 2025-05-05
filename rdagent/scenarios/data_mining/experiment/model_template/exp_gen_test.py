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
        name: str,
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ) -> None:
        """
        Initialize the logger.

        Parameters
        ----------
        name : str
            Name of the logger.
        level : int, optional
            Logging level. Defaults to logging.INFO.
        log_file : Optional[str], optional
            Path to the log file. If None, logs are not written to a file. Defaults to None.
        log_format : str, optional
            Format of the log messages.
            Defaults to "%(asctime)s - %(name)s - %(levelname)s - %(message)s".
        """

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = logging.Formatter(log_format)

        # Stream handler for console output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # File handler for file output
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message at the DEBUG level.

        Parameters
        ----------
        msg : str
            The message to be logged.
        *args : Any
            Positional arguments to be passed to the logging function.
        **kwargs : Any
            Keyword arguments to be passed to the logging function.
        """
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message at the INFO level.

        Parameters
        ----------
        msg : str
            The message to be logged.
        *args : Any
            Positional arguments to be passed to the logging function.
        **kwargs : Any
            Keyword arguments to be passed to the logging function.
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message at the WARNING level.

        Parameters
        ----------
        msg : str
            The message to be logged.
        *args : Any
            Positional arguments to be passed to the logging function.
        **kwargs : Any
            Keyword arguments to be passed to the logging function.
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message at the ERROR level.

        Parameters
        ----------
        msg : str
            The message to be logged.
        *args : Any
            Positional arguments to be passed to the logging function.
        **kwargs : Any
            Keyword arguments to be passed to the logging function.
        """
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message at the CRITICAL level.

        Parameters
        ----------
        msg : str
            The message to be logged.
        *args : Any
            Positional arguments to be passed to the logging function.
        **kwargs : Any
            Keyword arguments to be passed to the logging function.
        """
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message at the ERROR level with exception information.

        Parameters
        ----------
        msg : str
            The message to be logged.
        *args : Any
            Positional arguments to be passed to the logging function.
        **kwargs : Any
            Keyword arguments to be passed to the logging function.
        """
        self.logger.exception(msg, *args, **kwargs)