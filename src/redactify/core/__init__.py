"""Core module — engine, detector, redactor, and filters."""

from redactify.core.allowlist import Allowlist
from redactify.core.detector import BaseDetector, PIIEntity, PIIType
from redactify.core.engine import RedactionEngine
from redactify.core.filters import filter_by_confidence, filter_by_min_length, filter_by_type
from redactify.core.redactor import Redactor, RedactionMode
from redactify.core.results import TextResult

__all__ = [
    "Allowlist",
    "BaseDetector",
    "PIIEntity",
    "PIIType",
    "RedactionEngine",
    "RedactionMode",
    "Redactor",
    "TextResult",
    "filter_by_confidence",
    "filter_by_min_length",
    "filter_by_type",
]
