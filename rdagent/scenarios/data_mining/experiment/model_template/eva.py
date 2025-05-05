import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from qlib.utils import init_instance_by_config, lazy_sort_key
from qlib.utils.time import Freq
from qlib.workflow.record_temp import TempRecord

from rdagent.core.exception import RLException
from rdagent.core.prompts import RDPrompt
from rdagent.log.base import logger
from rdagent.utils.agent.ret import ActionRet
from rdagent.utils.agent.workflow import AgentInfra
from rdagent.utils.conf import Conf
from rdagent.utils.env import Env
from rdagent.utils.fmt import make_bold_red_text
from rdagent.utils.repo.diff import get_diff_files

# Remove deprecated functionality

class FactorTemplate:
    """
    Factor Template
    """

    def __init__(self, agent_infra: AgentInfra = None, conf: Dict = None):
        """
        Parameters
        ----------
        agent_infra: AgentInfra
            agent infrastructure
        conf: dict
            the config of model template
        """
        self.agent_infra = agent_infra or AgentInfra()
        self.conf: Dict = conf or dict()

    def _get_factor_dir(self):
        """
        Get factor directory

        Returns
        -------
        str
            factor directory
        """
        factor_dir = self.conf.get("factor_dir", "./factor")
        if factor_dir is None:
            raise RLException(f"factor_dir must be specified in template config")
        return factor_dir

    def _get_factor_code_path(self, factor_name: str):
        """
        Get factor code path

        Parameters
        ----------
        factor_name : str
            factor name

        Returns
        -------
        str
            factor code path
        """
        factor_dir = self._get_factor_dir()
        return os.path.join(factor_dir, factor_name + ".py")

    def create_factor_code(self, factor_name: str, factor_code: str, force_overwrite=False) -> ActionRet:
        """
        Create factor code

        Parameters
        ----------
        factor_name : str
            factor name
        factor_code : str
            factor code
        force_overwrite: bool
            force overwrite

        Returns
        -------
        ActionRet
            action result
        """
        if not isinstance(factor_name, str) or not isinstance(factor_code, str):
            raise ValueError(f"factor_name and factor_code must be string, got {type(factor_name)} and {type(factor_code)}")

        factor_path = self._get_factor_code_path(factor_name)
        if os.path.exists(factor_path) and not force_overwrite:
            logger.warning(f"factor code already exists: {factor_path}, skip creation")
            return ActionRet(False, f"factor code already exists: {factor_path}")
        os.makedirs(os.path.dirname(factor_path), exist_ok=True)
        with open(factor_path, "w") as f:
            f.write(factor_code)
        logger.info(f"factor code is created to: {factor_path}")
        return ActionRet(True, f"factor code is created to: {factor_path}")

    def generate_factor_code_by_prompt(
        self, factor_name: str, instruction: str = None, force_overwrite=False
    ) -> Tuple[ActionRet, str]:
        """
        Generate factor code by prompt

        Parameters
        ----------
        factor_name : str
            factor name
        instruction : str
            instruction
        force_overwrite: bool
            force overwrite

        Returns
        -------
        Tuple[ActionRet, str]
            action result and factor code
        """
        if not isinstance(factor_name, str):
            raise ValueError(f"factor_name must be string, got {type(factor_name)}")
        if instruction is not None and not isinstance(instruction, str):
            raise ValueError(f"instruction must be string, got {type(instruction)}")

        factor_code_path = self._get_factor_code_path(factor_name)
        if os.path.exists(factor_code_path) and not force_overwrite:
            logger.warning(f"factor code already exists: {factor_code_path}, skip generation")
            return ActionRet(False, f"factor code already exists: {factor_code_path}"), None
        prompts = {
            "factor_name": factor_name,
            "factor_description": instruction,
        }
        prompt = RDPrompt("factor_coder", **prompts).generate_prompt()

        action_ret, code = self.agent_infra.do_coding(prompt)
        if action_ret.is_success():
            # create factor code file
            self.create_factor_code(factor_name, code, force_overwrite)
        return action_ret, code

    def generate_factor_by_prompt(
        self, factor_name: str, instruction: str = None, force_overwrite=False
    ) -> Tuple[ActionRet, Any]:
        """
        Generate factor by prompt

        Parameters
        ----------
        factor_name : str
            factor name
        instruction : str
            instruction
        force_overwrite: bool
            force overwrite

        Returns
        -------
        Tuple[ActionRet, Any]
            action result and factor
        """
        action_ret, code = self.generate_factor_code_by_prompt(
            factor_name, instruction, force_overwrite=force_overwrite
        )
        if action_ret.is_success():
            logger.info(f"successfully generate factor code for: {factor_name}")
            factor_instance = self.create_factor_instance(factor_name)
            return action_ret, factor_instance
        else:
            return action_ret, None

    def create_factor_instance(self, factor_name: str) -> Any:
        """
        Create factor instance

        Parameters
        ----------
        factor_name : str
            factor name

        Returns
        -------
        Any
            factor instance
        """
        factor_code_path = self._get_factor_code_path(factor_name)
        if not os.path.exists(factor_code_path):
            raise RLException(f"factor code file does not exist: {factor_code_path}")
        # add factor dir to sys path
        factor_dir = self._get_factor_dir()
        if factor_dir not in sys.path:
            sys.path.append(factor_dir)
        try:
            factor_instance = init_instance_by_config(
                {"class": factor_name, "module_path": os.path.dirname(factor_code_path)},
                accept_types=[pd.DataFrame],
            )
        except Exception as e:
            logger.exception(e)
            raise RLException(
                make_bold_red_text(
                    f"error happened when creating factor instance: {factor_name} by factor code: {factor_code_path}"
                )
            )
        return factor_instance

    def get_report_diff_files(self, report_path: str, git_branch: Optional[str] = None) -> List:
        """
        Get the diff files from the last commit

        Parameters
        ----------
        report_path : str
            report path
        git_branch : str
            git branch

        Returns
        -------
        list
            list of diff files
        """
        logger.info(f"report_path is {report_path}")
        # get the report diff files
        repo_files = get_diff_files(git_branch)
        if not isinstance(repo_files, list) or len(repo_files) == 0:
            logger.warning(f"no diff files found in branch {git_branch}")
            repo_files = []
        logger.info(f"repo diff files: {repo_files}")
        return repo_files

    def get_factor_report_diff_files(
        self,
        report_path: str,
        git_branch: Optional[str] = None,
    ) -> List:
        """
        Get the factor report diff files

        Parameters
        ----------
        report_path : str
            report path
        git_branch : str
            git branch

        Returns
        -------
        list
            list of factor report diff files
        """
        # get the diff files in report
        diff_files = self.get_report_diff_files(report_path, git_branch)
        # get the factor code path in the diff files
        factor_files = []
        factor_dir = self._get_factor_dir()
        for diff_file in diff_files:
            if diff_file.startswith(factor_dir):
                factor_files.append(diff_file)
        return factor_files

    def eval_factor_by_instance(
        self,
        factor_name: str,
        factor_instance: Any,
        qlib_env_conf: Dict,
        data_freq: Union[str, Freq] = "day",
        eval_start_time: Union[str, pd.Timestamp] = None,
        eval_end_time: Union[str, pd.Timestamp] = None,
    ):
        """
        Evaluate factor by instance

        Parameters
        ----------
        factor_name : str
            factor name
        factor_instance : Any
            factor instance
        qlib_env_conf : dict
            qlib environment config
        data_freq : str or Freq
            data frequency
        eval_start_time : str or pd.Timestamp
            eval start time
        eval_end_time : str or pd.Timestamp
            eval end time
        """

        # init qlib env
        if Env.is_qlib_env_inited():
            logger.info("qlib env has already inited, skip init")
        else:
            Env.init_qlib_env(qlib_env_conf)

        # create temp report record
        with TempRecord(recorder=self.conf.get("recorder", None)) as factor_rec:
            factor_rec.save_objects(**{"factor_name": factor_name, "factor": factor_instance})
            # add factor eval record to agent infra
            self.agent_infra.add_factor_eval_record(factor_rec)
            report_info = self.agent_infra.get_factor_report_info(factor_rec, factor_name)

            factor_eval_obj = init_instance_by_config(
                self.conf.get("factor_evaluator"),
                **{
                    "report_info": report_info,
                    "data_freq": data_freq,
                    "eval_start_time": eval_start_time,
                    "eval_end_time": eval_end_time,
                },
            )
            factor_eval_result = factor_eval_obj.eval()
        return factor_eval_result

    def eval_factor_by_name(
        self,
        factor_name: str,
        qlib_env_conf: Dict,
        data_freq: Union[str, Freq] = "day",
        eval_start_time: Union[str, pd.Timestamp] = None,
        eval_end_time: Union[str, pd.Timestamp] = None,
    ):
        """
        Evaluate factor by name

        Parameters
        ----------
        factor_name : str
            factor name
        qlib_env_conf : dict
            qlib environment config
        data_freq : str or Freq
            data frequency
        eval_start_time : str or pd.Timestamp
            eval start time
        eval_end_time : str or pd.Timestamp
            eval end time
        """
        factor_instance = self.create_factor_instance(factor_name)
        factor_eval_result = self.eval_factor_by_instance(
            factor_name, factor_instance, qlib_env_conf, data_freq, eval_start_time, eval_end_time
        )
        return factor_eval_result

    def eval_all_factors(
        self,
        factor_names: List,
        qlib_env_conf: Dict,
        data_freq: Union[str, Freq] = "day",
        eval_start_time: Union[str, pd.Timestamp] = None,
        eval_end_time: Union[str, pd.Timestamp] = None,
    ):
        """
        Evaluate all factors

        Parameters
        ----------
        factor_names : list
            list of factor name
        qlib_env_conf : dict
            qlib environment config
        data_freq : str or Freq
            data frequency
        eval_start_time : str or pd.Timestamp
            eval start time
        eval_end_time : str or pd.Timestamp
            eval end time
        """
        eval_results = {}
        for factor_name in sorted(factor_names, key=lazy_sort_key):
            eval_results[factor_name] = self.eval_factor_by_name(
                factor_name, qlib_env_conf, data_freq, eval_start_time, eval_end_time
            )
        return eval_results