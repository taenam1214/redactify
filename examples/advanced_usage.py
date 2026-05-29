"""Advanced usage example — custom patterns and batch processing."""

from pathlib import Path
import tempfile

from redactify import RedactionEngine, RedactionMode

# Create engine with custom patterns
engine = RedactionEngine(
    mode=RedactionMode.HASH,
    use_ner=False,
    confidence_threshold=0.5,
    custom_patterns=[
        {"name": "medical_record", "pattern": r"MRN-\d{6}"},
        {"name": "employee_id", "pattern": r"EMP-\d{4}"},
    ],
)

# Demo text with custom PII
text = """
Patient: John Doe
Medical Record: MRN-123456
Employee handling: EMP-0042
Email: john.doe@hospital.com
Phone: (555) 000-1234
"""

# Write to temp
tmp_dir = Path(tempfile.mkdtemp())
(tmp_dir / "patient_record.txt").write_text(text)
(tmp_dir / "another_file.txt").write_text("Contact EMP-0099 at admin@test.com")

# Batch scan
print("=== BATCH SCAN ===")
reports = engine.scan_directory(tmp_dir)
for report in reports:
    print(f"  {report.source_file.name}: {report.total_entities} entities")
    for t, c in report.entities_by_type.items():
        print(f"    {t}: {c}")

# Batch redact
print("\n=== BATCH REDACT ===")
output_dir = tmp_dir / "redacted"
reports = engine.redact_directory(tmp_dir, output_dir=output_dir)
for report in reports:
    out_file = output_dir / report.source_file.name
    print(f"\n  {out_file.name}:")
    print(out_file.read_text())

# Cleanup
import shutil
shutil.rmtree(tmp_dir)
