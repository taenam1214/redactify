"""Tests for display utilities."""

from redactify.utils.display import pii_highlight, success, warning, error, info


class TestDisplayUtils:
    def test_pii_highlight_contains_text(self):
        result = pii_highlight("john@test.com", "email")
        assert "john@test.com" in result
        assert "email" in result

    def test_functions_do_not_crash(self, capsys):
        # These just print, verify they don't raise
        success("test message")
        warning("test warning")
        error("test error")
        info("test info")
        captured = capsys.readouterr()
        assert "test message" in captured.out
        assert "test warning" in captured.out
