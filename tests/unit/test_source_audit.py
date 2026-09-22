import unittest
from pathlib import Path

from allm.data import AuditDecision, SourceAudit, SourceAuditRegistry, SourceRegistry


class SourceAuditTests(unittest.TestCase):
    def test_all_registered_sources_have_blocked_pre_audits(self):
        sources = SourceRegistry.from_json(Path("configs/data/sources.json"))
        audits = SourceAuditRegistry.from_json(Path("configs/data/source_audits.json"))
        audits.validate_against_sources(sources)
        self.assertEqual(len(audits.list()), 4)
        self.assertTrue(all(audit.decision is AuditDecision.BLOCKED_PENDING_REVIEW for audit in audits.list()))

    def test_audit_requires_evidence(self):
        audit = SourceAudit(
            source_id="source",
            checked_at="2026-09-22",
            reviewer="test",
            evidence_urls=(),
            observed_license="unknown",
            observed_permissions=(),
            findings=("pending",),
            decision=AuditDecision.BLOCKED_PENDING_REVIEW,
            next_action="review",
        )
        with self.assertRaises(ValueError):
            audit.validate()

    def test_redistributable_audit_requires_permissions(self):
        audit = SourceAudit(
            source_id="source",
            checked_at="2026-09-22",
            reviewer="test",
            evidence_urls=("https://example.test/license",),
            observed_license="CC-BY-4.0",
            observed_permissions=("commercial_training",),
            findings=("partial",),
            decision=AuditDecision.APPROVED_REDISTRIBUTABLE,
            next_action="none",
        )
        with self.assertRaises(ValueError):
            audit.validate()


if __name__ == "__main__":
    unittest.main()
