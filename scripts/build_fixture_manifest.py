"""Build a tiny local manifest for smoke tests; no licensed corpus is bundled."""

import argparse
import json
from pathlib import Path

from allm.data import build_manifest, build_release
from allm.domain import Document, SourceRecord


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="manifest JSON destination")
    args = parser.parse_args()

    source = SourceRecord("local-fixture", "internal-test", "general", "msa")
    documents = [
        Document("fixture-001", source, "هذه عينة عربية للاختبار.", "train"),
        Document("fixture-002", source, "وهذه جملة أخرى للاختبار.", "dev"),
    ]
    release = build_release(documents, "arabic-mini", "0.1.0")
    manifest = {
        "release": release.__dict__,
        "documents": build_manifest(documents),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=list) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, default=list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
