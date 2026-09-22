"""Evaluate a tiny closed suite to validate the evaluation contract."""

import json

from allm.evaluation import EvaluationCase, evaluate_cases


if __name__ == "__main__":
    cases = [
        EvaluationCase("morph-001", "morphology", ("كتب", "وا"), ("كتب", "وا")),
        EvaluationCase("syntax-001", "syntax", ("هو", "ذهب"), ("هو", "ذهبت")),
    ]
    result = evaluate_cases(cases)
    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
