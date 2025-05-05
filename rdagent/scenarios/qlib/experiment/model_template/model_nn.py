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
    # Convert categorical columns to numerical using one-hot encoding
    categorical_cols = df.select_dtypes(include=['object']).columns
    df = pd.get_dummies(df, columns=categorical_cols, dummy_na=False)
    # Handle missing values (example: fill with the mean)
    numerical_cols = df.select_dtypes(include=['number']).columns
    for col in numerical_cols:
        df[col].fillna(df[col].mean(), inplace=True)
    
    return df