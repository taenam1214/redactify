"""Redactify CLI — command-line interface."""

from pathlib import Path

import click

from redactify.core.engine import RedactionEngine
from redactify.core.detector import PIIType
from redactify.core.redactor import RedactionMode
from redactify.reporters.console import ConsoleReporter
from redactify.reporters.json_reporter import JSONReporter


PII_TYPE_CHOICES = [t.value for t in PIIType if t != PIIType.CUSTOM]
MODE_CHOICES = [m.value for m in RedactionMode]


@click.group()
@click.version_option()
def main():
    """Redactify — Privacy-preserving document redaction.

    Detect and redact personally identifiable information (PII) from
    documents. All processing happens locally on your machine.
    """
    pass


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), help="Output file path.")
@click.option(
    "--mode",
    type=click.Choice(MODE_CHOICES),
    default="blackout",
    help="Redaction mode.",
)
@click.option("--detect", type=str, default=None, help="Comma-separated PII types to detect.")
@click.option("--no-ner", is_flag=True, help="Disable NER-based detection (names, orgs, locations).")
@click.option("--format", "report_format", type=click.Choice(["console", "json"]), default="console")
def redact(file: Path, output: Path | None, mode: str, detect: str | None, no_ner: bool, report_format: str):
    """Redact PII from a document."""
    detect_types = _parse_detect_types(detect)
    redaction_mode = RedactionMode(mode)

    engine = RedactionEngine(
        mode=redaction_mode,
        detect_types=detect_types,
        use_ner=not no_ner,
    )

    report = engine.redact(file, output_path=output)

    reporter = JSONReporter() if report_format == "json" else ConsoleReporter()
    click.echo(reporter.report(report))

    if report.redacted:
        out_path = output or file.parent / f"{file.stem}.redacted{file.suffix}"
        click.echo(f"\n  Output written to: {out_path}")


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--detect", type=str, default=None, help="Comma-separated PII types to detect.")
@click.option("--no-ner", is_flag=True, help="Disable NER-based detection.")
@click.option("--format", "report_format", type=click.Choice(["console", "json"]), default="console")
def scan(file: Path, detect: str | None, no_ner: bool, report_format: str):
    """Scan a document for PII without redacting."""
    detect_types = _parse_detect_types(detect)

    engine = RedactionEngine(
        detect_types=detect_types,
        use_ner=not no_ner,
    )

    report = engine.scan(file)

    reporter = JSONReporter() if report_format == "json" else ConsoleReporter()
    click.echo(reporter.report(report))


def _parse_detect_types(detect: str | None) -> list[PIIType] | None:
    """Parse comma-separated PII type string into a list."""
    if detect is None:
        return None
    types = []
    for name in detect.split(","):
        name = name.strip().lower()
        try:
            types.append(PIIType(name))
        except ValueError:
            click.echo(f"Warning: Unknown PII type '{name}', skipping.", err=True)
    return types if types else None


if __name__ == "__main__":
    main()
