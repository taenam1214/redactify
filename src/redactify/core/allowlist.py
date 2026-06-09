"""Allowlist for excluding known-safe strings from PII detection."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from redactify.core.detector import PIIEntity


@dataclass
class Allowlist:
    """Defines strings and patterns that should NOT be flagged as PII.

    Supports:
    - Exact string matches (case-insensitive by default)
    - Regex patterns for flexible matching
    """

    exact_strings: set[str] = field(default_factory=set)
    patterns: list[re.Pattern] = field(default_factory=list)

    def add_string(self, value: str) -> None:
        """Add an exact string to the allowlist."""
        self.exact_strings.add(value.lower())

    def add_pattern(self, pattern: str) -> None:
        """Add a regex pattern to the allowlist."""
        self.patterns.append(re.compile(pattern))

    def is_allowed(self, text: str) -> bool:
        """Check if the given text is allowlisted."""
        if text.lower() in self.exact_strings:
            return True
        return any(p.fullmatch(text) for p in self.patterns)

    def filter_entities(self, entities: list[PIIEntity]) -> list[PIIEntity]:
        """Remove allowlisted entities from a detection result."""
        return [e for e in entities if not self.is_allowed(e.text)]

    @classmethod
    def from_file(cls, path: Path) -> Allowlist:
        """Load an allowlist from a text file.

        Each line is treated as an exact match unless it starts with
        ``regex:`` in which case the remainder is compiled as a regex.
        Empty lines and lines starting with ``#`` are ignored.
        """
        allowlist = cls()
        path = Path(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("regex:"):
                allowlist.add_pattern(line[6:].strip())
            else:
                allowlist.add_string(line)
        return allowlist

    @classmethod
    def from_list(cls, items: list[str]) -> Allowlist:
        """Create an allowlist from a list of strings/patterns."""
        allowlist = cls()
        for item in items:
            if item.startswith("regex:"):
                allowlist.add_pattern(item[6:].strip())
            else:
                allowlist.add_string(item)
        return allowlist
