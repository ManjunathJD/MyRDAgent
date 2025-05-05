import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from rdagent.utils.env import get_env_config
from rdagent.utils.fmt import fmt_err

logger = logging.getLogger(__name__)


class MLEStorage(object):
    """
    Storage for mle-like data (model, metric, hyper-parameters).

    MLE means machine learning experiment.
    """

    def __init__(self, storage_dir: str, exp_id: str) -> None:
        """Init storage."""
        self.storage_dir = storage_dir
        self.exp_id = exp_id
        self.exp_dir = os.path.join(self.storage_dir, self.exp_id)
        self._ensure_dir(self.exp_dir)

        self.data: Dict[str, Dict[str, Any]] = {}

    def _ensure_dir(self, dir: str) -> None:
        """Ensure dir."""
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)

    def load_data(self, data_id: str) -> Dict[str, Any]:
        """Load data."""
        return self.data.get(data_id, {})

    def save_data(self, data_id: str, data: Dict[str, Any]) -> None:
        """Save data."""
        self.data[data_id] = data

    def save_text(self, text: str, path: str) -> None:
        """Save text."""
        with open(path, "w") as f:
            f.write(text)

    def load_text(self, path: str) -> str:
        """Load text."""
        with open(path, "r") as f:
            return f.read()

    def save_df(self, df: pd.DataFrame, path: str, index: bool = False) -> None:
        """Save dataframe."""
        df.to_csv(path, index=index)

    def load_df(self, path: str) -> pd.DataFrame:
        """Load dataframe."""
        return pd.read_csv(path)

    def _save(
        self,
        data_id: str,
        data: Union[Dict, str, pd.DataFrame],
        file_name: str,
        force_save: bool = False,
        index: bool = False,
    ) -> Optional[str]:
        """Save data."""
        if data_id not in self.data or force_save:
            path = os.path.join(self.exp_dir, file_name)
            if isinstance(data, Dict):
                self.save_data(data_id, data)
            elif isinstance(data, str):
                self.save_text(data, path)
            elif isinstance(data, pd.DataFrame):
                self.save_df(data, path, index=index)
            else:
                raise ValueError(fmt_err("Not support saving {} to file", type(data)))
            return path
        else:
            return None

    def _load(self, data_id: str, file_name: str, file_type: type) -> Any:
        """Load data."""
        if data_id not in self.data:
            path = os.path.join(self.exp_dir, file_name)
            if os.path.exists(path):
                if file_type == Dict:
                    return self.load_data(data_id)
                elif file_type == str:
                    return self.load_text(path)
                elif file_type == pd.DataFrame:
                    return self.load_df(path)
                else:
                    raise ValueError(
                        fmt_err(
                            "Not support loading {} from file",
                            file_type,
                        )
                    )
            else:
                raise ValueError(fmt_err("Path {} not exists", path))
        else:
            return self.data[data_id]

    def load_metrics(self, metric_id: str, file_name: str = "metric.csv") -> pd.DataFrame:
        """Load metrics."""
        return self._load(metric_id, file_name, pd.DataFrame)

    def save_metrics(
        self, metrics: pd.DataFrame, metric_id: str, file_name: str = "metric.csv", force_save: bool = False
    ) -> Optional[str]:
        """Save metrics."""
        return self._save(metric_id, metrics, file_name, force_save=force_save, index=True)

    def load_model_param(self, model_param_id: str, file_name: str = "model_param.txt") -> str:
        """Load model parameters."""
        return self._load(model_param_id, file_name, str)

    def save_model_param(
        self, model_param: str, model_param_id: str, file_name: str = "model_param.txt", force_save: bool = False
    ) -> Optional[str]:
        """Save model parameters."""
        return self._save(model_param_id, model_param, file_name, force_save=force_save)

    def load_hyper_param(self, hyper_param_id: str, file_name: str = "hyper_param.txt") -> str:
        """Load hyper parameters."""
        return self._load(hyper_param_id, file_name, str)

    def save_hyper_param(
        self, hyper_param: str, hyper_param_id: str, file_name: str = "hyper_param.txt", force_save: bool = False
    ) -> Optional[str]:
        """Save hyper parameters."""
        return self._save(hyper_param_id, hyper_param, file_name, force_save=force_save)

    def load_model(self, model_id: str, file_name: str = "model.txt") -> str:
        """Load model."""
        return self._load(model_id, file_name, str)

    def save_model(self, model: str, model_id: str, file_name: str = "model.txt", force_save: bool = False) -> Optional[str]:
        """Save model."""
        return self._save(model_id, model, file_name, force_save=force_save)

    def __del__(self):
        """Destroy storage."""
        pass