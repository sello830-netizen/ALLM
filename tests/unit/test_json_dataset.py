import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from extract_json_dataset import load_dataset


class JsonDatasetTests(unittest.TestCase):
    def test_fixture_has_35_unique_arabic_records(self):
        payload = load_dataset(Path("data/fixtures/arabic_multiview_pilot_001.json"))
        self.assertEqual(payload["language"], "ar")
        self.assertEqual(payload["_validated_record_count"], 35)
        self.assertGreater(payload["_validated_character_count"], 4000)

    def test_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps({
                "language": "ar",
                "data": [
                    {"source_id": "same", "text": "نص أول"},
                    {"source_id": "same", "text": "نص ثان"},
                ],
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_dataset(path)


if __name__ == "__main__":
    unittest.main()
