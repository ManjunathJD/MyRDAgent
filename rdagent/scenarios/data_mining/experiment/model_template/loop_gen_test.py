import logging
import os
import sys
from typing import Any, Dict, List, Optional, TextIO, Union

from .formatter import Formatter
from .storage import get_storage_factory, storage_conf

_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: str,
    level: int = logging.INFO,
    format: str = _DEFAULT_LOG_FORMAT,
    datefmt: str = _DEFAULT_DATE_FORMAT,
    storage: Union[str, Dict[str, Any]] = "print",
    file: Optional[str] = None,
    file_mode: str = "a",
    file_encoding: str = "utf-8",
    stream: Optional[TextIO] = None,
    formatter_class: type = Formatter,
    propagate: bool = False,
) -> logging.Logger:
    """Get logger

    Args:
        name (str): logger name
        level (int): logging level
        format (str): logging format
        datefmt (str): logging date format
        storage (str or dict): log storage type or conf
        file (str): log file path
        file_mode (str): log file mode
        file_encoding (str): log file encoding
        stream (TextIO): output stream
        formatter_class (type): formatter class
        propagate (bool): Whether to propagate log message to the parent logger.

    Returns:
        logging.Logger: logger
    """
    logger = logging.getLogger(name)
    logger.propagate = propagate
    if logger.handlers:
        return logger
    logger.setLevel(level)

    formatter = formatter_class(fmt=format, datefmt=datefmt)

    storage_type = storage
    storage_conf = {}
    if isinstance(storage, dict):
        storage_type = storage.get("type", "print")
        storage_conf = storage
    if storage_type == "print":
        stream = stream or sys.stdout
        handler = logging.StreamHandler(stream)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    elif storage_type == "file":
        if file is None:
            raise ValueError("file is None when storage type is file")
        os.makedirs(os.path.dirname(file), exist_ok=True)
        handler = logging.FileHandler(
            file, mode=file_mode, encoding=file_encoding, **storage_conf
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    elif storage_type == "storage":
        storage_factory = get_storage_factory(**storage_conf)
        if file is None:
            raise ValueError("file is None when storage type is storage")
        os.makedirs(os.path.dirname(file), exist_ok=True)
        handler = storage_factory(file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")

    return logger


def get_root_logger(
    level: int = logging.INFO,
    format: str = _DEFAULT_LOG_FORMAT,
    datefmt: str = _DEFAULT_DATE_FORMAT,
    storage: Union[str, Dict[str, Any]] = "print",
    file: Optional[str] = None,
    file_mode: str = "a",
    file_encoding: str = "utf-8",
    stream: Optional[TextIO] = None,
    formatter_class: type = Formatter,
    propagate: bool = False,
) -> logging.Logger:
    """Get root logger

    Args:
        level (int): logging level
        format (str): logging format
        datefmt (str): logging date format
        storage (str or dict): log storage type or conf
        file (str): log file path
        file_mode (str): log file mode
        file_encoding (str): log file encoding
        stream (TextIO): output stream
        formatter_class (type): formatter class
        propagate (bool): Whether to propagate log message to the parent logger.

    Returns:
        logging.Logger: logger
    """
    return get_logger(
        name=None,
        level=level,
        format=format,
        datefmt=datefmt,
        storage=storage,
        file=file,
        file_mode=file_mode,
        file_encoding=file_encoding,
        stream=stream,
        formatter_class=formatter_class,
        propagate=propagate,
    )


def set_logger_level(logger_name: Optional[str], level: int):
    """Set logger level

    Args:
        logger_name (Optional[str]): logger name
        level (int): logging level
    """
    logging.getLogger(logger_name).setLevel(level)


def set_logger_levels(levels: Dict[Optional[str, str]]):
    """Set loggers level

    Args:
        levels (Dict[Optional[str, str]]): Dict of logger name and level.
        Example: {None: "INFO", "rdagent": "DEBUG"}
    """
    for name, level in levels.items():
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        logging.getLogger(name).setLevel(level)


def remove_logger_handlers(logger_name: Optional[str]):
    """Remove logger handlers

    Args:
        logger_name (Optional[str]): logger name
    """
    logger = logging.getLogger(logger_name)
    for handler in logger.handlers:
        logger.removeHandler(handler)


def remove_loggers_handlers(logger_names: List[Optional[str]]):
    """Remove loggers handlers

    Args:
        logger_names (List[Optional[str]]): List of logger name
    """
    for logger_name in logger_names:
        remove_logger_handlers(logger_name)