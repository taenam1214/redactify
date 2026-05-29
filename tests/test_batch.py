"""Tests for batch directory processing."""

from pathlib import Path

from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode

FIXTURES = Path(__file__).parent / "fixtures"


class TestBatchProcessing:
    def test_scan_directory(self):
        engine = RedactionEngine(use_ner=False)
        reports = engine.scan_directory(FIXTURES)
        assert len(reports) >= 2  # At least sample_email.txt and multi_pii.txt

    def test_redact_directory(self, tmp_path):
        engine = RedactionEngine(mode=RedactionMode.LABEL, use_ner=False)
        reports = engine.redact_directory(FIXTURES, output_dir=tmp_path)
        assert len(reports) >= 2
        # Check output files exist
        for report in reports:
            out_file = tmp_path / report.source_file.name
            assert out_file.exists()

    def test_redact_directory_creates_output_dir(self, tmp_path):
        output = tmp_path / "subdir" / "output"
        engine = RedactionEngine(use_ner=False)
        engine.redact_directory(FIXTURES, output_dir=output)
        assert output.is_dir()

    def test_skips_unsupported_files(self, tmp_path):
        # Create a directory with a mix of supported and unsupported files
        (tmp_path / "good.txt").write_text("Email: test@example.com")
        (tmp_path / "bad.xyz").write_text("Unsupported format")
        output = tmp_path / "out"
        engine = RedactionEngine(use_ner=False)
        reports = engine.redact_directory(tmp_path, output_dir=output)
        filenames = [r.source_file.name for r in reports]
        assert "good.txt" in filenames
        assert "bad.xyz" not in filenames

    def test_scan_directory_invalid_path(self):
        engine = RedactionEngine(use_ner=False)
        try:
            engine.scan_directory(Path("/nonexistent/dir"))
            assert False, "Should have raised"
        except NotADirectoryError:
            pass
