# CLI Reference

## Commands

### `redactify redact`

Redact PII from a document or directory.

```bash
redactify redact FILE [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-o, --output PATH` | Output file or directory |
| `--mode MODE` | Redaction mode: blackout, label, hash, custom |
| `--detect TYPES` | Comma-separated PII types to detect |
| `--no-ner` | Disable NER-based detection |
| `--confidence FLOAT` | Minimum confidence threshold (0.0-1.0) |
| `-r, --recursive` | Process directories recursively |
| `--dry-run` | Preview without writing files |
| `--format FORMAT` | Output format: console, json |

### `redactify scan`

Scan for PII without modifying files.

```bash
redactify scan FILE [OPTIONS]
```

Same options as `redact` except `-o` and `--mode`.

### `redactify config`

Manage configuration.

```bash
redactify config --init              # Create default config
redactify config --show              # Show current config
redactify config --init --path FILE  # Create config at path
```

### `redactify supported`

List all supported PII types and file formats.

```bash
redactify supported
```

## Examples

```bash
# Redact a PDF with label mode
redactify redact report.pdf -o clean.pdf --mode label

# Scan a directory recursively, JSON output
redactify scan ./documents -r --format json

# Redact only emails and phones
redactify redact file.txt --detect email,phone

# Preview what would be redacted
redactify redact file.txt --dry-run

# High-confidence detections only
redactify redact file.txt --confidence 0.8
```
