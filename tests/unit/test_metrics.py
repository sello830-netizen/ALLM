import unittest

from allm.evaluation import token_accuracy, unigram_perplexity


class MetricsTests(unittest.TestCase):
    def test_token_accuracy(self):
        self.assertAlmostEqual(token_accuracy(["أ", "ب"], ["أ", "ج"]), 0.5)

    def test_unigram_perplexity_is_deterministic(self):
        self.assertAlmostEqual(unigram_perplexity(["أ", "أ", "ب"]), 1.8898815748)


if __name__ == "__main__":
    unittest.main()
