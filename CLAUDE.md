# Redactify — Project Guide

## Project Overview
Redactify is an open-source, privacy-preserving document redaction tool.
It runs 100% locally — no data ever leaves the user's machine.
Target audience: developers, lawyers, doctors, HR, journalists, and everyday people.

## Core Principles
- **Privacy first**: All processing happens locally. Zero network calls for redaction.
- **Simplicity**: Non-technical users should be able to use it with zero config.
- **Extensible**: Developers can use it as a CLI, library, or integrate into pipelines.
- **Multi-format**: Support PDF, DOCX, plain text, and images (OCR).
- **Multi-language**: Start with English, expand internationally.

## Git Conventions
- Micro-commits: every meaningful change gets its own commit (~100 total).
- Commit messages: short, imperative, descriptive (e.g., "add email regex detector").
- Do NOT add Co-Authored-By lines. Commits are authored solely by the user.

## Tech Stack (Planned)
- **Language**: Python 3.10+
- **NER Model**: spaCy (en_core_web_trf or en_core_web_sm for lightweight)
- **PDF handling**: PyMuPDF (fitz) for reading/writing PDFs
- **DOCX handling**: python-docx
- **OCR**: Tesseract via pytesseract (optional dependency)
- **CLI framework**: Click
- **Testing**: pytest
- **Packaging**: pyproject.toml (PEP 621), pip installable
- **Linting**: ruff
- **CI**: GitHub Actions

## Architecture
```
redactify/
├── src/
│   └── redactify/
│       ├── __init__.py
│       ├── cli.py              # Click CLI entrypoint
│       ├── core/
│       │   ├── __init__.py
│       │   ├── engine.py       # Main redaction orchestrator
│       │   ├── detector.py     # PII detection interface
│       │   └── redactor.py     # Applies redaction to content
│       ├── detectors/
│       │   ├── __init__.py
│       │   ├── regex.py        # Regex-based detectors (email, phone, SSN, etc.)
│       │   ├── ner.py          # spaCy NER-based detector (names, orgs, locations)
│       │   └── composite.py    # Combines multiple detectors
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract parser interface
│       │   ├── text.py         # Plain text parser
│       │   ├── pdf.py          # PDF parser (PyMuPDF)
│       │   └── docx.py         # DOCX parser (python-docx)
│       ├── reporters/
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract reporter interface
│       │   ├── json_reporter.py
│       │   └── console.py      # Human-readable console output
│       └── utils/
│           ├── __init__.py
│           └── config.py       # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_detectors/
│   ├── test_parsers/
│   ├── test_engine.py
│   └── fixtures/               # Sample test documents
├── docs/
│   └── ...
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── .github/
    └── workflows/
        └── ci.yml
```

## PII Types to Detect (v0.1)
1. **Email addresses** — regex
2. **Phone numbers** — regex (US + international formats)
3. **SSN / national IDs** — regex
4. **Credit card numbers** — regex + Luhn validation
5. **IP addresses** — regex
6. **Dates of birth** — regex + context
7. **Person names** — spaCy NER
8. **Organization names** — spaCy NER
9. **Locations / addresses** — spaCy NER
10. **Custom patterns** — user-defined regex via config

## Redaction Modes
- **Blackout**: Replace PII with █████ blocks
- **Label**: Replace with [PERSON], [EMAIL], [PHONE], etc.
- **Hash**: Replace with deterministic hash (preserves referential integrity)
- **Custom**: User-provided replacement string

## MVP Milestones
### Phase 1 — Foundation
- Project scaffolding (pyproject.toml, directory structure, git init)
- Base interfaces (detector, parser, reporter)
- Plain text parser
- Regex detectors (email, phone, SSN, credit card, IP)

### Phase 2 — NER & Core Engine
- spaCy NER detector (names, orgs, locations)
- Composite detector (merges regex + NER results)
- Redaction engine (ties detection + redaction together)
- Console reporter

### Phase 3 — File Format Support
- PDF parser + redactor
- DOCX parser + redactor
- JSON reporter

### Phase 4 — CLI & UX
- Click CLI with subcommands (redact, scan, config)
- Progress bars, colored output
- Config file support (.redactify.yml)

### Phase 5 — Quality & Release
- Comprehensive tests
- GitHub Actions CI
- README with examples, badges, GIFs
- PyPI publish setup
- CHANGELOG, CONTRIBUTING.md

## Commands (Planned)
```bash
# Basic usage
redactify redact document.pdf -o redacted.pdf

# Scan without redacting (report only)
redactify scan document.docx

# Specify redaction mode
redactify redact file.txt --mode label

# Custom PII types
redactify redact file.txt --detect email,phone,names

# Batch processing
redactify redact ./documents/ -o ./redacted/
```

## Notes
- Always read this file before starting work on any task.
- Keep commits granular and focused.
- Prioritize working software over perfection.
