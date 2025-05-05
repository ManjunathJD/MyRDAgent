# rdagent/scenarios/data_mining/experiment/factor_template/dataset_gen_test.py
import pytest
from rdagent.scenarios.data_mining.experiment.factor_template.utils import generate_dataset

def test_generate_dataset():
    data = generate_dataset(num_samples=100, num_features=5, noise=0.1)
    assert data is not None
    assert len(data[0]) == 100
    assert len(data[0][0]) == 5
    assert len(data) == 2