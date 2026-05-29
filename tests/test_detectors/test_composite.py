"""Tests for the composite detector."""

from redactify.core.detector import PIIEntity, PIIType
from redactify.detectors.composite import CompositeDetector
from redactify.detectors.regex import EmailDetector, PhoneDetector


class TestCompositeDetector:
    def test_combines_multiple_detectors(self):
        composite = CompositeDetector([EmailDetector(), PhoneDetector()])
        text = "Email john@test.com or call 555-123-4567"
        entities = composite.detect(text)
        types = {e.pii_type for e in entities}
        assert PIIType.EMAIL in types
        assert PIIType.PHONE in types

    def test_deduplicates_overlapping_entities(self):
        entities = [
            PIIEntity(text="John Smith", pii_type=PIIType.PERSON, start=0, end=10, confidence=0.9),
            PIIEntity(text="John Smith", pii_type=PIIType.PERSON, start=0, end=10, confidence=0.7),
        ]
        result = CompositeDetector._deduplicate(entities)
        assert len(result) == 1
        assert result[0].confidence == 0.9

    def test_keeps_non_overlapping_entities(self):
        entities = [
            PIIEntity(text="John", pii_type=PIIType.PERSON, start=0, end=4, confidence=0.9),
            PIIEntity(text="Smith", pii_type=PIIType.PERSON, start=5, end=10, confidence=0.9),
        ]
        result = CompositeDetector._deduplicate(entities)
        assert len(result) == 2

    def test_supported_types_aggregates(self):
        composite = CompositeDetector([EmailDetector(), PhoneDetector()])
        types = composite.supported_types
        assert PIIType.EMAIL in types
        assert PIIType.PHONE in types

    def test_empty_text(self):
        composite = CompositeDetector([EmailDetector()])
        entities = composite.detect("")
        assert entities == []
