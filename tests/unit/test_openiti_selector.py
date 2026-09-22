import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from select_openiti_metadata import select_metadata


class OpenITIMetadataSelectorTests(unittest.TestCase):
    def test_selects_only_arabic_metadata_and_never_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "metadata.tsv"
            output = root / "pilot.json"
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["language", "title"], delimiter="\t")
                writer.writeheader()
                writer.writerow({"language": "ar", "title": "Arabic"})
                writer.writerow({"language": "English", "title": "English"})
                writer.writerow({"language": "ara", "title": "Arabic two"})
            result = select_metadata(source, output, limit=10)
            self.assertEqual(result["selection"]["candidate_count"], 2)
            self.assertFalse(result["text_downloaded"])
            self.assertEqual(len(json.loads(output.read_text(encoding="utf-8"))["records"]), 2)


if __name__ == "__main__":
    unittest.main()
