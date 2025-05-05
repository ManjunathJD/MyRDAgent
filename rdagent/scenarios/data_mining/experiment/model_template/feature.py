import numpy as np
import pandas as pd
from qlib.data import D
from qlib.data.dataset import DatasetH
from qlib.data.dataset.handler import DataHandlerLP

def load_data(instruments, start_time, end_time, freq, fields):
    """Load factor data from Qlib."""
    handler = {
        "class": "Alpha158",
        "module_path": "qlib.contrib.data.handler",
        "kwargs": {
            "start_time": start_time,
            "end_time": end_time,
            "instruments": instruments,
        },
    }

    ds = DatasetH(handler, segments={"train": (start_time, end_time)})
    df = ds.prepare(["train"], col_set=["feature"])

    return df.to_dataframe()


def generate_factor(data_df):
    """Generate factor from data."""
    return data_df["CLOSE"] - data_df["OPEN"]


def evaluate_factor(factor, data_df):
    """Evaluate factor."""
    data_df["factor"] = factor
    return data_df.groupby("datetime")["factor"].mean()