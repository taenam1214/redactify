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


class URLDetector(BaseDetector):
    """Detects URLs that may contain PII in their path or query parameters.

    Flags URLs containing indicators of personal data such as email addresses,
    names, IDs, or tokens in paths/query strings.
    """

    # Match HTTP/HTTPS URLs
    URL_PATTERN = re.compile(
        r"https?://[^\s<>\"']+",
        re.IGNORECASE,
    )

    # PII indicators that suggest a URL contains personal information
    PII_PATH_INDICATORS = re.compile(
        r"(?:"
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"  # email in URL
        r"|/users?/[^/\s]+"  # /user/username or /users/id
        r"|/profiles?/[^/\s]+"  # /profile/name
        r"|/accounts?/[^/\s]+"  # /account/id
        r"|[?&](?:email|name|user|ssn|phone|token|key|secret|password|api_key)="  # PII query params
        r")",
        re.IGNORECASE,
    )

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.URL_PATTERN.finditer(text):
            url = match.group()
            # Only flag URLs that contain PII indicators
            if self.PII_PATH_INDICATORS.search(url):
                entities.append(
                    PIIEntity(
                        text=url,
                        pii_type=PIIType.URL,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.7,
                    )
                )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.URL]


class PassportDetector(BaseDetector):
    """Detects passport numbers using context keywords and country-specific formats."""

    # Patterns for common passport formats
    PASSPORT_PATTERNS: list[re.Pattern] = [
        # US: 9 digits
        re.compile(r"\b\d{9}\b"),
        # UK: 9 digits (same format, but context differentiates)
        # EU / generic: 1-2 letters + 6-7 digits
        re.compile(r"\b[A-Z]{1,2}\d{6,7}\b"),
        # Some countries: 2 letters + 7 digits
        re.compile(r"\b[A-Z]{2}\d{7}\b"),
    ]

    CONTEXT_KEYWORDS = {
        "passport", "passport#", "passport no", "passport number",
        "travel document", "travel doc",
    }

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        text_lower = text.lower()

        # Only look for passport numbers if context keywords are present
        has_context = any(kw in text_lower for kw in self.CONTEXT_KEYWORDS)
        if not has_context:
            return entities

        for pattern in self.PASSPORT_PATTERNS:
            for match in pattern.finditer(text):
                # Check local context around the match
                context_start = max(0, match.start() - 60)
                context_end = min(len(text), match.end() + 30)
                context = text_lower[context_start:context_end]

                if any(kw in context for kw in self.CONTEXT_KEYWORDS):
                    entity = PIIEntity(
                        text=match.group(),
                        pii_type=PIIType.PASSPORT,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.8,
                    )
                    # Avoid duplicates from overlapping patterns
                    if not any(
                        e.start == entity.start and e.end == entity.end
                        for e in entities
                    ):
                        entities.append(entity)

        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.PASSPORT]


