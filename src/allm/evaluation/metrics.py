"""Framework-independent baseline metrics."""

from __future__ import annotations

import math
from collections import Counter


def token_accuracy(expected: list[str], predicted: list[str]) -> float:
    if not expected or len(expected) != len(predicted):
        raise ValueError("expected and predicted must have equal non-zero length")
    return sum(left == right for left, right in zip(expected, predicted)) / len(expected)


def unigram_perplexity(tokens: list[str]) -> float:
    """Compute a transparent maximum-likelihood unigram perplexity."""
    if not tokens:
        raise ValueError("tokens must not be empty")
    counts = Counter(tokens)
    total = len(tokens)
    cross_entropy = -sum((count / total) * math.log(count / total) for count in counts.values())
    return math.exp(cross_entropy)
