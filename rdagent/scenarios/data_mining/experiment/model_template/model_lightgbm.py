# rdagent/scenarios/kaggle/experiment/templates/meta_tpl_deprecated/fea_share_preprocess.py

import pandas as pd


def preprocess(df):
    """
    This function performs preprocessing on the input DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The preprocessed DataFrame.
    """
    # Example preprocessing steps:
    # Fill missing values with the mean of each column
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in ['int64', 'float64']:
                df[col].fillna(df[col].mean(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)

    return df