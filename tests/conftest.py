"""Pytest configuration and shared fixtures for PDF-Bench tests.

This module provides pytest configuration and shared fixtures that are
available to all test modules in the suite.
"""

from pathlib import Path

import pytest


@pytest.fixture
def sample_pdf() -> Path:
    """Fixture providing path to sample PDF file.

    Returns:
        Absolute path to tests/fixtures/sample.pdf

    Example:
        >>> def test_parser(sample_pdf):
        ...     result = parse_pdf(sample_pdf)
        ...     assert result is not None
    """
    fixture_path = Path(__file__).parent / "fixtures" / "sample.pdf"
    assert fixture_path.exists(), f"Sample PDF not found: {fixture_path}"
    return fixture_path


@pytest.fixture
def sample_ground_truth() -> Path:
    """Fixture providing path to ground truth markdown file.

    Returns:
        Absolute path to tests/fixtures/sample_ground_truth.md

    Example:
        >>> def test_accuracy(sample_pdf, sample_ground_truth):
        ...     actual = parse_pdf(sample_pdf)
        ...     expected = sample_ground_truth.read_text()
        ...     assert_markdown_similar(actual, expected)
    """
    fixture_path = Path(__file__).parent / "fixtures" / "sample_ground_truth.md"
    assert fixture_path.exists(), f"Ground truth not found: {fixture_path}"
    return fixture_path


@pytest.fixture
def sample_ground_truth_text(sample_ground_truth: Path) -> str:
    """Fixture providing ground truth markdown content as string.

    Convenience fixture that reads the ground truth file and returns
    its content, saving test code from having to read it.

    Args:
        sample_ground_truth: Path fixture (dependency)

    Returns:
        Content of the ground truth markdown file

    Example:
        >>> def test_content(sample_ground_truth_text):
        ...     assert "PDF Bench Sample Document" in sample_ground_truth_text
    """
    return sample_ground_truth.read_text(encoding="utf-8")


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Fixture providing temporary output directory for tests.

    Uses pytest's tmp_path fixture to create a unique temporary directory
    that is automatically cleaned up after the test.

    Args:
        tmp_path: Pytest's built-in tmp_path fixture

    Returns:
        Path to temporary directory

    Example:
        >>> def test_output(temp_output_dir):
        ...     output_file = temp_output_dir / "result.md"
        ...     output_file.write_text("# Test")
        ...     assert output_file.exists()
    """
    return tmp_path


@pytest.fixture
def fixtures_dir() -> Path:
    """Fixture providing path to fixtures directory.

    Returns:
        Absolute path to tests/fixtures/

    Example:
        >>> def test_fixtures(fixtures_dir):
        ...     all_fixtures = list(fixtures_dir.glob("*"))
        ...     assert len(all_fixtures) > 0
    """
    return Path(__file__).parent / "fixtures"


# Configure pytest settings
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "requires_api: marks tests that require API credentials")
