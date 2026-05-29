"""Custom pattern detector — user-defined regex patterns."""

import re

from redactify.core.detector import BaseDetector, PIIEntity, PIIType


class CustomPatternDetector(BaseDetector):
    """Detects PII using user-defined regex patterns."""

    def __init__(self, patterns: list[dict] | None = None):
        """Initialize with custom patterns.

        Args:
            patterns: List of dicts with 'name' and 'pattern' keys.
                      Example: [{"name": "order_id", "pattern": r"ORD-\\d+"}]
        """
        self._patterns: list[tuple[str, re.Pattern]] = []
        if patterns:
            for p in patterns:
                name = p.get("name", "custom")
                regex = p.get("pattern", "")
                if regex:
                    self._patterns.append((name, re.compile(regex)))

    def add_pattern(self, name: str, pattern: str) -> None:
        """Add a custom regex pattern."""
        self._patterns.append((name, re.compile(pattern)))

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for name, pattern in self._patterns:
            for match in pattern.finditer(text):
                entities.append(
                    PIIEntity(
                        text=match.group(),
                        pii_type=PIIType.CUSTOM,
                        start=match.start(),
                        end=match.end(),
                        confidence=1.0,
                    )
                )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.CUSTOM]
