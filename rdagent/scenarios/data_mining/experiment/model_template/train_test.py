import logging
import os
import sys
from typing import Any, Dict, Optional, Union

import qlib
from qlib.config import REG_CN

from rdagent.log.storage import LogStorage


class Logger:
    """
    A general logger for RDAgent.

    Parameters
    ----------
    name : str
        The name of the logger.
    level : int, optional
        The logging level, by default logging.INFO.
    log_path : str, optional
        The path to store the log file, by default None.
    enable_console : bool, optional
        Whether to enable console output, by default True.
    """

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        log_path: Optional[str] = None,
        enable_console: bool = True,
    ):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        # Avoid duplicate loggers.
        if self._logger.hasHandlers():
            return

        if log_path:
            log_dir = os.path.dirname(log_path)
            os.makedirs(log_dir, exist_ok=True)
            fh = logging.FileHandler(log_path)
            fh.setLevel(level)
            self._logger.addHandler(fh)

        if enable_console:
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(level)
            self._logger.addHandler(ch)

        formatter = logging.Formatter(
            "[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d] %(message)s"
        )
        for hdlr in self._logger.handlers:
            hdlr.setFormatter(formatter)

    def __getattr__(self, name: str):
        return getattr(self._logger, name)


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_path: Optional[str] = None,
    enable_console: bool = True,
) -> Logger:
    """
    Get a general logger for RDAgent.

    Parameters
    ----------
    name : str
        The name of the logger.
    level : int, optional
        The logging level, by default logging.INFO.
    log_path : str, optional
        The path to store the log file, by default None.
    enable_console : bool, optional
        Whether to enable console output, by default True.

    Returns
    -------
    Logger
        The general logger for RDAgent.
    """
    return Logger(name, level, log_path, enable_console)


class LogFilter(logging.Filter):
    """
    Log filter that filters out log records with a specific message.
    """

    def __init__(self, filtered_message):
        super().__init__()
        self.filtered_message = filtered_message

    def filter(self, record):
        return record.getMessage() != self.filtered_message


class BaseLog:
    """
    Base class for logs.
    """

    LOG_FILE = "log.log"
    DEFAULT_LOGGER_NAME = "default"

    def __init__(
        self,
        log_path: Optional[str] = None,
        log_level: int = logging.INFO,
        logger_name: str = DEFAULT_LOGGER_NAME,
        log_storage_conf: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.log_path = log_path
        self.log_level = log_level
        self.logger_name = logger_name
        self.logger = self.get_logger()
        self.log_storage = LogStorage(**(log_storage_conf or {})) if log_storage_conf is not None else LogStorage()

    def get_logger(self) -> logging.Logger:
        """
        Get the logger.

        Returns
        -------
        logging.Logger
            The logger.
        """
        log_path = self.log_path
        if log_path is None:
            log_path = os.path.join(os.getcwd(), self.LOG_FILE)
        self.logger = get_logger(self.logger_name, self.log_level, log_path)
        return self.logger

    def _log_handler(self, level: int, msg: str, *args, **kwargs) -> None:
        """
        Handler for log.

        Parameters
        ----------
        level : int
            The logging level.
        msg : str
            The logging message.
        *args : tuple
            Additional arguments.
        **kwargs : dict
            Additional keyword arguments.
        """
        self.logger.log(level, msg, *args, **kwargs)
        self.log_storage.add_log(msg)

    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        """
        Log a message.

        Parameters
        ----------
        level : int
            The logging level.
        msg : str
            The logging message.
        *args : tuple
            Additional arguments.
        **kwargs : dict
            Additional keyword arguments.
        """
        self._log_handler(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs) -> None:
        """
        Log a debug message.

        Parameters
        ----------
        msg : str
            The logging message.
        *args : tuple
            Additional arguments.
        **kwargs : dict
            Additional keyword arguments.
        """
        self._log_handler(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """
        Log an info message.

        Parameters
        ----------
        msg : str
            The logging message.
        *args : tuple
            Additional arguments.
        **kwargs : dict
            Additional keyword arguments.
        """
        self._log_handler(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """
        Log a warning message.

        Parameters
        ----------
        msg : str
            The logging message.
        *args : tuple
            Additional arguments.
        **kwargs : dict
            Additional keyword arguments.
        """
        self._log_handler(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """
        Log an error message.

        Parameters
        ----------
        msg : str
            The logging message.
        *args : tuple
            Additional arguments.
        **kwargs : dict
            Additional keyword arguments.
        """
        self._log_handler(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """
        Log a critical message.

        Parameters
        ----------
        msg : str
            The logging message.
        *args : tuple
            Additional arguments.
        **kwargs : dict
            Additional keyword arguments.
        """
        self._log_handler(logging.CRITICAL, msg, *args, **kwargs)

    def set_log_level(self, level: int) -> None:
        """
        Set the log level.

        Parameters
        ----------
        level : int
            The logging level.
        """
        self.logger.setLevel(level)
        for hdlr in self.logger.handlers:
            hdlr.setLevel(level)
        self.log_level = level

    def set_log_path(self, log_path: str) -> None:
        """
        Set the log path.

        Parameters
        ----------
        log_path : str
            The path to store the log file.
        """
        if self.logger is None:
            self.log_path = log_path
            return
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                self.logger.removeHandler(handler)
        fh = logging.FileHandler(log_path)
        fh.setLevel(self.log_level)
        formatter = logging.Formatter(
            "[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d] %(message)s"
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.log_path = log_path

    def add_log_filter(self, log_filter: Union[logging.Filter, LogFilter]):
        """
        Add a log filter.

        Parameters
        ----------
        log_filter : Union[logging.Filter, LogFilter]
            The log filter to add.
        """
        self.logger.addFilter(log_filter)

    def remove_log_filter(self, log_filter: Union[logging.Filter, LogFilter]):
        """
        Remove a log filter.

        Parameters
        ----------
        log_filter : Union[logging.Filter, LogFilter]
            The log filter to remove.
        """
        self.logger.removeFilter(log_filter)

    def set_log_storage(self, log_storage_conf: Dict[str, Any]) -> None:
        self.log_storage = LogStorage(**(log_storage_conf or {}))

    def get_log_storage(self) -> LogStorage:
        return self.log_storage