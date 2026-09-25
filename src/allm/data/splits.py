"""Deterministic source-level train/dev/test splitting."""

from __future__ import annotations

from hashlib import sha256
from typing import Any, Iterable


def split_records(
    records: Iterable[dict[str, Any]],
    *,
    seed: int = 17,
    train_ratio: float = 0.8,
    dev_ratio: float = 0.1,
    stratify_by: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    records = list(records)
    if not records:
        raise ValueError("records must not be empty")
    if not 0 < train_ratio < 1 or not 0 <= dev_ratio < 1 or train_ratio + dev_ratio >= 1:
        raise ValueError("split ratios must leave a non-empty test split")
    source_ids = [str(record.get("source_id", "")) for record in records]
    if any(not source_id for source_id in source_ids):
        raise ValueError("every record requires source_id")
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("source IDs must be unique before splitting")
    if stratify_by is not None:
        groups: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            groups.setdefault(str(record.get(stratify_by, "")), []).append(record)
        if any(not key for key in groups):
            raise ValueError(f"every record requires stratification field: {stratify_by}")
        result = {"train": [], "dev": [], "test": []}
        for key in sorted(groups):
            group_split = split_records(
                groups[key],
                seed=seed,
                train_ratio=train_ratio,
                dev_ratio=dev_ratio,
            )
            for split_name in result:
                result[split_name].extend(group_split[split_name])
        for split_name in result:
            result[split_name].sort(key=lambda record: str(record["source_id"]))
        return result

    ordered = sorted(
        records,
        key=lambda record: sha256(f"{seed}:{record['source_id']}".encode("utf-8")).hexdigest(),
    )
    train_end = max(1, int(len(ordered) * train_ratio))
    dev_end = min(len(ordered) - 1, train_end + int(len(ordered) * dev_ratio))
    return {
        "train": ordered[:train_end],
        "dev": ordered[train_end:dev_end],
        "test": ordered[dev_end:],
    }
