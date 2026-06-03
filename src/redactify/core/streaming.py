"""Streaming processor for large files — processes text in chunks without loading fully into memory."""

from pathlib import Path
from typing import Generator

from redactify.core.detector import PIIEntity
from redactify.core.filters import filter_by_confidence
from redactify.core.redactor import Redactor
from redactify.detectors.composite import CompositeDetector

# Default chunk size: 1000 lines per chunk
DEFAULT_CHUNK_LINES = 1000


def iter_line_chunks(file_path: Path, chunk_lines: int = DEFAULT_CHUNK_LINES) -> Generator[str, None, None]:
    """Read a text file in chunks of N lines.

    Args:
        file_path: Path to the text file.
        chunk_lines: Number of lines per chunk.

    Yields:
        String chunks of the file content.
    """
    buffer: list[str] = []
    with open(file_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            buffer.append(line)
            if len(buffer) >= chunk_lines:
                yield "".join(buffer)
                buffer = []
    if buffer:
        yield "".join(buffer)


def stream_scan(
    file_path: Path,
    detector: CompositeDetector,
    confidence_threshold: float = 0.0,
    chunk_lines: int = DEFAULT_CHUNK_LINES,
) -> list[PIIEntity]:
    """Scan a file for PII using streaming chunks.

    Args:
        file_path: Path to the text file.
        detector: Composite detector to use.
        confidence_threshold: Minimum confidence filter.
        chunk_lines: Lines per processing chunk.

    Returns:
        List of all detected PIIEntity objects.
    """
    all_entities: list[PIIEntity] = []
    offset = 0

    for chunk in iter_line_chunks(file_path, chunk_lines):
        entities = detector.detect(chunk)
        if confidence_threshold > 0:
            entities = filter_by_confidence(entities, confidence_threshold)
        # Adjust entity positions to file-level offsets
        for entity in entities:
            adjusted = PIIEntity(
                text=entity.text,
                pii_type=entity.pii_type,
                start=entity.start + offset,
                end=entity.end + offset,
                confidence=entity.confidence,
            )
            all_entities.append(adjusted)
        offset += len(chunk)

    return all_entities


def stream_redact(
    file_path: Path,
    output_path: Path,
    detector: CompositeDetector,
    redactor: Redactor,
    confidence_threshold: float = 0.0,
    chunk_lines: int = DEFAULT_CHUNK_LINES,
) -> list[PIIEntity]:
    """Redact PII from a file using streaming chunks.

    Processes line by line in chunks, writing redacted output incrementally.

    Args:
        file_path: Path to the input file.
        output_path: Path for the redacted output.
        detector: Composite detector to use.
        redactor: Redactor instance for replacements.
        confidence_threshold: Minimum confidence filter.
        chunk_lines: Lines per processing chunk.

    Returns:
        List of all detected PIIEntity objects.
    """
    all_entities: list[PIIEntity] = []
    offset = 0

    with open(output_path, "w", encoding="utf-8") as out_f:
        for chunk in iter_line_chunks(file_path, chunk_lines):
            entities = detector.detect(chunk)
            if confidence_threshold > 0:
                entities = filter_by_confidence(entities, confidence_threshold)
            # Track entities with file-level offsets
            for entity in entities:
                adjusted = PIIEntity(
                    text=entity.text,
                    pii_type=entity.pii_type,
                    start=entity.start + offset,
                    end=entity.end + offset,
                    confidence=entity.confidence,
                )
                all_entities.append(adjusted)
            # Write redacted chunk
            redacted = redactor.redact(chunk, entities)
            out_f.write(redacted)
            offset += len(chunk)

    return all_entities
