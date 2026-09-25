import unittest

from allm.torch_backend import Vocabulary, vocabulary_oov_rate


class TorchMetricTests(unittest.TestCase):
    def test_oov_rate_does_not_expand_vocabulary(self):
        vocabulary = Vocabulary([["نص", "عربي"]])
        rate = vocabulary_oov_rate(["نص جديد"], vocabulary)
        self.assertAlmostEqual(rate, 0.5)
        self.assertNotIn("جديد", vocabulary.stoi)


if __name__ == "__main__":
    unittest.main()
