"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path

from redactify.utils.config import RedactifyConfig


class TestRedactifyConfig:
    def test_default_values(self):
        config = RedactifyConfig()
        assert config.mode == "blackout"
        assert config.use_ner is True
        assert config.detect_types == []
        assert config.output_format == "console"

    def test_from_file_returns_defaults_when_missing(self):
        config = RedactifyConfig.from_file(Path("/nonexistent/.redactify.json"))
        assert config.mode == "blackout"

    def test_roundtrip_to_and_from_file(self):
        config = RedactifyConfig(
            mode="label",
            detect_types=["email", "phone"],
            use_ner=False,
            output_format="json",
        )
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        config.to_file(path)
        loaded = RedactifyConfig.from_file(path)

        assert loaded.mode == "label"
        assert loaded.detect_types == ["email", "phone"]
        assert loaded.use_ner is False
        assert loaded.output_format == "json"
        path.unlink()

    def test_to_file_creates_valid_json(self):
        config = RedactifyConfig(mode="hash")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        config.to_file(path)
        data = json.loads(path.read_text())
        assert data["mode"] == "hash"
        path.unlink()

    def test_custom_patterns_field(self):
        config = RedactifyConfig(
            custom_patterns=[{"name": "order_id", "pattern": r"ORD-\d+"}]
        )
        assert len(config.custom_patterns) == 1
        assert config.custom_patterns[0]["name"] == "order_id"
