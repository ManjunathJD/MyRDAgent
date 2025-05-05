# rdagent/scenarios/data_mining/experiment/factor_template/gen_model_test.py

import pytest
from rdagent.scenarios.data_mining.experiment.model_template.utils import gen_model
from rdagent.scenarios.data_mining.experiment.model_template.base import BaseModel
from rdagent.scenarios.data_mining.experiment.model_template.factor import FactorBaseModel

@pytest.mark.parametrize("model_name", ["model_xgboost", "model_lightgbm"])
def test_gen_model(model_name: str):
    model = gen_model(model_name)
    assert isinstance(model, BaseModel)
    assert isinstance(model, FactorBaseModel)
    model.load_data()
    model.run()
    model.infer()
    model.predict()
    model.eva()
    model.train_test()
    assert model.name == model_name