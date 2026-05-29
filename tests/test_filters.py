"""Tests for entity filters."""

from redactify.core.detector import PIIEntity, PIIType
from redactify.core.filters import filter_by_confidence, filter_by_min_length, filter_by_type


class TestFilterByConfidence:
    def test_filters_below_threshold(self):
        entities = [
            PIIEntity(text="John", pii_type=PIIType.PERSON, start=0, end=4, confidence=0.9),
            PIIEntity(text="maybe", pii_type=PIIType.PERSON, start=5, end=10, confidence=0.3),
        ]
        result = filter_by_confidence(entities, threshold=0.5)
        assert len(result) == 1
        assert result[0].text == "John"

    def test_default_threshold(self):
        entities = [
            PIIEntity(text="a", pii_type=PIIType.PERSON, start=0, end=1, confidence=0.5),
            PIIEntity(text="b", pii_type=PIIType.PERSON, start=2, end=3, confidence=0.4),
        ]
        result = filter_by_confidence(entities)
        assert len(result) == 1


class TestFilterByType:
    def test_filters_by_type(self):
        entities = [
            PIIEntity(text="test@a.com", pii_type=PIIType.EMAIL, start=0, end=10),
            PIIEntity(text="555-1234", pii_type=PIIType.PHONE, start=11, end=19),
            PIIEntity(text="John", pii_type=PIIType.PERSON, start=20, end=24),
        ]
        result = filter_by_type(entities, [PIIType.EMAIL, PIIType.PHONE])
        assert len(result) == 2
        assert all(e.pii_type in (PIIType.EMAIL, PIIType.PHONE) for e in result)


class TestFilterByMinLength:
    def test_filters_short_entities(self):
        entities = [
            PIIEntity(text="Jo", pii_type=PIIType.PERSON, start=0, end=2),
            PIIEntity(text="John Smith", pii_type=PIIType.PERSON, start=3, end=13),
        ]
        result = filter_by_min_length(entities, min_length=3)
        assert len(result) == 1
        assert result[0].text == "John Smith"
