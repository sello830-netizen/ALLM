"""Machine-readable evidence and decisions for source license review."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any, Iterable

from .source_registry import SourceRegistry, SourceStatus


class AuditDecision(str, Enum):
    BLOCKED_PENDING_REVIEW = "blocked_pending_review"
    RESEARCH_ONLY_CANDIDATE = "research_only_candidate"
    REDISTRIBUTABLE_CANDIDATE = "redistributable_candidate"
    APPROVED_RESEARCH = "approved_research"
    APPROVED_REDISTRIBUTABLE = "approved_redistributable"
    REJECTED = "rejected"


@dataclass(frozen=True)
class SourceAudit:
    source_id: str
    checked_at: str
    reviewer: str
    evidence_urls: tuple[str, ...]
    observed_license: str
    observed_permissions: tuple[str, ...]
    findings: tuple[str, ...]
    decision: AuditDecision
    next_action: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SourceAudit":
        return cls(
            source_id=value["source_id"],
            checked_at=value["checked_at"],
            reviewer=value["reviewer"],
            evidence_urls=tuple(value.get("evidence_urls", [])),
            observed_license=value["observed_license"],
            observed_permissions=tuple(value.get("observed_permissions", [])),
            findings=tuple(value.get("findings", [])),
            decision=AuditDecision(value["decision"]),
            next_action=value["next_action"],
        )

    def validate(self) -> None:
        required = {
            "source_id": self.source_id,
            "checked_at": self.checked_at,
            "reviewer": self.reviewer,
            "observed_license": self.observed_license,
            "next_action": self.next_action,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"audit metadata is incomplete: {', '.join(missing)}")
        if not self.evidence_urls:
            raise ValueError(f"audit requires evidence URLs: {self.source_id}")
        if not self.findings:
            raise ValueError(f"audit requires findings: {self.source_id}")
        if self.decision is AuditDecision.APPROVED_REDISTRIBUTABLE and not {
            "commercial_training",
            "redistribution",
            "derived_model",
        }.issubset(self.observed_permissions):
            raise ValueError("redistributable approval requires three explicit permissions")


class SourceAuditRegistry:
    def __init__(self, audits: Iterable[SourceAudit]):
        self._audits = {audit.source_id: audit for audit in audits}
        if not self._audits:
            raise ValueError("source audit registry must not be empty")
        for audit in self._audits.values():
            audit.validate()

    @classmethod
    def from_json(cls, path: str | Path) -> "SourceAuditRegistry":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(SourceAudit.from_dict(value) for value in payload["audits"])

    def get(self, source_id: str) -> SourceAudit:
        try:
            return self._audits[source_id]
        except KeyError as error:
            raise KeyError(f"missing audit: {source_id}") from error

    def list(self) -> list[SourceAudit]:
        return [self._audits[key] for key in sorted(self._audits)]

    def validate_against_sources(self, sources: SourceRegistry) -> None:
        source_ids = {source.source_id for source in sources.list()}
        audit_ids = set(self._audits)
        missing = source_ids - audit_ids
        unknown = audit_ids - source_ids
        if missing:
            raise ValueError(f"sources without audits: {', '.join(sorted(missing))}")
        if unknown:
            raise ValueError(f"audits for unknown sources: {', '.join(sorted(unknown))}")
        for source in sources.list():
            audit = self.get(source.source_id)
            if audit.decision is AuditDecision.APPROVED_REDISTRIBUTABLE and source.status is not SourceStatus.APPROVED_REDISTRIBUTABLE:
                raise ValueError(f"audit approves unapproved source: {source.source_id}")
            if audit.decision is AuditDecision.APPROVED_RESEARCH and source.status not in {
                SourceStatus.APPROVED_RESEARCH,
                SourceStatus.APPROVED_REDISTRIBUTABLE,
            }:
                raise ValueError(f"audit approves unapproved research source: {source.source_id}")
