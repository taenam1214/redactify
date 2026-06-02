"""Integration test for HTML file redaction."""

from pathlib import Path

from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode

FIXTURES = Path(__file__).parent / "fixtures"


class TestHTMLIntegration:
    def test_scan_html_file(self):
        engine = RedactionEngine(use_ner=False)
        report = engine.scan(FIXTURES / "sample_page.html")
        assert report.total_entities > 0
        assert "email" in report.entities_by_type

    def test_redact_html_file(self, tmp_path):
        output = tmp_path / "redacted.html"
        engine = RedactionEngine(mode=RedactionMode.LABEL, use_ner=False)
        engine.redact(FIXTURES / "sample_page.html", output_path=output)
        assert output.exists()
        content = output.read_text()
        assert "sarah.johnson@company.com" not in content
        assert "[EMAIL]" in content
