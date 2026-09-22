"""Deterministic baseline tokenizer for smoke tests and measurements."""

from __future__ import annotations

from dataclasses import dataclass
import re

from allm.data import conservative_normalize
from allm.domain import stable_hash

_TOKEN = re.compile(r"[\u0600-\u06ff]+|[A-Za-z]+|\d+|[^\w\s]", re.UNICODE)


@dataclass(frozen=True)
class TokenizerSpec:
    tokenizer_id: str
    version: str
    normalization: str = "conservative"

    @property
    def fingerprint(self) -> str:
        return stable_hash({"id": self.tokenizer_id, "version": self.version, "normalization": self.normalization})


class BaselineTokenizer:
    """A transparent regex tokenizer; not a claim of production quality."""

    def __init__(self, spec: TokenizerSpec | None = None):
        self.spec = spec or TokenizerSpec("arabic-regex", "0.1.0")

    def tokenize(self, text: str) -> list[str]:
        return _TOKEN.findall(conservative_normalize(text))

    def measure(self, texts: list[str]) -> dict[str, float]:
        if not texts:
            raise ValueError("texts must not be empty")
        tokenized = [self.tokenize(text) for text in texts]
        character_count = sum(len(text) for text in texts)
        token_count = sum(len(tokens) for tokens in tokenized)
        return {
            "documents": float(len(texts)),
            "characters": float(character_count),
            "tokens": float(token_count),
            "tokens_per_document": token_count / len(texts),
            "characters_per_token": character_count / token_count if token_count else 0.0,
            "unknown_rate": 0.0,
        }
