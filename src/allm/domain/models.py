"""Typed contracts shared by data, training, evaluation, and registry layers."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
import hashlib
import json


class RunStatus(str, Enum):
    PLANNED = "planned"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INVALIDATED = "invalidated"
    ARCHIVED = "archived"


def stable_hash(value: Any) -> str:
    """Return a reproducible SHA-256 hash for JSON-compatible values."""
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    license: str
    domain: str
    register: str
    date_start: str | None = None
    date_end: str | None = None

    def validate(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")
        if not self.license.strip():
            raise ValueError("license metadata is required")


@dataclass(frozen=True)
class Document:
    document_id: str
    source: SourceRecord
    text: str
    split: str = "train"
    metadata: Mapping[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        self.source.validate()
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty")
        if not self.text.strip():
            raise ValueError("document text must not be empty")
        if self.split not in {"train", "dev", "test"}:
            raise ValueError(f"unsupported split: {self.split}")


@dataclass(frozen=True)
class DatasetRelease:
    dataset_id: str
    version: str
    manifest_hash: str
    document_count: int
    token_count: int
    source_ids: tuple[str, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> None:
        if not self.dataset_id or not self.version or len(self.manifest_hash) != 64:
            raise ValueError("dataset release identity is incomplete")
        if self.document_count < 0 or self.token_count < 0:
            raise ValueError("dataset counts cannot be negative")


@dataclass(frozen=True)
class Run:
    run_id: str
    experiment_id: str
    status: RunStatus
    code_revision: str
    config_hash: str
    dataset_hash: str
    tokenizer_hash: str
    evaluation_hash: str
    seed: int
    steps: int = 0
    tokens: int = 0
    metrics: Mapping[str, float] = field(default_factory=dict)
    parent_run_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> None:
        required = {
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "code_revision": self.code_revision,
            "config_hash": self.config_hash,
            "dataset_hash": self.dataset_hash,
            "tokenizer_hash": self.tokenizer_hash,
            "evaluation_hash": self.evaluation_hash,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"missing run metadata: {', '.join(missing)}")
        if self.steps < 0 or self.tokens < 0:
            raise ValueError("run counts cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        return value
