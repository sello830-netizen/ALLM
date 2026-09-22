"""Dependency-free reference language model for pipeline smoke tests."""

from __future__ import annotations

from collections import Counter, defaultdict
import math


class BigramLanguageModel:
    """Add-one smoothed bigram model; reference only, not the neural baseline."""

    def __init__(self, alpha: float = 1.0):
        if alpha <= 0:
            raise ValueError("alpha must be positive")
        self.alpha = alpha
        self._counts: dict[str, Counter[str]] = defaultdict(Counter)
        self._vocabulary: set[str] = set()
        self._trained = False

    def fit(self, sequences: list[list[str]]) -> "BigramLanguageModel":
        if not sequences or any(len(sequence) < 2 for sequence in sequences):
            raise ValueError("sequences must contain at least two tokens each")
        for sequence in sequences:
            self._vocabulary.update(sequence)
            for left, right in zip(sequence, sequence[1:]):
                self._counts[left][right] += 1
        self._trained = True
        return self

    def negative_log_likelihood(self, sequence: list[str]) -> float:
        if not self._trained:
            raise RuntimeError("model must be fit before evaluation")
        if len(sequence) < 2:
            raise ValueError("sequence must contain at least two tokens")
        vocabulary_size = len(self._vocabulary)
        total = 0.0
        for left, right in zip(sequence, sequence[1:]):
            denominator = sum(self._counts[left].values()) + self.alpha * vocabulary_size
            probability = (self._counts[left][right] + self.alpha) / denominator
            total -= math.log(probability)
        return total / (len(sequence) - 1)

    def perplexity(self, sequence: list[str]) -> float:
        return math.exp(self.negative_log_likelihood(sequence))
