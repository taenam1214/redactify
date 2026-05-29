"""Base reporter interface for redaction reports."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from redactify.core.detector import PIIEntity


@dataclass
class RedactionReport:
    """Summary of a redaction operation."""

    source_file: Path
    total_entities: int
    entities_by_type: dict[str, int] = field(default_factory=dict)
    entities: list[PIIEntity] = field(default_factory=list)
    redacted: bool = False


class BaseReporter(ABC):
    """Abstract base class for redaction reporters."""

    @abstractmethod
    def report(self, result: RedactionReport) -> str:
        """Generate a report from the redaction result.

        Args:
            result: The redaction report data.

        Returns:
            Formatted report string.
        """
        ...
