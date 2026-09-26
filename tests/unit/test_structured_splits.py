import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from prepare_structured_splits import main as prepare_main


class StructuredSplitTests(unittest.TestCase):
    def _annotation(self, source_id: str, text: str) -> dict:
        return {
            "source_id": source_id,
            "text": text,
            "review_status": "approved",
            "relations": [{"subject": "أ", "predicate": "ب", "object": "ج"}],
            "events": [],
            "states": [],
            "temporal": [],
            "causal": [],
        }

    def test_approved_views_share_source_split(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.jsonl"
            annotations = root / "annotations.jsonl"
            output = root / "split"
            corpus_rows = [{"id": f"doc-{i}", "domain": "d", "text": f"نص {i}"} for i in range(10)]
            corpus.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in corpus_rows) + "\n", encoding="utf-8")
            annotations.write_text(
                "\n".join(json.dumps(self._annotation(row["id"], row["text"]), ensure_ascii=False) for row in corpus_rows) + "\n",
                encoding="utf-8",
            )
            import sys as _sys
            old_argv = _sys.argv
            try:
                _sys.argv = ["prepare_structured_splits.py", str(corpus), str(annotations), str(output)]
                self.assertEqual(prepare_main(), 0)
            finally:
                _sys.argv = old_argv
            manifest = json.loads((output / "split_manifest.json").read_text(encoding="utf-8"))
            for split in manifest["splits"].values():
                self.assertEqual(split["record_count"], len(split["source_ids"]))
                self.assertGreater(split["structured_tokens"], 0)

    def test_unapproved_annotations_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.jsonl"
            annotations = root / "annotations.jsonl"
            corpus.write_text(json.dumps({"id": "doc", "text": "نص", "domain": "d"}) + "\n", encoding="utf-8")
            row = self._annotation("doc", "نص")
            row["review_status"] = "proposed_needs_review"
            annotations.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
            import sys as _sys
            old_argv = _sys.argv
            try:
                _sys.argv = ["prepare_structured_splits.py", str(corpus), str(annotations), str(root / "out")]
                with self.assertRaises(PermissionError):
                    prepare_main()
            finally:
                _sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
