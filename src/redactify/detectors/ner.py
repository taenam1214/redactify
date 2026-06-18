"""spaCy NER-based PII detector for names, organizations, and locations."""

from __future__ import annotations

from redactify.core.detector import BaseDetector, PIIEntity, PIIType

# Mapping from spaCy entity labels to our PIIType
_SPACY_LABEL_MAP = {
    "PERSON": PIIType.PERSON,
    "ORG": PIIType.ORGANIZATION,
    "GPE": PIIType.LOCATION,
    "LOC": PIIType.LOCATION,
    "FAC": PIIType.LOCATION,
}

# Module-level model cache — shared across all NERDetector instances
_MODEL_CACHE: dict[str, object] = {}


class NERDetector(BaseDetector):
    """Detects person names, organizations, and locations using spaCy NER."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self._model_name = model_name
        self._nlp = None

    def _load_model(self):
        """Lazy-load the spaCy model, reusing a cached instance if available."""
        if self._nlp is not None:
            return self._nlp

        if self._model_name in _MODEL_CACHE:
            self._nlp = _MODEL_CACHE[self._model_name]
            return self._nlp

        try:
            import spacy
            self._nlp = spacy.load(self._model_name)
            _MODEL_CACHE[self._model_name] = self._nlp
        except OSError:
            raise RuntimeError(
                f"spaCy model '{self._model_name}' not found. "
                f"Install it with: python -m spacy download {self._model_name}"
            )
        return self._nlp

    # Context keywords that boost confidence for each entity type
    _CONTEXT_BOOSTERS: dict[str, set[str]] = {
        "PERSON": {"mr", "mrs", "ms", "dr", "prof", "name", "contact", "dear", "signed", "author"},
        "ORG": {"inc", "corp", "ltd", "llc", "company", "organization", "department", "firm"},
        "GPE": {"city", "state", "country", "located", "address", "lives", "born", "from"},
        "LOC": {"city", "state", "country", "located", "address", "lives", "born", "from"},
        "FAC": {"building", "airport", "station", "bridge", "facility"},
    }

    def _compute_confidence(self, ent, text_lower: str) -> float:
        """Compute confidence score using spaCy's score and context keywords."""
        # Start with spaCy's entity score if available (transformer models),
        # otherwise use a baseline based on entity length
        if hasattr(ent, "kb_id_") and ent.kb_id_:
            base = 0.85
        elif len(ent.text.split()) > 1:
            base = 0.80  # Multi-word entities are more reliable
        else:
            base = 0.70  # Single-word entities are less certain

        # Check for context boosters around the entity
        context_start = max(0, ent.start_char - 40)
        context_end = min(len(text_lower), ent.end_char + 40)
        context = text_lower[context_start:context_end]

        boosters = self._CONTEXT_BOOSTERS.get(ent.label_, set())
        if any(kw in context for kw in boosters):
            base = min(base + 0.10, 1.0)

        return round(base, 2)

    def detect(self, text: str) -> list[PIIEntity]:
        nlp = self._load_model()
        doc = nlp(text)
        text_lower = text.lower()

        entities = []
        for ent in doc.ents:
            pii_type = _SPACY_LABEL_MAP.get(ent.label_)
            if pii_type is None:
                continue
            entities.append(
                PIIEntity(
                    text=ent.text,
                    pii_type=pii_type,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=self._compute_confidence(ent, text_lower),
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.PERSON, PIIType.ORGANIZATION, PIIType.LOCATION]
