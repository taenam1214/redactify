"""Property-based tests using Hypothesis."""

import pytest

try:
    from hypothesis import given, strategies as st, settings, assume
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

from redactify.core.detector import PIIType
from redactify.core.redactor import RedactionMode, Redactor
from redactify.detectors.regex import EmailDetector, PhoneDetector, SSNDetector


pytestmark = pytest.mark.skipif(not HAS_HYPOTHESIS, reason="hypothesis not installed")


class TestEmailDetectorProperties:
    def setup_method(self):
        self.detector = EmailDetector()

    @given(
        local=st.from_regex(r"[a-z][a-z0-9._%+]{1,20}", fullmatch=True),
        domain=st.from_regex(r"[a-z]{2,10}\.[a-z]{2,4}", fullmatch=True),
    )
    @settings(max_examples=50)
    def test_valid_emails_are_detected(self, local, domain):
        """Any string matching email format should be detected."""
        email = f"{local}@{domain}"
        entities = self.detector.detect(f"contact {email} now")
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.EMAIL for e in entities)


class TestRedactorProperties:
    @given(text=st.text(min_size=1, max_size=200))
    @settings(max_examples=50)
    def test_redact_with_no_entities_is_identity(self, text):
        """Redacting with no entities should return original text."""
        redactor = Redactor(mode=RedactionMode.LABEL)
        result = redactor.redact(text, [])
        assert result == text

    @given(text=st.text(min_size=1, max_size=200))
    @settings(max_examples=50)
    def test_redact_with_no_entities_blackout_is_identity(self, text):
        """Blackout redaction with no entities should return original text."""
        redactor = Redactor(mode=RedactionMode.BLACKOUT)
        result = redactor.redact(text, [])
        assert result == text


class TestScanRedactConsistency:
    @given(text=st.text(min_size=5, max_size=500, alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z"))))
    @settings(max_examples=30)
    def test_scan_and_redact_find_same_entity_count(self, text):
        """scan_text and redact_text should find the same number of entities."""
        from redactify.core.engine import RedactionEngine
        engine = RedactionEngine(use_ner=False)
        scan_entities = engine.scan_text(text)
        redact_result = engine.redact_text(text)
        assert len(scan_entities) == redact_result.total_entities
