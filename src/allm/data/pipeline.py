"""Small deterministic data preparation pipeline."""

from __future__ import annotations

from dataclasses import replace
import re
from typing import Iterable

from allm.domain.models import DatasetRelease, Document, stable_hash

_ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
_WHITESPACE = re.compile(r"\s+")


def conservative_normalize(text: str) -> str:
    """Normalize layout without erasing Arabic orthographic information."""
    text = text.replace("ـ", "")
    text = _WHITESPACE.sub(" ", text)
    return text.strip()


def sentence_split(text: str) -> list[str]:
    normalized = conservative_normalize(text)
    return [part.strip() for part in re.split(r"(?<=[.!؟؛])\s+", normalized) if part.strip()]


def exact_deduplicate(documents: Iterable[Document]) -> list[Document]:
    seen: set[str] = set()
    result: list[Document] = []
    for document in documents:
        normalized = conservative_normalize(document.text)
        fingerprint = stable_hash(normalized)
        if fingerprint not in seen:
            seen.add(fingerprint)
            result.append(replace(document, text=normalized))
    return result


def validate_documents(documents: Iterable[Document]) -> list[Document]:
    result = list(documents)
    for document in result:
        document.validate()
    if len({document.document_id for document in result}) != len(result):
        raise ValueError("document IDs must be unique")
    return result


def build_manifest(documents: Iterable[Document]) -> list[dict[str, object]]:
    """Create a stable, content-free manifest suitable for version control."""
    valid = validate_documents(exact_deduplicate(documents))
    return [
        {
            "document_id": document.document_id,
            "source_id": document.source.source_id,
            "license": document.source.license,
            "domain": document.source.domain,
            "register": document.source.register,
            "split": document.split,
            "text_hash": stable_hash(document.text),
            "character_count": len(document.text),
        }
        for document in sorted(valid, key=lambda item: item.document_id)
    ]


def build_release(
    documents: Iterable[Document], dataset_id: str, version: str
) -> DatasetRelease:
    valid = validate_documents(exact_deduplicate(documents))
    manifest = build_manifest(valid)
    release = DatasetRelease(
        dataset_id=dataset_id,
        version=version,
        manifest_hash=stable_hash(manifest),
        document_count=len(valid),
        token_count=sum(len(document.text.split()) for document in valid),
        source_ids=tuple(sorted({document.source.source_id for document in valid})),
    )
    release.validate()
    return release


def find_split_leaks(documents: Iterable[Document]) -> set[str]:
    by_text: dict[str, set[str]] = {}
    for document in documents:
        by_text.setdefault(stable_hash(conservative_normalize(document.text)), set()).add(document.split)
    return {text_hash for text_hash, splits in by_text.items() if len(splits) > 1}
