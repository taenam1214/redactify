"""Tests for batch directory processing."""

from pathlib import Path

import pytest

from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode
from redactify.exceptions import UnsupportedFileTypeError

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
        with pytest.raises(NotADirectoryError):
            engine.scan_directory(Path("/nonexistent/dir"))

    def test_unsupported_file_raises(self):
        engine = RedactionEngine(use_ner=False)
        with pytest.raises(UnsupportedFileTypeError):
            engine.scan(Path("/tmp/file.unsupported"))


class TestParallelBatch:
    """Tests for the workers parameter."""

    def test_scan_directory_parallel(self, tmp_path):
        for i in range(4):
            (tmp_path / f"f{i}.txt").write_text(f"user{i}@example.com")
        engine = RedactionEngine(use_ner=False)
        reports = engine.scan_directory(tmp_path, workers=2)
        assert len(reports) == 4
        for r in reports:
            assert r.total_entities >= 1

    def test_redact_directory_parallel(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        for i in range(3):
            (src / f"f{i}.txt").write_text(f"SSN: 123-45-678{i}")
        out = tmp_path / "out"
        engine = RedactionEngine(use_ner=False)
        reports = engine.redact_directory(src, output_dir=out, workers=2)
        assert len(reports) == 3
        assert all(r.redacted for r in reports)

    def test_parallel_matches_sequential(self, tmp_path):
        for i in range(4):
            (tmp_path / f"f{i}.txt").write_text(f"user{i}@test.com and 555-{i}23-4567")
        engine = RedactionEngine(use_ner=False)
        seq = engine.scan_directory(tmp_path, workers=1)
        par = engine.scan_directory(tmp_path, workers=3)
        seq_counts = sorted(r.total_entities for r in seq)
        par_counts = sorted(r.total_entities for r in par)
        assert seq_counts == par_counts
