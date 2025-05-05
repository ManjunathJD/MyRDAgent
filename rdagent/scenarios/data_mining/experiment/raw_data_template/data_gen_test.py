# rdagent/scenarios/data_mining/experiment/raw_data_template/utils.py
import pandas as pd

def load_data(data_path):
    """
    Loads data from a CSV file into a pandas DataFrame.

    Args:
        data_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded data as a DataFrame, or None if an error occurred.
    """
    try:
        data = pd.read_csv(data_path)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: Empty CSV file at {data_path}")
        return None
    except pd.errors.ParserError:
        print(f"Error: Could not parse CSV file at {data_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def preprocess_data(data):
    """
    Preprocesses the data by handling missing values and encoding categorical variables.

    Args:
        data (pd.DataFrame): The input data as a DataFrame.

    Returns:
        pd.DataFrame: The preprocessed data as a DataFrame.
    """
    if data is None:
        return None
    
    # Example preprocessing steps (customize as needed)
    # Handling missing values (example: fill with mean for numerical columns)
    for col in data.select_dtypes(include=['number']):
        data[col].fillna(data[col].mean(), inplace=True)

    # Encoding categorical variables (example: one-hot encoding)
    for col in data.select_dtypes(include=['object']):
        data = pd.get_dummies(data, columns=[col], dummy_na=True)
    
    return data