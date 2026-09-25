import unittest

from allm.data import split_records


class SplitTests(unittest.TestCase):
    def test_split_is_deterministic_and_disjoint(self):
        records = [{"source_id": f"doc-{index}", "text": f"نص {index}"} for index in range(35)]
        first = split_records(records, seed=17)
        second = split_records(records, seed=17)
        self.assertEqual(first, second)
        self.assertEqual([len(first[name]) for name in ("train", "dev", "test")], [28, 3, 4])
        ids = [record["source_id"] for split in first.values() for record in split]
        self.assertEqual(len(ids), len(set(ids)))

    def test_duplicate_source_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            split_records([{"source_id": "same"}, {"source_id": "same"}])


if __name__ == "__main__":
    unittest.main()
