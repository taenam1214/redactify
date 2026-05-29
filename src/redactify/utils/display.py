"""Display utilities — progress and colored output."""

import click


# Color scheme
COLORS = {
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "muted": "bright_black",
    "pii": "red",
    "label": "cyan",
}


def success(msg: str) -> None:
    """Print a success message."""
    click.echo(click.style(f"  ✓ {msg}", fg=COLORS["success"]))


def warning(msg: str) -> None:
    """Print a warning message."""
    click.echo(click.style(f"  ⚠ {msg}", fg=COLORS["warning"]))


def error(msg: str) -> None:
    """Print an error message."""
    click.echo(click.style(f"  ✗ {msg}", fg=COLORS["error"]))


def info(msg: str) -> None:
    """Print an info message."""
    click.echo(click.style(f"  ℹ {msg}", fg=COLORS["info"]))


def header(msg: str) -> None:
    """Print a header."""
    click.echo("")
    click.echo(click.style(f"  {msg}", bold=True))
    click.echo(click.style(f"  {'─' * len(msg)}", fg=COLORS["muted"]))


def pii_highlight(text: str, pii_type: str) -> str:
    """Format a PII entity for display."""
    return (
        click.style(text, fg=COLORS["pii"], bold=True)
        + " "
        + click.style(f"[{pii_type}]", fg=COLORS["label"])
    )


def stats_line(label: str, value: str | int) -> None:
    """Print a key-value stats line."""
    click.echo(
        click.style(f"  {label:<20}", fg=COLORS["muted"])
        + click.style(str(value), bold=True)
    )
