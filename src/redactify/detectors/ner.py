"""spaCy NER-based PII detector for names, organizations, and locations."""

from redactify.core.detector import BaseDetector, PIIEntity, PIIType

# Mapping from spaCy entity labels to our PIIType
_SPACY_LABEL_MAP = {
    "PERSON": PIIType.PERSON,
    "ORG": PIIType.ORGANIZATION,
    "GPE": PIIType.LOCATION,
    "LOC": PIIType.LOCATION,
    "FAC": PIIType.LOCATION,
}


class NERDetector(BaseDetector):
    """Detects person names, organizations, and locations using spaCy NER."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self._model_name = model_name
        self._nlp = None

    def _load_model(self):
        """Lazy-load the spaCy model."""
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load(self._model_name)
            except OSError:
                raise RuntimeError(
                    f"spaCy model '{self._model_name}' not found. "
                    f"Install it with: python -m spacy download {self._model_name}"
                )
        return self._nlp

    def detect(self, text: str) -> list[PIIEntity]:
        nlp = self._load_model()
        doc = nlp(text)

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
                    confidence=0.85,
                )
            )
        return entities

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.PERSON, PIIType.ORGANIZATION, PIIType.LOCATION]
