"""Benchmark individual detectors on synthetic corpus."""

import time
import random
import string


def generate_corpus(n_lines: int = 10_000) -> str:
    """Generate a synthetic corpus with scattered PII."""
    lines = []
    emails = ["alice@example.com", "bob@corp.co.uk", "carol+test@gmail.com"]
    phones = ["555-123-4567", "(800) 555-0199", "+1-212-555-0100"]
    ssns = ["123-45-6789", "234-56-7890", "345-67-8901"]

    for i in range(n_lines):
        if i % 50 == 0:
            lines.append(f"Contact {random.choice(emails)} for details.")
        elif i % 70 == 0:
            lines.append(f"Call {random.choice(phones)} now.")
        elif i % 90 == 0:
            lines.append(f"SSN: {random.choice(ssns)}")
        else:
            words = " ".join(
                "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
                for _ in range(random.randint(5, 15))
            )
            lines.append(words)
    return "\n".join(lines)


def bench_detector(detector, text: str, label: str) -> None:
    """Time a single detector over the given text."""
    start = time.perf_counter()
    entities = detector.detect(text)
    elapsed = time.perf_counter() - start
    print(f"  {label:30s}  {len(entities):5d} entities  {elapsed:.3f}s")


def main():
    from redactify.detectors.regex import (
        EmailDetector, PhoneDetector, SSNDetector,
        CreditCardDetector, IPAddressDetector, DateOfBirthDetector,
        IBANDetector, MACAddressDetector, IPv6Detector,
        URLDetector, PassportDetector, DriversLicenseDetector,
    )

    print("Generating 10,000-line corpus...")
    corpus = generate_corpus(10_000)
    print(f"Corpus size: {len(corpus):,} chars\n")

    detectors = [
        (EmailDetector(), "EmailDetector"),
        (PhoneDetector(), "PhoneDetector"),
        (SSNDetector(), "SSNDetector"),
        (CreditCardDetector(), "CreditCardDetector"),
        (IPAddressDetector(), "IPAddressDetector"),
        (DateOfBirthDetector(), "DateOfBirthDetector"),
        (IBANDetector(), "IBANDetector"),
        (MACAddressDetector(), "MACAddressDetector"),
        (IPv6Detector(), "IPv6Detector"),
        (URLDetector(), "URLDetector"),
        (PassportDetector(), "PassportDetector"),
        (DriversLicenseDetector(), "DriversLicenseDetector"),
    ]

    print("Detector benchmarks:")
    for detector, label in detectors:
        bench_detector(detector, corpus, label)


if __name__ == "__main__":
    main()
