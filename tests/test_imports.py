"""Test that all public imports work correctly."""


class TestTopLevelImports:
    def test_import_package(self):
        import redactify
        assert hasattr(redactify, "__version__")

    def test_import_engine(self):
        from redactify import RedactionEngine
        assert RedactionEngine is not None

    def test_import_pii_type(self):
        from redactify import PIIType
        assert PIIType.EMAIL.value == "email"

    def test_import_redaction_mode(self):
        from redactify import RedactionMode
        assert RedactionMode.BLACKOUT.value == "blackout"


class TestSubpackageImports:
    def test_import_detectors(self):
        from redactify.detectors import EmailDetector, PhoneDetector, CompositeDetector
        assert EmailDetector is not None
        assert PhoneDetector is not None
        assert CompositeDetector is not None

    def test_import_parsers(self):
        from redactify.parsers import TextParser, HTMLParser
        assert TextParser is not None
        assert HTMLParser is not None

    def test_import_reporters(self):
        from redactify.reporters import ConsoleReporter, JSONReporter, SummaryReporter
        assert ConsoleReporter is not None
        assert JSONReporter is not None
        assert SummaryReporter is not None

    def test_import_utils(self):
        from redactify.utils import RedactifyConfig, read_file_safe
        assert RedactifyConfig is not None
        assert read_file_safe is not None

    def test_import_exceptions(self):
        from redactify.exceptions import RedactifyError, UnsupportedFileTypeError
        assert issubclass(UnsupportedFileTypeError, RedactifyError)
