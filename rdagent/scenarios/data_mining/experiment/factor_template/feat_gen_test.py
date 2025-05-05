# rdagent/scenarios/data_mining/experiment/factor_template/feat_gen_test.py
import pytest

from rdagent.scenarios.data_mining.experiment.factor_template.utils import generate_factor_code


@pytest.mark.parametrize(
    "feat_type", ["ts_feat", "cs_feat", "customized_feat"]
)
def test_generate_factor_code(feat_type):
    if feat_type == "ts_feat":
        factor_code = generate_factor_code(
            feat_name="test_ts_feat",
            feat_type=feat_type,
            data_set_name="test_data",
            period_list=["1d"],
            feature_list=["open", "high", "low", "close"],
            extra_params={"test": "test_str"},
        )
        assert factor_code == """
def test_ts_feat(data_set_name, period_list):
    # please implement feature logic here
    # data_set_name is input, such as "test_data"
    # period_list is input, such as ["1d"]
    # return value must be a DataFrame, index is datetime and code
    pass
"""
    elif feat_type == "cs_feat":
        factor_code = generate_factor_code(
            feat_name="test_cs_feat",
            feat_type=feat_type,
            data_set_name="test_data",
            period_list=["1d"],
            feature_list=["open", "high", "low", "close"],
            extra_params={"test": "test_str"},
        )
        assert factor_code == """
def test_cs_feat(data_set_name, period_list):
    # please implement feature logic here
    # data_set_name is input, such as "test_data"
    # period_list is input, such as ["1d"]
    # return value must be a DataFrame, index is datetime and code
    pass
"""

    elif feat_type == "customized_feat":
        factor_code = generate_factor_code(
            feat_name="test_cus_feat",
            feat_type=feat_type,
            data_set_name="test_data",
            period_list=["1d"],
            feature_list=["open", "high", "low", "close"],
            extra_params={"test": "test_str"},
        )
        assert factor_code == """
def test_cus_feat(data_set_name, period_list):
    # please implement feature logic here
    # data_set_name is input, such as "test_data"
    # period_list is input, such as ["1d"]
    # return value must be a DataFrame, index is datetime and code
    pass
"""
    else:
        assert False