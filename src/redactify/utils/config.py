"""Configuration management for Redactify."""

from dataclasses import dataclass, field
from pathlib import Path

import json


DEFAULT_CONFIG_FILE = ".redactify.json"


@dataclass
class RedactifyConfig:
    """Configuration for a redaction session."""

    mode: str = "blackout"
    detect_types: list[str] = field(default_factory=list)
    use_ner: bool = True
    custom_patterns: list[dict] = field(default_factory=list)
    output_format: str = "console"

    @classmethod
    def from_file(cls, path: Path | None = None) -> "RedactifyConfig":
        """Load config from a JSON file."""
        if path is None:
            path = Path.cwd() / DEFAULT_CONFIG_FILE

        if not path.exists():
            return cls()

        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            mode=data.get("mode", "blackout"),
            detect_types=data.get("detect_types", []),
            use_ner=data.get("use_ner", True),
            custom_patterns=data.get("custom_patterns", []),
            output_format=data.get("output_format", "console"),
        )

    def to_file(self, path: Path | None = None) -> None:
        """Save config to a JSON file."""
        if path is None:
            path = Path.cwd() / DEFAULT_CONFIG_FILE

        data = {
            "mode": self.mode,
            "detect_types": self.detect_types,
            "use_ner": self.use_ner,
            "custom_patterns": self.custom_patterns,
            "output_format": self.output_format,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
