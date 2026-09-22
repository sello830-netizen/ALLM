import unittest

from allm.tokenization import BaselineTokenizer


class TokenizationTests(unittest.TestCase):
    def test_tokenization_is_deterministic(self):
        tokenizer = BaselineTokenizer()
        text = "مَرْحبًا بالعالم."
        self.assertEqual(tokenizer.tokenize(text), tokenizer.tokenize(text))
        self.assertIn("مَرْحبًا", tokenizer.tokenize(text))

    def test_measurement_has_expected_fields(self):
        result = BaselineTokenizer().measure(["نص عربي", "نص آخر"])
        self.assertEqual(result["documents"], 2.0)
        self.assertGreater(result["tokens"], 0)


if __name__ == "__main__":
    unittest.main()
