import unittest

from allm.data import (
    build_release,
    conservative_normalize,
    find_split_leaks,
    sentence_split,
)
from allm.domain import Document, SourceRecord


SOURCE = SourceRecord(
    source_id="fixture",
    license="CC-BY-4.0",
    domain="general",
    register="modern-standard-arabic",
)


class DataPipelineTests(unittest.TestCase):
    def test_normalization_preserves_diacritics_and_removes_tatweel(self):
        self.assertEqual(conservative_normalize("مَرْحـبًا   بالعالم"), "مَرْحبًا بالعالم")

    def test_sentence_split(self):
        self.assertEqual(sentence_split("أولاً. ثانيًا؟"), ["أولاً.", "ثانيًا؟"])

    def test_release_is_deduplicated_and_hashed(self):
        documents = [
            Document("a", SOURCE, "نص  واحد", "train"),
            Document("b", SOURCE, "نص واحد", "train"),
        ]
        release = build_release(documents, "fixture", "0.1.0")
        self.assertEqual(release.document_count, 1)
        self.assertEqual(len(release.manifest_hash), 64)

    def test_split_leak_is_detected(self):
        documents = [
            Document("a", SOURCE, "نص مشترك", "train"),
            Document("b", SOURCE, "نص مشترك", "test"),
        ]
        self.assertEqual(len(find_split_leaks(documents)), 1)


if __name__ == "__main__":
    unittest.main()
