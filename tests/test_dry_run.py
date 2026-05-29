"""Test the --dry-run flag."""

from pathlib import Path

from click.testing import CliRunner

from redactify.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


class TestDryRun:
    def test_dry_run_does_not_create_files(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["redact", str(FIXTURES / "sample_email.txt"), "-o", str(tmp_path / "out.txt"), "--no-ner", "--dry-run"],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert not (tmp_path / "out.txt").exists()

    def test_dry_run_shows_entities(self):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["redact", str(FIXTURES / "sample_email.txt"), "--no-ner", "--dry-run"],
        )
        assert result.exit_code == 0
        assert "email" in result.output.lower()
