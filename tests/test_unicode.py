"""Tests for unicode/international text handling."""

from pathlib import Path

from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode

FIXTURES = Path(__file__).parent / "fixtures"


class TestUnicodeHandling:
    def test_scan_unicode_file(self):
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(FIXTURES / "unicode_sample.txt")
        assert report.total_entities > 0
        assert "email" in report.entities_by_type

    def test_redact_unicode_preserves_characters(self, tmp_path):
        output = tmp_path / "redacted.txt"
        engine = RedactionEngine(mode=RedactionMode.LABEL, use_ner=False)
        engine.redact(FIXTURES / "unicode_sample.txt", output_path=output)
        content = output.read_text(encoding="utf-8")
        # Email should be redacted
        assert "jose.garcia@empresa.es" not in content
        assert "[EMAIL]" in content

    def test_unicode_email_detected(self):
        from redactify.detectors.regex import EmailDetector
        detector = EmailDetector()
        entities = detector.detect("Contact: user@example.com and tëst@domain.org")
        assert len(entities) >= 1
