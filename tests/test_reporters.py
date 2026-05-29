"""Tests for reporters."""

import json
from pathlib import Path

from redactify.core.detector import PIIEntity, PIIType
from redactify.reporters.base import RedactionReport
from redactify.reporters.console import ConsoleReporter
from redactify.reporters.json_reporter import JSONReporter


def _make_report() -> RedactionReport:
    return RedactionReport(
        source_file=Path("/tmp/test.txt"),
        total_entities=3,
        entities_by_type={"email": 2, "phone": 1},
        entities=[
            PIIEntity(text="a@b.com", pii_type=PIIType.EMAIL, start=0, end=7),
            PIIEntity(text="c@d.com", pii_type=PIIType.EMAIL, start=10, end=17),
            PIIEntity(text="555-1234", pii_type=PIIType.PHONE, start=20, end=28),
        ],
        redacted=True,
    )


class TestConsoleReporter:
    def test_includes_file_name(self):
        report = _make_report()
        output = ConsoleReporter().report(report)
        assert "test.txt" in output

    def test_includes_total_count(self):
        report = _make_report()
        output = ConsoleReporter().report(report)
        assert "3" in output

    def test_includes_type_breakdown(self):
        report = _make_report()
        output = ConsoleReporter().report(report)
        assert "email" in output
        assert "phone" in output

    def test_includes_redacted_status(self):
        report = _make_report()
        output = ConsoleReporter().report(report)
        assert "Yes" in output


class TestJSONReporter:
    def test_valid_json_output(self):
        report = _make_report()
        output = JSONReporter().report(report)
        data = json.loads(output)
        assert data["total_entities"] == 3

    def test_contains_entities(self):
        report = _make_report()
        output = JSONReporter().report(report)
        data = json.loads(output)
        assert len(data["entities"]) == 3

    def test_entity_fields(self):
        report = _make_report()
        output = JSONReporter().report(report)
        data = json.loads(output)
        entity = data["entities"][0]
        assert "text" in entity
        assert "type" in entity
        assert "start" in entity
        assert "end" in entity
        assert "confidence" in entity

    def test_source_file_path(self):
        report = _make_report()
        output = JSONReporter().report(report)
        data = json.loads(output)
        assert "test.txt" in data["source_file"]
