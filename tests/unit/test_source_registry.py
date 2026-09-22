import json
import tempfile
import unittest
from pathlib import Path

from allm.data import CorpusLayer, LicenseGate, SourceRegistry, SourceSpec, SourceStatus


class SourceRegistryTests(unittest.TestCase):
    def test_config_sources_are_rejected_until_approved(self):
        path = Path("configs/data/sources.json")
        registry = SourceRegistry.from_json(path)
        self.assertEqual(len(registry.list()), 4)
        for source in registry.list():
            self.assertFalse(registry.gate(source.source_id).allowed)

    def test_redistributable_source_requires_all_permissions(self):
        source = SourceSpec(
            source_id="approved",
            title="Approved fixture",
            provider="test",
            release="1",
            uri="https://example.test/source",
            license="CC-BY-4.0",
            layer=CorpusLayer.REDISTRIBUTABLE_TRAIN,
            status=SourceStatus.APPROVED_REDISTRIBUTABLE,
            language="ar",
            register="msa",
            domain="general",
            era="modern",
            provenance="test fixture",
            commercial_training_allowed=True,
            redistribution_allowed=True,
            derived_model_allowed=True,
            non_commercial=False,
        )
        self.assertTrue(LicenseGate().check(source).allowed)

    def test_research_source_cannot_pass_redistributable_gate(self):
        source = SourceSpec(
            source_id="research",
            title="Research fixture",
            provider="test",
            release="1",
            uri="https://example.test/source",
            license="research-only",
            layer=CorpusLayer.RESEARCH_ONLY_TRAIN,
            status=SourceStatus.APPROVED_RESEARCH,
            language="ar",
            register="classical",
            domain="heritage",
            era="classical",
            provenance="test fixture",
        )
        self.assertTrue(LicenseGate().check(source).allowed)
        self.assertFalse(LicenseGate().check(source, CorpusLayer.REDISTRIBUTABLE_TRAIN).allowed)

    def test_approved_redistributable_without_permissions_is_invalid(self):
        with self.assertRaises(ValueError):
            SourceSpec(
                source_id="invalid",
                title="Invalid fixture",
                provider="test",
                release="1",
                uri="https://example.test/source",
                license="unknown",
                layer=CorpusLayer.REDISTRIBUTABLE_TRAIN,
                status=SourceStatus.APPROVED_REDISTRIBUTABLE,
                language="ar",
                register="msa",
                domain="general",
                era="modern",
                provenance="test fixture",
            ).validate()


if __name__ == "__main__":
    unittest.main()
