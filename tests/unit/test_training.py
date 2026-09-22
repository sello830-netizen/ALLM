import unittest

from allm.training import BigramLanguageModel


class TrainingTests(unittest.TestCase):
    def test_reference_model_fits_and_scores(self):
        model = BigramLanguageModel().fit([["أ", "ب", "ج"], ["أ", "ب", "د"]])
        self.assertGreater(model.perplexity(["أ", "ب", "ج"]), 1.0)

    def test_unfit_model_is_rejected(self):
        with self.assertRaises(RuntimeError):
            BigramLanguageModel().perplexity(["أ", "ب"])


if __name__ == "__main__":
    unittest.main()
