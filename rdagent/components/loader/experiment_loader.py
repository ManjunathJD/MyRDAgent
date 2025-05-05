from rdagent.components.coder.factor_coder.factor import FactorExperiment
from rdagent.core.experiment import Loader
from rdagent.components.coder.model_coder.model import ModelExperiment


class FactorExperimentLoader(Loader[FactorExperiment]):
    pass


class ModelExperimentLoader(Loader[ModelExperiment]):
    pass
