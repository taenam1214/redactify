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
- `IBANDetector` — detects international bank account numbers with mod-97 checksum validation
- `PassportDetector` — detects passport numbers (US, UK, EU) with context-aware matching
- `URLDetector` — detects URLs containing PII in paths or query parameters
- `MACAddressDetector` — detects MAC addresses (colon, dash, and Cisco dot formats)
- `IPv6Detector` — detects full and abbreviated IPv6 addresses
- `DriversLicenseDetector` — detects US drivers license numbers with context-aware matching
- Allowlist system for excluding known-safe strings from PII detection
- Module-level spaCy model caching across NERDetector instances
- Parallel batch processing with `--workers N` flag for directory scan/redact
- Progress bar helper with TTY auto-detection and `--quiet` suppression
- `--verbose` / `-v` flag for detailed processing info
- YAML config support (`.redactify.yml`) with auto-detection and `--format yaml`
- `ConfigValidationError` exception for invalid config values
- Did-you-mean suggestions for misspelled PII types in CLI
- Release automation workflow (GitHub Release on version tag)
- Dockerfile with python:3.12-slim and pre-installed spaCy model
- `.dockerignore` for lean Docker builds
- GitHub Action (`action.yml`) for PII scanning in pull requests
- Benchmark suite: detector throughput, engine end-to-end, memory profiling
- `make bench` target for running benchmarks
- PDF and DOCX parser integration tests with skip markers
- Property-based tests using Hypothesis
- Fuzzing tests for unicode, extreme lengths, nested PII, control characters
- Minimum 80% code coverage enforcement in CI
- Security scanning workflow (pip-audit + bandit)
- Dependabot configuration for automated dependency updates
- `RedactionEngine.from_config()` factory method for config-file-driven instantiation
- `--allowlist` CLI flag for scan and redact commands
- Auto-loading allowlist from config file when no `--allowlist` flag is given
- Config validation on load: invalid modes, unknown PII types, broken regexes
- Enhanced `supported` command with descriptions and detection methods
- `allowlist` parameter on all convenience functions (`redact_text`, `scan_text`, etc.)
- Context-aware NER confidence scoring (replaces hardcoded 0.85)

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
