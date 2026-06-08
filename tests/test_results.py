"""Tests for the TextResult dataclass."""

from redactify.core.detector import PIIEntity, PIIType
from redactify.core.results import TextResult


class TestTextResult:
    def test_empty_result(self):
        result = TextResult(text="hello world")
        assert result.text == "hello world"
        assert result.total_entities == 0
        assert result.entities_by_type == {}
        assert result.has_pii is False
        assert result.source == "<string>"

    def test_result_with_entities(self):
        entities = [
            PIIEntity(text="john@example.com", pii_type=PIIType.EMAIL, start=0, end=16),
            PIIEntity(text="555-1234", pii_type=PIIType.PHONE, start=20, end=28),
        ]
        result = TextResult(text="redacted text", entities=entities)
        assert result.total_entities == 2
        assert result.has_pii is True
        assert result.entities_by_type == {"email": 1, "phone": 1}

    def test_entities_by_type_multiple_same_type(self):
        entities = [
            PIIEntity(text="a@b.com", pii_type=PIIType.EMAIL, start=0, end=7),
            PIIEntity(text="c@d.com", pii_type=PIIType.EMAIL, start=10, end=17),
            PIIEntity(text="555-1234", pii_type=PIIType.PHONE, start=20, end=28),
        ]
        result = TextResult(text="redacted", entities=entities)
        assert result.entities_by_type == {"email": 2, "phone": 1}

    def test_custom_source(self):
        result = TextResult(text="test", source="user_input")
        assert result.source == "user_input"
