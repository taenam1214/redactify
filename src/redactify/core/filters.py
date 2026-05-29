"""Filters for post-processing detected entities."""

from redactify.core.detector import PIIEntity, PIIType


def filter_by_confidence(entities: list[PIIEntity], threshold: float = 0.5) -> list[PIIEntity]:
    """Filter entities below a confidence threshold."""
    return [e for e in entities if e.confidence >= threshold]


def filter_by_type(entities: list[PIIEntity], include_types: list[PIIType]) -> list[PIIEntity]:
    """Keep only entities matching the specified types."""
    type_set = set(include_types)
    return [e for e in entities if e.pii_type in type_set]


def filter_by_min_length(entities: list[PIIEntity], min_length: int = 2) -> list[PIIEntity]:
    """Filter out entities shorter than min_length."""
    return [e for e in entities if len(e.text) >= min_length]
