import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import qlib
from qlib.config import C
from qlib.constant import REG_CN
from qlib.data import D
from qlib.data.dataset import DatasetH
from qlib.data.dataset.handler import DataHandlerLP
from qlib.log import get_module_logger
from qlib.utils import init_instance_by_config, unpack_df_to_tuple

from ...utils.agent.ret import AgentRetCode
from ...utils.agent.tpl import AgentTpl, AgentTplType
from ...utils.conf import Conf, load_conf
from ...utils.env import is_in_docker, is_rd_env
from ...utils.file import remove_dir, touch_file
from ..base_scenario import BaseScenario
from ..conf import ScenarioConf
from ..proposal.model_proposal import ModelProposal
from .base_dev import BaseDeveloper

logger = get_module_logger("rd_agent.data_mining.developer.model_runner")


class ModelRunner(BaseDeveloper):

    """
    ModelRunner:

    The ModelRunner is responsible for running the model code.

    It will:

    - Load the configuration of the model.

    - Load the dataset.

    - Run the model.

    - Save the results.
    """

    name: str = "ModelRunner"

    def __init__(
        self,
        *args,
        conf: Union[str, Dict, Conf] = None,
        proposal: ModelProposal = None,
        logger=logger,
        **kwargs,
    ):
        super().__init__(*args, conf=conf, proposal=proposal, logger=logger, **kwargs)

    def _init_env(self):
        """
        Init env and model
        """
        # init qlib env

        # set region
        if "region" not in self.conf and not is_in_docker():
            # use China stock data in default if not in docker
            self.conf.region = REG_CN

        if "qlib_conf" not in self.conf:
            if is_rd_env():
                self.conf.qlib_conf = "/home/rd/rd_project/conf/server/qlib_server_config.yaml"
            else:
                self.conf.qlib_conf = "/home/rd/rd_project/conf/local/qlib_local_config.yaml"
            logger.warning(f"qlib_conf not found in conf, use default value: {self.conf.qlib_conf}")

        # init qlib
        if not qlib.is_init():
            qlib.init(
                provider_uri=self.conf.qlib_provider_uri,
                region=self.conf.region,
                config=self.conf.qlib_conf,
            )

        # init conf
        if "model_conf" not in self.conf:
            self.conf.model_conf = "/home/rd/rd_project/conf/local/model_local_config.yaml"
            logger.warning(f"model_conf not found in conf, use default value: {self.conf.model_conf}")
        self.model_conf = load_conf(self.conf.model_conf)

        # load model params
        self.model_params = self.model_conf.get("model", {})
        self.model_params["log_path"] = os.path.join(self.conf.output_path, "log")
        self.model_params["checkpoint_path"] = os.path.join(self.conf.output_path, "checkpoint")

        # check log path and checkpoint path
        if not os.path.exists(self.model_params["log_path"]):
            os.makedirs(self.model_params["log_path"])
        if not os.path.exists(self.model_params["checkpoint_path"]):
            os.makedirs(self.model_params["checkpoint_path"])

    def _load_dataset(self):
        """
        Load the dataset

        Returns:

            tuple: (dataset, dataset_train, dataset_valid, dataset_test)
        """
        # load dataset
        dataset_conf: Dict = self.model_conf["dataset"]
        dataset_conf["handler"] = init_instance_by_config(dataset_conf["handler"])
        dataset_conf["segments"] = {
            "train": slice(*dataset_conf["train_segments"]),
            "valid": slice(*dataset_conf["valid_segments"]),
            "test": slice(*dataset_conf["test_segments"]),
        }
        dataset = DatasetH(**dataset_conf)
        return dataset, dataset.prepare(["train", "valid", "test"])

    def _init_model(self, dataset):
        """
        Init the model

        Args:
            dataset (Dataset): dataset
        """

        model_conf: Dict = self.model_conf["model"]
        if "module_path" in model_conf:
            model_name = model_conf.pop("module_path").split(".")[-1]
            model_module = __import__(model_conf["module_path"], fromlist=[model_name])
            self.model = getattr(model_module, model_name)(**self.model_params)
        else:
            self.model = init_instance_by_config(model_conf, **self.model_params)
        return self.model

    def _train(self, dataset_train, dataset_valid):
        """
        Train the model

        Args:
            dataset_train (tuple): train dataset
            dataset_valid (tuple): valid dataset
        """

        train_x, train_y = dataset_train
        valid_x, valid_y = dataset_valid

        self.model.fit(train_x, train_y, valid_x, valid_y)

    def _predict(self, dataset_test):
        """
        Predict the model

        Args:
            dataset_test (tuple): test dataset
        """
        test_x, test_y = dataset_test
        pred_y = self.model.predict(test_x)
        return pred_y

    def run(self, *args, **kwargs) -> Tuple[AgentRetCode, Dict]:
        """
        Run the model

        Returns:

            Tuple[AgentRetCode, Dict]: (ret_code, result)
        """
        self._init_env()
        dataset, (dataset_train, dataset_valid, dataset_test) = self._load_dataset()
        self._init_model(dataset)
        self._train(dataset_train, dataset_valid)
        pred_y = self._predict(dataset_test)

        # save pred_y
        pred_y.to_csv(os.path.join(self.conf.output_path, "pred_y.csv"))

        # save dataset
        with open(os.path.join(self.conf.output_path, "dataset.txt"), "w") as f:
            f.write(str(dataset))

        return AgentRetCode.SUCCESS, {}

    def check(self, *args, **kwargs) -> Tuple[AgentRetCode, Dict]:
        """
        Check the result of model runner

        Returns:
            Tuple[AgentRetCode, Dict]: (ret_code, result)
        """
        return AgentRetCode.SUCCESS, {}

    def _get_tpl_from_ret(self, ret) -> Optional[AgentTpl]:
        """
        Get the template from the result of the agent.

        Args:
            ret: the result of the agent.

        Returns:
            Optional[AgentTpl]: the template or None if there is no template in the result.
        """
        return AgentTpl(tpl_type=AgentTplType.MODEL_TEMPLATE, tpl_value=ret)

    def get_tpl(self, *args, **kwargs) -> Optional[AgentTpl]:
        """
        Get the template of the agent.

        Returns:
            Optional[AgentTpl]: the template or None if there is no template in the result.
        """
        return self._get_tpl_from_ret(self.run())