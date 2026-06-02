"""Summary reporter for batch operations."""

from redactify.reporters.base import BaseReporter, RedactionReport


class SummaryReporter(BaseReporter):
    """Produces a compact summary for batch operations."""

    def report(self, result: RedactionReport) -> str:
        status = "CLEAN" if result.total_entities == 0 else f"{result.total_entities} PII"
        return f"  {result.source_file.name:<30} {status}"

    def batch_report(self, results: list[RedactionReport]) -> str:
        """Generate a summary for multiple reports."""
        lines = []
        lines.append(f"{'=' * 50}")
        lines.append("  Batch Summary")
        lines.append(f"{'=' * 50}")

        total_files = len(results)
        total_entities = sum(r.total_entities for r in results)
        clean_files = sum(1 for r in results if r.total_entities == 0)

        lines.append(f"  Files processed:  {total_files}")
        lines.append(f"  Clean files:      {clean_files}")
        lines.append(f"  Files with PII:   {total_files - clean_files}")
        lines.append(f"  Total PII found:  {total_entities}")
        lines.append("")

        # Per-type breakdown
        type_totals: dict[str, int] = {}
        for r in results:
            for pii_type, count in r.entities_by_type.items():
                type_totals[pii_type] = type_totals.get(pii_type, 0) + count

        if type_totals:
            lines.append("  Breakdown by type:")
            for pii_type, count in sorted(type_totals.items()):
                lines.append(f"    {pii_type:<20} {count}")
            lines.append("")

        # Per-file listing
        lines.append("  Per-file results:")
        for r in results:
            lines.append(self.report(r))

        lines.append(f"{'=' * 50}")
        return "\n".join(lines)
