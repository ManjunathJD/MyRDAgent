import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from rdagent.utils.env import get_env_config
from rdagent.utils.fmt import fmt_datetime, fmt_str, read_json, write_json
from rdagent.utils.repo.repo_utils import RepoUtils

from .base import FileStorage

_logger = logging.getLogger(__name__)


class LocalFileStorage(FileStorage):
    def __init__(self, root: Optional[str] = None, project_name: Optional[str] = None):
        self._root = os.path.expanduser(root) if root else get_env_config("default_storage")
        if project_name is None:
            project_name = RepoUtils().repo_name
        self.project_name = project_name
        self.project_root = os.path.join(self._root, self.project_name)
        os.makedirs(self.project_root, exist_ok=True)

    def _check_path(self, relative_path: str):
        path = os.path.join(self.project_root, relative_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def write_str(self, data: str, relative_path: str, overwrite: bool = True):
        path = self._check_path(relative_path)
        if not overwrite and os.path.exists(path):
            raise ValueError(f"path: {path} exist. ")
        with open(path, "w") as f:
            f.write(data)
        return path

    def read_str(self, relative_path: str):
        path = os.path.join(self.project_root, relative_path)
        with open(path, "r") as f:
            data = f.read()
        return data

    def write_json(self, data: dict, relative_path: str, overwrite: bool = True):
        path = self._check_path(relative_path)
        if not overwrite and os.path.exists(path):
            raise ValueError(f"path: {path} exist. ")
        write_json(data, path)
        return path

    def read_json(self, relative_path: str) -> dict:
        path = os.path.join(self.project_root, relative_path)
        return read_json(path)

    def write_dataframe(
        self,
        df: pd.DataFrame,
        relative_path: str,
        overwrite: bool = True,
        to_csv_kwargs: Optional[dict] = None,
    ):
        path = self._check_path(relative_path)
        if not overwrite and os.path.exists(path):
            raise ValueError(f"path: {path} exist. ")
        if to_csv_kwargs is None:
            to_csv_kwargs = {}
        df.to_csv(path, **to_csv_kwargs)
        return path

    def read_dataframe(self, relative_path: str, **kwargs) -> pd.DataFrame:
        path = os.path.join(self.project_root, relative_path)
        return pd.read_csv(path, **kwargs)

    def read_image(self, relative_path: str):
        import cv2

        path = os.path.join(self.project_root, relative_path)
        if not os.path.exists(path):
            raise ValueError(f"image path: {path} is not found. ")
        return cv2.imread(path)

    def write_image(self, image, relative_path: str, overwrite: bool = True):
        import cv2

        path = self._check_path(relative_path)
        if not overwrite and os.path.exists(path):
            raise ValueError(f"path: {path} exist. ")
        cv2.imwrite(path, image)
        return path

    def list_dir(self, relative_path: str) -> list:
        path = os.path.join(self.project_root, relative_path)
        if not os.path.exists(path):
            _logger.warning(f"path: {path} is not found. ")
            return []
        return os.listdir(path)

    def delete(self, relative_path: str):
        path = os.path.join(self.project_root, relative_path)
        os.remove(path)

    def exist(self, relative_path: str):
        path = os.path.join(self.project_root, relative_path)
        return os.path.exists(path)

    def rename(self, relative_path_src, relative_path_dst):
        src = os.path.join(self.project_root, relative_path_src)
        dst = self._check_path(relative_path_dst)
        os.rename(src, dst)
        return dst