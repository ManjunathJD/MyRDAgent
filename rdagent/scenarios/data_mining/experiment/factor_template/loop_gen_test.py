# rdagent/scenarios/data_mining/experiment/factor_template/base_gen_test.py
import unittest
from unittest.mock import patch

from rdagent.scenarios.data_mining.experiment.factor_template.base import (
    Factor,
    FactorTemplate,
    get_factor_cls,
)


class TestFactorTemplate(unittest.TestCase):
    def test_init(self):
        template = FactorTemplate("test_factor")
        self.assertEqual(template.name, "test_factor")
        self.assertEqual(template.description, "test_factor")
        self.assertIsNone(template.factor_class)

    def test_register(self):
        template = FactorTemplate("test_factor")

        @template.register
        class TestFactor(Factor):
            pass

        self.assertIs(template.factor_class, TestFactor)

    def test_register_error(self):
        template = FactorTemplate("test_factor")
        with self.assertRaises(TypeError):

            @template.register
            class NotAFactor:
                pass

    def test_get_factor(self):
        template = FactorTemplate("test_factor")

        @template.register
        class TestFactor(Factor):
            pass

        self.assertIs(template.get_factor(), TestFactor)

    def test_get_factor_error(self):
        template = FactorTemplate("test_factor")
        with self.assertRaises(ValueError):
            template.get_factor()


class TestGetFactorCls(unittest.TestCase):
    def test_get_factor_cls(self):
        with patch("rdagent.scenarios.data_mining.experiment.factor_template.base.factor_template_map") as mock_map:
            template = FactorTemplate("test_factor")

            @template.register
            class TestFactor(Factor):
                pass

            mock_map.__getitem__.return_value = template
            factor_cls = get_factor_cls("test_factor")
            self.assertIs(factor_cls, TestFactor)

    def test_get_factor_cls_error(self):
        with patch("rdagent.scenarios.data_mining.experiment.factor_template.base.factor_template_map") as mock_map:
            mock_map.__getitem__.side_effect = KeyError
            with self.assertRaises(KeyError):
                get_factor_cls("not_exist_factor")