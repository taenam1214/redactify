"""Redactify CLI — command-line interface."""

import sys
from pathlib import Path

import click

from redactify.core.engine import RedactionEngine
from redactify.core.detector import PIIType
from redactify.core.redactor import RedactionMode
from redactify.reporters.console import ConsoleReporter
from redactify.reporters.json_reporter import JSONReporter
from redactify.utils.config import RedactifyConfig


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
@click.option("-o", "--output", type=click.Path(path_type=Path), help="Output file or directory path.")
@click.option(
    "--mode",
    type=click.Choice(MODE_CHOICES),
    default="blackout",
    help="Redaction mode.",
)
@click.option("--detect", type=str, default=None, help="Comma-separated PII types to detect.")
@click.option("--no-ner", is_flag=True, help="Disable NER-based detection (names, orgs, locations).")
@click.option("--confidence", type=float, default=0.0, help="Minimum confidence threshold (0.0-1.0).")
@click.option("-r", "--recursive", is_flag=True, help="Process directories recursively.")
@click.option("--dry-run", is_flag=True, help="Preview what would be redacted without writing files.")
@click.option("--format", "report_format", type=click.Choice(["console", "json"]), default="console")
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON (shorthand for --format json).")
@click.option("--strict", is_flag=True, help="Exit with code 1 if any PII is detected.")
def redact(file: Path, output: Path | None, mode: str, detect: str | None, no_ner: bool, confidence: float, recursive: bool, dry_run: bool, report_format: str, use_json: bool, strict: bool):
    """Redact PII from a document or directory."""
    detect_types = _parse_detect_types(detect)
    redaction_mode = RedactionMode(mode)

    engine = RedactionEngine(
        mode=redaction_mode,
        detect_types=detect_types,
        use_ner=not no_ner,
        confidence_threshold=confidence,
    )

    reporter = JSONReporter() if (use_json or report_format == "json") else ConsoleReporter()

    if dry_run:
        # Dry run: scan only, show what would be redacted
        if file.is_dir():
            reports = engine.scan_directory(file, recursive=recursive)
        else:
            reports = [engine.scan(file)]
        for report in reports:
            click.echo(reporter.report(report))
        click.echo("\n  [DRY RUN] No files were modified.")
        return

    if file.is_dir():
        reports = engine.redact_directory(file, output_dir=output, recursive=recursive)
        for report in reports:
            click.echo(reporter.report(report))
            click.echo("")
        out_dir = output or file / "redacted"
        click.echo(f"\n  {len(reports)} files redacted to: {out_dir}")
    else:
        report = engine.redact(file, output_path=output)
        reports = [report]
        click.echo(reporter.report(report))
        if report.redacted:
            out_path = output or file.parent / f"{file.stem}.redacted{file.suffix}"
            click.echo(f"\n  Output written to: {out_path}")

    if strict and any(r.total_entities > 0 for r in reports):
        sys.exit(1)


@main.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--detect", type=str, default=None, help="Comma-separated PII types to detect.")
@click.option("--no-ner", is_flag=True, help="Disable NER-based detection.")
@click.option("--confidence", type=float, default=0.0, help="Minimum confidence threshold (0.0-1.0).")
@click.option("-r", "--recursive", is_flag=True, help="Scan directories recursively.")
@click.option("--format", "report_format", type=click.Choice(["console", "json"]), default="console")
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON (shorthand for --format json).")
@click.option("--strict", is_flag=True, help="Exit with code 1 if any PII is detected.")
def scan(file: Path, detect: str | None, no_ner: bool, confidence: float, recursive: bool, report_format: str, use_json: bool, strict: bool):
    """Scan a document or directory for PII without redacting."""
    detect_types = _parse_detect_types(detect)

    engine = RedactionEngine(
        detect_types=detect_types,
        use_ner=not no_ner,
        confidence_threshold=confidence,
    )

    reporter = JSONReporter() if (use_json or report_format == "json") else ConsoleReporter()

    if file.is_dir():
        reports = engine.scan_directory(file, recursive=recursive)
        for report in reports:
            click.echo(reporter.report(report))
            click.echo("")
        total = sum(r.total_entities for r in reports)
        click.echo(f"\n  Scanned {len(reports)} files. Total PII found: {total}")
    else:
        reports = [engine.scan(file)]
        click.echo(reporter.report(reports[0]))

    if strict and any(r.total_entities > 0 for r in reports):
        sys.exit(1)


@main.command()
@click.option("--init", "do_init", is_flag=True, help="Create a default config file.")
@click.option("--show", is_flag=True, help="Show current configuration.")
@click.option("--path", type=click.Path(path_type=Path), default=None, help="Config file path.")
def config(do_init: bool, show: bool, path: Path | None):
    """Manage Redactify configuration."""
    if do_init:
        cfg = RedactifyConfig()
        cfg.to_file(path)
        out_path = path or Path.cwd() / ".redactify.json"
        click.echo(f"  Config created at: {out_path}")
    elif show:
        cfg = RedactifyConfig.from_file(path)
        click.echo(f"  Mode:          {cfg.mode}")
        click.echo(f"  Detect types:  {cfg.detect_types or 'all'}")
        click.echo(f"  Use NER:       {cfg.use_ner}")
        click.echo(f"  Output format: {cfg.output_format}")
        if cfg.custom_patterns:
            click.echo(f"  Custom patterns: {len(cfg.custom_patterns)}")
    else:
        click.echo("Use --init to create a config or --show to display current config.")


@main.command()
def supported():
    """List all supported PII types and file formats."""
    click.echo("\n  Supported PII types:")
    for pii_type in PIIType:
        click.echo(f"    - {pii_type.value}")
    click.echo("\n  Supported file formats:")
    click.echo("    - .txt, .csv, .log, .md (plain text)")
    click.echo("    - .html, .htm (HTML)")
    click.echo("    - .pdf (requires: pip install redactify[pdf])")
    click.echo("    - .docx (requires: pip install redactify[docx])")
    click.echo("")


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
