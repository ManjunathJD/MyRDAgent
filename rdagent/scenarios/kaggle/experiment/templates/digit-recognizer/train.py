import importlib.util
import random
from pathlib import Path

import numpy as np
import pandas as pd
from fea_share_preprocess import clean_and_impute_data, preprocess_script
from sklearn.metrics import accuracy_score

# Set random seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
DIRNAME = Path(__file__).absolute().resolve().parent


def compute_metrics_for_classification(y_true, y_pred):
    """Compute accuracy for classification."""
    return accuracy_score(y_true, y_pred)


def import_module_from_path(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# 1) Preprocess the data
X_train, X_valid, y_train, y_valid, X_test = preprocess_script()

# 2) Auto feature engineering
X_train_l, X_valid_l = [], []
X_test_l = []

for f in DIRNAME.glob("feature/feat*.py"):
    cls = import_module_from_path(f.stem, f).feature_engineering_cls()
    cls.fit(X_train)
    X_train_f = cls.transform(X_train.copy())
    X_valid_f = cls.transform(X_valid.copy())
    X_test_f = cls.transform(X_test.copy())

    if X_train_f.shape[-1] == X_valid_f.shape[-1] and X_train_f.shape[-1] == X_test_f.shape[-1]:
        X_train_l.append(X_train_f)
        X_valid_l.append(X_valid_f)
        X_test_l.append(X_test_f)

X_train = pd.concat(X_train_l, axis=1, keys=[f"feature_{i}" for i in range(len(X_train_l))])
X_valid = pd.concat(X_valid_l, axis=1, keys=[f"feature_{i}" for i in range(len(X_valid_l))])
X_test = pd.concat(X_test_l, axis=1, keys=[f"feature_{i}" for i in range(len(X_test_l))])

print(X_train.shape, X_valid.shape, X_test.shape)

# Handle inf and -inf values
X_train, X_valid, X_test = clean_and_impute_data(X_train, X_valid, X_test)


model_l = []  # list[tuple[model, predict_func]]
for f in DIRNAME.glob("model/model*.py"):
    select_python_path = f.with_name(f.stem.replace("model", "select") + f.suffix)
    select_m = import_module_from_path(select_python_path.stem, select_python_path)
    X_train_selected = select_m.select(X_train.copy())
    X_valid_selected = select_m.select(X_valid.copy())

    m = import_module_from_path(f.stem, f)
    model_l.append((m.fit(X_train_selected, y_train, X_valid_selected, y_valid), m.predict, select_m))

# 4) Evaluate the model on the validation set
metrics_all = []
for model, predict_func, select_m in model_l:
    X_valid_selected = select_m.select(X_valid.copy())
    y_valid_pred = predict_func(model, X_valid_selected)
    accuracy = accuracy_score(y_valid, y_valid_pred)
    print(f"final accuracy on valid set: {accuracy}")
    metrics_all.append(accuracy)

# 5) Save the validation accuracy
max_index = np.argmax(metrics_all)
pd.Series(data=[metrics_all[max_index]], index=["multi-class accuracy"]).to_csv("submission_score.csv")

# 6) Submit predictions for the test
ids = range(1, len(X_test) + 1)

print(X_valid_selected.columns)
y_test_pred = model_l[max_index][1](model_l[max_index][0], model_l[max_index][2].select(X_test)).flatten()
submission_result = pd.DataFrame({"ImageId": ids, "Label": y_test_pred})
submission_result.to_csv("submission.csv", index=False)
