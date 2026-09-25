import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from prepare_jsonl_splits import load_jsonl


class JsonlSplitTests(unittest.TestCase):
    def test_loads_valid_jsonl_and_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.jsonl"
            path.write_text(
                json.dumps({"id": "a", "text": "نص أول", "domain": "x", "source_type": "synthetic"}, ensure_ascii=False)
                + "\n"
                + json.dumps({"id": "b", "text": "نص ثان", "domain": "y", "source_type": "synthetic"}, ensure_ascii=False)
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(len(load_jsonl(path)), 2)
            path.write_text(
                json.dumps({"id": "a", "text": "نص"}, ensure_ascii=False) + "\n"
                + json.dumps({"id": "a", "text": "مكرر"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_jsonl(path)


if __name__ == "__main__":
    unittest.main()
