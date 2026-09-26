import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from prepare_structured_review_batch import main as prepare_main


class StructuredReviewBatchTests(unittest.TestCase):
    def test_batch_is_balanced_and_preserves_approved_annotations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.jsonl"
            existing = root / "existing.jsonl"
            output = root / "batch.jsonl"
            rows = [
                {"id": "a1", "domain": "a", "text": "نص أ1"},
                {"id": "a2", "domain": "a", "text": "نص أ2"},
                {"id": "b1", "domain": "b", "text": "نص ب1"},
                {"id": "b2", "domain": "b", "text": "نص ب2"},
            ]
            corpus.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
            approved = {"source_id": "a1", "text": "نص أ1", "review_status": "approved", "relations": [], "events": [], "states": [], "temporal": [], "causal": []}
            existing.write_text(json.dumps(approved, ensure_ascii=False) + "\n", encoding="utf-8")
            import sys as _sys
            old_argv = _sys.argv
            try:
                _sys.argv = ["prepare_structured_review_batch.py", str(corpus), str(existing), str(output), "--per-domain", "1"]
                self.assertEqual(prepare_main(), 0)
            finally:
                _sys.argv = old_argv
            result = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(result), 2)
            self.assertEqual(sum(row["review_status"] == "approved" for row in result), 1)


if __name__ == "__main__":
    unittest.main()
