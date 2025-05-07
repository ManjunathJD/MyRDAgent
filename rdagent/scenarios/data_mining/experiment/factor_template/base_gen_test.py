# rdagent/scenarios/data_mining/experiment/factor_template/base_gen_test.py
import pytest

from rdagent.scenarios.data_mining.experiment.factor_template.base import (
    FactorBase,
)

class TestFactor(FactorBase):
    def factor(self, data, params):
        return data

def test_factor_base_initialization():
    factor_base = TestFactor()
    assert factor_base is not None


def test_factor_base_factor_method_not_implemented():
    class TestFactor(FactorBase):
        def factor(self, data, params):
            raise NotImplementedError("Test implementation")
    
    test_factor = TestFactor()
    with pytest.raises(NotImplementedError):
        test_factor.factor(None, None)
