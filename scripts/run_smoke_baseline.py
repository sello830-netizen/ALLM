"""Run the dependency-free reference baseline and record a complete run."""

import argparse
import json
from pathlib import Path

from allm.domain import Run, RunStatus, stable_hash
from allm.registry import RunRegistry
from allm.tokenization import BaselineTokenizer
from allm.training import BigramLanguageModel


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="UTF-8 newline-delimited text")
    parser.add_argument("registry", type=Path, help="JSONL run registry")
    args = parser.parse_args()

    texts = [line.strip() for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    tokenizer = BaselineTokenizer()
    sequences = [tokenizer.tokenize(text) for text in texts]
    model = BigramLanguageModel().fit(sequences)
    perplexity = sum(model.perplexity(sequence) for sequence in sequences) / len(sequences)
    run = Run(
        run_id=f"smoke-{stable_hash(texts)[:12]}",
        experiment_id="reference-bigram-v0",
        status=RunStatus.COMPLETED,
        code_revision="working-tree",
        config_hash=stable_hash({"model": "bigram", "alpha": 1.0}),
        dataset_hash=stable_hash(texts),
        tokenizer_hash=tokenizer.spec.fingerprint,
        evaluation_hash="unigram-and-bigram-v0",
        seed=17,
        steps=len(sequences),
        tokens=sum(len(sequence) for sequence in sequences),
        metrics={"mean_perplexity": perplexity},
    )
    RunRegistry(args.registry).append(run)
    print(json.dumps(run.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
