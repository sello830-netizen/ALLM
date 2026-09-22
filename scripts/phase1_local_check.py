"""Run the complete dependency-light local phase gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from allm.data import build_release
from allm.domain import Document, Run, RunStatus, SourceRecord
from allm.evaluation import EvaluationCase, evaluate_cases
from allm.registry import RunRegistry
from allm.tokenization import BaselineTokenizer
from allm.training import BigramLanguageModel


def run_tests() -> tuple[int, bool]:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    return result.testsRun, result.wasSuccessful()


def run_gate() -> dict[str, object]:
    tests_run, tests_passed = run_tests()
    source = SourceRecord("phase1-fixture", "internal-test", "general", "msa")
    documents = [
        Document("phase1-001", source, "هذه عينة عربية للاختبار.", "train"),
        Document("phase1-002", source, "وهذه جملة أخرى للاختبار.", "dev"),
        Document("phase1-003", source, "النموذج المرجعي يتعلم انتقالات الرموز.", "test"),
    ]
    release = build_release(documents, "arabic-mini", "0.1.0")
    tokenizer = BaselineTokenizer()
    sequences = [tokenizer.tokenize(document.text) for document in documents]
    model = BigramLanguageModel().fit(sequences)
    mean_perplexity = sum(model.perplexity(sequence) for sequence in sequences) / len(sequences)
    evaluation = evaluate_cases([
        EvaluationCase("morph-001", "morphology", ("كتب", "وا"), ("كتب", "وا")),
        EvaluationCase("syntax-001", "syntax", ("هو", "ذهب"), ("هو", "ذهبت")),
    ])

    with tempfile.TemporaryDirectory() as directory:
        registry = RunRegistry(Path(directory) / "runs.jsonl")
        run = Run(
            run_id="phase1-local-001",
            experiment_id="reference-bigram-v0",
            status=RunStatus.COMPLETED,
            code_revision="working-tree",
            config_hash="reference-bigram-alpha-1.0",
            dataset_hash=release.manifest_hash,
            tokenizer_hash=tokenizer.spec.fingerprint,
            evaluation_hash=evaluation.suite_id,
            seed=17,
            steps=len(sequences),
            tokens=sum(len(sequence) for sequence in sequences),
            metrics={"mean_perplexity": mean_perplexity, "evaluation_accuracy": evaluation.overall_accuracy},
        )
        registry.append(run)
        registry.assert_lineage(
            run.run_id,
            dataset_hash=release.manifest_hash,
            tokenizer_hash=tokenizer.spec.fingerprint,
            evaluation_hash=evaluation.suite_id,
        )

    return {
        "status": "passed" if tests_passed else "failed",
        "tests_run": tests_run,
        "tests_passed": tests_passed,
        "dataset_manifest_hash": release.manifest_hash,
        "tokenizer_hash": tokenizer.spec.fingerprint,
        "mean_perplexity": mean_perplexity,
        "evaluation_accuracy": evaluation.overall_accuracy,
        "lineage_verified": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="optional JSON report path")
    args = parser.parse_args()
    report = run_gate()
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
