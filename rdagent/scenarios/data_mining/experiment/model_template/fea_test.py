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
        save_dir: str = "log",
        log_file: str = "log.txt",
        save_summary: bool = False,
    ):
        """
        Initialize the Logger instance.

        Args:
            name (str): Name of the logger. Defaults to 'rdagent'.
            level (int): Logging level. Defaults to logging.INFO.
            save_dir (str): Directory to save log files. Defaults to 'log'.
            log_file (str): Name of the log file. Defaults to 'log.txt'.
            save_summary (bool): Whether to save a summary of the log. Defaults to False.
        """
        super().__init__(name, level)
        self.log_dir: str = os.path.join(save_dir, name)
        self.log_file: str = log_file
        self.log_path: str = os.path.join(self.log_dir, self.log_file)
        self.summary_path: str = os.path.join(self.log_dir, "summary.txt")
        self.storage: Optional[Storage] = None
        self.save_summary: bool = save_summary
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Set up the logger with file and stream handlers."""
        os.makedirs(self.log_dir, exist_ok=True)
        self.storage = Storage(self.summary_path)

        file_handler = logging.FileHandler(self.log_path)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.addHandler(stream_handler)

    def log_summary(self, log_type: str, log_content: str) -> None:
        """
        Log a summary message to the summary file.

        Args:
            log_type (str): Type of the log message.
            log_content (str): Content of the log message.
        """
        if self.save_summary:
            self.storage.append_summary(log_type, log_content)

    def flush_summary(self) -> None:
        """Flush the summary buffer."""
        if self.save_summary:
            self.storage.flush()

    def close_summary(self) -> None:
        """Close the summary file."""
        if self.save_summary:
            self.storage.close()

    def add_log_content(self, log_type: str, log_content: str) -> None:
        """
        Add content to a specific log type.

        Args:
            log_type (str): Type of log.
            log_content (str): Content to add to the log.
        """
        if self.save_summary:
            self.storage.add_content(log_type, log_content)

    def get_log_content(self, log_type: str) -> Union[str, List[str]]:
        """
        Retrieve the content of a specific log type.

        Args:
            log_type (str): Type of log.

        Returns:
            Union[str, List[str]]: Content of the log.
        """
        if self.save_summary:
            return self.storage.get_content(log_type)
        return ""

    def set_log_content(self, log_type: str, log_content: Union[str, List[str]]) -> None:
        """
        Set content to a specific log type.

        Args:
            log_type (str): Type of log.
            log_content (Union[str, List[str]]): Content to set to the log.
        """
        if self.save_summary:
            self.storage.set_content(log_type, log_content)

    def info(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level INFO on the root logger.

        Args:
            msg (str): Message to log.
        """
        super().info(msg, *args, **kwargs)
        self.log_summary("INFO", msg)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level WARNING on the root logger.

        Args:
            msg (str): Message to log.
        """
        super().warning(msg, *args, **kwargs)
        self.log_summary("WARNING", msg)

    def error(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level ERROR on the root logger.

        Args:
            msg (str): Message to log.
        """
        super().error(msg, *args, **kwargs)
        self.log_summary("ERROR", msg)

    def debug(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level DEBUG on the root logger.

        Args:
            msg (str): Message to log.
        """
        super().debug(msg, *args, **kwargs)
        self.log_summary("DEBUG", msg)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level CRITICAL on the root logger.

        Args:
            msg (str): Message to log.
        """
        super().critical(msg, *args, **kwargs)
        self.log_summary("CRITICAL", msg)

    def exception(self, msg: str, *args, exc_info=True, **kwargs) -> None:
        """
        Log a message with level ERROR on the root logger, including exception information.

        Args:
            msg (str): Message to log.
            exc_info (bool): If true, exception information is included. Defaults to True.
        """
        super().exception(msg, *args, exc_info=exc_info, **kwargs)
        self.log_summary("EXCEPTION", msg)

    @staticmethod
    def get_logger(
        name: str = "rdagent",
        log_level: str = "INFO",
        log_dir: str = "log",
        log_file: str = "log.txt",
        save_summary: bool = True,
    ) -> "Logger":
        """
        Get a logger instance.

        Args:
            name (str): Name of the logger. Defaults to 'rdagent'.
            log_level (str): Logging level. Defaults to 'INFO'.
            log_dir (str): Directory to save log files. Defaults to 'log'.
            log_file (str): Name of the log file. Defaults to 'log.txt'.
            save_summary (bool): Whether to save a summary of the log. Defaults to True.

        Returns:
            Logger: Logger instance.
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if log_level not in level_map:
            raise ValueError(f"Invalid log level: {log_level}")

        log_level_int = level_map[log_level]

        return Logger(
            name=name,
            level=log_level_int,
            save_dir=log_dir,
            log_file=log_file,
            save_summary=save_summary,
        )