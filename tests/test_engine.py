"""Tests for the redaction engine."""

import tempfile
from pathlib import Path

import pytest

from redactify.core.detector import PIIType
from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode


class TestRedactionEngine:
    def _create_temp_file(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        f.write(content)
        f.flush()
        f.close()
        return Path(f.name)

    def test_scan_detects_email(self):
        path = self._create_temp_file("Contact john@example.com for info.")
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(path)
        assert report.total_entities >= 1
        assert "email" in report.entities_by_type
        assert not report.redacted
        path.unlink()

    def test_scan_detects_phone(self):
        path = self._create_temp_file("Call us at 555-123-4567.")
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(path)
        assert report.total_entities >= 1
        assert "phone" in report.entities_by_type
        path.unlink()

    def test_redact_blackout_mode(self):
        path = self._create_temp_file("Email: john@example.com")
        engine = RedactionEngine(mode=RedactionMode.BLACKOUT, use_ner=False)
        report = engine.redact(path)
        assert report.redacted
        output_path = path.parent / f"{path.stem}.redacted{path.suffix}"
        content = output_path.read_text()
        assert "john@example.com" not in content
        assert "█" in content
        path.unlink()
        output_path.unlink()

    def test_redact_label_mode(self):
        path = self._create_temp_file("Email: john@example.com")
        engine = RedactionEngine(mode=RedactionMode.LABEL, use_ner=False)
        engine.redact(path)
        output_path = path.parent / f"{path.stem}.redacted{path.suffix}"
        content = output_path.read_text()
        assert "[EMAIL]" in content
        path.unlink()
        output_path.unlink()

    def test_redact_custom_output_path(self):
        path = self._create_temp_file("SSN: 123-45-6789")
        output = path.parent / "output.txt"
        engine = RedactionEngine(use_ner=False)
        engine.redact(path, output_path=output)
        assert output.exists()
        content = output.read_text()
        assert "123-45-6789" not in content
        path.unlink()
        output.unlink()

    def test_scan_no_pii(self):
        path = self._create_temp_file("This is a perfectly safe sentence.")
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(path)
        assert report.total_entities == 0
        path.unlink()


class TestStringArgCoercion:
    """Test that string arguments are properly coerced to enums."""

    def test_mode_as_string(self):
        engine = RedactionEngine(mode="label", use_ner=False)
        assert engine.redactor.mode == RedactionMode.LABEL

    def test_mode_as_string_case_insensitive(self):
        engine = RedactionEngine(mode="BLACKOUT", use_ner=False)
        assert engine.redactor.mode == RedactionMode.BLACKOUT

    def test_mode_as_enum_still_works(self):
        engine = RedactionEngine(mode=RedactionMode.HASH, use_ner=False)
        assert engine.redactor.mode == RedactionMode.HASH

    def test_invalid_mode_string_raises(self):
        with pytest.raises(ValueError):
            RedactionEngine(mode="invalid", use_ner=False)

    def test_detect_types_as_strings(self):
        engine = RedactionEngine(detect_types=["email", "phone"], use_ner=False)
        supported = engine.detector.supported_types
        assert PIIType.EMAIL in supported
        assert PIIType.PHONE in supported

    def test_detect_types_mixed(self):
        engine = RedactionEngine(detect_types=[PIIType.EMAIL, "phone"], use_ner=False)
        supported = engine.detector.supported_types
        assert PIIType.EMAIL in supported
        assert PIIType.PHONE in supported

    def test_detect_types_case_insensitive(self):
        engine = RedactionEngine(detect_types=["EMAIL", "SSN"], use_ner=False)
        supported = engine.detector.supported_types
        assert PIIType.EMAIL in supported
        assert PIIType.SSN in supported

    def test_invalid_detect_type_string_raises(self):
        with pytest.raises(ValueError):
            RedactionEngine(detect_types=["not_a_type"], use_ner=False)


class TestScanText:
    """Tests for the in-memory scan_text method."""

    def test_scan_text_detects_email(self):
        engine = RedactionEngine(use_ner=False)
        entities = engine.scan_text("Contact john@example.com for info.")
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.EMAIL for e in entities)

    def test_scan_text_detects_phone(self):
        engine = RedactionEngine(use_ner=False)
        entities = engine.scan_text("Call us at 555-123-4567.")
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.PHONE for e in entities)

    def test_scan_text_no_pii(self):
        engine = RedactionEngine(use_ner=False)
        entities = engine.scan_text("This is a perfectly safe sentence.")
        assert entities == []

    def test_scan_text_respects_confidence_threshold(self):
        engine = RedactionEngine(use_ner=False, confidence_threshold=0.99)
        # Regex detectors have confidence=1.0, so they should still pass
        entities = engine.scan_text("Email: john@example.com")
        assert len(entities) >= 1
