"""Test version consistency."""

import redactify


class TestVersion:
    def test_version_string(self):
        assert redactify.__version__ == "0.1.0"

    def test_version_is_string(self):
        assert isinstance(redactify.__version__, str)

    def test_version_has_three_parts(self):
        parts = redactify.__version__.split(".")
        assert len(parts) == 3
