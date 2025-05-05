# rdagent/scenarios/data_mining/experiment/factor_template/predict.py

import pandas as pd

from rdagent.scenarios.data_mining.experiment.model_template import utils

def predict(data_path: str, save_path: str):
    """
    This is the predict function template.
    You should rewrite it.
    """
    # read data
    df = pd.read_csv(data_path)

    # predict
    df['pred'] = 0.5

    # save
    df[['pred']].to_csv(save_path, index=False)