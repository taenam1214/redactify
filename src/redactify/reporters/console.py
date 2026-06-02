"""Console reporter — human-readable terminal output."""

from redactify.reporters.base import BaseReporter, RedactionReport


class ConsoleReporter(BaseReporter):
    """Produces human-readable console output for redaction reports."""

    def report(self, result: RedactionReport) -> str:
        lines = []
        lines.append(f"{'=' * 50}")
        lines.append("  Redactify Report")
        lines.append(f"{'=' * 50}")
        lines.append(f"  File:     {result.source_file}")
        lines.append(f"  Redacted: {'Yes' if result.redacted else 'No (scan only)'}")
        lines.append(f"  Total PII found: {result.total_entities}")
        lines.append("")

        if result.entities_by_type:
            lines.append("  Breakdown by type:")
            for pii_type, count in sorted(result.entities_by_type.items()):
                lines.append(f"    {pii_type:<20} {count}")
            lines.append("")

        if result.entities:
            lines.append("  Detected entities:")
            for entity in result.entities:
                preview = entity.text[:30] + "..." if len(entity.text) > 30 else entity.text
                lines.append(
                    f"    [{entity.pii_type.value:<15}] "
                    f"pos {entity.start}-{entity.end}  "
                    f'"{preview}"'
                )
            lines.append("")

        lines.append(f"{'=' * 50}")
        return "\n".join(lines)
