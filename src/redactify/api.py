"""Module-level convenience functions for quick redaction and scanning."""

from __future__ import annotations

import functools
from pathlib import Path

from redactify.core.detector import PIIEntity, PIIType
from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode
from redactify.core.results import TextResult
from redactify.reporters.base import RedactionReport


@functools.lru_cache(maxsize=1)
def _get_default_engine() -> RedactionEngine:
    """Return a cached engine with all detectors + NER."""
    return RedactionEngine(use_ner=True)


@functools.lru_cache(maxsize=1)
def _get_regex_only_engine() -> RedactionEngine:
    """Return a cached engine with regex detectors only (no NER)."""
    return RedactionEngine(use_ner=False)


def _resolve_engine(
    *,
    mode: RedactionMode | str = RedactionMode.BLACKOUT,
    detect_types: list[PIIType | str] | None = None,
    use_ner: bool = True,
    confidence_threshold: float = 0.0,
    custom_patterns: list[dict] | None = None,
) -> RedactionEngine:
    """Return a cached default engine or build a new one for custom args."""
    is_default = (
        (mode is RedactionMode.BLACKOUT or mode == "blackout")
        and detect_types is None
        and confidence_threshold == 0.0
        and custom_patterns is None
    )
    if is_default and use_ner:
        return _get_default_engine()
    if is_default and not use_ner:
        return _get_regex_only_engine()
    return RedactionEngine(
        mode=mode,
        detect_types=detect_types,
        use_ner=use_ner,
        confidence_threshold=confidence_threshold,
        custom_patterns=custom_patterns,
    )


def redact_text(
    text: str,
    *,
    mode: RedactionMode | str = RedactionMode.BLACKOUT,
    detect_types: list[PIIType | str] | None = None,
    use_ner: bool = True,
    confidence_threshold: float = 0.0,
    custom_patterns: list[dict] | None = None,
) -> TextResult:
    """Redact PII from a string.

    Args:
        text: The text to redact.
        mode: Redaction mode (enum or string like ``"label"``).
        detect_types: PII types to detect (``None`` = all).
        use_ner: Whether to use spaCy NER. Defaults to ``True``.
        confidence_threshold: Minimum confidence score to keep.
        custom_patterns: Extra regex patterns.

    Returns:
        A :class:`TextResult` with the redacted text and entities.
    """
    engine = _resolve_engine(
        mode=mode,
        detect_types=detect_types,
        use_ner=use_ner,
        confidence_threshold=confidence_threshold,
        custom_patterns=custom_patterns,
    )
    return engine.redact_text(text)


def scan_text(
    text: str,
    *,
    detect_types: list[PIIType | str] | None = None,
    use_ner: bool = True,
    confidence_threshold: float = 0.0,
    custom_patterns: list[dict] | None = None,
) -> list[PIIEntity]:
    """Scan a string for PII without redacting.

    Args:
        text: The text to scan.
        detect_types: PII types to detect (``None`` = all).
        use_ner: Whether to use spaCy NER. Defaults to ``True``.
        confidence_threshold: Minimum confidence score to keep.
        custom_patterns: Extra regex patterns.

    Returns:
        A list of detected :class:`PIIEntity` instances.
    """
    engine = _resolve_engine(
        detect_types=detect_types,
        use_ner=use_ner,
        confidence_threshold=confidence_threshold,
        custom_patterns=custom_patterns,
    )
    return engine.scan_text(text)


def contains_pii(
    text: str,
    *,
    detect_types: list[PIIType | str] | None = None,
    use_ner: bool = False,
    confidence_threshold: float = 0.0,
    custom_patterns: list[dict] | None = None,
) -> bool:
    """Check whether a string contains any PII.

    Defaults to regex-only detection for speed. Pass ``use_ner=True``
    for NER-based detection at the cost of higher latency.

    Args:
        text: The text to check.
        detect_types: PII types to detect (``None`` = all).
        use_ner: Whether to use spaCy NER. Defaults to ``False``.
        confidence_threshold: Minimum confidence score to keep.
        custom_patterns: Extra regex patterns.

    Returns:
        ``True`` if any PII was detected.
    """
    entities = scan_text(
        text,
        detect_types=detect_types,
        use_ner=use_ner,
        confidence_threshold=confidence_threshold,
        custom_patterns=custom_patterns,
    )
    return len(entities) > 0


def scan(
    file_path: str | Path,
    *,
    detect_types: list[PIIType | str] | None = None,
    use_ner: bool = True,
    confidence_threshold: float = 0.0,
    custom_patterns: list[dict] | None = None,
) -> RedactionReport:
    """Scan a file for PII without redacting.

    Args:
        file_path: Path to the file to scan.
        detect_types: PII types to detect (``None`` = all).
        use_ner: Whether to use spaCy NER. Defaults to ``True``.
        confidence_threshold: Minimum confidence score to keep.
        custom_patterns: Extra regex patterns.

    Returns:
        A :class:`RedactionReport` with detected entities.
    """
    engine = _resolve_engine(
        detect_types=detect_types,
        use_ner=use_ner,
        confidence_threshold=confidence_threshold,
        custom_patterns=custom_patterns,
    )
    return engine.scan(Path(file_path))


def redact(
    file_path: str | Path,
    *,
    mode: RedactionMode | str = RedactionMode.BLACKOUT,
    output_path: str | Path | None = None,
    detect_types: list[PIIType | str] | None = None,
    use_ner: bool = True,
    confidence_threshold: float = 0.0,
    custom_patterns: list[dict] | None = None,
) -> RedactionReport:
    """Redact PII from a file.

    Args:
        file_path: Path to the file to redact.
        mode: Redaction mode (enum or string like ``"label"``).
        output_path: Output file path. Defaults to ``<name>.redacted.<ext>``.
        detect_types: PII types to detect (``None`` = all).
        use_ner: Whether to use spaCy NER. Defaults to ``True``.
        confidence_threshold: Minimum confidence score to keep.
        custom_patterns: Extra regex patterns.

    Returns:
        A :class:`RedactionReport` summarizing what was redacted.
    """
    engine = RedactionEngine(
        mode=mode,
        detect_types=detect_types,
        use_ner=use_ner,
        confidence_threshold=confidence_threshold,
        custom_patterns=custom_patterns,
    )
    out = Path(output_path) if output_path is not None else None
    return engine.redact(Path(file_path), output_path=out)
