"""Tests for regex-based PII detectors."""

from redactify.core.detector import PIIType
from redactify.detectors.regex import (
    CreditCardDetector,
    DateOfBirthDetector,
    DriversLicenseDetector,
    EmailDetector,
    IBANDetector,
    PassportDetector,
    URLDetector,
    IPAddressDetector,
    IPv6Detector,
    MACAddressDetector,
    PhoneDetector,
    SSNDetector,
)


class TestEmailDetector:
    def setup_method(self):
        self.detector = EmailDetector()

    def test_detects_simple_email(self):
        entities = self.detector.detect("Contact me at john@example.com please")
        assert len(entities) == 1
        assert entities[0].text == "john@example.com"
        assert entities[0].pii_type == PIIType.EMAIL

    def test_detects_multiple_emails(self):
        text = "Send to alice@test.org and bob@company.co.uk"
        entities = self.detector.detect(text)
        assert len(entities) == 2

    def test_detects_email_with_plus(self):
        entities = self.detector.detect("user+tag@gmail.com")
        assert len(entities) == 1
        assert entities[0].text == "user+tag@gmail.com"

    def test_no_false_positive_on_plain_text(self):
        entities = self.detector.detect("This is just a normal sentence.")
        assert len(entities) == 0


class TestPhoneDetector:
    def setup_method(self):
        self.detector = PhoneDetector()

    def test_detects_us_phone_with_dashes(self):
        entities = self.detector.detect("Call me at 555-123-4567")
        assert len(entities) == 1
        assert entities[0].pii_type == PIIType.PHONE

    def test_detects_us_phone_with_parens(self):
        entities = self.detector.detect("Phone: (555) 123-4567")
        assert len(entities) == 1

    def test_detects_international_phone(self):
        entities = self.detector.detect("Call +44 20 7946 0958")
        assert len(entities) == 1

    def test_no_false_positive(self):
        entities = self.detector.detect("The year 2024 was great.")
        assert len(entities) == 0


class TestSSNDetector:
    def setup_method(self):
        self.detector = SSNDetector()

    def test_detects_ssn_with_dashes(self):
        entities = self.detector.detect("SSN: 123-45-6789")
        assert len(entities) == 1
        assert entities[0].pii_type == PIIType.SSN

    def test_detects_ssn_without_dashes(self):
        entities = self.detector.detect("SSN: 123456789")
        assert len(entities) == 1

    def test_rejects_invalid_ssn_000(self):
        entities = self.detector.detect("SSN: 000-12-3456")
        assert len(entities) == 0

    def test_rejects_invalid_ssn_666(self):
        entities = self.detector.detect("SSN: 666-12-3456")
        assert len(entities) == 0


class TestCreditCardDetector:
    def setup_method(self):
        self.detector = CreditCardDetector()

    def test_detects_visa(self):
        # Valid Visa test number
        entities = self.detector.detect("Card: 4111 1111 1111 1111")
        assert len(entities) == 1
        assert entities[0].pii_type == PIIType.CREDIT_CARD

    def test_detects_with_dashes(self):
        entities = self.detector.detect("Card: 4111-1111-1111-1111")
        assert len(entities) == 1

    def test_rejects_invalid_luhn(self):
        entities = self.detector.detect("Card: 4111 1111 1111 1112")
        assert len(entities) == 0


class TestIPAddressDetector:
    def setup_method(self):
        self.detector = IPAddressDetector()

    def test_detects_valid_ip(self):
        entities = self.detector.detect("Server at 192.168.1.1")
        assert len(entities) == 1
        assert entities[0].text == "192.168.1.1"
        assert entities[0].pii_type == PIIType.IP_ADDRESS

    def test_rejects_invalid_ip(self):
        entities = self.detector.detect("Not an IP: 999.999.999.999")
        assert len(entities) == 0

    def test_detects_multiple_ips(self):
        text = "From 10.0.0.1 to 172.16.0.1"
        entities = self.detector.detect(text)
        assert len(entities) == 2


class TestURLDetector:
    def setup_method(self):
        self.detector = URLDetector()

    def test_detects_url_with_email(self):
        text = "Visit https://example.com/user/john@example.com/profile"
        entities = self.detector.detect(text)
        assert len(entities) == 1
        assert entities[0].pii_type == PIIType.URL

    def test_detects_url_with_user_path(self):
        text = "API: https://api.example.com/users/john_doe"
        entities = self.detector.detect(text)
        assert len(entities) == 1

    def test_detects_url_with_pii_query_param(self):
        text = "Link: https://site.com/search?email=john@test.com&page=1"
        entities = self.detector.detect(text)
        assert len(entities) == 1

    def test_detects_url_with_token_param(self):
        text = "Reset: https://app.com/reset?token=abc123&user=admin"
        entities = self.detector.detect(text)
        assert len(entities) == 1

    def test_ignores_safe_url(self):
        text = "Visit https://www.google.com/search?q=python"
        entities = self.detector.detect(text)
        assert len(entities) == 0

    def test_ignores_plain_text(self):
        entities = self.detector.detect("No URLs here at all.")
        assert len(entities) == 0

    def test_detects_url_with_account_path(self):
        text = "https://bank.com/account/123456789/statements"
        entities = self.detector.detect(text)
        assert len(entities) == 1

    def test_confidence_is_07(self):
        text = "https://example.com/users/admin"
        entities = self.detector.detect(text)
        assert len(entities) == 1
        assert entities[0].confidence == 0.7


