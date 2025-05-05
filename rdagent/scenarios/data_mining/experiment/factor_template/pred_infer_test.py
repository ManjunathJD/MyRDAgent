import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from rdagent.log.storage import Storage


class Logger:
    """
    A wrapper for the standard logger, which supports multiple output types and provides additional utility methods.

    Attributes:
        logger: The standard Python logger object.
        output_dir (Optional[str]): The directory where log files are stored.
        log_file (Optional[str]): The path to the log file.
        log_format (str): The format string for log messages.
        log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO).
    """

    def __init__(
        self,
        name: str = "RD-Agent",
        output_dir: Optional[str] = None,
        file_name: str = "main.log",
        log_level: int = logging.INFO,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ) -> None:
        """
        Initializes the Logger with the given name, output directory, file name, log level, and log format.

        Args:
            name (str): The name of the logger. Defaults to "RD-Agent".
            output_dir (Optional[str]): The directory for log files. Defaults to None.
            file_name (str): The name of the log file. Defaults to "main.log".
            log_level (int): The logging level. Defaults to logging.INFO.
            log_format (str): The format for log messages.
        """

        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.output_dir: Optional[str] = output_dir
        self.log_file: Optional[str] = None
        if output_dir is not None:
            self.log_file = os.path.join(output_dir, file_name)
            os.makedirs(output_dir, exist_ok=True)
        self.log_format: str = log_format
        self._add_handlers()

    def _add_handlers(self) -> None:
        """
        Adds handlers to the logger for console and file outputs.
        """

        formatter = logging.Formatter(self.log_format)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if self.log_file is not None:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with severity 'DEBUG' on the logger.
        """
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with severity 'INFO' on the logger.
        """
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with severity 'WARNING' on the logger.
        """
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with severity 'ERROR' on the logger.
        """
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with severity 'CRITICAL' on the logger.
        """
        self.logger.critical(message, *args, **kwargs)

    def log(self, level: int, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with an integer severity level on the logger.
        """
        self.logger.log(level, message, *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with severity 'ERROR' on this logger, also recording exception information.
        """
        self.logger.exception(message, *args, **kwargs)

    @classmethod
    def get_instance(cls, name: str = "RD-Agent") -> "Logger":
        """
        Retrieves a logger instance. If one with the given name doesn't exist, a new one is created.

        Args:
            name (str): The name of the logger.

        Returns:
            Logger: The logger instance.
        """
        if name not in logging.Logger.manager.loggerDict:
            logger = cls(name=name)
        else:
            logger = logging.getLogger(name)
        return logger