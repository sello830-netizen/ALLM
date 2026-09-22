import unittest

from allm.modeling import BaselineConfig


class ModelingTests(unittest.TestCase):
    def test_baseline_config_validates(self):
        BaselineConfig().validate()

    def test_invalid_context_is_rejected(self):
        with self.assertRaises(ValueError):
            BaselineConfig(context_length=0).validate()


if __name__ == "__main__":
    unittest.main()
