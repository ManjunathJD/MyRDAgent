import os

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split


def prepreprocess():
    """
    This method loads the data, drops the unnecessary columns, and splits it into train and validation sets.
    """
    # Load and preprocess the data
    data_df = pd.read_csv("/kaggle/input/train.csv")
    # data_df = data_df.drop(["ImageId"], axis=1)

    X = data_df.drop(["label"], axis=1)
    y = data_df["label"]

    # Split the data into training and validation sets
    X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.20, random_state=42)

    return X_train, X_valid, y_train, y_valid


def preprocess_script():
    """
    This method applies the preprocessing steps to the training, validation, and test datasets.
    """
    if os.path.exists("/kaggle/input/X_train.pkl"):
        X_train = pd.read_pickle("/kaggle/input/X_train.pkl")
        X_valid = pd.read_pickle("/kaggle/input/X_valid.pkl")
        y_train = pd.read_pickle("/kaggle/input/y_train.pkl")
        y_valid = pd.read_pickle("/kaggle/input/y_valid.pkl")
        X_test = pd.read_pickle("/kaggle/input/X_test.pkl")
        others = list(pd.read_pickle("/kaggle/input/others.pkl"))

        return X_train, X_valid, y_train, y_valid, X_test, *others

    X_train, X_valid, y_train, y_valid = prepreprocess()

    # Load and preprocess the test data
    submission_df = pd.read_csv("/kaggle/input/test.csv")
    # ids = submission_df["ImageId"]
    X_test = submission_df

    X_train = X_train / 255
    X_valid = X_valid / 255
    X_test = X_test / 255

    return X_train, X_valid, y_train, y_valid, X_test


def clean_and_impute_data(X_train, X_valid, X_test):
    """
    Handles inf and -inf values by replacing them with NaN,
    then imputes missing values using the mean strategy.
    Also removes duplicate columns.
    """
    # Impute missing values
    imputer = SimpleImputer(strategy="mean")
    X_train = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns)
    X_valid = pd.DataFrame(imputer.transform(X_valid), columns=X_valid.columns)
    X_test = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns)

    return X_train, X_valid, X_test
