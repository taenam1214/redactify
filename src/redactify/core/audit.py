"""Redaction audit trail — records what was redacted without revealing PII."""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from redactify.core.detector import PIIEntity


@dataclass
class AuditEntry:
    """A single redaction event in the audit trail."""

    pii_type: str
    start: int
    end: int
    length: int
    confidence: float
    redaction_mode: str
    content_hash: str  # SHA-256 of the original PII (for dedup, not reversal)

    @classmethod
    def from_entity(cls, entity: PIIEntity, redaction_mode: str) -> "AuditEntry":
        """Create an audit entry from a PIIEntity."""
        content_hash = hashlib.sha256(entity.text.encode("utf-8")).hexdigest()[:16]
        return cls(
            pii_type=entity.pii_type.value,
            start=entity.start,
            end=entity.end,
            length=entity.end - entity.start,
            confidence=entity.confidence,
            redaction_mode=redaction_mode,
            content_hash=content_hash,
        )


@dataclass
class AuditTrail:
    """Complete audit trail for a redaction operation."""

    source_file: str
    timestamp: str
    total_redactions: int
    redaction_mode: str
    entries: list[AuditEntry] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        source_file: Path,
        entities: list[PIIEntity],
        redaction_mode: str,
    ) -> "AuditTrail":
        """Build an audit trail from a list of detected entities."""
        entries = [AuditEntry.from_entity(e, redaction_mode) for e in entities]

        summary: dict[str, int] = {}
        for entity in entities:
            key = entity.pii_type.value
            summary[key] = summary.get(key, 0) + 1

        return cls(
            source_file=str(source_file),
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_redactions=len(entities),
            redaction_mode=redaction_mode,
            entries=entries,
            summary=summary,
        )

    def to_dict(self) -> dict:
        """Convert audit trail to a dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize audit trail to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def write(self, output_path: Path) -> None:
        """Write audit trail to a JSON file."""
        output_path = Path(output_path)
        output_path.write_text(self.to_json(), encoding="utf-8")
