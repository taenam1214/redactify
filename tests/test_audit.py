"""Tests for the redaction audit trail."""

import json
from pathlib import Path

from redactify.core.audit import AuditEntry, AuditTrail
from redactify.core.detector import PIIEntity, PIIType


class TestAuditEntry:
    """Tests for individual audit entries."""

    def test_from_entity(self):
        entity = PIIEntity(
            text="john@example.com",
            pii_type=PIIType.EMAIL,
            start=10,
            end=26,
            confidence=1.0,
        )
        entry = AuditEntry.from_entity(entity, "label")
        assert entry.pii_type == "email"
        assert entry.start == 10
        assert entry.end == 26
        assert entry.length == 16
        assert entry.confidence == 1.0
        assert entry.redaction_mode == "label"
        assert len(entry.content_hash) == 16

    def test_content_hash_is_deterministic(self):
        entity = PIIEntity(text="test@test.com", pii_type=PIIType.EMAIL, start=0, end=13)
        entry1 = AuditEntry.from_entity(entity, "blackout")
        entry2 = AuditEntry.from_entity(entity, "blackout")
        assert entry1.content_hash == entry2.content_hash

    def test_different_text_different_hash(self):
        e1 = PIIEntity(text="alice@test.com", pii_type=PIIType.EMAIL, start=0, end=14)
        e2 = PIIEntity(text="bob@test.com", pii_type=PIIType.EMAIL, start=0, end=12)
        entry1 = AuditEntry.from_entity(e1, "label")
        entry2 = AuditEntry.from_entity(e2, "label")
        assert entry1.content_hash != entry2.content_hash


class TestAuditTrail:
    """Tests for the full audit trail."""

    def _sample_entities(self) -> list[PIIEntity]:
        return [
            PIIEntity(text="john@example.com", pii_type=PIIType.EMAIL, start=10, end=26),
            PIIEntity(text="(555) 123-4567", pii_type=PIIType.PHONE, start=40, end=54),
            PIIEntity(text="Jane Doe", pii_type=PIIType.PERSON, start=60, end=68, confidence=0.85),
        ]

    def test_create_builds_trail(self):
        entities = self._sample_entities()
        trail = AuditTrail.create(Path("test.txt"), entities, "label")
        assert trail.total_redactions == 3
        assert trail.redaction_mode == "label"
        assert trail.summary == {"email": 1, "phone": 1, "person": 1}
        assert len(trail.entries) == 3
        assert trail.source_file == "test.txt"
        assert trail.timestamp  # Non-empty ISO timestamp

    def test_to_json_is_valid(self):
        entities = self._sample_entities()
        trail = AuditTrail.create(Path("doc.pdf"), entities, "blackout")
        json_str = trail.to_json()
        parsed = json.loads(json_str)
        assert parsed["total_redactions"] == 3
        assert parsed["redaction_mode"] == "blackout"
        assert len(parsed["entries"]) == 3

    def test_to_json_does_not_contain_pii(self):
        entities = self._sample_entities()
        trail = AuditTrail.create(Path("doc.txt"), entities, "label")
        json_str = trail.to_json()
        # The actual PII text should NOT appear in the audit trail
        assert "john@example.com" not in json_str
        assert "(555) 123-4567" not in json_str
        assert "Jane Doe" not in json_str

    def test_write_creates_file(self, tmp_path):
        entities = self._sample_entities()
        trail = AuditTrail.create(Path("input.txt"), entities, "hash")
        output = tmp_path / "audit.json"
        trail.write(output)
        assert output.exists()
        data = json.loads(output.read_text())
        assert data["total_redactions"] == 3

    def test_empty_entities_produces_valid_trail(self):
        trail = AuditTrail.create(Path("clean.txt"), [], "label")
        assert trail.total_redactions == 0
        assert trail.entries == []
        assert trail.summary == {}
