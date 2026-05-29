# Contributing to Redactify

Thank you for considering contributing to Redactify! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/redactify.git
   cd redactify
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev,all]"
   python -m spacy download en_core_web_sm
   ```
4. Create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

```bash
pytest tests/ -v
```

### Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

### Commit Messages

- Use imperative mood ("add feature" not "added feature")
- Keep commits small and focused
- Examples:
  - `add email regex detector`
  - `fix SSN validation edge case`
  - `update README installation instructions`

## What to Contribute

### Good First Issues

- Add regex patterns for new PII types (passport numbers, IBAN, etc.)
- Improve phone number detection for specific countries
- Add new test cases for edge cases
- Improve documentation

### Feature Ideas

- New file format parsers (HTML, CSV with headers, etc.)
- Language-specific NER models
- Performance benchmarks
- Web UI (local only)

## Adding a New Detector

1. Create a new file in `src/redactify/detectors/`
2. Implement the `BaseDetector` interface
3. Add tests in `tests/test_detectors/`
4. Register it in the engine if appropriate

Example:

```python
from redactify.core.detector import BaseDetector, PIIEntity, PIIType

class MyDetector(BaseDetector):
    def detect(self, text: str) -> list[PIIEntity]:
        # Your detection logic here
        ...

    @property
    def supported_types(self) -> list[PIIType]:
        return [PIIType.CUSTOM]
```

## Adding a New Parser

1. Create a new file in `src/redactify/parsers/`
2. Implement the `BaseParser` interface
3. Add tests in `tests/test_parsers/`
4. Register it in `engine.py`

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add a brief description of your changes
4. Link any related issues

## Code of Conduct

- Be respectful and constructive
- Focus on the code, not the person
- Assume good intent

## Questions?

Open an issue on GitHub — we're happy to help!
