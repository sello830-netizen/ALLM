"""Model-facing interfaces kept independent from a specific ML framework."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LanguageModel(Protocol):
    def loss(self, tokens: list[str]) -> float:
        """Return a scalar loss for a token sequence."""


@dataclass(frozen=True)
class BaselineConfig:
    model_id: str = "arabic-causal-baseline"
    version: str = "0.1.0"
    context_length: int = 256
    seed: int = 17
    parameter_count: int = 0

    def validate(self) -> None:
        if self.context_length <= 0:
            raise ValueError("context_length must be positive")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
