"""Build controlled original and masked-span pilot conditions from JSONL data."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any

from allm.data import split_records
from allm.tokenization import BaselineTokenizer


def masked_view(text: str, source_id: str) -> str:
    tokenizer = BaselineTokenizer()
    tokens = tokenizer.tokenize(text)
    if len(tokens) < 4:
        return f"TASK_MASK {text}"
    digest = int(hashlib.sha256(source_id.encode("utf-8")).hexdigest()[:8], 16)
    span_length = max(1, min(3, len(tokens) // 4))
    start = digest % (len(tokens) - span_length + 1)
    span = tokens[start : start + span_length]
    prefix = " ".join(tokens[:start])
    suffix = " ".join(tokens[start + span_length :])
    return f"TASK_MASK {prefix} MASK_TOKEN {suffix} TARGET_TOKEN {' '.join(span)}"


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            source_id = str(record.get("id", "")).strip()
            text = str(record.get("text", "")).strip()
            domain = str(record.get("domain", "")).strip()
            if not source_id or not text or not domain:
                raise ValueError(f"line {line_number} requires id, text, and domain")
            if source_id in seen:
                raise ValueError(f"duplicate id: {source_id}")
            seen.add(source_id)
            records.append({"source_id": source_id, "text": text, "domain": domain})
    return records


def write_condition(output_dir: Path, splits: dict[str, list[dict[str, Any]]], view_mode: str) -> dict[str, Any]:
    tokenizer = BaselineTokenizer()
    manifest: dict[str, Any] = {"view_mode": view_mode, "splits": {}}
    for split_name, records in splits.items():
        texts: list[str] = []
        source_ids: list[str] = []
        for record in records:
            original = str(record["text"])
            masked = masked_view(original, str(record["source_id"]))
            if view_mode == "original":
                selected = [original]
            elif view_mode == "masked":
                selected = [masked]
            elif view_mode == "multiview":
                selected = [original, masked]
            elif view_mode == "one_view":
                digest = int(hashlib.sha256(str(record["source_id"]).encode("utf-8")).hexdigest()[:8], 16)
                selected = [original if digest % 2 == 0 else masked]
            else:
                raise ValueError(f"unsupported view mode: {view_mode}")
            texts.extend(selected)
            source_ids.extend([str(record["source_id"])] * len(selected))
        output_dir.mkdir(parents=True, exist_ok=True)
        text = "\n".join(texts) + "\n"
        (output_dir / f"{split_name}.txt").write_text(text, encoding="utf-8")
        manifest["splits"][split_name] = {
            "source_count": len(records),
            "example_count": len(texts),
            "source_ids": source_ids,
            "token_count": int(tokenizer.measure(texts)["tokens"]),
        }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    records = load_records(args.input)
    splits = split_records(records, seed=args.seed, stratify_by="domain")
    manifests = {}
    for mode in ("original", "one_view", "multiview"):
        manifests[mode] = write_condition(args.output_dir / mode, splits, mode)
    payload = {
        "source_type": "synthetic",
        "input": str(args.input),
        "seed": args.seed,
        "view_modes": ["original", "one_view", "multiview"],
        "view_definition": "original text plus deterministic masked-span task; no generated semantic labels",
        "manifests": manifests,
    }
    (args.output_dir / "multiview_manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
