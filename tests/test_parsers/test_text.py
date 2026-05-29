"""Tests for the plain text parser."""

from pathlib import Path
import tempfile

import pytest

from redactify.parsers.text import TextParser


class TestTextParser:
    def setup_method(self):
        self.parser = TextParser()

    def test_can_handle_txt(self):
        assert self.parser.can_handle(Path("file.txt"))

    def test_can_handle_csv(self):
        assert self.parser.can_handle(Path("data.csv"))

    def test_can_handle_md(self):
        assert self.parser.can_handle(Path("README.md"))

    def test_cannot_handle_pdf(self):
        assert not self.parser.can_handle(Path("doc.pdf"))

    def test_cannot_handle_docx(self):
        assert not self.parser.can_handle(Path("doc.docx"))

    def test_parses_text_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Hello, my email is test@example.com")
            f.flush()
            path = Path(f.name)

        doc = self.parser.parse(path)
        assert len(doc.chunks) == 1
        assert "test@example.com" in doc.full_text
        assert doc.file_type == "text"
        path.unlink()

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            self.parser.parse(Path("/nonexistent/file.txt"))
