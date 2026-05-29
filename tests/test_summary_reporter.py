"""Tests for the summary reporter."""

from pathlib import Path

from redactify.core.detector import PIIEntity, PIIType
from redactify.reporters.base import RedactionReport
from redactify.reporters.summary import SummaryReporter


class TestSummaryReporter:
    def _make_report(self, name: str, count: int) -> RedactionReport:
        entities = [
            PIIEntity(text=f"entity{i}", pii_type=PIIType.EMAIL, start=i * 10, end=i * 10 + 5)
            for i in range(count)
        ]
        return RedactionReport(
            source_file=Path(f"/tmp/{name}"),
            total_entities=count,
            entities_by_type={"email": count} if count else {},
            entities=entities,
            redacted=True,
        )

    def test_single_report_clean(self):
        reporter = SummaryReporter()
        report = self._make_report("clean.txt", 0)
        output = reporter.report(report)
        assert "CLEAN" in output

    def test_single_report_with_pii(self):
        reporter = SummaryReporter()
        report = self._make_report("dirty.txt", 5)
        output = reporter.report(report)
        assert "5 PII" in output

    def test_batch_report(self):
        reporter = SummaryReporter()
        reports = [
            self._make_report("a.txt", 3),
            self._make_report("b.txt", 0),
            self._make_report("c.txt", 7),
        ]
        output = reporter.batch_report(reports)
        assert "3" in output  # files processed
        assert "10" in output  # total PII
        assert "Clean files" in output
        assert "a.txt" in output
        assert "b.txt" in output
        assert "c.txt" in output

    def test_batch_report_empty(self):
        reporter = SummaryReporter()
        output = reporter.batch_report([])
        assert "0" in output
