"""Deterministic data preparation services."""

from .source_audit import AuditDecision, SourceAudit, SourceAuditRegistry
from .splits import split_records
from .source_registry import CorpusLayer, LicenseGate, SourceRegistry, SourceSpec, SourceStatus
from .pipeline import (
    build_manifest,
    build_release,
    conservative_normalize,
    exact_deduplicate,
    find_split_leaks,
    sentence_split,
    validate_documents,
)

__all__ = ["AuditDecision", "CorpusLayer", "LicenseGate", "SourceAudit", "SourceAuditRegistry", "SourceRegistry", "SourceSpec", "SourceStatus", "build_manifest", "build_release", "conservative_normalize", "exact_deduplicate", "find_split_leaks", "sentence_split", "split_records", "validate_documents"]
