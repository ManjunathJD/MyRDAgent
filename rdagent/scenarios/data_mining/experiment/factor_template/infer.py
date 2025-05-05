import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from qlib.data import D
from qlib.data.dataset import DatasetH
from qlib.data.dataset.handler import DataHandlerLP

from rdagent.log import get_log_path

# Set up logging
log_path = get_log_path("data_mining_train.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout),
    ],
)


class FeatureGenerator:
    """
    A class for generating features for data mining tasks.

    Attributes:
        train_start_time (str): Start time for the training set.
        train_end_time (str): End time for the training set.
        valid_start_time (str): Start time for the validation set.
        valid_end_time (str): End time for the validation set.
        test_start_time (str): Start time for the test set.
        test_end_time (str): End time for the test set.
        data_list (List[str]): List of data to be processed.
        instrument (str): The financial instrument to be analyzed.
        freq (str): Frequency of the data (e.g., 'day', '1min').
        feature_list (List[str]): List of features to be generated.
        label_list (List[str]): List of labels to be generated.
        init_data (Optional[Dict[str, Any]]): Initial data to be loaded.
        train_data_generator (Optional[DataHandlerLP]): Data handler for training data.
        valid_data_generator (Optional[DataHandlerLP]): Data handler for validation data.
        test_data_generator (Optional[DataHandlerLP]): Data handler for test data.
    """

    def __init__(
        self,
        train_start_time: str,
        train_end_time: str,
        valid_start_time: str,
        valid_end_time: str,
        test_start_time: str,
        test_end_time: str,
        data_list: List[str],
        instrument: str = "csi300",
        freq: str = "day",
        feature_list: Optional[List[str]] = None,
        label_list: Optional[List[str]] = None,
    ):
        """
        Initializes the FeatureGenerator with parameters for data processing.

        Args:
            train_start_time (str): Start time for the training set.
            train_end_time (str): End time for the training set.
            valid_start_time (str): Start time for the validation set.
            valid_end_time (str): End time for the validation set.
            test_start_time (str): Start time for the test set.
            test_end_time (str): End time for the test set.
            data_list (List[str]): List of data to be processed.
            instrument (str, optional): The financial instrument to be analyzed. Defaults to "csi300".
            freq (str, optional): Frequency of the data. Defaults to "day".
            feature_list (Optional[List[str]], optional): List of features to generate. Defaults to None.
            label_list (Optional[List[str]], optional): List of labels to generate. Defaults to None.
        """
        self.train_start_time = train_start_time
        self.train_end_time = train_end_time
        self.valid_start_time = valid_start_time
        self.valid_end_time = valid_end_time
        self.test_start_time = test_start_time
        self.test_end_time = test_end_time
        self.data_list = data_list
        self.instrument = instrument
        self.freq = freq
        self.feature_list = feature_list
        self.label_list = label_list
        self.init_data: Optional[Dict[str, Any]] = None
        self.train_data_generator: Optional[DataHandlerLP] = None
        self.valid_data_generator: Optional[DataHandlerLP] = None
        self.test_data_generator: Optional[DataHandlerLP] = None

    def _get_handler_config(self) -> Dict[str, Any]:
        """
        Generates the configuration dictionary for the DataHandlerLP.

        Returns:
            Dict[str, Any]: Configuration for DataHandlerLP.
        """
        logging.info("Generating handler config...")
        if self.feature_list is None:
            feature_list = D.features(self.instrument)
        else:
            feature_list = self.feature_list

        if self.label_list is None:
            label_list = ["Ref($close, -2)/Ref($close, -1) - 1"]
        else:
            label_list = self.label_list

        handler_config = {
            "start_time": self.train_start_time,
            "end_time": self.test_end_time,
            "fit_start_time": self.train_start_time,
            "fit_end_time": self.train_end_time,
            "instruments": self.instrument,
            "freq": self.freq,
            "fields": feature_list + label_list,
        }
        return handler_config

    def _generate_data(self, handler_config: Dict[str, Any]) -> None:
        """
        Generates and preprocesses the data using DataHandlerLP.

        Args:
            handler_config (Dict[str, Any]): Configuration for DataHandlerLP.
        """
        logging.info("Generating and preprocessing data...")
        self.init_data = DataHandlerLP(**handler_config)

    def _generate_dataset(self) -> None:
        """
        Splits the data into training, validation, and test sets using DatasetH.
        """
        logging.info("Generating dataset...")
        handler_config = {
            "start_time": self.train_start_time,
            "end_time": self.train_end_time,
            "instruments": self.instrument,
            "freq": self.freq,
            "data_key": DataHandlerLP.DK_L,
        }
        if self.init_data is None:
            raise ValueError("Data has not been initialized. Please run _generate_data first.")

        self.train_data_generator = DatasetH(self.init_data, **handler_config)

        handler_config["start_time"] = self.valid_start_time
        handler_config["end_time"] = self.valid_end_time
        self.valid_data_generator = DatasetH(self.init_data, **handler_config)

        handler_config["start_time"] = self.test_start_time
        handler_config["end_time"] = self.test_end_time
        self.test_data_generator = DatasetH(self.init_data, **handler_config)

    def _check_data(self) -> None:
        """
        Checks if the data has been generated and splits have been made.
        """
        if self.init_data is None:
            raise ValueError("Data has not been initialized. Please run _generate_data first.")
        if (
            self.train_data_generator is None
            or self.valid_data_generator is None
            or self.test_data_generator is None
        ):
            raise ValueError(
                "Dataset has not been initialized. Please run _generate_dataset first."
            )

    def save_data(self, path: str) -> None:
        """
        Saves the generated data to a specified path.

        Args:
            path (str): Directory path to save the data.
        """
        self._check_data()

        if not os.path.exists(path):
            os.makedirs(path)
        logging.info(f"Saving data to {path}...")
        data_config = self._get_handler_config()
        data_config["data_list"] = self.data_list
        data_config["instrument"] = self.instrument
        data_config["freq"] = self.freq
        pd.DataFrame(data_config, index=[0]).to_csv(os.path.join(path, "config.csv"))

        train_df = self.train_data_generator.prepare(col_set="all")
        valid_df = self.valid_data_generator.prepare(col_set="all")
        test_df = self.test_data_generator.prepare(col_set="all")

        train_df.to_pickle(os.path.join(path, "train.pkl"))
        valid_df.to_pickle(os.path.join(path, "valid.pkl"))
        test_df.to_pickle(os.path.join(path, "test.pkl"))
        logging.info(f"Data saved successfully to {path}.")

    def load_data(self, path: str) -> Dict[str, pd.DataFrame]:
        """
        Loads the data from a specified path.

        Args:
            path (str): Directory path to load the data from.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary containing train, valid, and test dataframes.
        """
        logging.info(f"Loading data from {path}...")
        train_path = os.path.join(path, "train.pkl")
        valid_path = os.path.join(path, "valid.pkl")
        test_path = os.path.join(path, "test.pkl")

        if not (os.path.exists(train_path) and os.path.exists(valid_path) and os.path.exists(test_path)):
            raise FileNotFoundError(f"One or more data files are missing in {path}")

        train_df = pd.read_pickle(train_path)
        valid_df = pd.read_pickle(valid_path)
        test_df = pd.read_pickle(test_path)
        logging.info(f"Data loaded successfully from {path}.")
        return {"train": train_df, "valid": valid_df, "test": test_df}

    def fit(self, path: str) -> Dict[str, pd.DataFrame]:
        """
        Fits the feature generator by generating and saving data.

        Args:
            path (str): Directory path to save the data.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary containing train, valid, and test dataframes.
        """
        handler_config = self._get_handler_config()
        self._generate_data(handler_config)
        self._generate_dataset()
        self.save_data(path)
        return self.load_data(path)