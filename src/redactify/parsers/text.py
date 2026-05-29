"""Plain text file parser."""

from pathlib import Path

from redactify.parsers.base import BaseParser, DocumentChunk, ParsedDocument
from redactify.utils.encoding import read_file_safe


class TextParser(BaseParser):
    """Parser for plain text files (.txt, .csv, .log, .md)."""

    SUPPORTED_EXTENSIONS = {".txt", ".csv", ".log", ".md", ".text"}

    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse a plain text file into a ParsedDocument."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        text = read_file_safe(file_path)
        chunk = DocumentChunk(text=text)

        return ParsedDocument(
            chunks=[chunk],
            source_path=file_path,
            file_type="text",
        )

    def can_handle(self, file_path: Path) -> bool:
        """Check if this parser supports the given file."""
        return Path(file_path).suffix.lower() in self.SUPPORTED_EXTENSIONS
