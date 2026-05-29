"""Tests for the CLI interface."""

from pathlib import Path

from click.testing import CliRunner

from redactify.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


class TestCLIScan:
    def setup_method(self):
        self.runner = CliRunner()

    def test_scan_file(self):
        result = self.runner.invoke(main, ["scan", str(FIXTURES / "sample_email.txt"), "--no-ner"])
        assert result.exit_code == 0
        assert "email" in result.output.lower()

    def test_scan_no_pii(self):
        result = self.runner.invoke(main, ["scan", str(FIXTURES / "no_pii.txt"), "--no-ner"])
        assert result.exit_code == 0
        assert "0" in result.output

    def test_scan_json_format(self):
        result = self.runner.invoke(
            main, ["scan", str(FIXTURES / "sample_email.txt"), "--no-ner", "--format", "json"]
        )
        assert result.exit_code == 0
        assert '"total_entities"' in result.output

    def test_scan_with_detect_filter(self):
        result = self.runner.invoke(
            main, ["scan", str(FIXTURES / "sample_email.txt"), "--no-ner", "--detect", "email"]
        )
        assert result.exit_code == 0
        assert "email" in result.output.lower()

    def test_scan_directory(self):
        result = self.runner.invoke(main, ["scan", str(FIXTURES), "--no-ner"])
        assert result.exit_code == 0
        assert "Scanned" in result.output


class TestCLIRedact:
    def setup_method(self):
        self.runner = CliRunner()

    def test_redact_file(self, tmp_path):
        output = tmp_path / "out.txt"
        result = self.runner.invoke(
            main, ["redact", str(FIXTURES / "sample_email.txt"), "-o", str(output), "--no-ner"]
        )
        assert result.exit_code == 0
        assert output.exists()
        content = output.read_text()
        assert "john.smith@example.com" not in content

    def test_redact_label_mode(self, tmp_path):
        output = tmp_path / "out.txt"
        result = self.runner.invoke(
            main,
            ["redact", str(FIXTURES / "sample_email.txt"), "-o", str(output), "--no-ner", "--mode", "label"],
        )
        assert result.exit_code == 0
        content = output.read_text()
        assert "[EMAIL]" in content

    def test_redact_with_confidence(self, tmp_path):
        output = tmp_path / "out.txt"
        result = self.runner.invoke(
            main,
            ["redact", str(FIXTURES / "sample_email.txt"), "-o", str(output), "--no-ner", "--confidence", "0.9"],
        )
        assert result.exit_code == 0


class TestCLIConfig:
    def setup_method(self):
        self.runner = CliRunner()

    def test_config_init(self, tmp_path):
        config_path = tmp_path / ".redactify.json"
        result = self.runner.invoke(main, ["config", "--init", "--path", str(config_path)])
        assert result.exit_code == 0
        assert config_path.exists()

    def test_config_show(self, tmp_path):
        config_path = tmp_path / ".redactify.json"
        # Init first
        self.runner.invoke(main, ["config", "--init", "--path", str(config_path)])
        result = self.runner.invoke(main, ["config", "--show", "--path", str(config_path)])
        assert result.exit_code == 0
        assert "blackout" in result.output


class TestCLIVersion:
    def test_version_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
