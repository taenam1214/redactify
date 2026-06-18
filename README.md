<p align="center">
  <h1 align="center">🔒 Redactify</h1>
  <p align="center">
    <strong>Automatically detect and redact PII from documents. 100% local. Zero cloud. Zero trust required.</strong>
  </p>
  <p align="center">
    <a href="https://github.com/taenam1214/redactify/actions/workflows/ci.yml"><img src="https://github.com/taenam1214/redactify/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://codecov.io/gh/taenam1214/redactify"><img src="https://codecov.io/gh/taenam1214/redactify/branch/main/graph/badge.svg" alt="Coverage"></a>
    <a href="https://pypi.org/project/redactify/"><img src="https://img.shields.io/pypi/v/redactify.svg" alt="PyPI version"></a>
    <a href="https://pypi.org/project/redactify/"><img src="https://img.shields.io/pypi/dm/redactify.svg" alt="Downloads"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
    <a href="https://github.com/taenam1214/redactify/stargazers"><img src="https://img.shields.io/github/stars/taenam1214/redactify?style=social" alt="Stars"></a>
  </p>
</p>

---

<p align="center">
  <img src="assets/demo.gif" alt="Redactify demo" width="700">
  <br>
  <em>^ Record a demo GIF and place at <code>assets/demo.gif</code></em>
</p>

---

## Quick Start

### Install

```bash
pip install redactify
python -m spacy download en_core_web_sm
```

For PDF/DOCX support:
```bash
pip install redactify[all]
```

### CLI Usage

```bash
# Redact a document
redactify redact document.pdf -o redacted.pdf

# Scan without modifying (report only)
redactify scan document.txt

# Choose redaction mode
redactify redact file.txt --mode label
redactify redact file.txt --mode hash
redactify redact file.txt --mode blackout

# Select specific PII types
redactify redact file.txt --detect email,phone,ssn

# Batch process a directory
redactify redact ./documents/ -o ./redacted/ -r

# Parallel batch processing
redactify redact ./documents/ -o ./redacted/ -r --workers 4

# Preview without writing (dry run)
redactify redact file.txt --dry-run

# High-confidence detections only
redactify redact file.txt --confidence 0.8

# Exclude known-safe values
redactify redact file.txt --allowlist safe-values.txt

# List all supported PII types
redactify supported
```

### Docker

```bash
docker run --rm -v $(pwd):/data ghcr.io/taenam1214/redactify scan /data/file.txt
docker run --rm -v $(pwd):/data ghcr.io/taenam1214/redactify redact /data/file.txt -o /data/redacted.txt
```

---

## The Problem

Every day, sensitive documents containing names, emails, SSNs, credit cards, and phone numbers are shared, stored, and processed — often without proper redaction. Existing tools either:

- **Send your data to the cloud** (defeating the purpose of privacy)
- **Cost hundreds per month** (enterprise SaaS pricing)
- **Require manual effort** (highlighting PDFs by hand)

## The Solution

Redactify runs **entirely on your machine**. No API keys. No cloud accounts. No data ever leaves your device.

```
Input:  "Contact John Smith at john@acme.com or (555) 123-4567. SSN: 123-45-6789"
Output: "Contact [PERSON] at [EMAIL] or [PHONE]. SSN: [SSN]"
```

---

## Before & After

```diff
- Dear John Smith,
- Your SSN 123-45-6789 has been verified.
- Contact: john.smith@example.com | (555) 123-4567
- Card on file: 4111 1111 1111 1111

+ Dear [PERSON],
+ Your SSN [SSN] has been verified.
+ Contact: [EMAIL] | [PHONE]
+ Card on file: [CREDIT_CARD]
```

---

## Features

| Feature | Description |
|---------|-------------|
| 🏠 **100% Local** | No network calls, no cloud, no telemetry. Ever. |
| 📄 **Multi-format** | PDF, DOCX, HTML, plain text (.txt, .csv, .log, .md) |
| 🧠 **Smart Detection** | Regex patterns + spaCy NER for names, orgs, locations |
| 🎨 **4 Redaction Modes** | Blackout (█████), labels ([EMAIL]), hash, or custom |
| ⚡ **CLI & Python API** | Use from terminal or import as a library |
| 🔧 **Extensible** | Add custom regex patterns via config file |
| 📁 **Batch Processing** | Redact entire directories, recursively |
| 👁️ **Dry-run Mode** | Preview what would be redacted before writing |
| 🎯 **Confidence Filtering** | Set thresholds to control detection sensitivity |
| 🚫 **Allowlist** | Exclude known-safe values from detection |
| ⚡ **Parallel Processing** | `--workers N` for faster batch operations |
| 🐳 **Docker Ready** | Pre-built image with all models included |

---

## Why Redactify?

| Feature | Redactify | Presidio | scrubadub |
|---------|:---------:|:--------:|:---------:|
| 100% local | ✅ | ✅ | ✅ |
| Zero config | ✅ | ❌ | ✅ |
| PDF support | ✅ | ❌ | ❌ |
| DOCX support | ✅ | ❌ | ❌ |
| CLI tool | ✅ | ❌ | Limited |
| Batch processing | ✅ | ❌ | ❌ |
| Multiple redaction modes | 4 | Custom | 1 |
| Lightweight install | ~50MB | ~500MB+ | ~30MB |

---

## What It Detects

