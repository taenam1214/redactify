"""Regex-based PII detectors."""

import re

from redactify.core.detector import BaseDetector, PIIEntity, PIIType


class EmailDetector(BaseDetector):
    """Detects email addresses using regex."""

    PATTERN = re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    )

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.PATTERN.finditer(text):
            entities.append(
                PIIEntity(
                    text=match.group(),
                    pii_type=PIIType.EMAIL,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.EMAIL]


class PhoneDetector(BaseDetector):
    """Detects phone numbers (US and international formats)."""

    PATTERN = re.compile(
        r"(?:"
        r"\+?1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"  # US format
        r"|"
        r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"  # International
        r"|"
        r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"  # Simple US
        r")"
    )

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.PATTERN.finditer(text):
            entities.append(
                PIIEntity(
                    text=match.group(),
                    pii_type=PIIType.PHONE,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.PHONE]


class SSNDetector(BaseDetector):
    """Detects US Social Security Numbers."""

    PATTERN = re.compile(
        r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b"
    )

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.PATTERN.finditer(text):
            raw = re.sub(r"[-.\s]", "", match.group())
            # Filter out obviously invalid SSNs
            if raw[0:3] == "000" or raw[3:5] == "00" or raw[5:9] == "0000":
                continue
            if raw[0:3] == "666" or int(raw[0:3]) >= 900:
                continue
            entities.append(
                PIIEntity(
                    text=match.group(),
                    pii_type=PIIType.SSN,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.SSN]


class CreditCardDetector(BaseDetector):
    """Detects credit card numbers with Luhn validation."""

    PATTERN = re.compile(
        r"\b(?:\d[ -]*?){13,19}\b"
    )

    @staticmethod
    def _luhn_check(number: str) -> bool:
        """Validate a credit card number using the Luhn algorithm."""
        digits = [int(d) for d in number if d.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        checksum = 0
        reverse_digits = digits[::-1]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        return checksum % 10 == 0

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.PATTERN.finditer(text):
            raw = re.sub(r"[-\s]", "", match.group())
            if self._luhn_check(raw):
                entities.append(
                    PIIEntity(
                        text=match.group(),
                        pii_type=PIIType.CREDIT_CARD,
                        start=match.start(),
                        end=match.end(),
                    )
                )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.CREDIT_CARD]


class IPAddressDetector(BaseDetector):
    """Detects IPv4 addresses."""

    PATTERN = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    )

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.PATTERN.finditer(text):
            entities.append(
                PIIEntity(
                    text=match.group(),
                    pii_type=PIIType.IP_ADDRESS,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.IP_ADDRESS]


class DateOfBirthDetector(BaseDetector):
    """Detects dates that may be dates of birth based on context."""

    PATTERN = re.compile(
        r"\b(?:"
        r"\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}"  # MM/DD/YYYY or DD/MM/YYYY
        r"|"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
        r"|"
        r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4}"
        r")\b",
        re.IGNORECASE,
    )

    CONTEXT_KEYWORDS = {"born", "birth", "dob", "birthday", "date of birth", "b."}

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        text_lower = text.lower()
        for match in self.PATTERN.finditer(text):
            # Check surrounding context for birth-related keywords
            context_start = max(0, match.start() - 50)
            context_end = min(len(text), match.end() + 50)
            context = text_lower[context_start:context_end]

            if any(keyword in context for keyword in self.CONTEXT_KEYWORDS):
                confidence = 0.9
            else:
                confidence = 0.5

            entities.append(
                PIIEntity(
                    text=match.group(),
                    pii_type=PIIType.DATE_OF_BIRTH,
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.DATE_OF_BIRTH]
