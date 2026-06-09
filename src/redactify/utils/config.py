"""Configuration management for Redactify."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import json


DEFAULT_CONFIG_FILE = ".redactify.json"
YAML_EXTENSIONS = {".yml", ".yaml"}


@dataclass
class RedactifyConfig:
    """Configuration for a redaction session."""

    mode: str = "blackout"
    detect_types: list[str] = field(default_factory=list)
    use_ner: bool = True
    custom_patterns: list[dict] = field(default_factory=list)
    output_format: str = "console"
    allowlist: list[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path | None = None) -> RedactifyConfig:
        """Load config from a JSON or YAML file.

        Auto-detects format from file extension. If no path is provided,
        searches for .redactify.json, .redactify.yml, .redactify.yaml
        in the current directory.
        """
        if path is None:
            path = cls._find_config_file()

        if path is None or not path.exists():
            return cls()

        content = path.read_text(encoding="utf-8")

        if path.suffix in YAML_EXTENSIONS:
            data = cls._parse_yaml(content)
        else:
            data = json.loads(content)

        return cls(
            mode=data.get("mode", "blackout"),
            detect_types=data.get("detect_types", []),
            use_ner=data.get("use_ner", True),
            custom_patterns=data.get("custom_patterns", []),
            output_format=data.get("output_format", "console"),
            allowlist=data.get("allowlist", []),
        )

    @staticmethod
    def _find_config_file() -> Path | None:
        """Search for config file in current directory."""
        cwd = Path.cwd()
        candidates = [
            cwd / ".redactify.json",
            cwd / ".redactify.yml",
            cwd / ".redactify.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return cwd / DEFAULT_CONFIG_FILE

    @staticmethod
    def _parse_yaml(content: str) -> dict:
        """Parse YAML content, raising ImportError if pyyaml not installed."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "pyyaml is required for YAML config files. "
                "Install it with: pip install redactify[yaml]"
            )
        return yaml.safe_load(content) or {}

    def to_file(self, path: Path | None = None, fmt: str = "json") -> None:
        """Save config to a JSON or YAML file.

        Args:
            path: Output path. Defaults based on format.
            fmt: Format — "json" or "yaml".
        """
        if path is None:
            if fmt == "yaml":
                path = Path.cwd() / ".redactify.yml"
            else:
                path = Path.cwd() / DEFAULT_CONFIG_FILE

        data = {
            "mode": self.mode,
            "detect_types": self.detect_types,
            "use_ner": self.use_ner,
            "custom_patterns": self.custom_patterns,
            "output_format": self.output_format,
            "allowlist": self.allowlist,
        }

        if path.suffix in YAML_EXTENSIONS or fmt == "yaml":
            try:
                import yaml
            except ImportError:
                raise ImportError(
                    "pyyaml is required for YAML output. "
                    "Install it with: pip install redactify[yaml]"
                )
            path.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
        else:
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