class TestPassportDetector:
    def setup_method(self):
        self.detector = PassportDetector()

    def test_detects_us_passport(self):
        text = "Passport number: 123456789"
        entities = self.detector.detect(text)
        assert len(entities) >= 1
        assert entities[0].pii_type == PIIType.PASSPORT

    def test_detects_eu_passport(self):
        text = "Passport no AB1234567"
        entities = self.detector.detect(text)
        assert len(entities) >= 1

    def test_detects_uk_format(self):
        text = "Travel document: 987654321"
        entities = self.detector.detect(text)
        assert len(entities) >= 1

    def test_no_match_without_context(self):
        # 9 digits alone without passport context should not match
        text = "The order number is 123456789."
        entities = self.detector.detect(text)
        assert len(entities) == 0

    def test_no_match_on_plain_text(self):
        entities = self.detector.detect("This is just a normal sentence.")
        assert len(entities) == 0

    def test_confidence_is_08(self):
        text = "Passport: 123456789"
        entities = self.detector.detect(text)
        assert len(entities) >= 1
        assert entities[0].confidence == 0.8

    def test_case_insensitive_context(self):
        text = "PASSPORT NUMBER: 123456789"
        entities = self.detector.detect(text)
        assert len(entities) >= 1


class TestIBANDetector:
    def setup_method(self):
        self.detector = IBANDetector()

    def test_detects_german_iban(self):
        text = "Pay to DE89370400440532013000"
        entities = self.detector.detect(text)
        assert len(entities) == 1
        assert entities[0].text == "DE89370400440532013000"
        assert entities[0].pii_type == PIIType.IBAN

    def test_detects_british_iban(self):
        text = "Account: GB29NWBK60161331926819"
        entities = self.detector.detect(text)
        assert len(entities) == 1

    def test_detects_french_iban(self):
        text = "IBAN: FR7630006000011234567890189"
        entities = self.detector.detect(text)
        assert len(entities) == 1

    def test_detects_iban_with_spaces(self):
        text = "Transfer to DE89 3704 0044 0532 0130 00"
        entities = self.detector.detect(text)
        assert len(entities) == 1

    def test_rejects_invalid_checksum(self):
        # DE00 would fail mod-97
        text = "Account: DE00370400440532013000"
        entities = self.detector.detect(text)
        assert len(entities) == 0

    def test_rejects_wrong_length(self):
        # DE IBANs must be 22 chars, this is too short
        text = "Account: DE8937040044053"
        entities = self.detector.detect(text)
        assert len(entities) == 0

    def test_no_false_positive_on_plain_text(self):
        entities = self.detector.detect("This is just a normal sentence.")
        assert len(entities) == 0

    def test_detects_multiple_ibans(self):
        text = "From DE89370400440532013000 to GB29NWBK60161331926819"
        entities = self.detector.detect(text)
        assert len(entities) == 2


