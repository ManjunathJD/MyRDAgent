import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from rdagent.utils.agent.ret import AgentRetCode
from rdagent.utils.conf import Config

_logger = logging.getLogger(__name__)


def get_module_name(path):
    """get module name from path, such as a.b.c from a/b/c.py"""
    if path.endswith(".py"):
        path = path[:-3]
    elif path.endswith(".yaml") or path.endswith(".json"):
        pass
    else:
        raise ValueError("path should end with .py or .yaml")

    path = path.replace(os.sep, ".")
    if path.endswith(".__init__"):
        path = path[:-9]
    if path.startswith("."):
        path = path[1:]
    return path


class Env(Config):
    """
    global env
    """

    ENV_NAME = "RDAGENT"

    def __init__(self):
        super().__init__()
        # whether user run this in code
        self.is_code_mode: bool = True
        # whether user run this in debug mode
        self.debug_mode: bool = False
        # the id of the task
        self.task_id: Optional[str] = None
        # the id of the proposal
        self.proposal_id: Optional[str] = None
        # the id of the experiment
        self.experiment_id: Optional[str] = None
        # the id of the workflow
        self.workflow_id: Optional[str] = None
        # the dir of the project
        self.project_dir: Optional[str] = os.getcwd()
        # the dir of the cache
        self.cache_dir: Optional[str] = None
        # the dir of the log
        self.log_dir: Optional[str] = None
        # the dir of the proposal
        self.proposal_dir: Optional[str] = None
        # the dir of the experiment
        self.experiment_dir: Optional[str] = None
        # the dir of the workflow
        self.workflow_dir: Optional[str] = None
        # the name of the task
        self.task_name: Optional[str] = None
        # the name of the proposal
        self.proposal_name: Optional[str] = None
        # the name of the experiment
        self.experiment_name: Optional[str] = None
        # the name of the workflow
        self.workflow_name: Optional[str] = None

        self.mode: Optional[str] = None

        self.scenario: Optional[str] = None
        self.rd_agent_version: Optional[str] = None
        self.llm: Optional[str] = None
        self.llm_type: Optional[str] = None
        self.llm_config: Optional[str] = None
        self.llm_log_path: Optional[str] = None
        self.llm_prompt_path: Optional[str] = None
        self.llm_model: Optional[str] = None

        # for data_agent
        self.agent_type: Optional[str] = None
        self.agent_llm: Optional[str] = None
        self.agent_llm_model: Optional[str] = None
        self.agent_dir: Optional[str] = None

        # whether enable ui
        self.ui_enable: bool = True
        # ui port
        self.ui_port: int = 8501
        # the file to load all the tasks
        self.task_file: Optional[str] = None

        self.task_base_dir: Optional[str] = None
        self.proposal_base_dir: Optional[str] = None
        self.experiment_base_dir: Optional[str] = None
        self.workflow_base_dir: Optional[str] = None

        self.conf: Dict[str, Any] = {}
        self.sys_config: Dict[str, Any] = {}

        # whether use ui to get the parameter
        self.use_ui_param = False
        self.conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conf.yaml")

    def get_conf(self, conf_path: Optional[str] = None) -> Dict[str, Any]:
        """get conf, include user_conf and system_conf
        user_conf.yaml will be merged into sys_config.yaml if existed
        """
        self.conf = self._read_conf(conf_path)
        sys_conf = self.get_sys_config()

        self.conf = self.merge_config(sys_conf, self.conf)
        return self.conf

    def get_sys_config(self) -> Dict[str, Any]:
        """load system config"""
        conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sys_config.yaml")
        self.sys_config = self._read_conf(conf_path)
        return self.sys_config

    def _read_conf(self, conf_path: Optional[str] = None) -> Dict[str, Any]:
        if conf_path is None:
            conf_path = self.conf_path
        if not os.path.exists(conf_path):
            return {}

        conf = self.read_yaml(conf_path)
        return conf

    def init_env(self, env_name: str = None, **kwargs):
        """init env"""
        # load all config
        self.get_conf()
        # load sys config
        self.get_sys_config()
        # get env variable
        env_name = env_name or self.ENV_NAME
        if env_name in os.environ:
            env_str = os.environ[env_name]
            _logger.info("load env variable from env: %s:%s", env_name, env_str)
            self.load_from_json(env_str)

        # update from kwargs
        self.update(kwargs)

        # update system config if set
        if "sys_config" in self.conf:
            self.update(self.conf["sys_config"])
        # update cache dir from system config
        self.cache_dir = self.get("cache_dir", self.cache_dir)
        # update log dir from system config
        self.log_dir = self.get("log_dir", self.log_dir)
        # update llm config
        self.llm_config = self.get("llm_config", self.llm_config)
        # update ui enable
        self.ui_enable = self.get("ui_enable", self.ui_enable)
        # update ui port
        self.ui_port = self.get("ui_port", self.ui_port)

        # update task base dir
        self.task_base_dir = self.get("task_base_dir", self.task_base_dir)
        # update proposal base dir
        self.proposal_base_dir = self.get("proposal_base_dir", self.proposal_base_dir)
        # update experiment base dir
        self.experiment_base_dir = self.get("experiment_base_dir", self.experiment_base_dir)
        # update workflow base dir
        self.workflow_base_dir = self.get("workflow_base_dir", self.workflow_base_dir)

        # load llm config if existed
        if self.llm_config:
            if not os.path.exists(self.llm_config):
                raise ValueError(f"llm config not exist: {self.llm_config}")
            llm_conf = self.read_yaml(self.llm_config)
            self.update(llm_conf)
        self.init_dir()

    def init_dir(self):
        """init directory, such as cache, log..."""
        if self.project_dir is None:
            raise ValueError("project_dir is None")

        if self.task_base_dir is None:
            self.task_base_dir = os.path.join(self.project_dir, "tasks")
        if self.proposal_base_dir is None:
            self.proposal_base_dir = os.path.join(self.project_dir, "proposals")
        if self.experiment_base_dir is None:
            self.experiment_base_dir = os.path.join(self.project_dir, "experiments")
        if self.workflow_base_dir is None:
            self.workflow_base_dir = os.path.join(self.project_dir, "workflows")
        if self.cache_dir is None:
            self.cache_dir = os.path.join(self.project_dir, "cache")
        if self.log_dir is None:
            self.log_dir = os.path.join(self.project_dir, "log")

        self.create_dir(self.task_base_dir)
        self.create_dir(self.proposal_base_dir)
        self.create_dir(self.experiment_base_dir)
        self.create_dir(self.workflow_base_dir)
        self.create_dir(self.cache_dir)
        self.create_dir(self.log_dir)

    def set_task_info(self, task_id: str, task_name: str = None):
        """set task info"""
        self.task_id = task_id
        self.task_name = task_name
        if self.task_base_dir is None:
            raise ValueError("task_base_dir is None")
        self.task_dir = os.path.join(self.task_base_dir, task_id)
        self.create_dir(self.task_dir)

    def set_proposal_info(self, proposal_id: str, proposal_name: str = None):
        """set proposal info"""
        self.proposal_id = proposal_id
        self.proposal_name = proposal_name
        if self.proposal_base_dir is None:
            raise ValueError("proposal_base_dir is None")
        self.proposal_dir = os.path.join(self.proposal_base_dir, proposal_id)
        self.create_dir(self.proposal_dir)

    def set_experiment_info(self, experiment_id: str, experiment_name: str = None):
        """set experiment info"""
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        if self.experiment_base_dir is None:
            raise ValueError("experiment_base_dir is None")
        self.experiment_dir = os.path.join(self.experiment_base_dir, experiment_id)
        self.create_dir(self.experiment_dir)

    def set_workflow_info(self, workflow_id: str, workflow_name: str = None):
        """set workflow info"""
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        if self.workflow_base_dir is None:
            raise ValueError("workflow_base_dir is None")
        self.workflow_dir = os.path.join(self.workflow_base_dir, workflow_id)
        self.create_dir(self.workflow_dir)

    def check_llm(self, llm_name: str):
        """check if llm supported"""
        if llm_name not in self.conf["support_llm"]:
            raise ValueError(f"llm_name: {llm_name} not supported. support: {self.conf['support_llm']}")
        return AgentRetCode.SUCCESS

    def get_llm_model(self, llm_name: str):
        """get llm model name"""
        if llm_name not in self.conf["support_llm"]:
            raise ValueError(f"llm_name: {llm_name} not supported. support: {self.conf['support_llm']}")
        llm_model_list = self.conf["support_llm"][llm_name]
        return llm_model_list

    def check_scenario(self, scenario_name: str):
        """check if scenario supported"""
        if scenario_name not in self.conf["support_scenario"]:
            raise ValueError(
                f"scenario_name: {scenario_name} not supported. support: {self.conf['support_scenario']}"
            )
        return AgentRetCode.SUCCESS

    def get_scenario_class(self, scenario_name: str):
        """get scenario class"""
        if scenario_name not in self.conf["support_scenario"]:
            raise ValueError(
                f"scenario_name: {scenario_name} not supported. support: {self.conf['support_scenario']}"
            )
        return self.conf["support_scenario"][scenario_name]

    def create_dir(self, dir_path: str):
        """create dir if not exist"""
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            _logger.info("create dir: %s", dir_path)

    def get_current_task_dir(self):
        """get current task dir"""
        if self.task_dir is None:
            raise ValueError("task_dir is None")
        return self.task_dir

    def get_current_proposal_dir(self):
        """get current proposal dir"""
        if self.proposal_dir is None:
            raise ValueError("proposal_dir is None")
        return self.proposal_dir

    def get_current_experiment_dir(self):
        """get current experiment dir"""
        if self.experiment_dir is None:
            raise ValueError("experiment_dir is None")
        return self.experiment_dir

    def get_current_workflow_dir(self):
        """get current workflow dir"""
        if self.workflow_dir is None:
            raise ValueError("workflow_dir is None")
        return self.workflow_dir

    def clear_current_task(self):
        """clear current task dir"""
        if self.task_dir is not None and os.path.exists(self.task_dir):
            import shutil

            shutil.rmtree(self.task_dir)
        self.task_id = None
        self.task_name = None
        self.task_dir = None

    def clear_current_proposal(self):
        """clear current proposal dir"""
        if self.proposal_dir is not None and os.path.exists(self.proposal_dir):
            import shutil

            shutil.rmtree(self.proposal_dir)
        self.proposal_id = None
        self.proposal_name = None
        self.proposal_dir = None

    def clear_current_experiment(self):
        """clear current experiment dir"""
        if self.experiment_dir is not None and os.path.exists(self.experiment_dir):
            import shutil

            shutil.rmtree(self.experiment_dir)
        self.experiment_id = None
        self.experiment_name = None
        self.experiment_dir = None

    def clear_current_workflow(self):
        """clear current workflow dir"""
        if self.workflow_dir is not None and os.path.exists(self.workflow_dir):
            import shutil

            shutil.rmtree(self.workflow_dir)
        self.workflow_id = None
        self.workflow_name = None
        self.workflow_dir = None


# global env
env = Env()