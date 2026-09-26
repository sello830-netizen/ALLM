import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts"))

from build_multiview_pilot import masked_view, main, load_records, write_condition
from allm.data import split_records


class MultiViewPilotTests(unittest.TestCase):
    def test_masked_view_is_deterministic_and_keeps_source_information(self):
        text = "وصلت الشحنة إلى ميناء أبوظبي صباح اليوم."
        first = masked_view(text, "doc-1")
        second = masked_view(text, "doc-1")
        self.assertEqual(first, second)
        self.assertIn("MASK_TOKEN", first)
        self.assertIn("TARGET_TOKEN", first)

    def test_conditions_preserve_source_split_boundaries(self):
        records = [{"source_id": f"doc-{i}", "text": f"نص عربي {i}", "domain": "domain"} for i in range(20)]
        splits = split_records(records, seed=17, stratify_by="domain")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = write_condition(root / "multi", splits, "multiview")
            source_sets = [
                set(manifest["splits"][name]["source_ids"])
                for name in ("train", "dev", "test")
            ]
            self.assertEqual(len(source_sets[0] & source_sets[1]), 0)
            self.assertEqual(len(source_sets[0] & source_sets[2]), 0)
            self.assertEqual(len(source_sets[1] & source_sets[2]), 0)
            self.assertEqual(manifest["splits"]["train"]["example_count"], len(splits["train"]) * 2)


if __name__ == "__main__":
    unittest.main()
