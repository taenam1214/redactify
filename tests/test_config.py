"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path

import pytest

from redactify.exceptions import ConfigValidationError
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


class TestConfigValidation:
    def test_invalid_mode_raises(self, tmp_path):
        cfg_path = tmp_path / ".redactify.json"
        cfg_path.write_text(json.dumps({"mode": "destroy"}))
        with pytest.raises(ConfigValidationError, match="mode"):
            RedactifyConfig.from_file(cfg_path)

    def test_invalid_detect_type_raises(self, tmp_path):
        cfg_path = tmp_path / ".redactify.json"
        cfg_path.write_text(json.dumps({"detect_types": ["emal"]}))
        with pytest.raises(ConfigValidationError, match="detect_types"):
            RedactifyConfig.from_file(cfg_path)

    def test_invalid_custom_pattern_regex_raises(self, tmp_path):
        cfg_path = tmp_path / ".redactify.json"
        cfg_path.write_text(json.dumps({
            "custom_patterns": [{"name": "bad", "pattern": "[invalid"}]
        }))
        with pytest.raises(ConfigValidationError, match="custom_patterns"):
            RedactifyConfig.from_file(cfg_path)

    def test_invalid_allowlist_regex_raises(self, tmp_path):
        cfg_path = tmp_path / ".redactify.json"
        cfg_path.write_text(json.dumps({"allowlist": ["regex:[unclosed"]}))
        with pytest.raises(ConfigValidationError, match="allowlist"):
            RedactifyConfig.from_file(cfg_path)

    def test_valid_config_does_not_raise(self):
        cfg = RedactifyConfig(mode="label", detect_types=["email", "phone"])
        cfg.validate()  # should not raise
