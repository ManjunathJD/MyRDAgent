import logging
import os
import sys
from typing import Any, Dict, List, Optional, TextIO, Union

from .conf import LogConfig

DEFAULT_LOG_CONFIG = LogConfig()
DEFAULT_LOGGER_NAME = "rdagent"


class DefaultFormatter(logging.Formatter):
    def formatException(self, ei) -> str:
        return super().formatException(ei)


class ColorfulFormatter(logging.Formatter):
    COLOR_SEQ = "\033[1;%dm"
    COLOR_RESET = "\033[0m"

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    COLORS = {
        logging.DEBUG: COLOR_SEQ % (30 + WHITE),
        logging.INFO: COLOR_SEQ % (30 + GREEN),
        logging.WARNING: COLOR_SEQ % (30 + YELLOW),
        logging.ERROR: COLOR_SEQ % (30 + RED),
        logging.CRITICAL: COLOR_SEQ % (30 + RED),
    }

    def format(self, record: logging.LogRecord) -> str:
        log_message = super().format(record)
        if record.levelno in self.COLORS and sys.stdout.isatty():
            log_message = self.COLORS[record.levelno] + log_message + self.COLOR_RESET
        return log_message


class TextWriter:
    def __init__(self, stream: TextIO, encoding: Optional[str] = None) -> None:
        self.stream = stream
        self.encoding = encoding

    def write(self, log_message: str) -> None:
        if self.encoding:
            self.stream.write(log_message.encode(self.encoding, errors="replace").decode(self.encoding, errors="replace"))
        else:
            self.stream.write(log_message)
        self.flush()

    def flush(self) -> None:
        self.stream.flush()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        json_record: Dict[str, Any] = {
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S,%f"),
            "level": record.levelname,
            "name": record.name,
            "process": record.process,
            "thread": record.thread,
            "message": record.getMessage(),
        }
        if record.exc_info:
            json_record["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            json_record["stack_info"] = self.formatStack(record.stack_info)
        return str(json_record)


def get_logger(logger_name: str = DEFAULT_LOGGER_NAME, log_config: LogConfig = DEFAULT_LOG_CONFIG) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_config.level)
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear()
    if log_config.writer_type == "stdout":
        handler = logging.StreamHandler(sys.stdout)
        if log_config.formatter_type == "colorful":
            formatter = ColorfulFormatter(log_config.format, log_config.date_format)
        elif log_config.formatter_type == "json":
            formatter = JsonFormatter()
        else:
            formatter = DefaultFormatter(log_config.format, log_config.date_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    elif log_config.writer_type == "file":
        if log_config.log_path:
            log_dir = os.path.dirname(log_config.log_path)
            os.makedirs(log_dir, exist_ok=True)
            handler = logging.FileHandler(log_config.log_path, encoding=log_config.encoding)
            if log_config.formatter_type == "json":
                formatter = JsonFormatter()
            else:
                formatter = DefaultFormatter(log_config.format, log_config.date_format)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        else:
            print("log_path is None, ignored file handler")
    elif log_config.writer_type == "null":
        logger.addHandler(logging.NullHandler())
    else:
        raise ValueError(f"writer_type {log_config.writer_type} is invalid")
    return logger