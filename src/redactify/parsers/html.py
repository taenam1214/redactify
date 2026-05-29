"""HTML parser — strips tags and extracts text content."""

import re
from pathlib import Path

from redactify.parsers.base import BaseParser, DocumentChunk, ParsedDocument
from redactify.utils.encoding import read_file_safe

# Simple HTML tag stripper (no external dependency)
TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


def strip_html(html: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = TAG_PATTERN.sub(" ", html)
    text = WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


class HTMLParser(BaseParser):
    """Parser for HTML files — strips tags and extracts text."""

    SUPPORTED_EXTENSIONS = {".html", ".htm"}

    def parse(self, file_path: Path) -> ParsedDocument:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        raw_html = read_file_safe(file_path)
        text = strip_html(raw_html)
        chunk = DocumentChunk(text=text)

        return ParsedDocument(
            chunks=[chunk],
            source_path=file_path,
            file_type="html",
        )

    def can_handle(self, file_path: Path) -> bool:
        return Path(file_path).suffix.lower() in self.SUPPORTED_EXTENSIONS
