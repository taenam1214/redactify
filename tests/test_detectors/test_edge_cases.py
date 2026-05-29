"""Edge case tests for detectors."""

import pytest

from redactify.core.detector import PIIEntity, PIIType
from redactify.detectors.regex import (
    CreditCardDetector,
    EmailDetector,
    IPAddressDetector,
    PhoneDetector,
    SSNDetector,
)


class TestEmailEdgeCases:
    def setup_method(self):
        self.detector = EmailDetector()

    def test_email_with_dots_in_local(self):
        entities = self.detector.detect("first.last@example.com")
        assert len(entities) == 1

    def test_email_with_subdomain(self):
        entities = self.detector.detect("user@mail.example.co.uk")
        assert len(entities) == 1

    def test_email_not_detected_in_url(self):
        # Should not match things that look like emails but aren't
        entities = self.detector.detect("Visit http://example.com for info")
        assert len(entities) == 0

    def test_multiple_emails_on_same_line(self):
        text = "CC: alice@test.com, bob@test.com, charlie@test.com"
        entities = self.detector.detect(text)
        assert len(entities) == 3

    def test_email_at_start_and_end(self):
        entities = self.detector.detect("start@test.com and end@test.com")
        assert len(entities) == 2


class TestPhoneEdgeCases:
    def setup_method(self):
        self.detector = PhoneDetector()

    def test_phone_with_dots(self):
        entities = self.detector.detect("Call 555.123.4567")
        assert len(entities) == 1

    def test_phone_with_spaces(self):
        entities = self.detector.detect("Call 555 123 4567")
        assert len(entities) == 1

    def test_phone_with_country_code(self):
        entities = self.detector.detect("Call +1 555 123 4567")
        assert len(entities) == 1


class TestSSNEdgeCases:
    def setup_method(self):
        self.detector = SSNDetector()

    def test_rejects_all_zeros_area(self):
        entities = self.detector.detect("000-12-3456")
        assert len(entities) == 0

    def test_rejects_all_zeros_group(self):
        entities = self.detector.detect("123-00-3456")
        assert len(entities) == 0

    def test_rejects_all_zeros_serial(self):
        entities = self.detector.detect("123-45-0000")
        assert len(entities) == 0

    def test_rejects_900_plus_area(self):
        entities = self.detector.detect("900-12-3456")
        assert len(entities) == 0
        entities = self.detector.detect("999-12-3456")
        assert len(entities) == 0


class TestCreditCardEdgeCases:
    def setup_method(self):
        self.detector = CreditCardDetector()

    def test_mastercard(self):
        # Valid Mastercard test number
        entities = self.detector.detect("5500 0000 0000 0004")
        assert len(entities) == 1

    def test_amex(self):
        # Valid Amex test number
        entities = self.detector.detect("3782 822463 10005")
        assert len(entities) == 1

    def test_random_digits_fail_luhn(self):
        entities = self.detector.detect("1234 5678 9012 3456")
        assert len(entities) == 0


class TestIPEdgeCases:
    def setup_method(self):
        self.detector = IPAddressDetector()

    def test_loopback(self):
        entities = self.detector.detect("localhost at 127.0.0.1")
        assert len(entities) == 1

    def test_broadcast(self):
        entities = self.detector.detect("broadcast: 255.255.255.255")
        assert len(entities) == 1

    def test_rejects_out_of_range(self):
        entities = self.detector.detect("256.1.1.1")
        assert len(entities) == 0

    def test_rejects_too_few_octets(self):
        entities = self.detector.detect("192.168.1")
        assert len(entities) == 0


class TestPIIEntityValidation:
    def test_rejects_negative_start(self):
        with pytest.raises(ValueError):
            PIIEntity(text="test", pii_type=PIIType.EMAIL, start=-1, end=4)

    def test_rejects_end_before_start(self):
        with pytest.raises(ValueError):
            PIIEntity(text="test", pii_type=PIIType.EMAIL, start=5, end=3)

    def test_rejects_confidence_above_1(self):
        with pytest.raises(ValueError):
            PIIEntity(text="test", pii_type=PIIType.EMAIL, start=0, end=4, confidence=1.5)

    def test_rejects_negative_confidence(self):
        with pytest.raises(ValueError):
            PIIEntity(text="test", pii_type=PIIType.EMAIL, start=0, end=4, confidence=-0.1)

    def test_frozen_dataclass(self):
        entity = PIIEntity(text="test", pii_type=PIIType.EMAIL, start=0, end=4)
        with pytest.raises(AttributeError):
            entity.text = "changed"
