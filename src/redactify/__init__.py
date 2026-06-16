"""Redactify — Privacy-preserving document redaction tool."""

__version__ = "0.2.0"

from redactify.api import contains_pii, redact, redact_text, scan, scan_text
from redactify.core.allowlist import Allowlist
from redactify.core.audit import AuditTrail
from redactify.core.detector import PIIEntity, PIIType
from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode, Redactor
from redactify.core.results import TextResult

__all__ = [
    "Allowlist",
    "AuditTrail",
    "PIIEntity",
    "PIIType",
    "RedactionEngine",
    "RedactionMode",
    "Redactor",
    "TextResult",
    "contains_pii",
    "redact",
    "redact_text",
    "scan",
    "scan_text",
]
