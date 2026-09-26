"""Select a balanced structured-annotation review batch without approving new labels."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


EMPTY_FIELDS = {
    "relations": [],
    "events": [],
    "states": [],
    "temporal": [],
    "causal": [],
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("existing_annotations", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--per-domain", type=int, default=2)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()
    if args.per_domain <= 0:
        raise ValueError("per-domain must be positive")

    corpus = load_jsonl(args.corpus)
    existing = {str(row["source_id"]): row for row in load_jsonl(args.existing_annotations)}
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in corpus:
        groups[str(row.get("domain", ""))].append(row)
    if any(not domain for domain in groups):
        raise ValueError("every corpus record requires domain")

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for domain in sorted(groups):
        ordered = sorted(
            groups[domain],
            key=lambda row: hashlib.sha256(f"{args.seed}:{row['id']}".encode("utf-8")).hexdigest(),
        )
        existing_rows = [row for row in ordered if str(row["id"]) in existing]
        domain_rows = existing_rows + [
            row for row in ordered if str(row["id"]) not in existing and len(existing_rows) < args.per_domain
        ][: max(0, args.per_domain - len(existing_rows))]
        selected.extend(domain_rows)
        selected_ids.update(str(row["id"]) for row in domain_rows)

    # Preserve every existing annotation, even if a domain has more than the minimum.
    for row in sorted(corpus, key=lambda item: str(item["id"])):
        source_id = str(row["id"])
        if source_id in existing and source_id not in selected_ids:
            selected.append(row)
            selected_ids.add(source_id)

    output_rows: list[dict[str, Any]] = []
    for row in selected:
        source_id = str(row["id"])
        previous = existing.get(source_id)
        if previous:
            annotation = dict(previous)
            annotation["domain"] = row["domain"]
            annotation["text"] = row["text"]
        else:
            annotation = {
                "source_id": source_id,
                "domain": row["domain"],
                "text": row["text"],
                "review_status": "proposed_needs_review",
                **EMPTY_FIELDS,
                "review_notes": "Review relations, events, states, temporal order, and causal claims manually.",
            }
        output_rows.append(annotation)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in output_rows) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "review_batch_ready",
        "record_count": len(output_rows),
        "domain_count": len(groups),
        "per_domain": args.per_domain,
        "approved_existing": sum(row.get("review_status") == "approved" for row in output_rows),
        "needs_review": sum(row.get("review_status") != "approved" for row in output_rows),
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
