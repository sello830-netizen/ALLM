import unittest

from allm.evaluation import EvaluationCase, evaluate_cases


class EvaluationSuiteTests(unittest.TestCase):
    def test_scores_overall_and_by_category(self):
        result = evaluate_cases([
            EvaluationCase("morph-1", "morphology", ("كتب",), ("كتب",)),
            EvaluationCase("syntax-1", "syntax", ("هو", "ذهب"), ("هو", "ذهبت")),
        ])
        self.assertEqual(result.total_cases, 2)
        self.assertEqual(result.category_scores["morphology"], 1.0)
        self.assertEqual(result.category_scores["syntax"], 0.5)
        self.assertEqual(result.overall_accuracy, 0.75)

    def test_empty_suite_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_cases([])


if __name__ == "__main__":
    unittest.main()
