"""JSON reporter — machine-readable output."""

import json

from redactify.reporters.base import BaseReporter, RedactionReport


class JSONReporter(BaseReporter):
    """Produces JSON output for redaction reports."""

    def report(self, result: RedactionReport) -> str:
        data = {
            "source_file": str(result.source_file),
            "redacted": result.redacted,
            "total_entities": result.total_entities,
            "entities_by_type": result.entities_by_type,
            "entities": [
                {
                    "text": entity.text,
                    "type": entity.pii_type.value,
                    "start": entity.start,
                    "end": entity.end,
                    "confidence": entity.confidence,
                }
                for entity in result.entities
            ],
        }
        return json.dumps(data, indent=2)
