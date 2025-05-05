# rdagent/scenarios/data_mining/experiment/raw_data_template/base_gen_test.py

import unittest
import pandas as pd
from typing import Dict, List

from rdagent.scenarios.data_mining.experiment.raw_data_template.utils import RawDataGen
from rdagent.scenarios.data_mining.experiment.raw_data_template.base import BaseRawData
from rdagent.scenarios.data_mining.experiment.raw_data_template.data_template_test import RawDataTemplateTest


class RawDataGenTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_gen = RawDataGen()

    def test_extract_data(self):
        # Mock data for testing
        mock_data = {
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e'],
            'col3': [True, False, True, True, False]
        }
        df = pd.DataFrame(mock_data)

        # Mock a BaseRawData instance for testing
        class MockRawData(BaseRawData):
            def extract_data(self):
                return df
        
        mock_raw_data = MockRawData()
        
        result = self.data_gen.extract_data(mock_raw_data)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 5)
        self.assertListEqual(list(result.columns), ['col1', 'col2', 'col3'])

    def test_describe_data(self):
        # Mock data for testing
        mock_data = {
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e'],
            'col3': [True, False, True, True, False]
        }
        df = pd.DataFrame(mock_data)
        
        result = self.data_gen.describe_data(df)
        self.assertIsInstance(result, str)

    def test_get_data_info(self):
        # Mock data for testing
        mock_data = {
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e'],
            'col3': [True, False, True, True, False]
        }
        df = pd.DataFrame(mock_data)
        
        result = self.data_gen.get_data_info(df)
        self.assertIsInstance(result, Dict)

    def test_generate_dataset_description(self):
        # Mock data for testing
        mock_data = {
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e'],
            'col3': [True, False, True, True, False]
        }
        df = pd.DataFrame(mock_data)
        
        # Mock a RawDataTemplateTest instance for testing
        class MockDataTemplateTest(RawDataTemplateTest):
            def __init__(self):
                super().__init__()
                self.df = df

        data_test = MockDataTemplateTest()

        result = self.data_gen.generate_dataset_description(data_test)
        self.assertIsInstance(result, str)

    def test_generate_raw_data_loop(self):
        # Mock data for testing
        mock_data = {
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e'],
            'col3': [True, False, True, True, False]
        }
        df = pd.DataFrame(mock_data)

        # Mock a RawDataTemplateTest instance for testing
        class MockDataTemplateTest(RawDataTemplateTest):
            def __init__(self):
                super().__init__()
                self.df = df

        data_test = MockDataTemplateTest()

        result = self.data_gen.generate_raw_data_loop(data_test)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()