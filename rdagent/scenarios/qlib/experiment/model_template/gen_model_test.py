import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml
from pydantic import BaseModel, Field, model_validator

from rdagent.log.base import LogMixin
from rdagent.utils.import_utils import find_file, load_class

logger = logging.getLogger(__name__)


class BaseConfig(BaseModel, LogMixin):
    config_path: str = Field(None, description="path to config")
    _config_data: dict = Field(None, description="config data", exclude=True)

    @model_validator(mode="before")
    def load_config_file(cls, values: Dict[str, Any]):
        """load config file"""
        config_path = values.get("config_path")
        if config_path is not None:
            abs_config_path = find_file(config_path)
            if abs_config_path is None:
                raise ValueError(f"config path {config_path} not found")
            with open(abs_config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            values["_config_data"] = config_data
        return values

    @property
    def config_data(self):
        if self._config_data is None:
            raise ValueError(f"config data is None, please set config_path or load config first")
        return self._config_data

    def get_config(self, key: str):
        """get config by key"""
        if key not in self.config_data:
            raise ValueError(f"config key {key} not found")
        return self.config_data[key]

    def __getitem__(self, key: str):
        return self.get_config(key)