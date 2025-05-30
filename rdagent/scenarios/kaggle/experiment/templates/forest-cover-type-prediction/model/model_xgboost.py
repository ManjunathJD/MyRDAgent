"""
motivation  of the model
"""

import pandas as pd
import xgboost as xgb


def fit(X_train: pd.DataFrame, y_train: pd.DataFrame, X_valid: pd.DataFrame, y_valid: pd.DataFrame):
    """Define and train the model. Merge feature_select"""
    dtrain = xgb.DMatrix(data=X_train, label=y_train)
    dvalid = xgb.DMatrix(data=X_valid, label=y_valid)

    params = {
        "objective": "multi:softmax",  # Use softmax for multi-class classification
        "num_class": len(set(y_train)),  # Number of classes
        "nthread": -1,
        "tree_method": "hist",
        "device": "cuda",
    }
    num_round = 100

    evallist = [(dtrain, "train"), (dvalid, "eval")]
    bst = xgb.train(params, dtrain, num_round, evallist)

    return bst


def predict(model, X):
    """
    Keep feature select's consistency.
    """
    dtest = xgb.DMatrix(data=X)
    y_pred = model.predict(dtest)
    return y_pred.astype(int).reshape(-1, 1)
