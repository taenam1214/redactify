"""Custom exceptions for Redactify."""


class RedactifyError(Exception):
    """Base exception for all Redactify errors."""


class ParserError(RedactifyError):
    """Raised when document parsing fails."""


class DetectorError(RedactifyError):
    """Raised when PII detection fails."""


class UnsupportedFileTypeError(RedactifyError):
    """Raised when no parser is available for a file type."""

    def __init__(self, file_path):
        super().__init__(f"No parser available for file: {file_path}")
        self.file_path = file_path
