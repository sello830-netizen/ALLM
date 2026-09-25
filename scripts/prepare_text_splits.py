"""Create deterministic original-only text splits from the pilot JSON dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from allm.data import split_records
from allm.domain import stable_hash


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    splits = split_records(payload["data"], seed=args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "dataset_id": payload.get("dataset_id"),
        "version": payload.get("version"),
        "source_type": payload.get("source_type"),
        "seed": args.seed,
        "ratios": {"train": 0.8, "dev": 0.1, "test": 0.1},
        "splits": {},
    }
    for split_name, records in splits.items():
        text = "\n".join(str(record["text"]).strip() for record in records) + "\n"
        (args.output_dir / f"{split_name}.txt").write_text(text, encoding="utf-8")
        manifest["splits"][split_name] = {
            "record_count": len(records),
            "source_ids": [record["source_id"] for record in records],
            "text_hash": stable_hash(text),
        }
    (args.output_dir / "split_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
