# 🔒 Redactify

**Privacy-preserving document redaction. 100% local. Zero data leaves your machine.**

[![CI](https://github.com/taenam1214/redactify/actions/workflows/ci.yml/badge.svg)](https://github.com/taenam1214/redactify/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

Redactify automatically detects and removes personally identifiable information (PII) from your documents — **without ever sending your data to the cloud**.

Whether you're a lawyer redacting case files, a doctor handling patient records, or a developer building compliance pipelines — Redactify keeps your sensitive data where it belongs: on your machine.

## Features

- **100% Local** — No API calls, no cloud, no data transmission. Ever.
- **Multi-format** — Supports PDF, DOCX, and plain text files
- **Smart Detection** — Combines regex patterns with NLP (spaCy NER) for high accuracy
- **Multiple Redaction Modes** — Blackout, labels, deterministic hashing, or custom replacements
- **CLI & Library** — Use from the terminal or import directly in Python
- **Extensible** — Add custom PII patterns via configuration

## Quick Start

### Installation

```bash
pip install redactify

# Download the NER model
python -m spacy download en_core_web_sm
```

For PDF/DOCX support:

```bash
pip install redactify[all]
```

### Usage

#### Redact a document

```bash
redactify redact document.pdf -o redacted.pdf
```

#### Scan without redacting (report only)

```bash
redactify scan document.txt
```

#### Choose redaction mode

```bash
# Replace PII with type labels: [EMAIL], [PHONE], etc.
redactify redact file.txt --mode label

# Replace with deterministic hashes (preserves referential integrity)
redactify redact file.txt --mode hash

# Classic blackout
redactify redact file.txt --mode blackout
```

#### Select specific PII types

```bash
redactify redact file.txt --detect email,phone,ssn
```

### Python API

```python
from redactify.core.engine import RedactionEngine
from redactify.core.redactor import RedactionMode

engine = RedactionEngine(mode=RedactionMode.LABEL)

# Scan for PII
report = engine.scan("document.txt")
print(f"Found {report.total_entities} PII entities")

# Redact
report = engine.redact("document.txt", output_path="clean.txt")
```

## What It Detects

| PII Type | Method | Examples |
|----------|--------|----------|
| Email addresses | Regex | john@example.com |
| Phone numbers | Regex | (555) 123-4567, +44 20 7946 0958 |
| SSN | Regex + validation | 123-45-6789 |
| Credit cards | Regex + Luhn | 4111 1111 1111 1111 |
| IP addresses | Regex | 192.168.1.1 |
| Dates of birth | Regex + context | Born on 01/15/1990 |
| Person names | spaCy NER | John Smith |
| Organizations | spaCy NER | Google, NHS |
| Locations | spaCy NER | New York, London |

## Redaction Modes

| Mode | Example Output | Use Case |
|------|---------------|----------|
| `blackout` | `████████████████` | Maximum privacy |
| `label` | `[EMAIL]` | Readable output with type context |
| `hash` | `[REDACTED-a1b2c3d4e5f6]` | Preserves referential integrity |
| `custom` | `[REMOVED]` | Your own replacement string |

## Development

```bash
# Clone the repo
git clone https://github.com/taenam1214/redactify.git
cd redactify

# Install in development mode
pip install -e ".[dev,all]"
python -m spacy download en_core_web_sm

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/
```

## Roadmap

- [x] Batch processing (directories)
- [x] Custom pattern definitions via config file
- [x] Recursive directory scanning
- [x] HTML file support
- [x] Dry-run mode
- [x] Confidence threshold filtering
- [ ] OCR support (images with text)
- [ ] Web UI (local, no server)
- [ ] Multi-language NER support
- [ ] Pre-commit hook integration
- [ ] Streaming/large file support

## License

MIT — see [LICENSE](LICENSE) for details.

---

**Your data stays yours. Always.**
