"""Validate that every registered source has an explicit pre-audit."""

import argparse
import json
from pathlib import Path

from allm.data import SourceAuditRegistry, SourceRegistry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=Path)
    parser.add_argument("audits", type=Path)
    args = parser.parse_args()
    sources = SourceRegistry.from_json(args.sources)
    audits = SourceAuditRegistry.from_json(args.audits)
    audits.validate_against_sources(sources)
    report = [
        {
            "source_id": audit.source_id,
            "decision": audit.decision.value,
            "evidence_count": len(audit.evidence_urls),
            "next_action": audit.next_action,
        }
        for audit in audits.list()
    ]
    print(json.dumps({"status": "valid", "audits": report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
