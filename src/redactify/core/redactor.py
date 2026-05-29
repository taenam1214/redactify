"""Redactor module — applies redaction strategies to text."""

from enum import Enum
import hashlib

from redactify.core.detector import PIIEntity


class RedactionMode(Enum):
    """Available redaction strategies."""

    BLACKOUT = "blackout"
    LABEL = "label"
    HASH = "hash"
    CUSTOM = "custom"


def _blackout(entity: PIIEntity) -> str:
    return "█" * len(entity.text)


def _label(entity: PIIEntity) -> str:
    return f"[{entity.pii_type.value.upper()}]"


def _hash_replace(entity: PIIEntity) -> str:
    digest = hashlib.sha256(entity.text.encode()).hexdigest()[:12]
    return f"[REDACTED-{digest}]"


class Redactor:
    """Applies redaction to text based on detected PII entities."""

    def __init__(self, mode: RedactionMode = RedactionMode.BLACKOUT, custom_string: str = "[REDACTED]"):
        self.mode = mode
        self.custom_string = custom_string

    def get_replacement(self, entity: PIIEntity) -> str:
        """Get the replacement string for a given PII entity."""
        if self.mode == RedactionMode.BLACKOUT:
            return _blackout(entity)
        elif self.mode == RedactionMode.LABEL:
            return _label(entity)
        elif self.mode == RedactionMode.HASH:
            return _hash_replace(entity)
        elif self.mode == RedactionMode.CUSTOM:
            return self.custom_string
        raise ValueError(f"Unknown redaction mode: {self.mode}")

    def redact(self, text: str, entities: list[PIIEntity]) -> str:
        """Redact all detected PII entities from the text.

        Entities are processed in reverse order to preserve character positions.

        Args:
            text: Original text.
            entities: List of detected PII entities.

        Returns:
            Redacted text.
        """
        sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
        result = text
        for entity in sorted_entities:
            replacement = self.get_replacement(entity)
            result = result[:entity.start] + replacement + result[entity.end:]
        return result
