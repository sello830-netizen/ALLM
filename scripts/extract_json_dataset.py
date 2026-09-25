"""Validate a simple Arabic JSON dataset and export newline-delimited text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_dataset(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("language") != "ar":
        raise ValueError("dataset language must be ar")
    records = payload.get("data")
    if not isinstance(records, list) or not records:
        raise ValueError("dataset data must be a non-empty list")
    ids: set[str] = set()
    texts: list[str] = []
    for record in records:
        if not isinstance(record, dict) or not str(record.get("source_id", "")).strip():
            raise ValueError("each record requires source_id")
        source_id = str(record["source_id"])
        if source_id in ids:
            raise ValueError(f"duplicate source_id: {source_id}")
        text = str(record.get("text", "")).strip()
        if not text:
            raise ValueError(f"empty text: {source_id}")
        ids.add(source_id)
        texts.append(text)
    payload["_validated_record_count"] = len(texts)
    payload["_validated_character_count"] = sum(len(text) for text in texts)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    payload = load_dataset(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(record["text"].strip() for record in payload["data"]) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "dataset_id": payload.get("dataset_id"),
        "source_type": payload.get("source_type"),
        "records": payload["_validated_record_count"],
        "characters": payload["_validated_character_count"],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
