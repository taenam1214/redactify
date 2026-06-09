"""Tests for the allowlist system."""

import tempfile
from pathlib import Path

from redactify.core.allowlist import Allowlist
from redactify.core.detector import PIIEntity, PIIType
from redactify.core.engine import RedactionEngine


class TestAllowlistBasic:
    def test_exact_string_match(self):
        al = Allowlist()
        al.add_string("john@company.com")
        assert al.is_allowed("john@company.com") is True
        assert al.is_allowed("other@example.com") is False

    def test_case_insensitive(self):
        al = Allowlist()
        al.add_string("John@Company.com")
        assert al.is_allowed("john@company.com") is True

    def test_regex_pattern(self):
        al = Allowlist()
        al.add_pattern(r"support@.*\.example\.com")
        assert al.is_allowed("support@sales.example.com") is True
        assert al.is_allowed("admin@other.com") is False

    def test_filter_entities(self):
        al = Allowlist()
        al.add_string("safe@company.com")
        entities = [
            PIIEntity(text="safe@company.com", pii_type=PIIType.EMAIL, start=0, end=16),
            PIIEntity(text="private@gmail.com", pii_type=PIIType.EMAIL, start=20, end=37),
        ]
        filtered = al.filter_entities(entities)
        assert len(filtered) == 1
        assert filtered[0].text == "private@gmail.com"

    def test_empty_allowlist_passes_all(self):
        al = Allowlist()
        entities = [
            PIIEntity(text="a@b.com", pii_type=PIIType.EMAIL, start=0, end=7),
        ]
        assert al.filter_entities(entities) == entities


class TestAllowlistFromFile:
    def test_load_from_file(self):
        content = "# Company emails\nsafe@company.com\nregex:support@.*\\.corp\\.com\n\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        al = Allowlist.from_file(path)
        assert al.is_allowed("safe@company.com") is True
        assert al.is_allowed("support@sales.corp.com") is True
        assert al.is_allowed("other@gmail.com") is False
        path.unlink()

    def test_skips_comments_and_blank_lines(self):
        content = "# comment\n\n   \nvalid@test.com\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            f.flush()
            path = Path(f.name)

        al = Allowlist.from_file(path)
        assert len(al.exact_strings) == 1
        path.unlink()


class TestAllowlistFromList:
    def test_from_list(self):
        al = Allowlist.from_list(["safe@a.com", "regex:test@.*"])
        assert al.is_allowed("safe@a.com") is True
        assert al.is_allowed("test@anything.com") is True


class TestAllowlistEngineIntegration:
    def test_engine_with_allowlist(self):
        al = Allowlist()
        al.add_string("john@example.com")
        engine = RedactionEngine(use_ner=False, allowlist=al)
        entities = engine.scan_text("Contact john@example.com or bob@test.com")
        texts = [e.text for e in entities]
        assert "john@example.com" not in texts
        assert "bob@test.com" in texts

    def test_engine_without_allowlist(self):
        engine = RedactionEngine(use_ner=False)
        entities = engine.scan_text("Contact john@example.com")
        assert len(entities) >= 1

    def test_redact_text_with_allowlist(self):
        al = Allowlist.from_list(["555-123-4567"])
        engine = RedactionEngine(mode="label", use_ner=False, allowlist=al)
        result = engine.redact_text("Call 555-123-4567 or 555-987-6543")
        assert "555-123-4567" in result.text  # allowlisted, kept
        assert "[PHONE]" in result.text  # other one redacted
