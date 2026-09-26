"""Build approved structured views; proposed annotations are never trained by default."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("annotations", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--allow-proposed", action="store_true", help="dry-run inspection only; never use for training")
    parser.add_argument("--approved-only", action="store_true", help="build inspection views from approved subset only")
    args = parser.parse_args()
    annotations = load_jsonl(args.annotations)
    proposed_count = sum(item.get("review_status") != "approved" for item in annotations)
    if args.approved_only:
        annotations = [item for item in annotations if item.get("review_status") == "approved"]
        if not annotations:
            raise PermissionError("no approved annotations available")
    elif not args.allow_proposed and proposed_count:
        raise PermissionError("structured views require review_status=approved; use --approved-only for a reviewed subset")

    original: list[str] = []
    structured: list[str] = []
    for item in annotations:
        original.append(str(item["text"]))
        structured.append(
            "TASK_REL "
            + " | ".join(f"{relation['subject']} -> {relation['predicate']} -> {relation['object']}" for relation in item["relations"])
            + " TASK_EVENT "
            + " | ".join(f"{event['type']}:{event['argument']}" for event in item["events"])
            + " TASK_STATE "
            + " | ".join(f"{state['entity']}:{state['before']}->{state['after']}" for state in item["states"])
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "original.txt").write_text("\n".join(original) + "\n", encoding="utf-8")
    (args.output_dir / "structured.txt").write_text("\n".join(structured) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "built",
        "records": len(annotations),
        "excluded_unapproved": proposed_count if args.approved_only else 0,
        "training_ready": not args.approved_only and not proposed_count,
        "output_dir": str(args.output_dir),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
