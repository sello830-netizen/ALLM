import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from validate_structured_annotations import load_jsonl


class StructuredAnnotationTests(unittest.TestCase):
    def test_proposed_annotation_matches_source_text(self):
        corpus = Path("data/fixtures/arabic_baseline_corpus_500.jsonl")
        annotations = Path("data/fixtures/structured_micro_pilot_proposed.jsonl")
        source = {row["id"]: row for row in (json.loads(line) for line in corpus.read_text(encoding="utf-8").splitlines())}
        rows = load_jsonl(annotations)
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(row["review_status"] == "proposed_needs_review" for row in rows))
        self.assertTrue(all(source[row["source_id"]]["text"] == row["text"] for row in rows))

    def test_empty_or_mismatched_annotation_is_detectable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "annotations.jsonl"
            path.write_text(json.dumps({"source_id": "missing", "text": "x"}) + "\n", encoding="utf-8")
            self.assertEqual(load_jsonl(path)[0]["source_id"], "missing")


if __name__ == "__main__":
    unittest.main()
