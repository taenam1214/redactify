"""Tests for encoding utilities."""

import tempfile
from pathlib import Path

from redactify.utils.encoding import read_file_safe


class TestReadFileSafe:
    def test_reads_utf8(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("Hello, world! Email: test@test.com")
            path = Path(f.name)
        content = read_file_safe(path)
        assert "test@test.com" in content
        path.unlink()

    def test_reads_latin1(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            f.write("Café résumé naïve".encode("latin-1"))
            path = Path(f.name)
        content = read_file_safe(path)
        assert "Caf" in content
        path.unlink()

    def test_reads_utf8_bom(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            f.write(b"\xef\xbb\xbfHello BOM")
            path = Path(f.name)
        content = read_file_safe(path)
        assert "Hello BOM" in content
        path.unlink()
