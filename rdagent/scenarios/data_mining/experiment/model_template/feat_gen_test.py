import logging
import os
import sys
from typing import Any, Dict, Optional, TextIO, Union

DEFAULT_LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOGGING_DATEFMT = '%Y-%m-%d %H:%M:%S'


class LogFilter(logging.Filter):

    def __init__(self, level: int = logging.INFO):
        super().__init__()
        self._level = level

    def filter(self, record: logging.LogRecord) -> int:
        return record.levelno < self._level


def get_logger(name: str = 'rdagent', level: int = logging.INFO, log_file: Optional[str] = None,
               format: str = DEFAULT_LOGGING_FORMAT,
               datefmt: str = DEFAULT_LOGGING_DATEFMT, stream: Optional[TextIO] = sys.stdout) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(fmt=format, datefmt=datefmt)

    if log_file is not None:
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if stream is not None:
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


def set_logging_level(logger: Union[logging.Logger, str], level: int = logging.INFO):
    if isinstance(logger, str):
        logger = logging.getLogger(logger)

    logger.setLevel(level)


def set_logging_config(level: int = logging.INFO, log_file: Optional[str] = None,
                       format: str = DEFAULT_LOGGING_FORMAT, datefmt: str = DEFAULT_LOGGING_DATEFMT,
                       stream: Optional[TextIO] = sys.stdout, logger_names: Optional[list] = None):
    logging.basicConfig(level=level, format=format, datefmt=datefmt, stream=stream)
    if logger_names is None:
        logger_names = [name for name in logging.root.manager.loggerDict if name != "root"]

    for name in logger_names:
        logger = logging.getLogger(name)

        logger.handlers.clear()

        if log_file is not None:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(fmt=format, datefmt=datefmt))
            logger.addHandler(file_handler)
        if stream is not None:
            stream_handler = logging.StreamHandler(stream)
            stream_handler.setFormatter(logging.Formatter(fmt=format, datefmt=datefmt))
            logger.addHandler(stream_handler)

    logger = logging.getLogger('rdagent')
    set_logging_level(logger, level)


def _get_log_name(level: int) -> str:
    if level == logging.CRITICAL:
        return 'critical'
    elif level == logging.ERROR:
        return 'error'
    elif level == logging.WARNING:
        return 'warn'
    elif level == logging.INFO:
        return 'info'
    elif level == logging.DEBUG:
        return 'debug'
    else:
        return 'unknown'


class LoggerSummary:

    def __init__(self, logger: Union[logging.Logger, str] = 'rdagent'):
        if isinstance(logger, str):
            self._logger = logging.getLogger(logger)
        else:
            self._logger = logger
        self.record: Dict[str, int] = {}

    def record_log(self, level: int):
        name = _get_log_name(level)
        if name not in self.record:
            self.record[name] = 0
        self.record[name] += 1

    def info(self, msg: str, *args: Any, **kwargs: Any):
        self.record_log(logging.INFO)
        self._logger.info(msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any):
        self.record_log(logging.DEBUG)
        self._logger.debug(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any):
        self.record_log(logging.WARNING)
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any):
        self.record_log(logging.ERROR)
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any):
        self.record_log(logging.CRITICAL)
        self._logger.critical(msg, *args, **kwargs)

    def get_summary(self) -> Dict[str, int]:
        return self.record