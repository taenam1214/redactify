"""Tests for the NER detector (requires spaCy model)."""

import pytest

from redactify.core.detector import PIIType

try:
    import spacy
    spacy.load("en_core_web_sm")
    HAS_SPACY = True
except (ImportError, OSError):
    HAS_SPACY = False


@pytest.mark.skipif(not HAS_SPACY, reason="spaCy model not available")
class TestNERDetector:
    def setup_method(self):
        from redactify.detectors.ner import NERDetector
        self.detector = NERDetector()

    def test_detects_person_name(self):
        entities = self.detector.detect("John Smith went to the store.")
        names = [e for e in entities if e.pii_type == PIIType.PERSON]
        assert len(names) >= 1
        assert any("John" in e.text for e in names)

    def test_detects_organization(self):
        entities = self.detector.detect("She works at Google in Mountain View.")
        orgs = [e for e in entities if e.pii_type == PIIType.ORGANIZATION]
        assert len(orgs) >= 1

    def test_detects_location(self):
        entities = self.detector.detect("He traveled to New York last summer.")
        locs = [e for e in entities if e.pii_type == PIIType.LOCATION]
        assert len(locs) >= 1

    def test_empty_text(self):
        entities = self.detector.detect("")
        assert entities == []

    def test_no_entities_in_plain_text(self):
        entities = self.detector.detect("The quick brown fox jumps over the lazy dog.")
        # May or may not find entities, but should not crash
        assert isinstance(entities, list)

    def test_confidence_is_set(self):
        entities = self.detector.detect("Barack Obama was the president.")
        if entities:
            assert all(0 < e.confidence <= 1.0 for e in entities)

    def test_supported_types(self):
        types = self.detector.supported_types
        assert PIIType.PERSON in types
        assert PIIType.ORGANIZATION in types
        assert PIIType.LOCATION in types


class TestNERDetectorMissingModel:
    def test_raises_on_invalid_model(self):
        from redactify.detectors.ner import NERDetector
        detector = NERDetector(model_name="nonexistent_model_xyz")
        with pytest.raises(RuntimeError, match="not found"):
            detector.detect("Hello world")
