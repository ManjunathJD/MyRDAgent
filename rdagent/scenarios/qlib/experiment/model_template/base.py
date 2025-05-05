# rdagent/scenarios/qlib/experiment/model_template/utils.py

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import qlib
from qlib.data import D
from qlib.utils import init_instance_by_config, get_or_create_path

from ...utils.logger import get_logger

logger = get_logger(__name__)


class ModelHandler:
    def __init__(self, model, dataset, metric_list=None):
        self.model = model
        self.dataset = dataset
        if metric_list is None:
            metric_list = ["MAE", "MSE", "R2"]
        self.metric_list = metric_list

        self.feature_list = None
        self.label = None

        self.train_len = None
        self.valid_len = None
        self.test_len = None

    def init_data(self, feature_list, label, train_len=None, valid_len=None, test_len=None):
        self.feature_list = feature_list
        self.label = label
        self.train_len = train_len
        self.valid_len = valid_len
        self.test_len = test_len

    def generate_data(self, data_type="test"):
        if self.feature_list is None or self.label is None:
            raise ValueError("feature list or label is None, please init data")

        if data_type == "train":
            data_len = self.train_len
            data = self.dataset.prepare(
                ["train", "valid", "test"], col_set=["feature", "label"], data_key=slice(None, data_len)
            )
        elif data_type == "valid":
            data_len = self.valid_len
            data = self.dataset.prepare(
                ["train", "valid", "test"],
                col_set=["feature", "label"],
                data_key=slice(self.train_len, self.train_len + data_len),
            )
        elif data_type == "test":
            data_len = self.test_len
            data = self.dataset.prepare(
                ["train", "valid", "test"],
                col_set=["feature", "label"],
                data_key=slice(
                    self.train_len + self.valid_len, self.train_len + self.valid_len + data_len
                ),
            )
        else:
            raise ValueError("data type only support train, valid, test")

        if data.get("label") is None:
            return None

        x = data["feature"]
        y = data["label"]

        x_data = pd.DataFrame(x)
        y_data = pd.DataFrame(y)

        return x_data, y_data

    def train(self, **kwargs):
        x_train, y_train = self.generate_data("train")
        if x_train is None:
            logger.warning("No train data! please check dataset")
            return None
        self.model.fit(x_train, y_train, **kwargs)

    def predict(self, data_type="test"):
        x_data, _ = self.generate_data(data_type)

        if x_data is None:
            logger.warning("No data! please check dataset")
            return None

        preds = self.model.predict(x_data)
        return preds

    def get_metric(self, preds, y_true):
        metric_result = {}
        for metric in self.metric_list:
            if metric == "MAE":
                metric_result[metric] = mean_absolute_error(y_true, preds)
            elif metric == "MSE":
                metric_result[metric] = mean_squared_error(y_true, preds)
            elif metric == "R2":
                metric_result[metric] = r2_score(y_true, preds)
            else:
                raise NotImplementedError("The metric is not implemented")

        return metric_result

    def evaluate(self, data_type="test"):
        _, y_true = self.generate_data(data_type)

        if y_true is None:
            logger.warning("No data! please check dataset")
            return None

        preds = self.predict(data_type)
        return self.get_metric(preds, y_true)