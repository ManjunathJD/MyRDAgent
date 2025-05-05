import unittest


class CoSTEERTest(unittest.TestCase):
    maxDiff = None  # Add this line to show full diff


    def setUp(self):
        self.test_competition = "aerial-cactus-identification"

    def tearDown(self):
        pass

    def to_str(self, obj):
        return "".join(str(obj).split())

    def test_data_loader(self):        
        from rdagent.components.coder.data_science.raw_data_loader.test import develop_one_competition        
        exp = develop_one_competition(self.test_competition) 
        self.assertIsNotNone(exp)
    
    def test_feature(self):        
        from rdagent.components.coder.data_science.feature.test import develop_one_competition        
        exp = develop_one_competition(self.test_competition)
        self.assertIsNotNone(exp)
    
    def test_model(self):        
        from rdagent.components.coder.data_science.model.test import develop_one_competition       
        exp = develop_one_competition(self.test_competition)
        self.assertIsNotNone(exp)
    
    def test_ensemble(self):        
        from rdagent.components.coder.data_science.ensemble.test import develop_one_competition       
        exp = develop_one_competition(self.test_competition)
        self.assertIsNotNone(exp)
    
    def test_workflow(self):        
        from rdagent.components.coder.data_science.workflow.test import develop_one_competition       
        exp = develop_one_competition(self.test_competition)
        self.assertIsNotNone(exp)


if __name__ == "__main__":
    unittest.main()
    # pytest test/utils/coder/test_CoSTEER.py
