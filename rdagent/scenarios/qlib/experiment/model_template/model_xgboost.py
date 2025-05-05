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
    # Convert categorical columns to string type
    for col in df.select_dtypes(include=['category']).columns:
        df[col] = df[col].astype(str)

    # Convert object type columns to string type
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str)
    
    # Convert datetime columns to datetime type
    for col in df.select_dtypes(include=['datetime64']).columns:
        df[col] = pd.to_datetime(df[col])

    # Fill missing values with the mean for numeric columns
    for col in df.select_dtypes(include=['number']).columns:
        df[col] = df[col].fillna(df[col].mean())

    # Fill missing values with the mode for non-numeric columns
    for col in df.select_dtypes(exclude=['number']).columns:
        df[col] = df[col].fillna(df[col].mode()[0])

    return df