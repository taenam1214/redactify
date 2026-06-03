"""Tests for streaming file processor."""

from pathlib import Path

from redactify.core.streaming import iter_line_chunks, stream_redact, stream_scan
from redactify.core.redactor import Redactor, RedactionMode
from redactify.detectors.composite import CompositeDetector
from redactify.detectors.regex import EmailDetector, PhoneDetector


class TestIterLineChunks:
    """Tests for line-based chunked reading."""

    def test_small_file_single_chunk(self, tmp_path):
        f = tmp_path / "small.txt"
        f.write_text("line1\nline2\nline3\n")
        chunks = list(iter_line_chunks(f, chunk_lines=10))
        assert len(chunks) == 1
        assert chunks[0] == "line1\nline2\nline3\n"

    def test_exact_chunk_boundary(self, tmp_path):
        f = tmp_path / "exact.txt"
        f.write_text("a\nb\nc\nd\n")
        chunks = list(iter_line_chunks(f, chunk_lines=2))
        assert len(chunks) == 2
        assert chunks[0] == "a\nb\n"
        assert chunks[1] == "c\nd\n"

    def test_uneven_chunks(self, tmp_path):
        f = tmp_path / "uneven.txt"
        f.write_text("a\nb\nc\n")
        chunks = list(iter_line_chunks(f, chunk_lines=2))
        assert len(chunks) == 2
        assert chunks[0] == "a\nb\n"
        assert chunks[1] == "c\n"

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        chunks = list(iter_line_chunks(f, chunk_lines=5))
        assert len(chunks) == 0


class TestStreamScan:
    """Tests for streaming scan."""

    def test_detects_pii_across_chunks(self, tmp_path):
        f = tmp_path / "multi.txt"
        content = "Email: test@example.com\n" * 5 + "Phone: (555) 123-4567\n"
        f.write_text(content)

        detector = CompositeDetector()
        detector.add_detector(EmailDetector())
        detector.add_detector(PhoneDetector())

        entities = stream_scan(f, detector, chunk_lines=2)
        emails = [e for e in entities if e.pii_type.value == "email"]
        phones = [e for e in entities if e.pii_type.value == "phone"]
        assert len(emails) == 5
        assert len(phones) == 1

    def test_respects_confidence_threshold(self, tmp_path):
        f = tmp_path / "conf.txt"
        f.write_text("Email: user@test.com\n")

        detector = CompositeDetector()
        detector.add_detector(EmailDetector())

        # Email detector has confidence 1.0, so threshold 0.9 keeps it
        entities = stream_scan(f, detector, confidence_threshold=0.9)
        assert len(entities) == 1

        # Threshold above 1.0 should filter everything
        entities = stream_scan(f, detector, confidence_threshold=1.1)
        assert len(entities) == 0


class TestStreamRedact:
    """Tests for streaming redact."""

    def test_redacts_and_writes_output(self, tmp_path):
        f = tmp_path / "input.txt"
        f.write_text("Contact: user@example.com\nPhone: (555) 999-0000\n")
        output = tmp_path / "output.txt"

        detector = CompositeDetector()
        detector.add_detector(EmailDetector())
        detector.add_detector(PhoneDetector())
        redactor = Redactor(mode=RedactionMode.LABEL)

        entities = stream_redact(f, output, detector, redactor, chunk_lines=1)
        assert len(entities) == 2
        assert output.exists()

        result = output.read_text()
        assert "[EMAIL]" in result
        assert "[PHONE]" in result
        assert "user@example.com" not in result

    def test_preserves_non_pii_content(self, tmp_path):
        f = tmp_path / "safe.txt"
        f.write_text("Hello world\nNo PII here\n")
        output = tmp_path / "safe_out.txt"

        detector = CompositeDetector()
        detector.add_detector(EmailDetector())
        redactor = Redactor(mode=RedactionMode.LABEL)

        entities = stream_redact(f, output, detector, redactor)
        assert len(entities) == 0
        assert output.read_text() == "Hello world\nNo PII here\n"
