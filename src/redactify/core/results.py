"""Result types for in-memory text operations."""

from dataclasses import dataclass, field

from redactify.core.detector import PIIEntity


@dataclass
class TextResult:
    """Result of a text redaction or scan operation.

    Unlike RedactionReport (which requires a source file path), TextResult
    is designed for in-memory string operations.
    """

    text: str
    entities: list[PIIEntity] = field(default_factory=list)
    source: str = "<string>"

    @property
    def total_entities(self) -> int:
        """Total number of detected entities."""
        return len(self.entities)

    @property
    def entities_by_type(self) -> dict[str, int]:
        """Count of entities grouped by PII type."""
        counts: dict[str, int] = {}
        for entity in self.entities:
            key = entity.pii_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    @property
    def has_pii(self) -> bool:
        """Whether any PII was detected."""
        return len(self.entities) > 0