class TestIPv6Detector:
    def setup_method(self):
        self.detector = IPv6Detector()

    def test_detects_full_ipv6(self):
        entities = self.detector.detect("Address: 2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        assert len(entities) == 1
        assert entities[0].text == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        assert entities[0].pii_type == PIIType.IPV6

    def test_detects_abbreviated_ipv6(self):
        entities = self.detector.detect("Gateway: 2001:db8::1")
        assert len(entities) == 1

    def test_detects_loopback(self):
        entities = self.detector.detect("Loopback: ::1")
        assert len(entities) == 1
        assert entities[0].text == "::1"

    def test_detects_link_local(self):
        entities = self.detector.detect("Link-local: fe80::200:5eff:fe00:5312")
        assert len(entities) == 1

    def test_detects_multiple_ipv6(self):
        text = "From 2001:db8::1 to 2001:db8::2"
        entities = self.detector.detect(text)
        assert len(entities) == 2

    def test_no_false_positive_on_plain_text(self):
        entities = self.detector.detect("This is just a normal sentence.")
        assert len(entities) == 0

    def test_does_not_match_mac_address(self):
        # MAC addresses use different format - should not trigger IPv6
        entities = self.detector.detect("MAC: 00:1A:2B:3C:4D:5E")
        assert len(entities) == 0


class TestMACAddressDetector:
    def setup_method(self):
        self.detector = MACAddressDetector()

    def test_detects_colon_format(self):
        entities = self.detector.detect("NIC: 00:1A:2B:3C:4D:5E")
        assert len(entities) == 1
        assert entities[0].text == "00:1A:2B:3C:4D:5E"
        assert entities[0].pii_type == PIIType.MAC_ADDRESS

    def test_detects_dash_format(self):
        entities = self.detector.detect("MAC: AA-BB-CC-DD-EE-FF")
        assert len(entities) == 1
        assert entities[0].text == "AA-BB-CC-DD-EE-FF"

    def test_detects_cisco_dot_format(self):
        entities = self.detector.detect("Interface: 0011.2233.4455")
        assert len(entities) == 1
        assert entities[0].text == "0011.2233.4455"

    def test_detects_multiple_macs(self):
        text = "From 00:1A:2B:3C:4D:5E to AA-BB-CC-DD-EE-FF"
        entities = self.detector.detect(text)
        assert len(entities) == 2

    def test_detects_lowercase(self):
        entities = self.detector.detect("mac: aa:bb:cc:dd:ee:ff")
        assert len(entities) == 1

    def test_no_false_positive_on_plain_text(self):
        entities = self.detector.detect("This is just a normal sentence.")
        assert len(entities) == 0

    def test_rejects_partial_mac(self):
        entities = self.detector.detect("Partial: 00:1A:2B")
        assert len(entities) == 0

    def test_rejects_invalid_hex(self):
        entities = self.detector.detect("Bad: ZZ:ZZ:ZZ:ZZ:ZZ:ZZ")
        assert len(entities) == 0


class TestDateOfBirthDetector:
    def setup_method(self):
        self.detector = DateOfBirthDetector()

    def test_detects_dob_with_context(self):
        text = "Date of birth: 01/15/1990"
        entities = self.detector.detect(text)
        assert len(entities) == 1
        assert entities[0].confidence == 0.9

    def test_lower_confidence_without_context(self):
        text = "The date was 03/25/2020 when we met."
        entities = self.detector.detect(text)
        if entities:
            assert entities[0].confidence == 0.5

    def test_detects_written_date(self):
        text = "Born on January 15, 1990"
        entities = self.detector.detect(text)
        assert len(entities) == 1


class TestDriversLicenseDetectorBasic:
    def setup_method(self):
        self.detector = DriversLicenseDetector()

    def test_detects_california_format(self):
        text = "Driver's license: D1234567"
        entities = self.detector.detect(text)
        assert len(entities) >= 1
        assert entities[0].pii_type == PIIType.DRIVERS_LICENSE

    def test_detects_florida_format(self):
        text = "DL# F123456789012"
        entities = self.detector.detect(text)
        assert len(entities) >= 1

    def test_detects_ohio_format(self):
        text = "License number: AB123456"
        entities = self.detector.detect(text)
        assert len(entities) >= 1

    def test_detects_texas_format(self):
        text = "DL: 12345678"
        entities = self.detector.detect(text)
        assert len(entities) >= 1

    def test_confidence_is_08(self):
        text = "Driver's license: D1234567"
        entities = self.detector.detect(text)
        assert len(entities) >= 1
        assert entities[0].confidence == 0.8


class TestDriversLicenseDetectorStateFormats:
    """Test detection of state-specific DL formats."""

    def setup_method(self):
        self.detector = DriversLicenseDetector()

    def test_washington_wdl_prefix(self):
        text = "Driver's license WDL123ABC4567"
        entities = self.detector.detect(text)
        assert len(entities) >= 1
        assert any("WDL" in e.text for e in entities)

    def test_illinois_format(self):
        # 1 letter + 11 digits
        text = "License: B12345678901"
        entities = self.detector.detect(text)
        assert len(entities) >= 1

    def test_multiple_formats_in_one_text(self):
        text = "Driver's license D1234567, also DL# AB123456"
        entities = self.detector.detect(text)
        assert len(entities) >= 2

    def test_case_insensitive_context(self):
        text = "DRIVER'S LICENSE: D1234567"
        entities = self.detector.detect(text)
        assert len(entities) >= 1

    def test_dl_abbreviation_context(self):
        text = "DL D1234567"
        entities = self.detector.detect(text)
        assert len(entities) >= 1


class TestDriversLicenseDetectorNegative:
    """Test that the DL detector avoids false positives."""

    def setup_method(self):
        self.detector = DriversLicenseDetector()

    def test_no_match_without_context(self):
        # Same pattern as CA DL, but no license context keywords
        text = "Product code D1234567 is in stock."
        entities = self.detector.detect(text)
        assert len(entities) == 0

    def test_no_match_on_plain_sentence(self):
        entities = self.detector.detect("This is a totally normal sentence.")
        assert len(entities) == 0

    def test_no_match_random_digits(self):
        text = "The year 2024 and temperature 72 degrees."
        entities = self.detector.detect(text)
        assert len(entities) == 0

    def test_no_match_short_numbers_without_context(self):
        text = "Order #12345678 confirmed."
        entities = self.detector.detect(text)
        assert len(entities) == 0

    def test_no_duplicate_entities(self):
        # Ensure overlapping patterns don't produce duplicates
        text = "License: D1234567"
        entities = self.detector.detect(text)
        starts = [(e.start, e.end) for e in entities]
        assert len(starts) == len(set(starts))
