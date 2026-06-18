"""Configuration management for Redactify."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import json

from redactify.exceptions import ConfigValidationError


DEFAULT_CONFIG_FILE = ".redactify.json"
YAML_EXTENSIONS = {".yml", ".yaml"}

_VALID_MODES = {"blackout", "label", "hash", "custom"}


@dataclass
class RedactifyConfig:
    """Configuration for a redaction session."""

    mode: str = "blackout"
    detect_types: list[str] = field(default_factory=list)
    use_ner: bool = True
    custom_patterns: list[dict] = field(default_factory=list)
    output_format: str = "console"
    allowlist: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validate config values, raising ConfigValidationError on problems."""
        if self.mode not in _VALID_MODES:
            raise ConfigValidationError(
                f"'{self.mode}' is not a valid mode. Choose from: {', '.join(sorted(_VALID_MODES))}",
                field="mode",
            )

        # Validate detect_types are real PIIType values
        if self.detect_types:
            from redactify.core.detector import PIIType
            valid_types = {t.value for t in PIIType}
            for dt in self.detect_types:
                if dt.lower() not in valid_types:
                    raise ConfigValidationError(
                        f"'{dt}' is not a recognized PII type. "
                        f"Valid types: {', '.join(sorted(valid_types))}",
                        field="detect_types",
                    )

        # Validate custom pattern regexes compile
        for i, pattern in enumerate(self.custom_patterns):
            if "pattern" in pattern:
                try:
                    re.compile(pattern["pattern"])
                except re.error as e:
                    name = pattern.get("name", f"pattern[{i}]")
                    raise ConfigValidationError(
                        f"Invalid regex in '{name}': {e}",
                        field="custom_patterns",
                    )

        # Validate allowlist regex entries compile
        for entry in self.allowlist:
            if entry.startswith("regex:"):
                try:
                    re.compile(entry[6:].strip())
                except re.error as e:
                    raise ConfigValidationError(
                        f"Invalid allowlist regex '{entry}': {e}",
                        field="allowlist",
                    )

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

        config = cls(
            mode=data.get("mode", "blackout"),
            detect_types=data.get("detect_types", []),
            use_ner=data.get("use_ner", True),
            custom_patterns=data.get("custom_patterns", []),
            output_format=data.get("output_format", "console"),
            allowlist=data.get("allowlist", []),
        )
        config.validate()
        return config

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
