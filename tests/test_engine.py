"""Tests for the redaction engine."""

import json
import tempfile
from pathlib import Path

import pytest

from redactify.core.detector import PIIType
from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode


class TestRedactionEngine:
    def _create_temp_file(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        f.write(content)
        f.flush()
        f.close()
        return Path(f.name)

    def test_scan_detects_email(self):
        path = self._create_temp_file("Contact john@example.com for info.")
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(path)
        assert report.total_entities >= 1
        assert "email" in report.entities_by_type
        assert not report.redacted
        path.unlink()

    def test_scan_detects_phone(self):
        path = self._create_temp_file("Call us at 555-123-4567.")
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(path)
        assert report.total_entities >= 1
        assert "phone" in report.entities_by_type
        path.unlink()

    def test_redact_blackout_mode(self):
        path = self._create_temp_file("Email: john@example.com")
        engine = RedactionEngine(mode=RedactionMode.BLACKOUT, use_ner=False)
        report = engine.redact(path)
        assert report.redacted
        output_path = path.parent / f"{path.stem}.redacted{path.suffix}"
        content = output_path.read_text()
        assert "john@example.com" not in content
        assert "█" in content
        path.unlink()
        output_path.unlink()

    def test_redact_label_mode(self):
        path = self._create_temp_file("Email: john@example.com")
        engine = RedactionEngine(mode=RedactionMode.LABEL, use_ner=False)
        engine.redact(path)
        output_path = path.parent / f"{path.stem}.redacted{path.suffix}"
        content = output_path.read_text()
        assert "[EMAIL]" in content
        path.unlink()
        output_path.unlink()

    def test_redact_custom_output_path(self):
        path = self._create_temp_file("SSN: 123-45-6789")
        output = path.parent / "output.txt"
        engine = RedactionEngine(use_ner=False)
        engine.redact(path, output_path=output)
        assert output.exists()
        content = output.read_text()
        assert "123-45-6789" not in content
        path.unlink()
        output.unlink()

    def test_scan_no_pii(self):
        path = self._create_temp_file("This is a perfectly safe sentence.")
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(path)
        assert report.total_entities == 0
        path.unlink()


class TestStringArgCoercion:
    """Test that string arguments are properly coerced to enums."""

    def test_mode_as_string(self):
        engine = RedactionEngine(mode="label", use_ner=False)
        assert engine.redactor.mode == RedactionMode.LABEL

    def test_mode_as_string_case_insensitive(self):
        engine = RedactionEngine(mode="BLACKOUT", use_ner=False)
        assert engine.redactor.mode == RedactionMode.BLACKOUT

    def test_mode_as_enum_still_works(self):
        engine = RedactionEngine(mode=RedactionMode.HASH, use_ner=False)
        assert engine.redactor.mode == RedactionMode.HASH

    def test_invalid_mode_string_raises(self):
        with pytest.raises(ValueError):
            RedactionEngine(mode="invalid", use_ner=False)

    def test_detect_types_as_strings(self):
        engine = RedactionEngine(detect_types=["email", "phone"], use_ner=False)
        supported = engine.detector.supported_types
        assert PIIType.EMAIL in supported
        assert PIIType.PHONE in supported

    def test_detect_types_mixed(self):
        engine = RedactionEngine(detect_types=[PIIType.EMAIL, "phone"], use_ner=False)
        supported = engine.detector.supported_types
        assert PIIType.EMAIL in supported
        assert PIIType.PHONE in supported

    def test_detect_types_case_insensitive(self):
        engine = RedactionEngine(detect_types=["EMAIL", "SSN"], use_ner=False)
        supported = engine.detector.supported_types
        assert PIIType.EMAIL in supported
        assert PIIType.SSN in supported

    def test_invalid_detect_type_string_raises(self):
        with pytest.raises(ValueError):
            RedactionEngine(detect_types=["not_a_type"], use_ner=False)


class TestScanText:
    """Tests for the in-memory scan_text method."""

    def test_scan_text_detects_email(self):
        engine = RedactionEngine(use_ner=False)
        entities = engine.scan_text("Contact john@example.com for info.")
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.EMAIL for e in entities)

    def test_scan_text_detects_phone(self):
        engine = RedactionEngine(use_ner=False)
        entities = engine.scan_text("Call us at 555-123-4567.")
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.PHONE for e in entities)

    def test_scan_text_no_pii(self):
        engine = RedactionEngine(use_ner=False)
        entities = engine.scan_text("This is a perfectly safe sentence.")
        assert entities == []

    def test_scan_text_respects_confidence_threshold(self):
        engine = RedactionEngine(use_ner=False, confidence_threshold=0.99)
        # Regex detectors have confidence=1.0, so they should still pass
        entities = engine.scan_text("Email: john@example.com")
        assert len(entities) >= 1


