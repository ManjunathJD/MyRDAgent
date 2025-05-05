# rdagent/scenarios/data_mining/experiment/factor_template/base_gen_test.py
import pytest

from rdagent.scenarios.data_mining.experiment.factor_template.base import (
    FactorBase,
)


def test_factor_base_initialization():
    factor_base = FactorBase()
    assert factor_base is not None


def test_factor_base_factor_method_not_implemented():
    factor_base = FactorBase()
    with pytest.raises(NotImplementedError):
        factor_base.factor(None, None)