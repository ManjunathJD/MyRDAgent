import logging
import os
import sys
import time
from functools import wraps
from io import StringIO
from typing import Callable, Optional

from rdagent.log.mle_summary import mle_summary

_logger: Optional[logging.Logger] = None
logger_time_format = "%Y-%m-%d %H:%M:%S,%f"

class _CustomFormatter(logging.Formatter):

    white = "\x1b[37m"
    grey = "\x1b[38m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "[%(asctime)s][%(levelname)s][%(name)s:%(lineno)d] %(message)s"
    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: white + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=logger_time_format)
        return formatter.format(record)


def get_logger(name: str = "rd_agent") -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    # create logger with 'spam_application'
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(_CustomFormatter())

    logger.addHandler(ch)

    logger.propagate = False
    _logger = logger

    return logger


def log_function_call(logger_name="rd_agent", level=logging.INFO):
    """Decorator to log function call details.
    Args:
        logger_name (str): Name of the logger to use. Defaults to "rd_agent".
        level (int): Log level for the function call. Defaults to logging.INFO.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            func_name = func.__name__
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.log(level, f"Calling {func_name}({signature})")
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error in {func_name}: {e}")
                raise

        return wrapper

    return decorator


def redirect_stdout(logger_name="rd_agent", level=logging.INFO):
    """Redirect stdout to logger.
    Args:
        logger_name (str): Name of the logger to use. Defaults to "rd_agent".
        level (int): Log level for the stdout. Defaults to logging.INFO.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            try:
                result = func(*args, **kwargs)
                captured_text = captured_output.getvalue()
                if captured_text:
                    logger.log(level, f"stdout:\n{captured_text}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise
            finally:
                sys.stdout = old_stdout
        return wrapper

    return decorator


def timeit(logger_name="rd_agent", level=logging.INFO):
    """Decorator to log function execution time.
    Args:
        logger_name (str): Name of the logger to use. Defaults to "rd_agent".
        level (int): Log level for the execution time. Defaults to logging.INFO.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                logger.log(level, f"Function {func.__name__} took {duration:.4f} seconds")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise

        return wrapper

    return decorator


def log_exceptions(logger_name="rd_agent"):
    """Decorator to log exceptions that occur in a function.
    Args:
        logger_name (str): Name of the logger to use. Defaults to "rd_agent".
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Exception occurred in function '{func.__name__}': {e}")
                raise

        return wrapper

    return decorator

def log_mle_summary(logger_name="rd_agent"):
    """Decorator to log exceptions that occur in a function.
    Args:
        logger_name (str): Name of the logger to use. Defaults to "rd_agent".
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            try:
                return_value = func(*args, **kwargs)
                mle_summary.append(return_value)
                return return_value
            except Exception as e:
                logger.exception(f"Exception occurred in function '{func.__name__}': {e}")
                raise

        return wrapper

    return decorator


def set_log_path(log_path: str):
    logger = get_logger()
    fh = logging.FileHandler(log_path)
    logger.addHandler(fh)