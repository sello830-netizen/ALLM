"""Measure the baseline tokenizer on newline-delimited UTF-8 text."""

import argparse
import json
from pathlib import Path

from allm.tokenization import BaselineTokenizer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    texts = [line.strip() for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    tokenizer = BaselineTokenizer()
    result = {"tokenizer_hash": tokenizer.spec.fingerprint, **tokenizer.measure(texts)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
