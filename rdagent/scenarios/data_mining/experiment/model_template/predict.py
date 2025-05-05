import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from qlib.utils import init_instance_by_config, lazy_sort_key, parse_config

from ...core.developer import BaseDeveloper
from ...core.evaluation import BaseEvaluator
from ...core.exception import EvolvingError
from ...core.experiment import Experiment
from ...core.prompts import Prompts
from ...core.proposal import BaseProposal, Proposal
from ...utils import get_file_modified_time, list_files
from ...utils.agent.ret import AgentRet
from ...utils.agent.tpl import BaseAgent, create_agent
from ...utils.workflow import Executor


class BaseDataMiningProposal(BaseProposal):
    """
    This is the base class of DataMiningProposal.
    It defines some basic properties and methods for DataMiningProposal.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_scenario_info(self) -> Dict[str, Any]:
        """
        Get scenario information.

        Returns
        -------
        Dict[str, Any]:
            Scenario information.
        """
        info = super().get_scenario_info()
        info["domain"] = "DataMining"
        return info


class ModelProposal(BaseDataMiningProposal):
    """
    This is the class of ModelProposal.
    It defines the properties and methods for ModelProposal.
    """

    def __init__(
        self,
        agent: Optional[Union[str, BaseAgent]] = None,
        agent_prompt_name: Optional[str] = None,
        agent_prompt_path: Optional[str] = None,
        agent_prompt_kwargs: Optional[Dict[str, Any]] = None,
        evaluators: Optional[List[Union[str, BaseEvaluator]]] = None,
        evaluator_prompt_name: Optional[str] = None,
        evaluator_prompt_path: Optional[str] = None,
        evaluator_prompt_kwargs: Optional[Dict[str, Any]] = None,
        developer: Optional[Union[str, BaseDeveloper]] = None,
        developer_prompt_name: Optional[str] = None,
        developer_prompt_path: Optional[str] = None,
        developer_prompt_kwargs: Optional[Dict[str, Any]] = None,
        executor: Optional[Executor] = None,
        # file to check
        template_path: Optional[str] = "model_template",
        data_dir: Optional[str] = "data",
        exp_conf: Optional[Union[str, Dict[str, Any]]] = "model_template_conf.yaml",
        **kwargs,
    ):
        """
        Parameters
        ----------
        agent : Optional[Union[str, BaseAgent]], optional
            The agent of the proposal, by default None
        agent_prompt_name : Optional[str], optional
            The prompt name of the agent, by default None
        agent_prompt_path : Optional[str], optional
            The prompt path of the agent, by default None
        agent_prompt_kwargs : Optional[Dict[str, Any]], optional
            The prompt kwargs of the agent, by default None
        evaluators : Optional[List[Union[str, BaseEvaluator]]], optional
            The evaluators of the proposal, by default None
        evaluator_prompt_name : Optional[str], optional
            The prompt name of the evaluator, by default None
        evaluator_prompt_path : Optional[str], optional
            The prompt path of the evaluator, by default None
        evaluator_prompt_kwargs : Optional[Dict[str, Any]], optional
            The prompt kwargs of the evaluator, by default None
        developer : Optional[Union[str, BaseDeveloper]], optional
            The developer of the proposal, by default None
        developer_prompt_name : Optional[str], optional
            The prompt name of the developer, by default None
        developer_prompt_path : Optional[str], optional
            The prompt path of the developer, by default None
        developer_prompt_kwargs : Optional[Dict[str, Any]], optional
            The prompt kwargs of the developer, by default None
        executor : Optional[Executor], optional
            The executor of the proposal, by default None
        template_path : Optional[str], optional
            The template path of the proposal, by default "model_template"
        data_dir : Optional[str], optional
            The data dir of the proposal, by default "data"
        exp_conf : Optional[Union[str, Dict[str, Any]]], optional
            The experiment config of the proposal, by default "model_template_conf.yaml"
        """

        super().__init__(**kwargs)
        # proposal
        self.agent_prompt_name = agent_prompt_name or "model_proposal_agent"
        self.agent_prompt_path = agent_prompt_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "prompts.yaml"
        )
        self.agent_prompt_kwargs = agent_prompt_kwargs or {}

        self.evaluator_prompt_name = evaluator_prompt_name or "model_proposal_evaluator"
        self.evaluator_prompt_path = evaluator_prompt_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "prompts.yaml"
        )
        self.evaluator_prompt_kwargs = evaluator_prompt_kwargs or {}

        self.developer_prompt_name = developer_prompt_name or "model_proposal_developer"
        self.developer_prompt_path = developer_prompt_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "prompts.yaml"
        )
        self.developer_prompt_kwargs = developer_prompt_kwargs or {}

        # file to check
        self.template_path = template_path
        self.data_dir = data_dir
        self.exp_conf = exp_conf

        # add to proposal
        self.agent = agent or "model_proposal_agent"
        self.evaluators = evaluators or ["model_proposal_evaluator"]
        self.developer = developer or "model_proposal_developer"
        self.executor = executor or Executor()

        # load prompt
        self.agent_prompt: Prompts = self._load_prompt(
            self.agent_prompt_name, self.agent_prompt_path, **self.agent_prompt_kwargs
        )
        self.evaluator_prompt: Prompts = self._load_prompt(
            self.evaluator_prompt_name, self.evaluator_prompt_path, **self.evaluator_prompt_kwargs
        )
        self.developer_prompt: Prompts = self._load_prompt(
            self.developer_prompt_name, self.developer_prompt_path, **self.developer_prompt_kwargs
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate(self, experiment: Experiment, **kwargs) -> AgentRet:
        """
        Generate model proposal.

        Parameters
        ----------
        experiment : Experiment
            The experiment.

        Returns
        -------
        AgentRet
            The agent return.
        """
        # 1. Init agent
        agent: BaseAgent = create_agent(
            self.agent,
            self.agent_prompt,
            self.logger,
            self.get_scenario_info(),
            self.agent_prompt_kwargs,
        )
        self.logger.info(f"agent: {agent.name}")

        # 2. Create proposal with agent
        res = agent(experiment=experiment)

        # check
        if not isinstance(res, AgentRet):
            raise EvolvingError(f"Agent must return AgentRet, but got {type(res)}")
        if res.status != "succeeded":
            self.logger.error(f"Agent failed: {res.result}")
            raise EvolvingError(f"Agent failed: {res.result}")

        # 3. save
        if res.result and isinstance(res.result, str):
            self.logger.info("agent output:\n" + res.result)
            experiment.save_file(res.result, "proposal.md")
        return res

    def evaluate(self, proposal: Proposal, experiment: Experiment, **kwargs) -> List[AgentRet]:
        """
        Evaluate model proposal.

        Parameters
        ----------
        proposal : Proposal
            The proposal.
        experiment : Experiment
            The experiment.

        Returns
        -------
        List[AgentRet]
            The list of agent return.
        """
        res_list: List[AgentRet] = []

        # 1. Init evaluator
        for evaluator in self.evaluators:
            evaluator: BaseEvaluator = init_instance_by_config(
                evaluator,
                default_module=sys.modules[__name__],
                default_kwargs={
                    "logger": self.logger,
                    "scenario_info": self.get_scenario_info(),
                    "prompt": self.evaluator_prompt,
                    "prompt_kwargs": self.evaluator_prompt_kwargs,
                },
            )
            self.logger.info(f"evaluator: {evaluator.name}")

            # 2. Create evaluation with evaluator
            res = evaluator(proposal=proposal, experiment=experiment)

            # check
            if not isinstance(res, AgentRet):
                raise EvolvingError(f"Evaluator must return AgentRet, but got {type(res)}")
            if res.status != "succeeded":
                self.logger.error(f"Evaluator failed: {res.result}")
                raise EvolvingError(f"Evaluator failed: {res.result}")

            # 3. save
            if res.result and isinstance(res.result, str):
                self.logger.info(f"{evaluator.name} output:\n" + res.result)
                experiment.save_file(res.result, f"{evaluator.name}.md")

            res_list.append(res)

        return res_list

    def develop(self, proposal: Proposal, experiment: Experiment, **kwargs) -> List[AgentRet]:
        """
        Develop model proposal.

        Parameters
        ----------
        proposal : Proposal
            The proposal.
        experiment : Experiment
            The experiment.

        Returns
        -------
        List[AgentRet]
            The list of agent return.
        """
        # 1. Init developer
        developer: BaseDeveloper = init_instance_by_config(
            self.developer,
            default_module=sys.modules[__name__],
            default_kwargs={
                "logger": self.logger,
                "scenario_info": self.get_scenario_info(),
                "prompt": self.developer_prompt,
                "prompt_kwargs": self.developer_prompt_kwargs,
            },
        )
        self.logger.info(f"developer: {developer.name}")

        # 2. Create development with developer
        res = developer(proposal=proposal, experiment=experiment)

        # check
        if not isinstance(res, AgentRet):
            raise EvolvingError(f"Developer must return AgentRet, but got {type(res)}")
        if res.status != "succeeded":
            self.logger.error(f"Developer failed: {res.result}")
            raise EvolvingError(f"Developer failed: {res.result}")

        # 3. save
        if res.result and isinstance(res.result, str):
            self.logger.info("developer output:\n" + res.result)
            experiment.save_file(res.result, "code.md")

        return [res]

    def get_run_conf(self, proposal: Proposal, experiment: Experiment, **kwargs) -> Dict[str, Any]:
        """
        Get run config.

        Parameters
        ----------
        proposal : Proposal
            The proposal.
        experiment : Experiment
            The experiment.

        Returns
        -------
        Dict[str, Any]
            The run config.
        """
        # 1. get the run config
        path_model_conf = os.path.join(experiment.working_dir, self.template_path, self.exp_conf)
        # parse conf
        model_conf = parse_config(path_model_conf)
        return model_conf

    def get_run_files(self, proposal: Proposal, experiment: Experiment, **kwargs) -> Dict[str, Tuple[str, int]]:
        """
        Get run files.

        Parameters
        ----------
        proposal : Proposal
            The proposal.
        experiment : Experiment
            The experiment.

        Returns
        -------
        Dict[str, Tuple[str, int]]
            The run files.
        """
        # 1. get the run files
        path_template = os.path.join(experiment.working_dir, self.template_path)
        list_files_model = list_files(path_template, suffix=".py")
        # 2. sort list_files_model by lazy_sort_key
        list_files_model = sorted(list_files_model, key=lazy_sort_key)

        # 3. get file modified time
        files_modified_time_model = {
            file: get_file_modified_time(os.path.join(path_template, file)) for file in list_files_model
        }
        return files_modified_time_model

    def get_data(self, proposal: Proposal, experiment: Experiment, **kwargs) -> Dict[str, Any]:
        """
        Get data.

        Parameters
        ----------
        proposal : Proposal
            The proposal.
        experiment : Experiment
            The experiment.

        Returns
        -------
        Dict[str, Any]
            The data.
        """
        # 1. get the data
        path_data = os.path.join(experiment.working_dir, self.data_dir)
        if not os.path.exists(path_data):
            self.logger.warning(f"Data dir {path_data} does not exist.")
            return {}

        # 2. list files
        list_files_data = list_files(path_data, suffix=(".csv", ".pkl", ".feather", ".hdf5", ".parquet"))

        # 3. read files
        data_dict = {}
        for file in list_files_data:
            try:
                file_path = os.path.join(path_data, file)
                if file.endswith(".csv"):
                    data_dict[file] = pd.read_csv(file_path)
                elif file.endswith(".pkl"):
                    data_dict[file] = pd.read_pickle(file_path)
                elif file.endswith(".feather"):
                    data_dict[file] = pd.read_feather(file_path)
                elif file.endswith(".hdf5"):
                    data_dict[file] = pd.read_hdf(file_path)
                elif file.endswith(".parquet"):
                    data_dict[file] = pd.read_parquet(file_path)
                else:
                    self.logger.warning(f"Unknown file type: {file}")
            except Exception as e:
                self.logger.warning(f"Failed to read file: {file}, error: {e}")

        return data_dict