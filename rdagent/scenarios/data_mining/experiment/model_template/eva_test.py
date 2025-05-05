# rdagent/scenarios/data_mining/experiment/model_template/gen_model_test.py
import os
import unittest

from rdagent.scenarios.data_mining.experiment.model_template.model_template_conf import cfg
from rdagent.scenarios.data_mining.experiment.model_template.train import Model as ModelTrain


class TestModel(unittest.TestCase):
    def test_default(self):
        # model_template_conf.py
        self.assertIsNotNone(cfg.get("model_name"))
        self.assertIsNotNone(cfg.get("model_type"))
        self.assertIsNotNone(cfg.get("feature_name"))
        self.assertIsNotNone(cfg.get("train_name"))
        self.assertIsNotNone(cfg.get("infer_name"))

    def test_train_class(self):
        model = ModelTrain()
        self.assertIsNotNone(model)
        model.train()

    def test_infer_class(self):
        from rdagent.scenarios.data_mining.experiment.model_template.infer import Model as ModelInfer

        model = ModelInfer()
        self.assertIsNotNone(model)
        model.infer()

    def test_train_run(self):
        os.system("python rdagent/scenarios/data_mining/experiment/model_template/train.py")

    def test_infer_run(self):
        os.system("python rdagent/scenarios/data_mining/experiment/model_template/infer.py")

    def test_predict_run(self):
        os.system("python rdagent/scenarios/data_mining/experiment/model_template/predict.py")

    def test_eva_run(self):
        os.system("python rdagent/scenarios/data_mining/experiment/model_template/eva.py")

    def test_infer_test_run(self):
        os.system("python rdagent/scenarios/data_mining/experiment/model_template/infer_test.py")

    def test_train_test_run(self):
        os.system("python rdagent/scenarios/data_mining/experiment/model_template/train_test.py")


if __name__ == "__main__":
    unittest.main()