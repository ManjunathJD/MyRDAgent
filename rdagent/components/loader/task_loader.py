import json
from pathlib import Path
from typing import Sequence, Optional, Any
from collections.abc import Mapping
from rdagent.components.coder.factor_coder.factor import FactorTask
from rdagent.components.coder.model_coder.model import ModelFBWorkspace, ModelTask
from rdagent.core.experiment import Loader, WsLoader


class FactorTaskLoader(Loader[FactorTask]):
    pass


class ModelTaskLoader(Loader[ModelTask]):
    pass


class ModelTaskLoaderJson(ModelTaskLoader):
    def __init__(self, json_uri: str) -> None:
        super().__init__()
        self.json_uri = json_uri

    def load(self, *argT: Any, **kwargs: Any) -> Sequence[ModelTask]:
        # json is supposed to be in the format of {model_name: dict{model_data}}
        model_dict = json.load(open(self.json_uri, "r"))
        # FIXME: the model in the json file is not right due to extraction error
        #       We should fix them case by case in the future
        #
        # formula_info = {
        #     "name": "Anti-Symmetric Deep Graph Network (A-DGN)",
        #     "description": "A framework for stable and non-dissipative DGN design. It ensures long-range information preservation between nodes and prevents gradient vanishing or explosion during training.",
        #     "formulation": r"\mathbf{x}^{\prime}_i = \mathbf{x}_i + \epsilon \cdot \sigma \left( (\mathbf{W}-\mathbf{W}^T-\gamma \mathbf{I}) \mathbf{x}_i + \Phi(\mathbf{X}, \mathcal{N}_i) + \mathbf{b}\right),",
        #     "variables": {
        #         r"\mathbf{x}_i": "The state of node i at previous layer",
        #         r"\epsilon": "The step size in the Euler discretization",
        #         r"\sigma": "A monotonically non-decreasing activation function",
        #         r"\Phi": "A graph convolutional operator",
        #         r"W": "An anti-symmetric weight matrix",
        #         r"\mathbf{x}^{\prime}_i": "The node feature matrix at layer l-1",
        #         r"\mathcal{N}_i": "The set of neighbors of node u",
        #         r"\mathbf{b}": "A bias vector",
        #     },
        #     "key": "A-DGN",
        # }
        model_impl_task_list = []
        for model_name, model_data in model_dict.items():
            model_impl_task = ModelTask(
                name=model_name,
                description=model_data["description"],
                formulation=model_data["formulation"],
                variables=model_data["variables"],
                model_type=model_data["model_type"],
                architecture="",
                hyperparameters="",
            )
            model_impl_task_list.append(model_impl_task)
        return model_impl_task_list


class ModelWsLoader(WsLoader[ModelTask, ModelFBWorkspace]):
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self, task: ModelTask) -> ModelFBWorkspace: 
        assert task.name is not None
        mti = ModelFBWorkspace(task)
        mti.prepare()
        with open(self.path / f"{task.name}.py", "r") as f:
            code = f.read()
        mti.inject_files(**{"model.py": code})
        return mti