class IBANDetector(BaseDetector):
    """Detects International Bank Account Numbers with mod-97 validation."""

    # IBAN: 2 uppercase letters (country) + 2 check digits + up to 30 alphanumeric (BBAN)
    PATTERN = re.compile(
        r"\b([A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?(?:[A-Z0-9]{4}[\s]?){1,7}[A-Z0-9]{1,4})\b"
    )

    # Known IBAN lengths by country code
    COUNTRY_LENGTHS: dict[str, int] = {
        "AL": 28, "AD": 24, "AT": 20, "AZ": 28, "BH": 22, "BY": 28,
        "BE": 16, "BA": 20, "BR": 29, "BG": 22, "CR": 22, "HR": 21,
        "CY": 28, "CZ": 24, "DK": 18, "DO": 28, "TL": 23, "EE": 20,
        "FO": 18, "FI": 18, "FR": 27, "GE": 22, "DE": 22, "GI": 23,
        "GR": 27, "GL": 18, "GT": 28, "HU": 28, "IS": 26, "IQ": 23,
        "IE": 22, "IL": 23, "IT": 27, "JO": 30, "KZ": 20, "XK": 20,
        "KW": 30, "LV": 21, "LB": 28, "LI": 21, "LT": 20, "LU": 20,
        "MT": 31, "MR": 27, "MU": 30, "MC": 27, "MD": 24, "ME": 22,
        "NL": 18, "MK": 19, "NO": 15, "PK": 24, "PS": 29, "PL": 28,
        "PT": 25, "QA": 29, "RO": 24, "LC": 32, "SM": 27, "SA": 24,
        "RS": 22, "SC": 31, "SK": 24, "SI": 19, "ES": 24, "SE": 24,
        "CH": 21, "TN": 24, "TR": 26, "UA": 29, "AE": 23, "GB": 22,
        "VA": 22, "VG": 24,
    }

    @staticmethod
    def _mod97_check(iban: str) -> bool:
        """Validate IBAN using the mod-97 algorithm (ISO 7064)."""
        # Remove spaces and move first 4 chars to end
        clean = iban.replace(" ", "")
        rearranged = clean[4:] + clean[:4]
        # Convert letters to numbers (A=10, B=11, ..., Z=35)
        numeric = ""
        for ch in rearranged:
            if ch.isdigit():
                numeric += ch
            else:
                numeric += str(ord(ch) - ord("A") + 10)
        return int(numeric) % 97 == 1

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.PATTERN.finditer(text):
            iban = match.group(1).replace(" ", "")
            country = iban[:2]

            # Validate length for known countries
            if country in self.COUNTRY_LENGTHS:
                if len(iban) != self.COUNTRY_LENGTHS[country]:
                    continue

            # Validate mod-97 checksum
            if not self._mod97_check(iban):
                continue

            entities.append(
                PIIEntity(
                    text=match.group(1),
                    pii_type=PIIType.IBAN,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.IBAN]


class MACAddressDetector(BaseDetector):
    """Detects MAC addresses in common formats."""

    PATTERN = re.compile(
        r"\b(?:"
        r"[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}"  # AA:BB:CC:DD:EE:FF
        r"|"
        r"[0-9A-Fa-f]{2}(?:-[0-9A-Fa-f]{2}){5}"  # AA-BB-CC-DD-EE-FF
        r"|"
        r"[0-9A-Fa-f]{4}(?:\.[0-9A-Fa-f]{4}){2}"  # AABB.CCDD.EEFF (Cisco)
        r")\b"
    )

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.PATTERN.finditer(text):
            entities.append(
                PIIEntity(
                    text=match.group(),
                    pii_type=PIIType.MAC_ADDRESS,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.MAC_ADDRESS]


class IPv6Detector(BaseDetector):
    """Detects IPv6 addresses in full and abbreviated formats."""

    # Full form: 8 groups of 4 hex digits separated by colons
    # Abbreviated: contains :: for zero compression
    # Requires at least two colon-separated hex groups to avoid matching
    # short hex strings. Uses negative lookbehind/lookahead to avoid
    # matching inside MAC addresses (which use single-octet hex groups).
    PATTERN = re.compile(
        r"(?<![0-9A-Fa-f]:)"  # not preceded by hex:
        r"\b("
        # Full 8-group form
        r"(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}"
        r"|"
        # :: at the start
        r"::(?:[0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4}"
        r"|"
        # :: at the end
        r"(?:[0-9A-Fa-f]{1,4}:){1,6}:"
        r"|"
        # :: in the middle
        r"(?:[0-9A-Fa-f]{1,4}:){1,5}:[0-9A-Fa-f]{1,4}"
        r"|"
        r"(?:[0-9A-Fa-f]{1,4}:){1,4}(?::[0-9A-Fa-f]{1,4}){1,2}"
        r"|"
        r"(?:[0-9A-Fa-f]{1,4}:){1,3}(?::[0-9A-Fa-f]{1,4}){1,3}"
        r"|"
        r"(?:[0-9A-Fa-f]{1,4}:){1,2}(?::[0-9A-Fa-f]{1,4}){1,4}"
        r"|"
        r"[0-9A-Fa-f]{1,4}:(?::[0-9A-Fa-f]{1,4}){1,5}"
        r"|"
        # Loopback
        r"::1"
        r"|"
        # Unspecified
        r"::"
        r")\b"
        r"(?!:[0-9A-Fa-f])"  # not followed by :hex
    )

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        for match in self.PATTERN.finditer(text):
            entities.append(
                PIIEntity(
                    text=match.group(),
                    pii_type=PIIType.IPV6,
                    start=match.start(),
                    end=match.end(),
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.IPV6]


class DriversLicenseDetector(BaseDetector):
    """Detects US drivers license numbers using state-specific patterns.

    Uses context keywords (driver, license, DL, etc.) combined with
    state-prefix patterns to reduce false positives.
    """

    # State-specific DL patterns (state code prefix + format)
    # Covers the most common US state formats
    STATE_PATTERNS: list[re.Pattern] = [
        # California: 1 letter + 7 digits
        re.compile(r"\b[A-Z]\d{7}\b"),
        # New York: 3 digits + 3 spaces + 3 digits + 3 spaces + 3 digits (or no spaces)
        re.compile(r"\b\d{3}[-\s]?\d{3}[-\s]?\d{3}\b"),
        # Texas: 8 digits
        re.compile(r"\b\d{8}\b"),
        # Florida: 1 letter + 12 digits
        re.compile(r"\b[A-Z]\d{12}\b"),
        # Illinois: 1 letter + 11 digits
        re.compile(r"\b[A-Z]\d{11}\b"),
        # Pennsylvania: 2 digits + 6 digits (8 total)
        re.compile(r"\b\d{2}[-\s]?\d{3}[-\s]?\d{3}\b"),
        # Ohio: 2 letters + 6 digits
        re.compile(r"\b[A-Z]{2}\d{6}\b"),
        # Michigan: 1 letter + 12 digits
        re.compile(r"\b[A-Z]\d{12}\b"),
        # Washington: prefix WDL + 9-12 chars
        re.compile(r"\bWDL[A-Z0-9*]{9,12}\b"),
    ]

    CONTEXT_KEYWORDS = {
        "driver", "license", "licence", "dl", "d.l.", "driver's",
        "driving", "dmv", "motor vehicle", "dl#", "dl no",
    }

    def detect(self, text: str) -> list[PIIEntity]:
        entities = []
        text_lower = text.lower()

        # Only look for DL numbers if context keywords are present
        has_context = any(kw in text_lower for kw in self.CONTEXT_KEYWORDS)
        if not has_context:
            return entities

        for pattern in self.STATE_PATTERNS:
            for match in pattern.finditer(text):
                # Check local context around the match
                context_start = max(0, match.start() - 60)
                context_end = min(len(text), match.end() + 30)
                context = text_lower[context_start:context_end]

                if any(kw in context for kw in self.CONTEXT_KEYWORDS):
                    entity = PIIEntity(
                        text=match.group(),
                        pii_type=PIIType.DRIVERS_LICENSE,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.8,
                    )
                    # Avoid duplicates from overlapping patterns
                    if not any(
                        e.start == entity.start and e.end == entity.end
                        for e in entities
                    ):
                        entities.append(entity)

        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.DRIVERS_LICENSE]


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
