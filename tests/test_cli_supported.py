"""Test the supported CLI command."""

from click.testing import CliRunner

from redactify.cli import main


class TestSupportedCommand:
    def test_lists_pii_types(self):
        runner = CliRunner()
        result = runner.invoke(main, ["supported"])
        assert result.exit_code == 0
        assert "email" in result.output
        assert "phone" in result.output
        assert "ssn" in result.output
        assert "person" in result.output

    def test_lists_file_formats(self):
        runner = CliRunner()
        result = runner.invoke(main, ["supported"])
        assert result.exit_code == 0
        assert ".txt" in result.output
        assert ".pdf" in result.output
        assert ".html" in result.output
