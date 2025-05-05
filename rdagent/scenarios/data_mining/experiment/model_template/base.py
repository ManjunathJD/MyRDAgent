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
        handlers: Optional[List[logging.Handler]] = None,
        propagate: bool = True,
        log_dir: Optional[str] = None,
        log_file_name: str = "rdagent.log",
        log_file_mode: str = "w",
    ) -> None:
        """Initialize the Logger with specified configurations.

        Args:
            name (str): Name of the logger. Defaults to "rdagent".
            level (int): Logging level (e.g., logging.INFO). Defaults to logging.INFO.
            handlers (Optional[List[logging.Handler]]): List of handlers for the logger. Defaults to None.
            propagate (bool): Whether to propagate log messages to parent loggers. Defaults to True.
            log_dir (Optional[str]): Directory to store log files. Defaults to None.
            log_file_name (str): Name of the log file. Defaults to "rdagent.log".
            log_file_mode (str): Mode for opening the log file (e.g., 'w', 'a'). Defaults to "w".
        """
        super().__init__(name, level)
        self.propagate = propagate

        if log_dir is not None:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_file_path = os.path.join(log_dir, log_file_name)
            file_handler = logging.FileHandler(log_file_path, mode=log_file_mode)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.addHandler(file_handler)

        if handlers is not None:
            for handler in handlers:
                self.addHandler(handler)
        else:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.addHandler(stream_handler)

        self.storage = Storage(logger=self)
    def log_storage(self, data_dict: Dict[str, Any], tag: str) -> None:
        """Logs the storage data.

        Args:
            data_dict (Dict[str, Any]): The data to be stored.
            tag (str): The tag associated with the data.
        """
        self.storage.log(data_dict, tag)

    def get_storage_record(
        self,
        tag: str,
        begin_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieves storage records based on the specified tag and time range.

        Args:
            tag (str): The tag associated with the data.
            begin_time (Optional[str]): Start time of the retrieval period. Defaults to None.
            end_time (Optional[str]): End time of the retrieval period. Defaults to None.
            limit (Optional[int]): The maximum number of records to retrieve. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of storage records.
        """
        return self.storage.get_record(tag, begin_time, end_time, limit)
    def get_storage_keys(self) -> list[str]:
        """Get all keys in the storage.

        Returns:
            list[str]: List of storage keys.
        """
        return self.storage.get_keys()


def get_logger(name: str = "rdagent") -> Logger:
    """Retrieves a Logger instance.

    Args:
        name (str): Name of the logger. Defaults to "rdagent".

    Returns:
        Logger: An instance of the Logger.
    """
    return Logger(name=name)