"""Tests for the PDF parser."""

import pytest

from redactify.core.detector import PIIType

try:
    from redactify.parsers.pdf import PDFParser
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


@pytest.mark.skipif(not HAS_PDF, reason="PyMuPDF not installed")
class TestPDFParser:
    def setup_method(self):
        self.parser = PDFParser()

    def test_supported_extensions(self):
        from pathlib import Path
        assert self.parser.can_handle(Path("test.pdf"))
        assert not self.parser.can_handle(Path("test.txt"))


@pytest.mark.skipif(not HAS_PDF, reason="PyMuPDF not installed")
class TestPDFIntegration:
    def test_scan_pdf_with_engine(self, tmp_path):
        """Create a simple PDF with PII and scan it."""
        try:
            import fitz
        except ImportError:
            pytest.skip("PyMuPDF not installed")

        from redactify.core.engine import RedactionEngine

        pdf_path = tmp_path / "test.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Contact john@example.com for info.")
        doc.save(str(pdf_path))
        doc.close()

        engine = RedactionEngine(use_ner=False)
        report = engine.scan(pdf_path)
        assert report.total_entities >= 1
        assert "email" in report.entities_by_type
