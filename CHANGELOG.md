# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - Unreleased

### Added
- Core redaction engine with scan and redact operations
- Regex-based detectors: email, phone, SSN, credit card, IP address, date of birth
- spaCy NER detector for person names, organizations, and locations
- Composite detector with deduplication of overlapping entities
- Plain text parser
- PDF parser (PyMuPDF)
- DOCX parser (python-docx)
- Four redaction modes: blackout, label, hash, custom
- CLI with `redact` and `scan` commands
- Console and JSON reporters
- Configuration management
- GitHub Actions CI pipeline
