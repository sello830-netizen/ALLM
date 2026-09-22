"""Deterministic data preparation services."""

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

__all__ = ["CorpusLayer", "LicenseGate", "SourceRegistry", "SourceSpec", "SourceStatus", "build_manifest", "build_release", "conservative_normalize", "exact_deduplicate", "find_split_leaks", "sentence_split", "validate_documents"]
