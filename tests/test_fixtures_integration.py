"""Integration tests using fixture files."""

from pathlib import Path

from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode

FIXTURES = Path(__file__).parent / "fixtures"


class TestFixtureIntegration:
    def test_sample_email_detects_all_types(self):
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(FIXTURES / "sample_email.txt")
        assert report.total_entities > 0
        assert "email" in report.entities_by_type
        assert "phone" in report.entities_by_type
        assert "ssn" in report.entities_by_type
        assert "ip_address" in report.entities_by_type

    def test_no_pii_file_clean(self):
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(FIXTURES / "no_pii.txt")
        assert report.total_entities == 0

    def test_multi_pii_detects_many(self):
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(FIXTURES / "multi_pii.txt")
        assert report.total_entities >= 5
        assert "email" in report.entities_by_type
        assert "phone" in report.entities_by_type

    def test_redact_produces_output_file(self, tmp_path):
        output = tmp_path / "redacted.txt"
        engine = RedactionEngine(mode=RedactionMode.LABEL, use_ner=False)
        engine.redact(FIXTURES / "sample_email.txt", output_path=output)
        assert output.exists()
        content = output.read_text()
        assert "john.smith@example.com" not in content
        assert "[EMAIL]" in content

    def test_redact_blackout_removes_pii(self, tmp_path):
        output = tmp_path / "redacted.txt"
        engine = RedactionEngine(mode=RedactionMode.BLACKOUT, use_ner=False)
        engine.redact(FIXTURES / "sample_email.txt", output_path=output)
        content = output.read_text()
        assert "john.smith@example.com" not in content
        assert "123-45-6789" not in content
        assert "█" in content

    def test_hash_mode_preserves_referential_integrity(self, tmp_path):
        output = tmp_path / "redacted.txt"
        engine = RedactionEngine(mode=RedactionMode.HASH, use_ner=False)
        engine.redact(FIXTURES / "multi_pii.txt", output_path=output)
        content = output.read_text()
        assert "[REDACTED-" in content
