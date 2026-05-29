"""Shared pytest fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_text():
    """Sample text with various PII types."""
    return (
        "Dear John Smith,\n"
        "Your email is john@example.com and phone is (555) 123-4567.\n"
        "SSN: 123-45-6789\n"
        "Card: 4111 1111 1111 1111\n"
        "IP: 192.168.1.1\n"
    )


@pytest.fixture
def clean_text():
    """Text with no PII."""
    return "The quick brown fox jumps over the lazy dog."
