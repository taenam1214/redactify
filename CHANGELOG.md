# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `TextResult` dataclass for in-memory text operations
- `RedactionEngine.scan_text()` method for scanning strings without file I/O
- `RedactionEngine.redact_text()` method for redacting strings without file I/O
- String-to-enum coercion: `RedactionEngine(mode="label")` and `detect_types=["email"]` now work
- Module-level convenience functions: `redact_text()`, `scan_text()`, `contains_pii()`, `scan()`, `redact()`
- Engine caching for convenience functions to avoid repeated initialization
- `MACAddressDetector` — detects MAC addresses (colon, dash, and Cisco dot formats)
- `IPv6Detector` — detects full and abbreviated IPv6 addresses
- `DriversLicenseDetector` — detects US drivers license numbers with context-aware matching

## [0.2.0] - 2026-06-04

### Added
- `--strict` flag for scan and redact: exit code 1 when PII is detected (CI/pre-commit)
- `--stream` flag for scan and redact: low-memory chunked processing for large files
- `--audit` flag for redact: write JSON audit trail of redactions
- `--json` shorthand flag for scan and redact
- Pre-commit hook configuration (`.pre-commit-hooks.yaml`)
- Streaming processor (`core/streaming.py`) for line-based chunked I/O
- `AuditTrail` model with hashed PII references (no PII in output)
- `make coverage` target for local HTML coverage reports

## [0.1.0] - 2025-06-01

### Added
- Core redaction engine with scan and redact operations
- Regex-based detectors: email, phone, SSN, credit card, IP address, date of birth
- spaCy NER detector for person names, organizations, and locations
- Custom pattern detector for user-defined regex patterns
- Composite detector with deduplication of overlapping entities
- Confidence threshold filtering
- Entity filters (by confidence, type, and length)
- Plain text parser with multi-encoding support
- PDF parser (PyMuPDF)
- DOCX parser (python-docx)
- HTML parser with tag stripping
- Four redaction modes: blackout, label, hash, custom
- CLI with `redact`, `scan`, `config`, and `supported` commands
- Batch directory processing with recursive support
- Dry-run mode for preview without writing
- Console, JSON, and summary reporters
- Configuration management via `.redactify.json`
- GitHub Actions CI pipeline
- PyPI publish workflow
- Comprehensive test suite
- API reference documentation
- Contributing guidelines
- Security policy
- Issue and PR templates
