"""Encoding utilities for safe file reading."""

from pathlib import Path

# Common encodings to try in order
ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]


def read_file_safe(file_path: Path) -> str:
    """Read a file trying multiple encodings.

    Args:
        file_path: Path to the file to read.

    Returns:
        The file content as a string.

    Raises:
        UnicodeDecodeError: If no encoding works.
    """
    for encoding in ENCODINGS:
        try:
            return file_path.read_text(encoding=encoding)
        except (UnicodeDecodeError, ValueError):
            continue
    # Last resort: read with errors replaced
    return file_path.read_text(encoding="utf-8", errors="replace")
