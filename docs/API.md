# Redactify API Reference

## Quick Start

```python
from redactify import RedactionEngine, RedactionMode, PIIType

# Basic usage
engine = RedactionEngine()
report = engine.scan("document.txt")
report = engine.redact("document.txt")
```

## RedactionEngine

The main entry point for all redaction operations.

### Constructor

```python
RedactionEngine(
    mode: RedactionMode = RedactionMode.BLACKOUT,
    custom_string: str = "[REDACTED]",
    detect_types: list[PIIType] | None = None,
    use_ner: bool = True,
    custom_patterns: list[dict] | None = None,
    confidence_threshold: float = 0.0,
)
```

### Methods

- `scan(file_path) -> RedactionReport` — Detect PII without modifying the file.
- `redact(file_path, output_path=None) -> RedactionReport` — Detect and redact PII.
- `scan_directory(input_dir, recursive=False) -> list[RedactionReport]` — Scan all files in a directory.
- `redact_directory(input_dir, output_dir=None, recursive=False) -> list[RedactionReport]` — Redact all files.

## PIIType

Enum of detectable PII types:

- `EMAIL`, `PHONE`, `SSN`, `CREDIT_CARD`, `IP_ADDRESS`
- `DATE_OF_BIRTH`, `PERSON`, `ORGANIZATION`, `LOCATION`, `CUSTOM`

## RedactionMode

- `BLACKOUT` — Replace with █ characters
- `LABEL` — Replace with [TYPE] labels
- `HASH` — Replace with deterministic hash
- `CUSTOM` — Replace with custom string

## Custom Patterns

```python
engine = RedactionEngine(
    custom_patterns=[
        {"name": "order_id", "pattern": r"ORD-\d+"},
        {"name": "medical_id", "pattern": r"MRN-\d{6}"},
    ]
)
```

## RedactionReport

```python
@dataclass
class RedactionReport:
    source_file: Path
    total_entities: int
    entities_by_type: dict[str, int]
    entities: list[PIIEntity]
    redacted: bool
```
