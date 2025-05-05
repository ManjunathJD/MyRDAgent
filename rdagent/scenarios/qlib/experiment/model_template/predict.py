import logging
import os
import sys
from typing import Any, Dict, List, Optional, TextIO, Union

from qlib.log import get_module_logger


class TextFormatter(logging.Formatter):
    """Text formatter for logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as text."""
        s = super().format(record)
        return f"[{record.levelname:<8}] {s}"


class JsonFormatter(logging.Formatter):
    """JSON formatter for logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as JSON."""
        data = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        return str(data)


class MyLogger(logging.Logger):
    """Custom logger."""

    def __init__(self, name, level=logging.NOTSET):
        """Initialize the logger."""
        super().__init__(name, level)

    def set_file(self, log_file, fmt: Optional[str] = None) -> None:
        """Set the file handler for the logger."""
        if fmt is None:
            fmt = "[%(asctime)s %(filename)s:%(lineno)d] %(message)s"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def set_console(self, fmt: Optional[str] = None) -> None:
        """Set the console handler for the logger."""
        if fmt is None:
            fmt = "[%(asctime)s %(filename)s:%(lineno)d] %(message)s"
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def get_module_logger(self, module_name: str) -> logging.Logger:
        """Get a logger for a specific module."""
        return logging.getLogger(f"{self.name}.{module_name}")


class MyFormatter:
    """Custom formatter."""

    def __init__(self, fmt: str) -> None:
        """Initialize the formatter."""
        self.fmt = fmt

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        return self.fmt % record.__dict__


class Logger:
    """Main logger class."""

    def __init__(
        self,
        log_file: Optional[str] = None,
        log_level: int = logging.INFO,
        file_log_level: int = logging.DEBUG,
        console_log_level: int = logging.INFO,
        fmt: Optional[str] = None,
        log_json: bool = False,
        name: str = "RD-Agent",
    ):
        """Initialize the logger."""
        self.logger = get_module_logger(name)
        self.logger.setLevel(log_level)

        if fmt is None:
            fmt = "[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s"

        formatter = JsonFormatter() if log_json else TextFormatter(fmt)

        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setLevel(file_log_level)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(console_log_level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, msg: str, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        """Log an exception message."""
        self.logger.exception(msg, *args, **kwargs)

    def log(self, level, msg: str, *args, **kwargs):
        """Log a message at the specified level."""
        self.logger.log(level, msg, *args, **kwargs)

    def get_logger(self, module_name: str):
        """Get a logger for a specific module."""
        return logging.getLogger(f"{self.logger.name}.{module_name}")


def get_logger(
    log_file: Optional[str] = None,
    log_level: int = logging.INFO,
    file_log_level: int = logging.DEBUG,
    console_log_level: int = logging.INFO,
    fmt: Optional[str] = None,
    log_json: bool = False,
    name: str = "RD-Agent",
) -> Logger:
    """Get a logger instance."""
    return Logger(log_file, log_level, file_log_level, console_log_level, fmt, log_json, name)