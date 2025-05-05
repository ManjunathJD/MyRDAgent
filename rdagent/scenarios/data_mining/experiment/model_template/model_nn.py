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

def one_hot_encode(df, columns_to_encode):
    """
    One-hot encodes specified columns in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns_to_encode (list): A list of column names to be one-hot encoded.

    Returns:
        pd.DataFrame: The DataFrame with the specified columns one-hot encoded.
    """
    for col in columns_to_encode:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col)
            df = pd.concat([df, dummies], axis=1)
            df.drop(col, axis=1, inplace=True)
        else:
            print(f"Warning: Column '{col}' not found in DataFrame. Skipping one-hot encoding for this column.")
    return df

def create_interaction_features(df, column_pairs):
    """
    Creates interaction features by multiplying pairs of columns.

    Args:
        df (pd.DataFrame): The input DataFrame.
        column_pairs (list of tuples): A list of tuples, where each tuple contains two column names.

    Returns:
        pd.DataFrame: The DataFrame with interaction features added.
    """
    for col1, col2 in column_pairs:
        if col1 in df.columns and col2 in df.columns:
            df[f"{col1}_x_{col2}"] = df[col1] * df[col2]
        else:
            print(f"Warning: Columns '{col1}' and/or '{col2}' not found in DataFrame. Skipping interaction feature creation for these columns.")
    return df