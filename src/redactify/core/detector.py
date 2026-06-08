"""Base detector interface for PII detection."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class PIIType(Enum):
    """Types of personally identifiable information."""

    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    MAC_ADDRESS = "mac_address"
    IPV6 = "ipv6"
    DRIVERS_LICENSE = "drivers_license"
    CUSTOM = "custom"


@dataclass(frozen=True)
class PIIEntity:
    """A detected PII entity with its location and metadata."""

    text: str
    pii_type: PIIType
    start: int
    end: int
    confidence: float = 1.0

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.start < 0 or self.end < self.start:
            raise ValueError("Invalid start/end positions")


class BaseDetector(ABC):
    """Abstract base class for PII detectors."""

    @abstractmethod
    def detect(self, text: str) -> list[PIIEntity]:
        """Detect PII entities in the given text.

        Args:
            text: The text to scan for PII.

        Returns:
            A list of detected PII entities.
        """
        ...

    @property
    @abstractmethod
    def supported_types(self) -> list[PIIType]:
        """Return the PII types this detector can identify."""
        ...
