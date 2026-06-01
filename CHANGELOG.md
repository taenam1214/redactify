# Changelog

All notable changes to this project will be documented in this file.

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
