"""Basic usage example for Redactify."""

from redactify import RedactionEngine, RedactionMode

# Create an engine with label mode (no NER for speed)
engine = RedactionEngine(mode=RedactionMode.LABEL, use_ner=False)

# Sample text with PII
text = """
Dear John Smith,

Your SSN 123-45-6789 has been verified.
Please contact us at support@example.com or call (555) 123-4567.

Payment card: 4111 1111 1111 1111
Server IP: 192.168.1.50
"""

# Write to a temp file for demo
from pathlib import Path
import tempfile

tmp = Path(tempfile.mktemp(suffix=".txt"))
tmp.write_text(text)

# Scan (no modification)
print("=== SCAN ===")
report = engine.scan(tmp)
print(f"Found {report.total_entities} PII entities:")
for pii_type, count in report.entities_by_type.items():
    print(f"  {pii_type}: {count}")

# Redact
print("\n=== REDACT ===")
output = tmp.parent / "redacted_output.txt"
report = engine.redact(tmp, output_path=output)
print(f"Redacted output saved to: {output}")
print(f"\nRedacted content:")
print(output.read_text())

# Cleanup
tmp.unlink()
output.unlink()
