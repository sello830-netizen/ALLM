"""Validate proposed/approved relation-state annotations against a JSONL corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("annotations", type=Path)
    args = parser.parse_args()
    corpus = {str(record["id"]): record for record in load_jsonl(args.corpus)}
    annotations = load_jsonl(args.annotations)
    seen: set[str] = set()
    statuses: dict[str, int] = {}
    for annotation in annotations:
        source_id = str(annotation.get("source_id", ""))
        if not source_id or source_id in seen:
            raise ValueError(f"missing or duplicate annotation source_id: {source_id}")
        if source_id not in corpus:
            raise ValueError(f"annotation source is absent from corpus: {source_id}")
        if annotation.get("text") != corpus[source_id].get("text"):
            raise ValueError(f"annotation text mismatch: {source_id}")
        for field in ("relations", "events", "states", "temporal", "causal"):
            if not isinstance(annotation.get(field), list):
                raise ValueError(f"annotation field must be a list: {source_id}/{field}")
        status = str(annotation.get("review_status", ""))
        if status not in {"proposed_needs_review", "approved"}:
            raise ValueError(f"unsupported review_status: {status}")
        statuses[status] = statuses.get(status, 0) + 1
        seen.add(source_id)
    print(json.dumps({
        "status": "valid",
        "corpus_records": len(corpus),
        "annotated_records": len(annotations),
        "review_status_counts": statuses,
        "approved_for_training": statuses.get("approved", 0),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
