import logging
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from rdagent.log import ui
from rdagent.log.base import BaseLogger
from rdagent.log.storage import LogStorage
from rdagent.utils import get_traceback_str


class UILogger(BaseLogger):
    """UILogger is used to log to UI"""

    def __init__(self, storage_path: Optional[str] = None, level: int = logging.INFO) -> None:
        super().__init__(level)
        self._storage: LogStorage = LogStorage(storage_path)
        self.console_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(logging.Formatter("%(message)s"))
        self.console_handler.setLevel(level)
        self.addHandler(self.console_handler)
        self._in_ui: bool = False
        self._last_log: Optional[Dict[str, Any]] = None

    def _log(
        self,
        level: int,
        msg: Any,
        args: Tuple[Any, ...],
        exc_info: Optional[Tuple[Any, Any, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
    ) -> None:
        if self.isEnabledFor(level):
            if extra is None:
                extra = {}
            if "log_id" not in extra:
                extra["log_id"] = self._get_log_id()
            if "ui_tag" not in extra:
                extra["ui_tag"] = "system"
            record: logging.LogRecord = self.makeRecord(
                self.name, level, "", 0, msg, args, exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel
            )
            if record.levelname == "ERROR":
                traceback_str: Optional[str] = get_traceback_str(record)
                if traceback_str is not None:
                    record.msg = f"{record.msg}\n{traceback_str}"
            self.handle(record)

    def _ui_log(self, record: logging.LogRecord):
        """Log to UI"""
        self._last_log = {
            "log_id": record.log_id,
            "time": record.created,
            "tag": record.ui_tag,
            "msg": record.msg,
            "type": record.levelname,
        }
        ui.log_ui_msg(self._last_log)

    def handle(self, record: logging.LogRecord):
        """Handle log record

        Args:
            record (logging.LogRecord): log record
        """
        self._storage.log_record(record)
        if self._in_ui:
            self._ui_log(record)
        super().handle(record)

    def in_ui(self, flag: bool = True) -> None:
        """
        set log to UI flag

        Args:
            flag (bool, optional): set ui flag. Defaults to True.
        """
        self._in_ui = flag

    def get_last_log(self) -> Optional[Dict[str, Any]]:
        """get last log message

        Returns:
            Optional[Dict[str, Any]]: last log message
        """
        return self._last_log

    def show_html(
        self,
        content: str,
        ui_tag: str = "system",
        log_id: Optional[str] = None,
        level: int = logging.INFO,
    ):
        """Show html content in UI

        Args:
            content (str): html content
            ui_tag (str, optional): ui tag. Defaults to "system".
            log_id (Optional[str], optional): log id. Defaults to None.
            level (int, optional): log level. Defaults to logging.INFO.
        """
        self._log(level, content, (), extra={"ui_tag": ui_tag, "log_id": log_id})

    def show_image(self, url: str, ui_tag: str = "system", log_id: Optional[str] = None, level: int = logging.INFO):
        """Show image in UI

        Args:
            url (str): image url
            ui_tag (str, optional): ui tag. Defaults to "system".
            log_id (Optional[str], optional): log id. Defaults to None.
            level (int, optional): log level. Defaults to logging.INFO.
        """
        self._log(level, url, (), extra={"ui_tag": ui_tag, "log_id": log_id})

    def show_table(
        self,
        data: List[Dict[str, Union[str, int, float]]],
        ui_tag: str = "system",
        log_id: Optional[str] = None,
        level: int = logging.INFO,
    ):
        """Show table in UI

        Args:
            data (List[Dict[str, Union[str, int, float]]]): table data
            ui_tag (str, optional): ui tag. Defaults to "system".
            log_id (Optional[str], optional): log id. Defaults to None.
            level (int, optional): log level. Defaults to logging.INFO.
        """
        self._log(level, data, (), extra={"ui_tag": ui_tag, "log_id": log_id})

    def show_code(
        self, code: str, language: str, ui_tag: str = "system", log_id: Optional[str] = None, level: int = logging.INFO
    ):
        """Show code in UI

        Args:
            code (str): code content
            language (str): code language
            ui_tag (str, optional): ui tag. Defaults to "system".
            log_id (Optional[str], optional): log id. Defaults to None.
            level (int, optional): log level. Defaults to logging.INFO.
        """
        self._log(level, {"code": code, "language": language}, (), extra={"ui_tag": ui_tag, "log_id": log_id})

    def show_result(self, result: str, ui_tag: str = "system", log_id: Optional[str] = None, level: int = logging.INFO):
        """Show result in UI

        Args:
            result (str): result content
            ui_tag (str, optional): ui tag. Defaults to "system".
            log_id (Optional[str], optional): log id. Defaults to None.
            level (int, optional): log level. Defaults to logging.INFO.
        """
        self._log(level, result, (), extra={"ui_tag": ui_tag, "log_id": log_id})

    def show_json(
        self, json_str: Union[str, Dict[str, Any]], ui_tag: str = "system", log_id: Optional[str] = None, level: int = logging.INFO
    ):
        """Show json in UI

        Args:
            json_str (Union[str, Dict[str, Any]]): json content
            ui_tag (str, optional): ui tag. Defaults to "system".
            log_id (Optional[str], optional): log id. Defaults to None.
            level (int, optional): log level. Defaults to logging.INFO.
        """
        self._log(level, json_str, (), extra={"ui_tag": ui_tag, "log_id": log_id})