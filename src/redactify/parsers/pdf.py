"""PDF parser using PyMuPDF."""

from pathlib import Path

from redactify.parsers.base import BaseParser, DocumentChunk, ParsedDocument


class PDFParser(BaseParser):
    """Parser for PDF files using PyMuPDF (fitz)."""

    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse a PDF file, extracting text from each page."""
        try:
            import fitz
        except ImportError:
            raise ImportError(
                "PyMuPDF is required for PDF support. "
                "Install it with: pip install redactify[pdf]"
            )

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        doc = fitz.open(file_path)
        chunks = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                chunks.append(
                    DocumentChunk(
                        text=text,
                        page=page_num + 1,
                        metadata={"width": page.rect.width, "height": page.rect.height},
                    )
                )

        doc.close()

        return ParsedDocument(
            chunks=chunks,
            source_path=file_path,
            file_type="pdf",
        )

    def can_handle(self, file_path: Path) -> bool:
        return Path(file_path).suffix.lower() == ".pdf"
