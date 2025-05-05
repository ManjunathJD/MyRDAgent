# coding: utf-8
import os
import copy
import unittest

from rdagent.core.conf import Config
from rdagent.core.experiment import Experiment
from rdagent.core.proposal import Proposal
from rdagent.scenarios.qlib.experiment.utils import load_exp_conf

class ExpGenTest(unittest.TestCase):
    """test for experiment generation"""

    def setUp(self):
        """
        setup
        """
        self.maxDiff = None
        self.temp_exp = "temp_exp"
        self.data_dir = "temp_data"
        self.exp_file = os.path.join("temp_data", "exp.json")
        self.proposal_dir = "proposal"
        self.proposal_file = os.path.join("proposal", "proposal.yaml")
        if not os.path.exists(self.temp_exp):
            os.makedirs(self.temp_exp)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists(self.proposal_dir):
            os.makedirs(self.proposal_dir)

        with open(self.proposal_file, "w") as f:
            f.write("""
name: test_proposal
content:
  model_type: test
  task:
    id: test
    qlib_config:
        start_time: 2020-01-01
        end_time: 2020-01-02
    train_conf:
        loss: mse
        lr: 0.001
    """)
        with open(self.exp_file, "w") as f:
            f.write("""
{
    "model_type": "test",
    "train_conf": {
        "loss": "mse",
        "lr": 0.001
    },
    "task": {
        "id": "test",
        "qlib_config": {
            "start_time": "2020-01-01",
            "end_time": "2020-01-02"
        }
    }
}
    """)
    def tearDown(self):
        """
        tear down
        """
        if os.path.exists(self.temp_exp):
            import shutil
            shutil.rmtree(self.temp_exp)
        if os.path.exists(self.data_dir):
            import shutil
            shutil.rmtree(self.data_dir)
        if os.path.exists(self.proposal_dir):
            import shutil
            shutil.rmtree(self.proposal_dir)
        pass

    def test_gen_exp(self):
        """
        Test the generation of experiments
        """
        config = Config()
        exp_dir = os.path.join(self.temp_exp, "temp")
        
        # Load proposal, and generate experiment.
        proposal = Proposal.load(config, self.proposal_file)
        exp = proposal.generate_exp(exp_dir)
        conf = load_exp_conf(exp.exp_file)

        # Load exp_file and compare content.
        with open(self.exp_file, "r") as f:
            exp_file_content = eval(f.read())
        
        self.assertDictEqual(conf, exp_file_content)

    def test_gen_exps(self):
        """
        Test the generation of experiment groups
        """
        config = Config()
        exp_dir = os.path.join(self.temp_exp, "temp")
        proposal = Proposal.load(config, self.proposal_file)
        
        # Set up multi config.
        proposal.content["train_conf"] = [
            {"loss": "mse", "lr": 0.001},
            {"loss": "mae", "lr": 0.002}
        ]
        proposal.content["task"]["id"] = ["test1", "test2"]

        # Generate multiple experiments
        exps = proposal.generate_exps(exp_dir)
        self.assertEqual(len(exps), 4)

        # Check the contents of exps are correct.
        exp1_file = os.path.join(exp_dir, "0", "exp.json")
        exp2_file = os.path.join(exp_dir, "1", "exp.json")
        exp3_file = os.path.join(exp_dir, "2", "exp.json")
        exp4_file = os.path.join(exp_dir, "3", "exp.json")
        conf1 = load_exp_conf(exp1_file)
        conf2 = load_exp_conf(exp2_file)
        conf3 = load_exp_conf(exp3_file)
        conf4 = load_exp_conf(exp4_file)
        with open(self.exp_file, "r") as f:
            exp_file_content = eval(f.read())
        exp_file_content_1 = copy.deepcopy(exp_file_content)
        exp_file_content_1["task"]["id"] = "test1"
        exp_file_content_2 = copy.deepcopy(exp_file_content)
        exp_file_content_2["task"]["id"] = "test2"
        exp_file_content_3 = copy.deepcopy(exp_file_content)
        exp_file_content_3["train_conf"]["loss"] = "mae"
        exp_file_content_3["train_conf"]["lr"] = 0.002
        exp_file_content_3["task"]["id"] = "test1"
        exp_file_content_4 = copy.deepcopy(exp_file_content)
        exp_file_content_4["train_conf"]["loss"] = "mae"
        exp_file_content_4["train_conf"]["lr"] = 0.002
        exp_file_content_4["task"]["id"] = "test2"
        self.assertDictEqual(conf1, exp_file_content_1)
        self.assertDictEqual(conf2, exp_file_content_2)
        self.assertDictEqual(conf3, exp_file_content_3)
        self.assertDictEqual(conf4, exp_file_content_4)

if __name__ == "__main__":
    unittest.main()