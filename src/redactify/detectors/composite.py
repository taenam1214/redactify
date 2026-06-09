"""Composite detector that combines multiple detectors."""

from __future__ import annotations

from redactify.core.allowlist import Allowlist
from redactify.core.detector import BaseDetector, PIIEntity, PIIType


class CompositeDetector(BaseDetector):
    """Combines multiple detectors and deduplicates overlapping entities."""

    def __init__(
        self,
        detectors: list[BaseDetector] | None = None,
        allowlist: Allowlist | None = None,
    ):
        self._detectors: list[BaseDetector] = detectors or []
        self.allowlist: Allowlist | None = allowlist

    def add_detector(self, detector: BaseDetector) -> None:
        """Add a detector to the composite."""
        self._detectors.append(detector)

    def detect(self, text: str) -> list[PIIEntity]:
        all_entities: list[PIIEntity] = []
        for detector in self._detectors:
            all_entities.extend(detector.detect(text))

        deduplicated = self._deduplicate(all_entities)

        # Apply allowlist as post-filter
        if self.allowlist is not None:
            return self.allowlist.filter_entities(deduplicated)
        return deduplicated

    @staticmethod
    def _deduplicate(entities: list[PIIEntity]) -> list[PIIEntity]:
        """Remove overlapping entities, keeping the one with higher confidence."""
        if not entities:
            return []

        sorted_entities = sorted(entities, key=lambda e: (e.start, -(e.end - e.start)))
        result: list[PIIEntity] = []

        for entity in sorted_entities:
            overlaps = False
            for i, existing in enumerate(result):
                if entity.start < existing.end and entity.end > existing.start:
                    overlaps = True
                    # Keep the one with higher confidence
                    if entity.confidence > existing.confidence:
                        result[i] = entity
                    break
            if not overlaps:
                result.append(entity)

        return sorted(result, key=lambda e: e.start)

    @property
    def supported_types(self) -> list[PIIType]:
        types: set[PIIType] = set()
        for detector in self._detectors:
            types.update(detector.supported_types)
        return list(types)
