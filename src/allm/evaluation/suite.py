"""Small closed evaluation suite for deterministic smoke and regression tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .metrics import token_accuracy


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    category: str
    expected: tuple[str, ...]
    predicted: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationResult:
    suite_id: str
    total_cases: int
    category_scores: dict[str, float]
    overall_accuracy: float


def evaluate_cases(cases: Iterable[EvaluationCase], suite_id: str = "evaluation-v0") -> EvaluationResult:
    values = list(cases)
    if not values:
        raise ValueError("evaluation suite must contain at least one case")
    scores: dict[str, list[float]] = {}
    case_scores: list[float] = []
    for case in values:
        if not case.expected or len(case.expected) != len(case.predicted):
            raise ValueError(f"invalid case: {case.case_id}")
        score = token_accuracy(list(case.expected), list(case.predicted))
        scores.setdefault(case.category, []).append(score)
        case_scores.append(score)
    category_scores = {
        category: sum(category_values) / len(category_values)
        for category, category_values in sorted(scores.items())
    }
    return EvaluationResult(
        suite_id=suite_id,
        total_cases=len(values),
        category_scores=category_scores,
        overall_accuracy=sum(case_scores) / len(case_scores),
    )


def run_predictor(
    cases: Iterable[EvaluationCase], predictor: Callable[[tuple[str, ...]], tuple[str, ...]], suite_id: str = "evaluation-v0"
) -> EvaluationResult:
    return evaluate_cases(
        (
            EvaluationCase(case.case_id, case.category, case.expected, predictor(case.expected))
            for case in cases
        ),
        suite_id=suite_id,
    )
