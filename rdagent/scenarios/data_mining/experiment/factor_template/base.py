from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class FactorBase(ABC):
    """
    Abstract base class for factor generation.
    """
    @abstractmethod
    def factor(self, data, params):
        """
        Generate factor values from input data.
        
        Args:
            data: Input data for factor calculation
            params: Parameters for factor calculation
            
        Returns:
            Calculated factor values
        """
        pass

def generate_random_factor_data(num_rows=100, num_cols=5, data_type='float'):
    """
    Generate a random DataFrame for factor data.

    Args:
        num_rows (int): Number of rows.
        num_cols (int): Number of columns.
        data_type (str): Type of data ('float', 'int').

    Returns:
        pd.DataFrame: Randomly generated factor data.
    """
    if data_type == 'float':
        data = np.random.rand(num_rows, num_cols)
    elif data_type == 'int':
        data = np.random.randint(0, 100, size=(num_rows, num_cols))
    else:
        raise ValueError("Invalid data_type. Choose from 'float' or 'int'.")
    
    return pd.DataFrame(data, columns=[f'Factor_{i}' for i in range(num_cols)])

def generate_random_label_data(num_rows=100, data_type='float'):
    """
    Generate a random DataFrame for label data.

    Args:
        num_rows (int): Number of rows.
        data_type (str): Type of data ('float', 'int').

    Returns:
        pd.DataFrame: Randomly generated label data.
    """
    if data_type == 'float':
        data = np.random.rand(num_rows)
    elif data_type == 'int':
        data = np.random.randint(0, 100, size=num_rows)
    else:
        raise ValueError("Invalid data_type. Choose from 'float' or 'int'.")
    
    return pd.DataFrame(data, columns=['Label'])

def evaluate_factor(factor_data, label_data, metric='correlation'):
    """
    Evaluate the factor data with a given metric.

    Args:
        factor_data (pd.DataFrame): Factor data.
        label_data (pd.DataFrame): Label data.
        metric (str): Evaluation metric.

    Returns:
        float: Evaluation result.
    """
    if metric == 'correlation':
        return factor_data.corrwith(label_data['Label']).mean()
    elif metric == 'mean_absolute_deviation':
        return np.abs(factor_data.mean(axis=1) - label_data['Label']).mean()
    else:
        raise ValueError("Invalid metric. Choose from 'correlation' or 'mean_absolute_deviation'.")

def infer_factor(factor_data, model):
    """
    Infer with a given model.
    Args:
        factor_data(pd.DataFrame):
        model: The model
    """
    if model is None:
        return factor_data.sum(axis=1)
    else:
        # Implement the logic here if a model is provided
        pass

def predict_factor(ffactor_data, model):
    """
    Predict with a given model.
    Args:
        factor_data(pd.DataFrame):
        model: The model
    """
    if model is None:
        return factor_data.sum(axis=1)
    else:
        # Implement the logic here if a model is provided
        pass

def train_factor(factor_data, label_data, model=None):
    """
    Train the factor data with a given model.
    Args:
        factor_data(pd.DataFrame):
        label_data(pd.DataFrame):
        model: The model
    """
    if model is None:
        pass
    else:
        # Implement the logic here if a model is provided
        pass
