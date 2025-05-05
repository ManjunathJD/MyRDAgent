import logging
import os
import sys
import time
from functools import wraps
from io import StringIO
from typing import Callable, Optional

from rdagent.utils.fmt import fmt_json


def log_with_level(
    level: int = logging.INFO,
    tag: str = "default_tag",
    logger: Optional[logging.Logger] = None,
    msg_prefix: str = "",
):
    """
    Log the function execution with the specified level.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(level, f"{msg_prefix}{tag} - Start: {func.__name__}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                logger.log(
                    level,
                    f"{msg_prefix}{tag} - End: {func.__name__} - Cost: {end_time - start_time:.2f}s",
                )
                return result
            except Exception as e:
                end_time = time.time()
                logger.log(
                    logging.ERROR,
                    f"{msg_prefix}{tag} - Error: {func.__name__} - Cost: {end_time - start_time:.2f}s - Error: {e}",
                )
                raise

        return wrapper

    return decorator


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger: logging.Logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf: str):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def capture_output_to_logger(func):
    """
    Capture the output of the function and redirect it to a logger.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StreamToLogger(logger, logging.INFO)
        sys.stderr = StreamToLogger(logger, logging.ERROR)

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    return wrapper


class TqdmToLogger(StringIO):
    """
    Output stream for TQDM which will output to logger module instead of stdout.
    """

    logger = None
    level = None
    buf = ""

    def __init__(self, logger, level=None):
        super(TqdmToLogger, self).__init__()
        self.logger = logger
        self.level = level or logging.INFO

    def write(self, buf):
        self.buf = buf.strip("\r\n\t ")

    def flush(self):
        self.logger.log(self.level, self.buf)


def logging_format_file(
    path: str, log_name: str, stdout_print: bool = True, file_log: bool = True
):
    """
    configure file logging
    """
    log_file = os.path.join(path, log_name)
    if not os.path.exists(path):
        os.makedirs(path)

    if file_log:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        if stdout_print:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        return logger
    else:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        if stdout_print:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        return logger


def logging_config_from_json_file(logger: logging.Logger, file_path: str):
    """
    load logging config from json file
    """
    try:
        import json
    except ImportError:
        logger.warning("cannot import json module!")
        return

    if not os.path.exists(file_path):
        logger.warning(f"config file {file_path} not exists")
        return

    with open(file_path, "r") as f:
        config = json.load(f)

    for handler_name, handler_config in config.get("handlers", {}).items():
        handler_type = handler_config.get("type")
        handler_level = handler_config.get("level", logging.INFO)
        handler_formatter = handler_config.get("formatter", "%(message)s")
        if handler_type == "file":
            handler_path = handler_config.get("path")
            handler = logging.FileHandler(handler_path)
        elif handler_type == "stream":
            handler = logging.StreamHandler()
        else:
            logger.warning(f"unknown handler type {handler_type}")
            continue

        formatter = logging.Formatter(handler_formatter)
        handler.setFormatter(formatter)
        handler.setLevel(handler_level)
        logger.addHandler(handler)
        logger.info(f"add handler {handler_name} to logger")

    logger.setLevel(config.get("level", logging.INFO))
    logger.info(f"set logger level to {config.get('level', logging.INFO)}")

    logger.info(f"load logger config from {file_path} success")