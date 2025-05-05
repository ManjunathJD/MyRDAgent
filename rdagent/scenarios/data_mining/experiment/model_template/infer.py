import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from rdagent.utils.env import get_env_config
from rdagent.utils.fmt import fmt_error
from rdagent.utils.module_ops import get_class_from_module, get_func_from_module
from rdagent.utils.repo import get_file_sha
from rdagent.utils.time_ops import Timer

logger = logging.getLogger(__name__)


class BaseEvaluation:
    """
    Base class for evaluation
    """

    def __init__(
        self,
        repo_root: str = None,
        code_root: str = None,
        data_root: str = None,
        eval_conf: Dict = None,
        eval_conf_path: str = None,
        task_name: str = None,
        eval_name: str = None,
        eval_class_name: str = None,
        eval_method_name: str = None,
        input_vars: Dict[str, Any] = None,
        output_vars: List[str] = None,
        model_path: str = None,
        model_func: str = None,
        data_path: str = None,
        data_func: str = None,
        data_file: str = None,
        gt_data_path: str = None,
        gt_data_func: str = None,
        gt_data_file: str = None,
    ):
        self.repo_root = repo_root or get_env_config().get("repo_root")
        self.code_root = code_root or os.path.join(self.repo_root, get_env_config().get("code_root"))
        self.data_root = data_root or os.path.join(self.repo_root, get_env_config().get("data_root"))
        self.eval_conf = eval_conf
        self.eval_conf_path = eval_conf_path
        self.task_name = task_name
        self.eval_name = eval_name
        self.eval_class_name = eval_class_name
        self.eval_method_name = eval_method_name
        self.input_vars = input_vars
        self.output_vars = output_vars
        self.model_path = model_path
        self.model_func = model_func
        self.data_path = data_path
        self.data_func = data_func
        self.data_file = data_file
        self.gt_data_path = gt_data_path
        self.gt_data_func = gt_data_func
        self.gt_data_file = gt_data_file

        self.check_path_exists()

        self.model_module, self.model_instance = self.load_model()
        self.data_module, self.data_instance = self.load_data()
        self.gt_data_module, self.gt_data_instance = self.load_gt_data()
        self.eval_module, self.eval_instance = self.load_eval()

    def check_path_exists(self):
        if self.repo_root is None:
            raise ValueError("repo_root is not set")
        if not os.path.exists(self.repo_root):
            raise ValueError(f"repo_root {self.repo_root} does not exist")
        if self.code_root is None:
            raise ValueError("code_root is not set")
        if not os.path.exists(self.code_root):
            raise ValueError(f"code_root {self.code_root} does not exist")
        if self.data_root is None:
            raise ValueError("data_root is not set")
        if not os.path.exists(self.data_root):
            raise ValueError(f"data_root {self.data_root} does not exist")
        if self.eval_conf_path is None:
            raise ValueError("eval_conf_path is not set")
        if not os.path.exists(self.eval_conf_path):
            raise ValueError(f"eval_conf_path {self.eval_conf_path} does not exist")
        if self.model_path is not None:
            abs_model_path = os.path.join(self.code_root, self.model_path)
            if not os.path.exists(abs_model_path):
                raise ValueError(f"model_path {abs_model_path} does not exist")
        if self.data_path is not None:
            abs_data_path = os.path.join(self.data_root, self.data_path)
            if not os.path.exists(abs_data_path):
                raise ValueError(f"data_path {abs_data_path} does not exist")
        if self.gt_data_path is not None:
            abs_gt_data_path = os.path.join(self.data_root, self.gt_data_path)
            if not os.path.exists(abs_gt_data_path):
                raise ValueError(f"gt_data_path {abs_gt_data_path} does not exist")

    def load_model(self) -> Tuple[Any, Any]:
        """
        load model code from code path
        """
        if self.model_path is None:
            return None, None
        abs_model_path = os.path.join(self.code_root, self.model_path)
        if self.model_func is not None:
            model_module, model_instance = get_class_from_module(
                abs_model_path, self.model_func
            )
        else:
            model_module, model_instance = None, None
        return model_module, model_instance

    def load_data(self) -> Tuple[Any, Any]:
        """
        load data from data path
        """
        if self.data_path is None:
            return None, None
        abs_data_path = os.path.join(self.data_root, self.data_path)
        if self.data_func is not None:
            data_module, data_instance = get_func_from_module(abs_data_path, self.data_func)
        else:
            data_module, data_instance = None, None
        return data_module, data_instance

    def load_gt_data(self) -> Tuple[Any, Any]:
        """
        load gt_data from data path
        """
        if self.gt_data_path is None:
            return None, None
        abs_gt_data_path = os.path.join(self.data_root, self.gt_data_path)
        if self.gt_data_func is not None:
            gt_data_module, gt_data_instance = get_func_from_module(
                abs_gt_data_path, self.gt_data_func
            )
        else:
            gt_data_module, gt_data_instance = None, None
        return gt_data_module, gt_data_instance

    def load_eval(self) -> Tuple[Any, Any]:
        """
        load eval code from eval conf
        """
        if self.eval_name is None or self.eval_class_name is None:
            raise ValueError("eval_name or eval_class_name is not set")
        eval_path_in_conf = self.eval_conf[self.eval_name]["file"]
        abs_eval_path = os.path.join(self.code_root, eval_path_in_conf)
        eval_module, eval_instance = get_class_from_module(abs_eval_path, self.eval_class_name)
        return eval_module, eval_instance

    def run_eval(self) -> Any:
        """
        run eval method
        """
        with Timer(f"{self.eval_name}.{self.eval_method_name}") as _:
            if self.eval_method_name is None:
                raise ValueError("eval_method_name is not set")
            if self.eval_instance is None:
                raise ValueError("eval_instance is not set")
            if self.model_instance is not None:
                if hasattr(self.model_instance, "__call__"):
                    logger.info(f"model instance is callable")
                    if self.data_instance is not None and hasattr(self.data_instance, "__call__"):
                        logger.info(f"data instance is callable")
                        if self.gt_data_instance is not None and hasattr(self.gt_data_instance, "__call__"):
                            logger.info(f"gt_data instance is callable")
                            gt_data_obj = self.gt_data_instance()
                            data_obj = self.data_instance()
                            model_obj = self.model_instance(data_obj, gt_data_obj)

                        else:
                            data_obj = self.data_instance()
                            model_obj = self.model_instance(data_obj)

                    else:
                        model_obj = self.model_instance()

                else:
                    logger.info(f"model instance is NOT callable")
                    model_obj = self.model_instance

            else:
                logger.info(f"model_instance is None")
                model_obj = None

            eval_method = getattr(self.eval_instance, self.eval_method_name)

            if self.input_vars is None:
                eval_ret = eval_method(model_obj)
            else:
                input_vars = {}
                if model_obj is not None:
                    input_vars["model"] = model_obj
                for var_name, var_path_in_conf in self.input_vars.items():
                    if "file" in var_path_in_conf and "func" in var_path_in_conf:
                        var_file = os.path.join(self.data_root, var_path_in_conf["file"])
                        var_func_name = var_path_in_conf["func"]
                        _, var_obj = get_func_from_module(var_file, var_func_name)
                        input_vars[var_name] = var_obj()

                    elif "file" in var_path_in_conf and "class" in var_path_in_conf:
                        var_file = os.path.join(self.data_root, var_path_in_conf["file"])
                        var_class_name = var_path_in_conf["class"]
                        _, var_obj = get_class_from_module(var_file, var_class_name)
                        input_vars[var_name] = var_obj()
                    else:
                        raise ValueError(f"invalid var_path_in_conf: {var_path_in_conf}")

                eval_ret = eval_method(**input_vars)

        if self.output_vars is not None:
            if not isinstance(eval_ret, tuple):
                raise ValueError("eval_ret is not a tuple")
            if len(eval_ret) != len(self.output_vars):
                raise ValueError(
                    f"length of eval_ret {len(eval_ret)} is not equal to output_vars {len(self.output_vars)}"
                )
            for idx, var_name in enumerate(self.output_vars):
                setattr(self, var_name, eval_ret[idx])
        else:
            self.ret = eval_ret

        return eval_ret

    def eval_all_method(self):
        """
        eval all method in the same class
        """
        method_list = [
            m
            for m in dir(self.eval_instance)
            if not m.startswith("_") and callable(getattr(self.eval_instance, m))
        ]
        logger.info(f"method_list: {method_list}")
        for method_name in method_list:
            self.eval_method_name = method_name
            self.run_eval()

    def save_eval_ret(self, save_path: str, filename: str = None, **kwargs):
        """
        save eval_ret
        """
        if not hasattr(self, "ret") or self.ret is None:
            logger.info("eval_ret is None, skip save_eval_ret")
            return
        os.makedirs(save_path, exist_ok=True)
        if filename is None:
            if self.eval_name is None or self.eval_method_name is None:
                raise ValueError("eval_name or eval_method_name is not set")
            filename = f"{self.eval_name}.{self.eval_method_name}.result.txt"
        save_filepath = os.path.join(save_path, filename)
        logger.info(f"save_filepath: {save_filepath}")
        if isinstance(self.ret, pd.DataFrame):
            self.ret.to_csv(save_filepath, **kwargs)
        elif isinstance(self.ret, dict):
            with open(save_filepath, "w") as f:
                f.write(str(self.ret))
        else:
            with open(save_filepath, "w") as f:
                f.write(str(self.ret))
        logger.info(f"save_eval_ret to {save_filepath} done")

    def save_eval_rets(self, save_path: str, **kwargs):
        """
        save eval_rets
        """
        os.makedirs(save_path, exist_ok=True)
        for var_name in self.output_vars:
            if hasattr(self, var_name) and getattr(self, var_name) is not None:
                filename = f"{self.eval_name}.{self.eval_method_name}.{var_name}.txt"
                save_filepath = os.path.join(save_path, filename)
                logger.info(f"save_filepath: {save_filepath}")
                save_obj = getattr(self, var_name)
                if isinstance(save_obj, pd.DataFrame):
                    save_obj.to_csv(save_filepath, **kwargs)
                elif isinstance(save_obj, dict):
                    with open(save_filepath, "w") as f:
                        f.write(str(save_obj))
                else:
                    with open(save_filepath, "w") as f:
                        f.write(str(save_obj))
                logger.info(f"save_eval_ret to {save_filepath} done")
            else:
                logger.info(f"var_name: {var_name} has no value, skip")

    def load_eval_ret(self, load_path: str, filename: str = None):
        """
        load eval_ret
        """
        if filename is None:
            if self.eval_name is None or self.eval_method_name is None:
                raise ValueError("eval_name or eval_method_name is not set")
            filename = f"{self.eval_name}.{self.eval_method_name}.result.txt"
        load_filepath = os.path.join(load_path, filename)
        logger.info(f"load_filepath: {load_filepath}")
        if not os.path.exists(load_filepath):
            raise ValueError(f"load_filepath {load_filepath} does not exist")

        with open(load_filepath, "r") as f:
            ret = f.read()
        self.ret = ret

    def load_eval_rets(self, load_path: str):
        """
        load eval_rets
        """
        for var_name in self.output_vars:
            filename = f"{self.eval_name}.{self.eval_method_name}.{var_name}.txt"
            load_filepath = os.path.join(load_path, filename)
            logger.info(f"load_filepath: {load_filepath}")
            if os.path.exists(load_filepath):
                with open(load_filepath, "r") as f:
                    ret = f.read()
                setattr(self, var_name, ret)
            else:
                logger.info(f"var_name: {var_name} has no file, skip")

    def get_file_sha(self) -> Optional[str]:
        """
        get file sha
        """
        if self.eval_conf is None:
            return None
        eval_file = self.eval_conf[self.eval_name]["file"]
        eval_abs_path = os.path.join(self.code_root, eval_file)
        file_sha = get_file_sha(eval_abs_path)
        return file_sha