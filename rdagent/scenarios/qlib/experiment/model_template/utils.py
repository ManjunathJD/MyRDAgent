import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import qlib
from qlib.config import C
from qlib.data import D
from qlib.data.dataset import DatasetH
from qlib.data.dataset.handler import DataHandlerLP
from qlib.log import get_module_logger
from qlib.model.trainer import task_train
from qlib.utils import init_instance_by_config, save_multiple_parts_of_config
from qlib.workflow import R
from qlib.workflow.task.gen import task_generator

from ...core.exception import EvolvingAgentError
from ...core.prompts import PromptManager
from ...core.utils import load_yaml, save_yaml
from ...log.mle_summary import MLESummary
from ..utils import (
    EXPERIMENT_NAME,
    OUTPUT_DIR_NAME,
    EXPERIMENT_FILE_NAME,
    get_file_path,
    load_exp_info,
    load_prompts,
    save_exp_info,
    get_experiment_dir,
)
from .base import ModelTemplateTest

logger = get_module_logger("model_template", level=logging.INFO)


class ModelTemplate:
    def __init__(self, config: Optional[Union[str, Dict]] = None) -> None:
        """
        The experiment will be organized as follows:
        experiment_root/
            ├── model_template_conf.yaml
            ├── prompts.yaml
            ├── train.py
            ├── infer.py
            ├── predict.py
            ├── eva.py
            └── model_template_test.py

        config: The path of experiment config file or config dict.
        """
        self.config = self.load_config(config)
        self.prompts = load_prompts(get_file_path(__file__, "prompts.yaml"))
        self.model_template_root = get_experiment_dir(__file__)
        self.save_model_template_conf(self.config)
        # initialize qlib
        self.initialize_qlib()
        # PromptManager
        self.prompt_manager = PromptManager()

    def load_config(self, config: Optional[Union[str, Dict]] = None):
        if isinstance(config, str):
            config = load_yaml(config)
        elif isinstance(config, dict):
            config = config
        elif config is None:
            config = load_yaml(get_file_path(__file__, "model_template_conf.yaml"))
        else:
            raise EvolvingAgentError(f"Config must be a str or dict, but get {type(config)}")

        return config

    def save_model_template_conf(self, config: Dict) -> str:
        """save model config"""
        path = os.path.join(self.model_template_root, "model_template_conf.yaml")
        save_yaml(config, path)
        return path

    def initialize_qlib(self):
        """initialize qlib, it will load and preprocess all config in the config file."""
        # qlib initialization
        if qlib.get_provider() is None:
            qlib.init(**self.config.get("qlib_init", {}))

        # check if there is a conflict between the configurations.
        model_conf_name = self.config.get("model", {}).get("module_path", None)
        if model_conf_name is not None:
            self.config["model"]["module_path"] = os.path.join(self.model_template_root, model_conf_name)

        dataset_conf = self.config.get("dataset", {})
        handler_conf = dataset_conf.get("handler", {})
        if handler_conf:
            # get handler config from file path.
            handler_conf_file = handler_conf.pop("file_path", None)
            if handler_conf_file:
                handler_conf_file = os.path.join(self.model_template_root, handler_conf_file)
                handler_config = load_yaml(handler_conf_file)
                if isinstance(handler_config, list):
                    handler_conf["kwargs"] = handler_config
                else:
                    handler_conf.update(handler_config)
            dataset_conf["handler"] = handler_conf

    def data_preprocess(
        self,
        handler_config: Optional[Dict] = None,
        data_path: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        fit_start_time: Optional[str] = None,
        fit_end_time: Optional[str] = None,
        infer_start_time: Optional[str] = None,
        infer_end_time: Optional[str] = None,
    ) -> DataHandlerLP:
        """data preprocess will load the data and generate dataset by handler config.
        It will save the handler into the experiment path, and you can reload it again by load_handler.

        Args:
            handler_config (Optional[Dict]): handler config to generate dataset.
            data_path (Optional[str]): data root.
            start_time (Optional[str]): start time of data
            end_time (Optional[str]): end time of data
            fit_start_time (Optional[str]): fit start time
            fit_end_time (Optional[str]): fit end time
            infer_start_time (Optional[str]): infer start time
            infer_end_time (Optional[str]): infer end time

        Returns:
            DataHandlerLP: handler
        """
        if data_path is None:
            data_path = self.config.get("data_path", C.get("provider_uri"))
        if handler_config is None:
            handler_config = self.config.get("dataset", {}).get("handler", {})
        if start_time is None:
            start_time = self.config.get("start_time", None)
        if end_time is None:
            end_time = self.config.get("end_time", None)
        if fit_start_time is None:
            fit_start_time = self.config.get("fit_start_time", None)
        if fit_end_time is None:
            fit_end_time = self.config.get("fit_end_time", None)
        if infer_start_time is None:
            infer_start_time = self.config.get("infer_start_time", None)
        if infer_end_time is None:
            infer_end_time = self.config.get("infer_end_time", None)

        logger.info(f"Handler config: {handler_config}")

        # save handler config
        handler_config_path = os.path.join(self.model_template_root, "handler_config.yaml")
        save_yaml(handler_config, handler_config_path)

        # set data and time range.
        if start_time and end_time:
            D.set_time_range(start_time, end_time)
        if data_path:
            qlib.set_provider_uri(data_path)
            logger.info(f"Set data path to {data_path}")

        # generate handler
        handler = init_instance_by_config(handler_config)
        if fit_start_time is not None and fit_end_time is not None:
            handler.fit_start_time = fit_start_time
            handler.fit_end_time = fit_end_time
        if infer_start_time is not None and infer_end_time is not None:
            handler.infer_start_time = infer_start_time
            handler.infer_end_time = infer_end_time
        self.handler = handler

        return handler

    def load_handler(self) -> DataHandlerLP:
        """load saved handler"""
        handler_config_path = os.path.join(self.model_template_root, "handler_config.yaml")
        handler_config = load_yaml(handler_config_path)
        handler = init_instance_by_config(handler_config)
        self.handler = handler
        return handler

    def generate_dataset(
        self,
        data_path: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        fit_start_time: Optional[str] = None,
        fit_end_time: Optional[str] = None,
        infer_start_time: Optional[str] = None,
        infer_end_time: Optional[str] = None,
        segments: Optional[Dict[str, Tuple[str, str]]] = None,
        handler: Optional[DataHandlerLP] = None,
    ) -> DatasetH:
        """generate dataset by handler.

        Args:
            data_path (Optional[str]): data root
            start_time (Optional[str]): start time of data
            end_time (Optional[str]): end time of data
            fit_start_time (Optional[str]): fit start time
            fit_end_time (Optional[str]): fit end time
            infer_start_time (Optional[str]): infer start time
            infer_end_time (Optional[str]): infer end time
            segments (Optional[Dict[str, Tuple[str, str]]]): segments of data.
            handler (Optional[DataHandlerLP]): handler, if None, will load the handler saved before.

        Returns:
            DatasetH: dataset
        """
        if data_path is None:
            data_path = self.config.get("data_path", C.get("provider_uri"))
        if start_time is None:
            start_time = self.config.get("start_time", None)
        if end_time is None:
            end_time = self.config.get("end_time", None)
        if fit_start_time is None:
            fit_start_time = self.config.get("fit_start_time", None)
        if fit_end_time is None:
            fit_end_time = self.config.get("fit_end_time", None)
        if infer_start_time is None:
            infer_start_time = self.config.get("infer_start_time", None)
        if infer_end_time is None:
            infer_end_time = self.config.get("infer_end_time", None)
        if segments is None:
            segments = self.config.get("dataset", {}).get("segments", {})

        if handler is None:
            handler = self.load_handler()

        # set data and time range.
        if start_time and end_time:
            D.set_time_range(start_time, end_time)
        if data_path:
            qlib.set_provider_uri(data_path)
            logger.info(f"Set data path to {data_path}")

        self.dataset = DatasetH(handler, segments)
        self.segments = segments
        self.dataset_config = {
            "data_path": data_path,
            "start_time": start_time,
            "end_time": end_time,
            "fit_start_time": fit_start_time,
            "fit_end_time": fit_end_time,
            "infer_start_time": infer_start_time,
            "infer_end_time": infer_end_time,
            "segments": segments,
        }

        return self.dataset

    def get_dataset(self) -> DatasetH:
        if self.dataset is None:
            raise EvolvingAgentError("Please generate dataset first by generate_dataset.")
        return self.dataset

    def generate_model(self) -> Any:
        """generate model, it will load model config from config file.

        Returns:
            Any: model
        """
        model_config = self.config.get("model")
        self.model = init_instance_by_config(model_config)
        return self.model

    def get_model(self) -> Any:
        """get model

        Returns:
            Any: model
        """
        if self.model is None:
            raise EvolvingAgentError("Please generate model first by generate_model.")
        return self.model

    def generate_task(self, model_test: Optional[ModelTemplateTest] = None) -> List[Dict]:
        """generate task, it will load task config from config file.

        Args:
            model_test (Optional[ModelTemplateTest]): model test

        Returns:
            List[Dict]: tasks.
        """
        dataset = self.get_dataset()

        task_config = self.config.get("task", {})
        task_config["dataset"] = dataset
        task_config["model"] = self.get_model()
        task_config["model_test"] = model_test
        self.task = task_generator(**task_config)
        logger.info(f"Task config: {self.task}")

        return self.task

    def get_task(self) -> List[Dict]:
        """get task

        Returns:
            List[Dict]: tasks.
        """
        if self.task is None:
            raise EvolvingAgentError("Please generate task first by generate_task.")
        return self.task

    def save_experiment_info(self, task_id: str) -> str:
        """save experiment info into the experiment path.

        Args:
            task_id (str): task id

        Returns:
            str: experiment path
        """
        exp_info = {
            "task_id": task_id,
            "model_template_path": self.model_template_root,
            "dataset_config": self.dataset_config,
            "config": self.config,
        }
        self.experiment_path = os.path.join(self.model_template_root, OUTPUT_DIR_NAME)
        if not os.path.exists(self.experiment_path):
            os.makedirs(self.experiment_path)
        path = os.path.join(self.experiment_path, EXPERIMENT_FILE_NAME)
        save_exp_info(exp_info, path)
        return self.experiment_path

    def load_experiment_info(self) -> Dict:
        """load experiment info from the experiment path."""
        self.experiment_path = os.path.join(self.model_template_root, OUTPUT_DIR_NAME)
        if not os.path.exists(self.experiment_path):
            raise EvolvingAgentError(f"There is no experiment in {self.experiment_path}")
        path = os.path.join(self.experiment_path, EXPERIMENT_FILE_NAME)
        return load_exp_info(path)

    def train(
        self,
        task: Optional[List[Dict]] = None,
        experiment_name: Optional[str] = None,
        model_test: Optional[ModelTemplateTest] = None,
    ) -> Any:
        """train model, it will train model by task config.

        Args:
            task (Optional[List[Dict]]): tasks
            experiment_name (Optional[str]): experiment name
            model_test (Optional[ModelTemplateTest]): model test

        Returns:
            Any: result of training
        """
        if experiment_name is None:
            experiment_name = self.config.get("experiment_name", EXPERIMENT_NAME)

        if task is None:
            task = self.generate_task(model_test)

        # save experiment info
        self.task = task
        with R.start(experiment_name=experiment_name, resume=True) as r:
            self.save_experiment_info(task_id=r.get_task_id())
            # train
            task_train(task)
        return r

    def generate_feature(self, prompt: Optional[str] = None, **kwargs) -> str:
        """generate feature by prompt.

        Args:
            prompt (Optional[str]): prompt to generate feature.

        Returns:
            str: code of generating feature.
        """
        if prompt is None:
            prompt = self.prompts["generate_feature"]

        code = self.prompt_manager.get_code(prompt, **kwargs)

        return code

    def generate_train(self, prompt: Optional[str] = None, **kwargs) -> str:
        """generate train code by prompt.

        Args:
            prompt (Optional[str]): prompt to generate train code.

        Returns:
            str: code of training.
        """
        if prompt is None:
            prompt = self.prompts["generate_train"]

        code = self.prompt_manager.get_code(prompt, **kwargs)

        return code

    def generate_infer(self, prompt: Optional[str] = None, **kwargs) -> str:
        """generate infer code by prompt.

        Args:
            prompt (Optional[str]): prompt to generate infer code.

        Returns:
            str: code of inferring.
        """
        if prompt is None:
            prompt = self.prompts["generate_infer"]

        code = self.prompt_manager.get_code(prompt, **kwargs)

        return code

    def generate_predict(self, prompt: Optional[str] = None, **kwargs) -> str:
        """generate predict code by prompt.

        Args:
            prompt (Optional[str]): prompt to generate predict code.

        Returns:
            str: code of predicting.
        """
        if prompt is None:
            prompt = self.prompts["generate_predict"]

        code = self.prompt_manager.get_code(prompt, **kwargs)

        return code

    def generate_evaluate(self, prompt: Optional[str] = None, **kwargs) -> str:
        """generate evaluate code by prompt.

        Args:
            prompt (Optional[str]): prompt to generate evaluate code.

        Returns:
            str: code of evaluating.
        """
        if prompt is None:
            prompt = self.prompts["generate_evaluate"]

        code = self.prompt_manager.get_code(prompt, **kwargs)

        return code

    def generate_code(
        self,
        prompt_name: str,
        **kwargs,
    ) -> str:
        """generate code by prompt name.

        Args:
            prompt_name (str): prompt name.

        Returns:
            str: code.
        """
        prompt = self.prompts.get(prompt_name)
        if prompt is None:
            raise EvolvingAgentError(f"There is no prompt named {prompt_name}")

        code = self.prompt_manager.get_code(prompt, **kwargs)

        return code