| PII Type | Method | Examples |
|----------|--------|----------|
| Email addresses | Regex | `john@example.com` |
| Phone numbers | Regex | `(555) 123-4567`, `+44 20 7946 0958` |
| SSN / National IDs | Regex + validation | `123-45-6789` |
| Credit card numbers | Regex + Luhn | `4111 1111 1111 1111` |
| IP addresses (v4) | Regex | `192.168.1.1` |
| IPv6 addresses | Regex | `2001:0db8:85a3::8a2e:0370:7334` |
| MAC addresses | Regex | `00:1A:2B:3C:4D:5E` |
| IBAN | Regex + mod-97 | `DE89370400440532013000` |
| Passport numbers | Regex + context | `Passport: 123456789` |
| Drivers licenses | Regex + context | `DL: D1234567` (CA format) |
| URLs with PII | Regex + path analysis | `https://api.com/users/john` |
| Dates of birth | Regex + context | `Born on 01/15/1990` |
| Person names | spaCy NER | `John Smith`, `María García` |
| Organizations | spaCy NER | `Google`, `NHS`, `Acme Corp` |
| Locations | spaCy NER | `New York`, `London`, `Tokyo` |
| Custom patterns | User-defined regex | `MRN-123456`, `ORD-00042` |

## Redaction Modes

| Mode | Output | Best For |
|------|--------|----------|
| `blackout` | `████████████████` | Maximum privacy, legal documents |
| `label` | `[EMAIL]` | Readable output, training data |
| `hash` | `[REDACTED-a1b2c3d4]` | Preserving referential integrity |
| `custom` | `[REMOVED]` | Custom compliance requirements |

---

## Python API

### Quick Functions (no setup required)

```python
import redactify

# One-liner redaction
result = redactify.redact_text("Email john@acme.com for info", mode="label")
print(result.text)  # "Email [EMAIL] for info"

# Quick PII check (regex-only, fast)
redactify.contains_pii("Call 555-123-4567")  # True

# Scan for entities
entities = redactify.scan_text("SSN: 123-45-6789")
for e in entities:
    print(f"  {e.pii_type.value}: {e.text}")
```

### Engine API (full control)

```python
from redactify import RedactionEngine, Allowlist

# String args work — no need for enum imports
engine = RedactionEngine(mode="label", detect_types=["email", "phone"])

# In-memory operations (no file I/O)
result = engine.redact_text("Contact john@acme.com or 555-1234")
print(result.text)           # "Contact [EMAIL] or [PHONE]"
print(result.has_pii)        # True
print(result.entities_by_type)  # {"email": 1, "phone": 1}

# File-based operations
report = engine.scan("document.txt")
report = engine.redact("document.txt", output_path="clean.txt")

# Allowlist: exclude known-safe values
al = Allowlist.from_file("safe-values.txt")
engine = RedactionEngine(mode="label", allowlist=al)
```

### Custom Patterns

```python
engine = RedactionEngine(
    custom_patterns=[
        {"name": "medical_record", "pattern": r"MRN-\d{6}"},
        {"name": "employee_id", "pattern": r"EMP-\d{4}"},
    ]
)
```

---

## Use Cases

- **Healthcare** — Redact patient records (HIPAA compliance)
- **Legal** — Strip PII from case files before sharing
- **HR** — Anonymize resumes and employee documents
- **Journalism** — Protect source identities in leaked documents
- **Development** — Sanitize logs and test data before committing
- **Compliance** — GDPR right-to-erasure workflows
- **Research** — Anonymize survey responses and interview transcripts

---

## Architecture

```
redactify/
├── src/redactify/
│   ├── cli.py              # Click CLI (redact, scan, config, supported)
│   ├── core/
│   │   ├── engine.py       # Main orchestrator
│   │   ├── detector.py     # Detection interface + PIIType/PIIEntity
│   │   ├── redactor.py     # Redaction strategies
│   │   └── filters.py      # Confidence/type/length filtering
│   ├── detectors/
│   │   ├── regex.py        # Email, phone, SSN, credit card, IP, DOB
│   │   ├── ner.py          # spaCy NER (names, orgs, locations)
│   │   ├── composite.py    # Multi-detector with deduplication
│   │   └── custom.py       # User-defined patterns
│   ├── parsers/
│   │   ├── text.py         # .txt, .csv, .log, .md
│   │   ├── pdf.py          # PDF (PyMuPDF)
│   │   ├── docx.py         # DOCX (python-docx)
│   │   └── html.py         # HTML (tag stripping)
│   └── reporters/
│       ├── console.py      # Human-readable output
│       ├── json_reporter.py # Machine-readable JSON
│       └── summary.py      # Batch operation summaries
└── tests/                  # Comprehensive test suite
```

---

## Development

```bash
git clone https://github.com/taenam1214/redactify.git
cd redactify

# Install with dev dependencies
make dev

# Run tests
make test

# Lint
make lint
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Roadmap

- [x] Core redaction engine
- [x] Regex + NER detection
- [x] PDF, DOCX, HTML, plain text support
- [x] Batch processing with recursive directory support
- [x] Custom pattern definitions via config
- [x] Dry-run mode
- [x] Confidence threshold filtering
- [x] Pre-commit hook integration
- [x] Streaming support for large files
- [x] Redaction audit trail
- [ ] OCR support (images with text)
- [ ] Local web UI (drag-and-drop)
- [ ] Multi-language NER models

---

## Privacy Guarantee

Redactify makes **zero network calls** during operation. The only network activity is downloading the spaCy model during initial setup (`python -m spacy download en_core_web_sm`). After that, it works fully offline.

You can verify this: disconnect from the internet and run `redactify redact file.txt`. It works.

See [docs/PRIVACY.md](docs/PRIVACY.md) for the full privacy guarantee.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Your data stays yours. Always.</strong>
  <br><br>
  <a href="https://github.com/taenam1214/redactify">⭐ Star this repo</a> if you believe privacy tools should be free and open source.
</p>
