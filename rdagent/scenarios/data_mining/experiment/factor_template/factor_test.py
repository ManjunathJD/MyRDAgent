# rdagent/scenarios/data_mining/experiment/factor_template/factor.py

import pandas as pd

from rdagent.log import logger

class Factor(object):
    def __init__(self, factor_name: str, data: pd.DataFrame = None):
        self.factor_name = factor_name
        self.data = data
        logger.info(f"Factor {factor_name} initialized")

    def cal_factor(self, data: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate factor, return a DataFrame with index and factor_name
        """
        if data is None and self.data is None:
            raise ValueError("No data provided")
        if data is not None:
            self.data = data
        return self.data.rename(columns={"value": self.factor_name})