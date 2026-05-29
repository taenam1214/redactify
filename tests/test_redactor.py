"""Tests for the redactor module."""

from redactify.core.detector import PIIEntity, PIIType
from redactify.core.redactor import Redactor, RedactionMode


class TestRedactorBlackout:
    def setup_method(self):
        self.redactor = Redactor(mode=RedactionMode.BLACKOUT)

    def test_replaces_with_blocks(self):
        entity = PIIEntity(text="john@test.com", pii_type=PIIType.EMAIL, start=7, end=20)
        result = self.redactor.redact("Email: john@test.com", [entity])
        assert "john@test.com" not in result
        assert "█" * 13 in result

    def test_preserves_surrounding_text(self):
        entity = PIIEntity(text="john@test.com", pii_type=PIIType.EMAIL, start=7, end=20)
        result = self.redactor.redact("Email: john@test.com end", [entity])
        assert result.startswith("Email: ")
        assert result.endswith(" end")

    def test_handles_empty_entities(self):
        result = self.redactor.redact("No PII here", [])
        assert result == "No PII here"


class TestRedactorLabel:
    def setup_method(self):
        self.redactor = Redactor(mode=RedactionMode.LABEL)

    def test_replaces_with_type_label(self):
        entity = PIIEntity(text="john@test.com", pii_type=PIIType.EMAIL, start=0, end=13)
        result = self.redactor.redact("john@test.com", [entity])
        assert result == "[EMAIL]"

    def test_phone_label(self):
        entity = PIIEntity(text="555-1234", pii_type=PIIType.PHONE, start=0, end=8)
        result = self.redactor.redact("555-1234", [entity])
        assert result == "[PHONE]"

    def test_person_label(self):
        entity = PIIEntity(text="John Smith", pii_type=PIIType.PERSON, start=0, end=10)
        result = self.redactor.redact("John Smith", [entity])
        assert result == "[PERSON]"


class TestRedactorHash:
    def setup_method(self):
        self.redactor = Redactor(mode=RedactionMode.HASH)

    def test_replaces_with_hash(self):
        entity = PIIEntity(text="john@test.com", pii_type=PIIType.EMAIL, start=0, end=13)
        result = self.redactor.redact("john@test.com", [entity])
        assert result.startswith("[REDACTED-")
        assert result.endswith("]")

    def test_deterministic_hash(self):
        entity = PIIEntity(text="john@test.com", pii_type=PIIType.EMAIL, start=0, end=13)
        result1 = self.redactor.get_replacement(entity)
        result2 = self.redactor.get_replacement(entity)
        assert result1 == result2

    def test_different_inputs_different_hashes(self):
        e1 = PIIEntity(text="john@test.com", pii_type=PIIType.EMAIL, start=0, end=13)
        e2 = PIIEntity(text="jane@test.com", pii_type=PIIType.EMAIL, start=0, end=13)
        assert self.redactor.get_replacement(e1) != self.redactor.get_replacement(e2)


class TestRedactorCustom:
    def test_replaces_with_custom_string(self):
        redactor = Redactor(mode=RedactionMode.CUSTOM, custom_string="***")
        entity = PIIEntity(text="john@test.com", pii_type=PIIType.EMAIL, start=0, end=13)
        result = redactor.redact("john@test.com", [entity])
        assert result == "***"


class TestRedactorMultipleEntities:
    def test_redacts_multiple_entities_correctly(self):
        redactor = Redactor(mode=RedactionMode.LABEL)
        entities = [
            PIIEntity(text="john@test.com", pii_type=PIIType.EMAIL, start=7, end=20),
            PIIEntity(text="555-1234", pii_type=PIIType.PHONE, start=28, end=36),
        ]
        text = "Email: john@test.com Phone: 555-1234"
        result = redactor.redact(text, entities)
        assert "[EMAIL]" in result
        assert "[PHONE]" in result
        assert "john@test.com" not in result
        assert "555-1234" not in result
