"""Fuzzing and adversarial input tests."""

from redactify.core.engine import RedactionEngine


class TestUnicodeEdgeCases:
    def setup_method(self):
        self.engine = RedactionEngine(use_ner=False)

    def test_zero_width_joiners(self):
        # Email with zero-width joiners shouldn't crash
        text = "Email: j\u200bohn@exa\u200bmple.com"
        result = self.engine.redact_text(text)
        assert result.text is not None

    def test_rtl_marks(self):
        # Right-to-left override characters
        text = "Phone: \u202e555-123-4567\u202c"
        result = self.engine.redact_text(text)
        assert result.text is not None

    def test_combining_characters(self):
        text = "Name: Jöhn Dö\u0308e, email: jo\u0308hn@test.com"
        result = self.engine.redact_text(text)
        assert result.text is not None

    def test_emoji_in_text(self):
        text = "Call 📞 555-123-4567 or email 📧 test@example.com"
        result = self.engine.redact_text(text)
        assert result.has_pii

    def test_null_characters(self):
        text = "Email: john\x00@example.com"
        result = self.engine.redact_text(text)
        assert result.text is not None

    def test_mixed_scripts(self):
        text = "用户email: тест@example.com and phone: 555-123-4567"
        entities = self.engine.scan_text(text)
        # Should still find phone
        assert len(entities) >= 1


class TestExtremeLengths:
    def setup_method(self):
        self.engine = RedactionEngine(use_ner=False)

    def test_empty_string(self):
        result = self.engine.redact_text("")
        assert result.text == ""
        assert not result.has_pii

    def test_single_character(self):
        result = self.engine.redact_text("a")
        assert result.text == "a"

    def test_very_long_line(self):
        # 100KB single line
        text = "x" * 100_000 + " john@example.com " + "y" * 100_000
        result = self.engine.redact_text(text)
        assert result.has_pii
        assert "john@example.com" not in result.text

    def test_many_short_lines(self):
        text = "\n".join(f"Line {i}: test@example{i}.com" for i in range(1000))
        entities = self.engine.scan_text(text)
        assert len(entities) == 1000


class TestNestedPII:
    def setup_method(self):
        self.engine = RedactionEngine(use_ner=False)

    def test_email_containing_digits_like_ssn(self):
        # Should detect as email, not SSN
        text = "Contact 123-45-6789@gmail.com"
        entities = self.engine.scan_text(text)
        assert any(e.pii_type.value == "email" for e in entities)

    def test_pii_adjacent_to_punctuation(self):
        text = "(john@example.com)"
        entities = self.engine.scan_text(text)
        assert len(entities) >= 1

    def test_multiple_pii_no_separator(self):
        text = "john@example.com555-123-4567"
        entities = self.engine.scan_text(text)
        assert len(entities) >= 1


class TestControlCharacters:
    def setup_method(self):
        self.engine = RedactionEngine(use_ner=False)

    def test_tab_separated(self):
        text = "Name\tEmail\tPhone\nJohn\tjohn@ex.com\t555-123-4567"
        entities = self.engine.scan_text(text)
        assert len(entities) >= 2

    def test_carriage_return(self):
        text = "Email: test@example.com\r\nPhone: 555-123-4567\r\n"
        entities = self.engine.scan_text(text)
        assert len(entities) >= 2

    def test_form_feed(self):
        text = "Page 1\x0cEmail: a@b.com\x0cPage 3"
        entities = self.engine.scan_text(text)
        assert len(entities) >= 1
