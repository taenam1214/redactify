"""Main redaction engine — orchestrates parsing, detection, and redaction."""

from pathlib import Path

from redactify.core.detector import PIIEntity, PIIType
from redactify.core.filters import filter_by_confidence
from redactify.core.redactor import Redactor, RedactionMode
from redactify.detectors.composite import CompositeDetector
from redactify.detectors.regex import (
    CreditCardDetector,
    DateOfBirthDetector,
    EmailDetector,
    IPAddressDetector,
    PhoneDetector,
    SSNDetector,
)
from redactify.parsers.base import BaseParser, ParsedDocument
from redactify.parsers.text import TextParser
from redactify.reporters.base import RedactionReport


class RedactionEngine:
    """Core engine that orchestrates the full redaction pipeline."""

    def __init__(
        self,
        mode: RedactionMode = RedactionMode.BLACKOUT,
        custom_string: str = "[REDACTED]",
        detect_types: list[PIIType] | None = None,
        use_ner: bool = True,
        custom_patterns: list[dict] | None = None,
        confidence_threshold: float = 0.0,
    ):
        self.redactor = Redactor(mode=mode, custom_string=custom_string)
        self.detector = self._build_detector(detect_types, use_ner, custom_patterns)
        self.parsers: list[BaseParser] = self._build_parsers()
        self.confidence_threshold = confidence_threshold

    @staticmethod
    def _build_parsers() -> list[BaseParser]:
        """Build list of available parsers."""
        parsers: list[BaseParser] = [TextParser()]
        try:
            from redactify.parsers.pdf import PDFParser
            parsers.append(PDFParser())
        except ImportError:
            pass
        try:
            from redactify.parsers.docx import DocxParser
            parsers.append(DocxParser())
        except ImportError:
            pass
        return parsers

    def _build_detector(
        self, detect_types: list[PIIType] | None, use_ner: bool, custom_patterns: list[dict] | None = None
    ) -> CompositeDetector:
        """Build a composite detector based on requested PII types."""
        composite = CompositeDetector()

        # Map of PIIType to regex detector class
        regex_map = {
            PIIType.EMAIL: EmailDetector,
            PIIType.PHONE: PhoneDetector,
            PIIType.SSN: SSNDetector,
            PIIType.CREDIT_CARD: CreditCardDetector,
            PIIType.IP_ADDRESS: IPAddressDetector,
            PIIType.DATE_OF_BIRTH: DateOfBirthDetector,
        }

        if detect_types is None:
            # Add all regex detectors
            for detector_cls in regex_map.values():
                composite.add_detector(detector_cls())
        else:
            # Add only requested regex detectors
            for pii_type in detect_types:
                if pii_type in regex_map:
                    composite.add_detector(regex_map[pii_type]())

        # Add NER detector if requested
        if use_ner:
            ner_types = {PIIType.PERSON, PIIType.ORGANIZATION, PIIType.LOCATION}
            if detect_types is None or ner_types.intersection(detect_types):
                try:
                    from redactify.detectors.ner import NERDetector
                    composite.add_detector(NERDetector())
                except RuntimeError:
                    pass  # spaCy model not available, skip NER

        # Add custom pattern detector if patterns provided
        if custom_patterns:
            from redactify.detectors.custom import CustomPatternDetector
            composite.add_detector(CustomPatternDetector(custom_patterns))

        return composite

    def _get_parser(self, file_path: Path) -> BaseParser:
        """Find an appropriate parser for the given file."""
        for parser in self.parsers:
            if parser.can_handle(file_path):
                return parser
        raise ValueError(f"No parser available for file: {file_path}")

    def scan(self, file_path: Path) -> RedactionReport:
        """Scan a file for PII without redacting.

        Args:
            file_path: Path to the file to scan.

        Returns:
            A RedactionReport with detected entities.
        """
        file_path = Path(file_path)
        parser = self._get_parser(file_path)
        document = parser.parse(file_path)

        all_entities: list[PIIEntity] = []
        for chunk in document.chunks:
            entities = self.detector.detect(chunk.text)
            all_entities.extend(entities)

        if self.confidence_threshold > 0:
            all_entities = filter_by_confidence(all_entities, self.confidence_threshold)

        entities_by_type: dict[str, int] = {}
        for entity in all_entities:
            key = entity.pii_type.value
            entities_by_type[key] = entities_by_type.get(key, 0) + 1

        return RedactionReport(
            source_file=file_path,
            total_entities=len(all_entities),
            entities_by_type=entities_by_type,
            entities=all_entities,
            redacted=False,
        )

    def redact(self, file_path: Path, output_path: Path | None = None) -> RedactionReport:
        """Redact PII from a file and write the result.

        Args:
            file_path: Path to the input file.
            output_path: Path for the redacted output. Defaults to <name>.redacted.<ext>.

        Returns:
            A RedactionReport summarizing what was redacted.
        """
        file_path = Path(file_path)
        parser = self._get_parser(file_path)
        document = parser.parse(file_path)

        all_entities: list[PIIEntity] = []
        redacted_chunks: list[str] = []

        for chunk in document.chunks:
            entities = self.detector.detect(chunk.text)
            if self.confidence_threshold > 0:
                entities = filter_by_confidence(entities, self.confidence_threshold)
            all_entities.extend(entities)
            redacted_text = self.redactor.redact(chunk.text, entities)
            redacted_chunks.append(redacted_text)

        # Determine output path
        if output_path is None:
            stem = file_path.stem
            suffix = file_path.suffix
            output_path = file_path.parent / f"{stem}.redacted{suffix}"

        output_path = Path(output_path)
        output_path.write_text("\n".join(redacted_chunks), encoding="utf-8")

        entities_by_type: dict[str, int] = {}
        for entity in all_entities:
            key = entity.pii_type.value
            entities_by_type[key] = entities_by_type.get(key, 0) + 1

        return RedactionReport(
            source_file=file_path,
            total_entities=len(all_entities),
            entities_by_type=entities_by_type,
            entities=all_entities,
            redacted=True,
        )

    def redact_directory(
        self, input_dir: Path, output_dir: Path | None = None
    ) -> list[RedactionReport]:
        """Redact all supported files in a directory.

        Args:
            input_dir: Path to the input directory.
            output_dir: Path for redacted outputs. Defaults to <input_dir>/redacted/.

        Returns:
            A list of RedactionReports for each processed file.
        """
        input_dir = Path(input_dir)
        if not input_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")

        if output_dir is None:
            output_dir = input_dir / "redacted"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        reports: list[RedactionReport] = []
        for file_path in sorted(input_dir.iterdir()):
            if file_path.is_file() and not file_path.name.startswith("."):
                try:
                    self._get_parser(file_path)
                except ValueError:
                    continue  # Skip unsupported files

                out_path = output_dir / file_path.name
                report = self.redact(file_path, output_path=out_path)
                reports.append(report)

        return reports

    def scan_directory(self, input_dir: Path) -> list[RedactionReport]:
        """Scan all supported files in a directory for PII.

        Args:
            input_dir: Path to the directory to scan.

        Returns:
            A list of RedactionReports for each scanned file.
        """
        input_dir = Path(input_dir)
        if not input_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")

        reports: list[RedactionReport] = []
        for file_path in sorted(input_dir.iterdir()):
            if file_path.is_file() and not file_path.name.startswith("."):
                try:
                    self._get_parser(file_path)
                except ValueError:
                    continue
                report = self.scan(file_path)
                reports.append(report)

        return reports
