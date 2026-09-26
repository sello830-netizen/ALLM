"""Prepare leakage-safe aligned original/structured splits for the approved micro-pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from allm.data import split_records
from allm.domain import stable_hash
from allm.tokenization import BaselineTokenizer


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def serialize_structured(annotation: dict[str, Any]) -> str:
    sections: list[str] = ["TASK_TEXT " + str(annotation["text"])]
    if annotation["relations"]:
        sections.append(
            "TASK_REL "
            + " | ".join(
                f"{item['subject']} -> {item['predicate']} -> {item['object']}"
                for item in annotation["relations"]
            )
        )
    if annotation["events"]:
        sections.append(
            "TASK_EVENT "
            + " | ".join(f"{item['type']}:{item['argument']}" for item in annotation["events"])
        )
    if annotation["states"]:
        sections.append(
            "TASK_STATE "
            + " | ".join(f"{item['entity']}:{item['before']}->{item['after']}" for item in annotation["states"])
        )
    if not sections:
        raise ValueError(f"annotation has no structured signal: {annotation['source_id']}")
    return " ".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("annotations", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    corpus = {str(row["id"]): row for row in load_jsonl(args.corpus)}
    annotations = load_jsonl(args.annotations)
    if not annotations:
        raise ValueError("annotations must not be empty")
    if any(row.get("review_status") != "approved" for row in annotations):
        raise PermissionError("all structured annotations must be approved before splitting")

    records: list[dict[str, Any]] = []
    for annotation in annotations:
        source_id = str(annotation["source_id"])
        if source_id not in corpus:
            raise ValueError(f"annotation source is absent from corpus: {source_id}")
        if annotation["text"] != corpus[source_id]["text"]:
            raise ValueError(f"annotation text mismatch: {source_id}")
        records.append({
            "source_id": source_id,
            "text": str(annotation["text"]),
            "domain": str(corpus[source_id].get("domain", "")),
            "structured": serialize_structured(annotation),
        })

    splits = split_records(records, seed=args.seed)
    tokenizer = BaselineTokenizer()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "status": "training_ready",
        "seed": args.seed,
        "record_count": len(records),
        "view_mode": "original_vs_approved_structured",
        "splits": {},
    }
    for split_name, split in splits.items():
        original = "\n".join(str(row["text"]) for row in split) + "\n"
        structured = "\n".join(str(row["structured"]) for row in split) + "\n"
        (args.output_dir / f"{split_name}.original.txt").write_text(original, encoding="utf-8")
        (args.output_dir / f"{split_name}.structured.txt").write_text(structured, encoding="utf-8")
        manifest["splits"][split_name] = {
            "source_ids": [row["source_id"] for row in split],
            "record_count": len(split),
            "original_tokens": int(tokenizer.measure([str(row["text"]) for row in split])["tokens"]),
            "structured_tokens": int(tokenizer.measure([str(row["structured"]) for row in split])["tokens"]),
            "original_hash": stable_hash(original),
            "structured_hash": stable_hash(structured),
        }
    (args.output_dir / "split_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
