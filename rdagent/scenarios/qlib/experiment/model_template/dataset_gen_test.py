# rdagent/scenarios/qlib/experiment/model_template/loop_gen_test.py

import unittest

from rdagent.scenarios.qlib.experiment.model_template import utils

class TestModelTemplateUtils(unittest.TestCase):
    def test_loop_gen_test(self):
        utils.loop_gen_test()

    def test_exp_gen_test(self):
        utils.exp_gen_test()

    def test_feat_gen_test(self):
        utils.feat_gen_test()

    def test_dataset_gen_test(self):
        utils.dataset_gen_test()
        
    def test_dataset_gen_test(self):
        utils.dataset_gen_test()

    def test_base_gen_test(self):
        utils.base_gen_test()

if __name__ == '__main__':
    unittest.main()