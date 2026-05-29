"""Tests for the redaction engine."""

import tempfile
from pathlib import Path

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
        report = engine.redact(path)
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
