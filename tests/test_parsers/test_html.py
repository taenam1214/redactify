"""Tests for the HTML parser."""

import tempfile
from pathlib import Path

from redactify.parsers.html import HTMLParser, strip_html


class TestStripHTML:
    def test_strips_basic_tags(self):
        assert strip_html("<p>Hello</p>") == "Hello"

    def test_strips_nested_tags(self):
        result = strip_html("<div><p>Hello <b>world</b></p></div>")
        assert "Hello" in result
        assert "world" in result
        assert "<" not in result

    def test_normalizes_whitespace(self):
        result = strip_html("<p>Hello</p>   <p>World</p>")
        assert "  " not in result

    def test_empty_string(self):
        assert strip_html("") == ""


class TestHTMLParser:
    def setup_method(self):
        self.parser = HTMLParser()

    def test_can_handle_html(self):
        assert self.parser.can_handle(Path("page.html"))
        assert self.parser.can_handle(Path("page.htm"))

    def test_cannot_handle_txt(self):
        assert not self.parser.can_handle(Path("file.txt"))

    def test_parses_html_file(self):
        html = "<html><body><p>Email: test@example.com</p></body></html>"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html)
            path = Path(f.name)

        doc = self.parser.parse(path)
        assert "test@example.com" in doc.full_text
        assert "<" not in doc.full_text
        path.unlink()
