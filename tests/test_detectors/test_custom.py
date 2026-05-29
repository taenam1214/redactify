"""Tests for the custom pattern detector."""

from redactify.core.detector import PIIType
from redactify.detectors.custom import CustomPatternDetector


class TestCustomPatternDetector:
    def test_detects_custom_pattern(self):
        detector = CustomPatternDetector([{"name": "order_id", "pattern": r"ORD-\d+"}])
        entities = detector.detect("Your order ORD-12345 is ready.")
        assert len(entities) == 1
        assert entities[0].text == "ORD-12345"
        assert entities[0].pii_type == PIIType.CUSTOM

    def test_multiple_patterns(self):
        patterns = [
            {"name": "order_id", "pattern": r"ORD-\d+"},
            {"name": "ticket_id", "pattern": r"TICK-\d+"},
        ]
        detector = CustomPatternDetector(patterns)
        text = "Order ORD-100, ticket TICK-200"
        entities = detector.detect(text)
        assert len(entities) == 2

    def test_add_pattern_dynamically(self):
        detector = CustomPatternDetector()
        detector.add_pattern("medical_id", r"MRN-\d{6}")
        entities = detector.detect("Patient MRN-123456 admitted.")
        assert len(entities) == 1
        assert entities[0].text == "MRN-123456"

    def test_no_match_returns_empty(self):
        detector = CustomPatternDetector([{"name": "test", "pattern": r"XYZ-\d+"}])
        entities = detector.detect("Nothing here.")
        assert entities == []

    def test_empty_patterns_list(self):
        detector = CustomPatternDetector([])
        entities = detector.detect("Some text")
        assert entities == []

    def test_invalid_pattern_key_skipped(self):
        detector = CustomPatternDetector([{"name": "bad", "pattern": ""}])
        entities = detector.detect("Some text")
        assert entities == []
