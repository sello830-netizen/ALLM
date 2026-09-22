"""Select a deterministic Arabic-only OpenITI metadata pilot without downloading text."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable


def _first_value(row: dict[str, str], fragments: Iterable[str]) -> str:
    for key, value in row.items():
        if any(fragment in key.lower() for fragment in fragments) and value.strip():
            return value.strip()
    return ""


def _is_arabic(row: dict[str, str]) -> bool:
    language = _first_value(row, ("language", "lang", "lng"))
    if not language:
        return False
    normalized = language.lower()
    return normalized == "ar" or "arab" in normalized or normalized.startswith("ara")


def _is_clean_primary_candidate(row: dict[str, str]) -> bool:
    token_length = row.get("tok_length", "").strip()
    return (
        _is_arabic(row)
        and row.get("status", "").strip().lower() == "pri"
        and row.get("uncorrected_OCR", "").strip().lower() == "false"
        and row.get("subcorpus", "").strip() == "ara"
        and bool(row.get("title_ar", "").strip())
        and bool(row.get("author_ar", "").strip())
        and token_length.isdigit()
        and 1_000 <= int(token_length) <= 500_000
    )


def select_metadata(input_path: Path, output_path: Path, limit: int) -> dict[str, object]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames:
            raise ValueError("metadata file has no header")
        rows = [row for row in reader if _is_clean_primary_candidate(row)]

    records: list[dict[str, object]] = []
    for row in rows:
        canonical = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        records.append({
            "record_hash": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "source_uri": _first_value(row, ("uri", "url", "path", "file", "id")),
            "author": _first_value(row, ("author", "auth")),
            "title": _first_value(row, ("title", "work", "book")),
            "year": _first_value(row, ("year", "date", "death")),
            "language": _first_value(row, ("language", "lang", "lng")),
            "raw_metadata": row,
        })
    records.sort(key=lambda record: str(record["record_hash"]))
    selected = records[:limit]
    output = {
        "status": "candidate_only",
        "source_id": "openiti-release",
        "release": "2025-1-9",
        "text_downloaded": False,
        "license_gate": "blocked_pending_review",
        "selection": {
            "language_filter": "Arabic language metadata only",
            "quality_filters": [
                "status=pri",
                "uncorrected_OCR=False",
                "subcorpus=ara",
                "title_ar and author_ar are present",
                "1000 <= tok_length <= 500000",
            ],
            "deterministic_limit": limit,
            "candidate_count": len(records),
            "selected_count": len(selected),
        },
        "records": selected,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    if args.limit <= 0:
        raise ValueError("limit must be positive")
    result = select_metadata(args.input, args.output, args.limit)
    print(json.dumps({key: value for key, value in result.items() if key != "records"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
