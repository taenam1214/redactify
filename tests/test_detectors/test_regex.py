"""Tests for regex-based PII detectors."""

from redactify.core.detector import PIIType
from redactify.detectors.regex import (
    CreditCardDetector,
    DateOfBirthDetector,
    DriversLicenseDetector,
    EmailDetector,
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
