import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from rdagent.log.storage import Storage


class Logger(logging.Logger):
    """Custom logger class for enhanced logging capabilities."""

    def __init__(
        self,
        name: str = "rdagent",
        level: int = logging.INFO,
        formatter: Optional[logging.Formatter] = None,
        handlers: Optional[List[logging.Handler]] = None,
    ):
        """Initialize the logger with custom settings.

        Args:
            name (str): The name of the logger.
            level (int): The minimum logging level to be captured.
            formatter (logging.Formatter): The format for log messages.
            handlers (List[logging.Handler]): List of handlers for the logger.
        """
        super().__init__(name, level)

        if formatter is None:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        if handlers is None:
            # default handler to console
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.addHandler(ch)
        else:
            for handler in handlers:
                handler.setFormatter(formatter)
                self.addHandler(handler)

    def log_file(
        self,
        storage_path: str,
        name: str = "file_logger",
        level: int = logging.INFO,
        formatter: Optional[logging.Formatter] = None,
    ) -> None:
        """Add a file handler to log messages to a file.

        Args:
            storage_path (str): The directory to store the log file.
            name (str): The base name of the log file.
            level (int): The minimum logging level to log to the file.
            formatter (logging.Formatter): The format for log messages.
        """
        if formatter is None:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        os.makedirs(storage_path, exist_ok=True)
        file_path = os.path.join(storage_path, name + ".log")

        fh = logging.FileHandler(file_path)
        fh.setFormatter(formatter)
        fh.setLevel(level)
        self.addHandler(fh)

    def set_level(self, level: Union[str, int]) -> None:
        """Set the logging level for the logger.

        Args:
            level (Union[str, int]): The logging level to set.
        """
        if isinstance(level, str):
            level = logging.getLevelName(level.upper())
        self.setLevel(level)
        for hdlr in self.handlers:
            hdlr.setLevel(level)

    def get_level(self) -> int:
        """Get the current logging level for the logger.

        Returns:
            int: The current logging level.
        """
        return self.level

    def info(self, msg: str, *args, **kwargs):
        super().info(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        super().error(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        super().warning(msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        super().debug(msg, *args, **kwargs)

    def log(self, level: int, msg: str, *args, **kwargs):
        """Log a message with the specified level."""
        super().log(level, msg, *args, **kwargs)


# Create and configure a default logger instance
logger = Logger()