"""Audit source metadata and print license-gate decisions."""

import argparse
import json
from pathlib import Path

from allm.data import SourceRegistry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    args = parser.parse_args()
    registry = SourceRegistry.from_json(args.registry)
    results = []
    for source in registry.list():
        decision = registry.gate(source.source_id)
        results.append({
            "source_id": source.source_id,
            "layer": source.layer.value,
            "status": source.status.value,
            "allowed": decision.allowed,
            "reason": decision.reason,
        })
    print(json.dumps({"sources": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
