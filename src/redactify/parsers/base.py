"""Base parser interface for document parsing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DocumentChunk:
    """A chunk of text extracted from a document with metadata."""

    text: str
    page: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """A fully parsed document containing text chunks."""

    chunks: list[DocumentChunk]
    source_path: Path
    file_type: str

    @property
    def full_text(self) -> str:
        """Return all chunks concatenated as a single string."""
        return "\n".join(chunk.text for chunk in self.chunks)


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse a document and return structured text content.

        Args:
            file_path: Path to the document file.

        Returns:
            A ParsedDocument containing extracted text chunks.
        """
        ...

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file type.

        Args:
            file_path: Path to check.

        Returns:
            True if this parser supports the file type.
        """
        ...
