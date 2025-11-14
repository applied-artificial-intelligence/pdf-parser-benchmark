# PDF-Bench Test Suite

Comprehensive test suite for the PDF-Bench benchmarking framework.

## Overview

The test suite is organized into logical modules that mirror the package structure:

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── helpers.py               # Test utility functions
├── fixtures/                # Test data files
│   ├── sample.pdf          # Sample PDF for testing
│   └── sample_ground_truth.md  # Expected markdown output
├── test_systems/           # Parser system tests
│   ├── test_base_parser.py
│   └── test_pymupdf.py
├── test_metrics/           # Metric calculation tests
│   └── test_edit_distance.py
└── test_utils/             # Utility module tests
    ├── test_caching.py
    ├── test_metadata.py
    └── test_normalization.py
```

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run with coverage
```bash
uv run pytest --cov=pdf_bench --cov-report=html
```

### Run specific test modules
```bash
uv run pytest tests/test_systems/
uv run pytest tests/test_metrics/test_edit_distance.py
```

### Run with verbose output
```bash
uv run pytest -v
```

### Run tests matching a pattern
```bash
uv run pytest -k "test_parse"
```

## Test Fixtures

### Shared Fixtures (conftest.py)

- **sample_pdf**: Path to sample PDF file
- **sample_ground_truth**: Path to ground truth markdown file
- **sample_ground_truth_text**: Content of ground truth markdown
- **temp_output_dir**: Temporary directory for test outputs
- **fixtures_dir**: Path to fixtures directory

Example usage:
```python
def test_parser(sample_pdf, sample_ground_truth_text):
    result = parse_pdf(sample_pdf)
    assert_markdown_similar(result, sample_ground_truth_text)
```

## Test Helpers

The `helpers.py` module provides utility functions:

### Comparison Helpers

- **assert_markdown_similar(actual, expected, threshold)**: Assert markdown similarity
- **assert_files_similar(actual_path, expected_path, threshold)**: Assert file similarity
- **normalize_whitespace(text)**: Normalize whitespace for lenient comparison
- **count_markdown_elements(text)**: Count markdown structural elements

### Path Helpers

- **get_fixture_path(filename)**: Get path to fixture file
- **get_test_output_dir(prefix)**: Create temporary output directory
- **read_fixture(filename)**: Read fixture file content

Example usage:
```python
from tests.helpers import assert_markdown_similar, get_fixture_path

def test_accuracy():
    actual = parser.parse("document.pdf")
    expected = get_fixture_path("expected.md").read_text()
    assert_markdown_similar(actual, expected, threshold=0.95)
```

## Test Markers

Custom pytest markers for organizing tests:

- **@pytest.mark.slow**: Marks slow tests (skip with `-m "not slow"`)
- **@pytest.mark.integration**: Marks integration tests
- **@pytest.mark.requires_api**: Marks tests requiring API credentials

Example:
```python
@pytest.mark.slow
def test_large_document():
    # Test that takes significant time
    pass

@pytest.mark.requires_api
def test_api_parser():
    # Test requiring API credentials
    pass
```

## CI Integration

Tests run automatically on GitHub Actions for:
- Python 3.10, 3.11, 3.12
- Push to main/develop branches
- Pull requests

See `.github/workflows/test.yml` for CI configuration.

## Writing New Tests

### Test Organization

- Place tests in the appropriate module directory
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use descriptive test names that explain what is being tested

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_parser_extracts_text(sample_pdf):
    # Arrange
    parser = PyMuPDFParser()

    # Act
    result = parser.parse(sample_pdf)

    # Assert
    assert "PDF Bench Sample Document" in result
    assert len(result) > 100
```

### Using Fixtures

Leverage shared fixtures for common test data:

```python
def test_metric_calculation(sample_ground_truth_text):
    # Fixture provides the text directly
    actual = "# PDF Bench Sample Document\n\nTest content"
    similarity = edit_similarity(actual, sample_ground_truth_text)
    assert similarity > 0.5
```

### Testing Parsers

When testing new parsers:

1. Use `sample_pdf` fixture for input
2. Compare against `sample_ground_truth_text`
3. Use `assert_markdown_similar()` with appropriate threshold
4. Test both success and error cases

Example:
```python
def test_new_parser(sample_pdf, sample_ground_truth_text):
    parser = NewParser()
    result = parser.parse(sample_pdf)

    # Use 0.90 threshold for less strict comparison
    assert_markdown_similar(result, sample_ground_truth_text, threshold=0.90)
```

### Testing Metrics

When testing metrics:

1. Use known inputs with expected outputs
2. Test edge cases (empty strings, identical strings, completely different strings)
3. Test properties (symmetry, triangle inequality, etc.)

Example:
```python
def test_metric_symmetry():
    text1 = "Hello world"
    text2 = "Hello earth"

    score1 = metric(text1, text2)
    score2 = metric(text2, text1)

    assert score1 == score2
```

## Coverage

Target coverage: 80%+

Generate coverage report:
```bash
uv run pytest --cov=pdf_bench --cov-report=html
open htmlcov/index.html
```

## Quality Checks

Before committing, run all quality checks:

```bash
# Format check
uv run ruff format --check pdf_bench/ tests/

# Lint check
uv run ruff check pdf_bench/ tests/

# Type check
uv run mypy pdf_bench/

# Run tests
uv run pytest
```

## Adding New Fixtures

When adding new test fixtures:

1. Place files in `tests/fixtures/`
2. Add fixture function to `conftest.py` if reusable
3. Document the fixture in this README
4. Keep fixtures small and focused

Example:
```python
@pytest.fixture
def complex_pdf() -> Path:
    """Fixture for PDF with tables and images."""
    return Path(__file__).parent / "fixtures" / "complex.pdf"
```

## Debugging Tests

### Run single test with output
```bash
uv run pytest tests/test_systems/test_pymupdf.py::test_parse -v -s
```

### Drop into debugger on failure
```bash
uv run pytest --pdb
```

### Show local variables on failure
```bash
uv run pytest -l
```

### Increase verbosity
```bash
uv run pytest -vv
```

## Performance

For performance-sensitive tests:

```python
import pytest

@pytest.mark.timeout(5)  # Fail if test takes > 5 seconds
def test_fast_operation():
    result = fast_function()
    assert result is not None
```

## Test Data Guidelines

- Keep test PDFs small (< 50KB)
- Use diverse test cases (simple text, tables, images)
- Version control all test fixtures
- Document expected behavior in comments

## Contributing

When contributing tests:

1. Ensure all tests pass locally
2. Add tests for new features
3. Maintain test coverage above 80%
4. Follow existing test patterns
5. Update this README if adding new test utilities
