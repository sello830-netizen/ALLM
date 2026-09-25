"""Validate and split a JSONL Arabic corpus by source ID."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from allm.data import split_records
from allm.domain import stable_hash


def load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at line {line_number}") from error
            source_id = str(record.get("id", "")).strip()
            text = str(record.get("text", "")).strip()
            if not source_id or not text:
                raise ValueError(f"line {line_number} requires id and text")
            if source_id in seen:
                raise ValueError(f"duplicate id: {source_id}")
            seen.add(source_id)
            records.append({
                "source_id": source_id,
                "text": text,
                "domain": str(record.get("domain", "")).strip(),
                "source_type": str(record.get("source_type", "")).strip(),
            })
    if not records:
        raise ValueError("JSONL corpus is empty")
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    records = load_jsonl(args.input)
    splits = split_records(records, seed=args.seed, stratify_by="domain")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "source_file": str(args.input),
        "source_type": sorted({str(record["source_type"]) for record in records}),
        "seed": args.seed,
        "stratified_by": "domain",
        "record_count": len(records),
        "token_count_estimate": sum(len(str(record["text"]).split()) for record in records),
        "domain_counts": dict(sorted(collections.Counter(str(record["domain"]) for record in records).items())),
        "splits": {},
    }
    for split_name, split in splits.items():
        text = "\n".join(str(record["text"]) for record in split) + "\n"
        (args.output_dir / f"{split_name}.txt").write_text(text, encoding="utf-8")
        manifest["splits"][split_name] = {
            "record_count": len(split),
            "source_ids": [record["source_id"] for record in split],
            "text_hash": stable_hash(text),
            "token_count_estimate": sum(len(str(record["text"]).split()) for record in split),
        }
    (args.output_dir / "split_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
