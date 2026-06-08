"""Tests for the module-level convenience API."""

import tempfile
from pathlib import Path

from redactify.api import (
    _get_default_engine,
    _get_regex_only_engine,
    contains_pii,
    redact,
    redact_text,
    scan,
    scan_text,
)
from redactify.core.detector import PIIType
from redactify.core.results import TextResult
from redactify.reporters.base import RedactionReport


class TestRedactText:
    def test_basic_redaction(self):
        result = redact_text("Email: john@example.com", mode="label", use_ner=False)
        assert isinstance(result, TextResult)
        assert "[EMAIL]" in result.text
        assert result.has_pii

    def test_blackout_mode(self):
        result = redact_text("Email: john@example.com", use_ner=False)
        assert "█" in result.text

    def test_no_pii(self):
        result = redact_text("Nothing here.", use_ner=False)
        assert result.text == "Nothing here."
        assert not result.has_pii


class TestScanText:
    def test_detects_email(self):
        entities = scan_text("Contact john@example.com", use_ner=False)
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.EMAIL for e in entities)

    def test_no_pii(self):
        entities = scan_text("Safe text", use_ner=False)
        assert entities == []

    def test_detect_types_filter(self):
        entities = scan_text(
            "john@example.com and 555-123-4567",
            detect_types=["email"],
            use_ner=False,
        )
        assert all(e.pii_type == PIIType.EMAIL for e in entities)


class TestContainsPii:
    def test_with_pii(self):
        assert contains_pii("Call 555-123-4567") is True

    def test_without_pii(self):
        assert contains_pii("Nothing sensitive") is False

    def test_defaults_to_no_ner(self):
        # Should still detect regex patterns without NER
        assert contains_pii("SSN: 123-45-6789") is True


class TestScanFile:
    def test_scan_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Email: john@example.com")
            f.flush()
            path = Path(f.name)

        report = scan(path, use_ner=False)
        assert isinstance(report, RedactionReport)
        assert report.total_entities >= 1
        assert "email" in report.entities_by_type
        path.unlink()

    def test_scan_file_string_path(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Phone: 555-123-4567")
            f.flush()
            path = f.name

        report = scan(path, use_ner=False)
        assert report.total_entities >= 1
        Path(path).unlink()


class TestRedactFile:
    def test_redact_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("SSN: 123-45-6789")
            f.flush()
            path = Path(f.name)

        report = redact(path, mode="label", use_ner=False)
        assert isinstance(report, RedactionReport)
        assert report.redacted
        output_path = path.parent / f"{path.stem}.redacted{path.suffix}"
        content = output_path.read_text()
        assert "[SSN]" in content
        path.unlink()
        output_path.unlink()

    def test_redact_file_custom_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Email: a@b.com")
            f.flush()
            path = Path(f.name)
        output = path.parent / "custom_output.txt"

        report = redact(path, output_path=output, use_ner=False)
        assert report.redacted
        assert output.exists()
        path.unlink()
        output.unlink()


class TestEngineCaching:
    def test_default_engine_is_cached(self):
        e1 = _get_default_engine()
        e2 = _get_default_engine()
        assert e1 is e2

    def test_regex_only_engine_is_cached(self):
        e1 = _get_regex_only_engine()
        e2 = _get_regex_only_engine()
        assert e1 is e2

    def test_default_and_regex_are_different(self):
        e1 = _get_default_engine()
        e2 = _get_regex_only_engine()
        assert e1 is not e2
