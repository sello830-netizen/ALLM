import tempfile
import unittest
from pathlib import Path

from allm.domain import Run, RunStatus
from allm.registry import RunRegistry


class RegistryTests(unittest.TestCase):
    def test_registry_is_append_only_and_round_trips(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = RunRegistry(Path(directory) / "runs.jsonl")
            run = Run(
                run_id="run-001",
                experiment_id="baseline",
                status=RunStatus.COMPLETED,
                code_revision="local",
                config_hash="config",
                dataset_hash="dataset",
                tokenizer_hash="tokenizer",
                evaluation_hash="evaluation",
                seed=17,
                steps=10,
                tokens=100,
                metrics={"loss": 1.2},
            )
            registry.append(run)
            self.assertEqual(registry.get("run-001"), run)
            registry.assert_lineage(
                "run-001",
                dataset_hash="dataset",
                tokenizer_hash="tokenizer",
                evaluation_hash="evaluation",
            )
            with self.assertRaises(ValueError):
                registry.assert_lineage(
                    "run-001",
                    dataset_hash="wrong-dataset",
                    tokenizer_hash="tokenizer",
                    evaluation_hash="evaluation",
                )
            with self.assertRaises(ValueError):
                registry.append(run)

    def test_incomplete_run_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = RunRegistry(Path(directory) / "runs.jsonl")
            run = Run(
                run_id="run-002",
                experiment_id="baseline",
                status=RunStatus.FAILED,
                code_revision="",
                config_hash="config",
                dataset_hash="dataset",
                tokenizer_hash="tokenizer",
                evaluation_hash="evaluation",
                seed=17,
            )
            with self.assertRaises(ValueError):
                registry.append(run)


if __name__ == "__main__":
    unittest.main()
