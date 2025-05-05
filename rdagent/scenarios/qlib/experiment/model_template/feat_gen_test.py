# rdagent/scenarios/qlib/experiment/model_template/feat_gen_test.py
import unittest

from rdagent.scenarios.qlib.experiment.model_template import utils

class TestFeatureGeneration(unittest.TestCase):

    def test_generate_features(self):
        """
        Test the generation of features using the utils function.
        """
        # This is a mock setup; in a real-world scenario, you would
        # load data and define feature specifications.
        # Here, we're just checking if the function runs without errors
        try:
            utils.generate_features()
        except Exception as e:
            self.fail(f"generate_features raised an exception: {e}")

    def test_generate_features_with_data(self):
        """
        Test the generation of features using the utils function with a mock dataset.
        """
        # Create a mock dataset
        mock_data = [{"id": 1, "feature1": 10, "feature2": 20},
                     {"id": 2, "feature1": 30, "feature2": 40}]
        try:
            utils.generate_features(data=mock_data)
        except Exception as e:
            self.fail(f"generate_features with data raised an exception: {e}")

    def test_generate_features_with_specs(self):
        """
        Test the generation of features using the utils function with feature specifications.
        """
        # Define mock feature specifications
        mock_specs = ["feature1", "feature2"]
        try:
            utils.generate_features(feature_specs=mock_specs)
        except Exception as e:
            self.fail(f"generate_features with specs raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()