class TestRedactText:
    """Tests for the in-memory redact_text method."""

    def test_redact_text_blackout(self):
        engine = RedactionEngine(mode="blackout", use_ner=False)
        result = engine.redact_text("Email: john@example.com")
        assert "john@example.com" not in result.text
        assert "█" in result.text
        assert result.has_pii

    def test_redact_text_label(self):
        engine = RedactionEngine(mode="label", use_ner=False)
        result = engine.redact_text("Email: john@example.com")
        assert "[EMAIL]" in result.text
        assert result.total_entities >= 1

    def test_redact_text_hash(self):
        engine = RedactionEngine(mode="hash", use_ner=False)
        result = engine.redact_text("Email: john@example.com")
        assert "[REDACTED-" in result.text

    def test_redact_text_no_pii(self):
        engine = RedactionEngine(use_ner=False)
        result = engine.redact_text("Nothing sensitive here.")
        assert result.text == "Nothing sensitive here."
        assert result.has_pii is False
        assert result.total_entities == 0

    def test_redact_text_entities_by_type(self):
        engine = RedactionEngine(use_ner=False)
        result = engine.redact_text("john@example.com and 555-123-4567")
        assert "email" in result.entities_by_type
        assert "phone" in result.entities_by_type


class TestNewDetectorsIntegration:
    """Test that new detectors work through the engine pipeline."""

    def test_engine_detects_mac_address(self):
        engine = RedactionEngine(detect_types=["mac_address"], use_ner=False)
        entities = engine.scan_text("NIC: 00:1A:2B:3C:4D:5E")
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.MAC_ADDRESS for e in entities)

    def test_engine_detects_ipv6(self):
        engine = RedactionEngine(detect_types=["ipv6"], use_ner=False)
        entities = engine.scan_text("Server: 2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.IPV6 for e in entities)

    def test_engine_detects_drivers_license(self):
        engine = RedactionEngine(detect_types=["drivers_license"], use_ner=False)
        entities = engine.scan_text("Driver's license: D1234567")
        assert len(entities) >= 1
        assert any(e.pii_type == PIIType.DRIVERS_LICENSE for e in entities)

    def test_redact_text_mac_address(self):
        engine = RedactionEngine(mode="label", detect_types=["mac_address"], use_ner=False)
        result = engine.redact_text("NIC: 00:1A:2B:3C:4D:5E")
        assert "[MAC_ADDRESS]" in result.text

    def test_redact_text_ipv6(self):
        engine = RedactionEngine(mode="label", detect_types=["ipv6"], use_ner=False)
        result = engine.redact_text("Server: 2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        assert "[IPV6]" in result.text

    def test_redact_text_drivers_license(self):
        engine = RedactionEngine(mode="label", detect_types=["drivers_license"], use_ner=False)
        result = engine.redact_text("DL: D1234567")
        assert "[DRIVERS_LICENSE]" in result.text

    def test_all_new_detectors_in_default_engine(self):
        engine = RedactionEngine(use_ner=False)
        supported = engine.detector.supported_types
        assert PIIType.MAC_ADDRESS in supported
        assert PIIType.IPV6 in supported
        assert PIIType.DRIVERS_LICENSE in supported


class TestFromConfig:
    """Tests for RedactionEngine.from_config()."""

    def test_from_config_json(self, tmp_path):
        config = {
            "mode": "label",
            "detect_types": ["email"],
            "use_ner": False,
        }
        cfg_path = tmp_path / ".redactify.json"
        cfg_path.write_text(json.dumps(config))
        engine = RedactionEngine.from_config(cfg_path)
        result = engine.redact_text("Email: john@example.com and 555-123-4567")
        assert "[EMAIL]" in result.text
        # Phone should not be detected since detect_types=["email"]
        assert "555-123-4567" in result.text

    def test_from_config_with_allowlist(self, tmp_path):
        config = {
            "mode": "label",
            "use_ner": False,
            "allowlist": ["john@example.com"],
        }
        cfg_path = tmp_path / ".redactify.json"
        cfg_path.write_text(json.dumps(config))
        engine = RedactionEngine.from_config(cfg_path)
        entities = engine.scan_text("Contact john@example.com or bob@test.com")
        texts = [e.text for e in entities]
        assert "john@example.com" not in texts
        assert "bob@test.com" in texts

    def test_from_config_defaults(self, tmp_path):
        cfg_path = tmp_path / ".redactify.json"
        cfg_path.write_text("{}")
        engine = RedactionEngine.from_config(cfg_path)
        result = engine.redact_text("Email: john@example.com")
        assert "john@example.com" not in result.text
