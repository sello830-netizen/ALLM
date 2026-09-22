import tempfile
import unittest
from pathlib import Path

from allm.data import build_release
from allm.domain import Document, Run, RunStatus, SourceRecord
from allm.registry import RunRegistry
from allm.tokenization import BaselineTokenizer


class FoundationFlowTests(unittest.TestCase):
    def test_manifest_tokenizer_and_run_lineage(self):
        source = SourceRecord("fixture", "internal-test", "general", "msa")
        documents = [Document("doc-1", source, "نص عربي للاختبار.")]
        release = build_release(documents, "fixture", "0.1.0")
        tokenizer = BaselineTokenizer()
        measurement = tokenizer.measure([document.text for document in documents])
        self.assertEqual(release.document_count, 1)
        self.assertGreater(measurement["tokens"], 0)

        with tempfile.TemporaryDirectory() as directory:
            registry = RunRegistry(Path(directory) / "runs.jsonl")
            registry.append(Run(
                run_id="smoke-001",
                experiment_id="baseline-v0",
                status=RunStatus.COMPLETED,
                code_revision="working-tree",
                config_hash="config-v0",
                dataset_hash=release.manifest_hash,
                tokenizer_hash=tokenizer.spec.fingerprint,
                evaluation_hash="evaluation-v0",
                seed=17,
                tokens=int(measurement["tokens"]),
                metrics={"tokenizer_tokens": measurement["tokens"]},
            ))
            self.assertEqual(len(list(registry.completed())), 1)


if __name__ == "__main__":
    unittest.main()
