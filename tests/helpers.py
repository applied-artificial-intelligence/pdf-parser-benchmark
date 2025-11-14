"""Test helper utilities for PDF-Bench tests.

This module provides reusable helper functions for testing PDF parsing,
markdown comparison, and file handling across the test suite.
"""

from pathlib import Path


def assert_markdown_similar(
    actual: str,
    expected: str,
    threshold: float = 0.95,
    metric: str = "edit_distance",
) -> None:
    """Assert that two markdown strings are similar within a threshold.

    Uses the edit distance metric to compare strings and asserts that
    their similarity score meets or exceeds the specified threshold.

    Args:
        actual: The actual markdown string produced by the parser
        expected: The expected markdown string (ground truth)
        threshold: Minimum similarity score (0.0-1.0). Default 0.95
        metric: Metric to use for comparison. Default "edit_distance"

    Raises:
        AssertionError: If similarity is below threshold

    Example:
        >>> actual = "# Header\\n\\nSome text"
        >>> expected = "# Header\\n\\nSome text."
        >>> assert_markdown_similar(actual, expected, threshold=0.90)
    """
    from pdf_bench.metrics.edit_distance import edit_similarity

    if metric != "edit_distance":
        raise ValueError(f"Unsupported metric: {metric}")

    similarity = edit_similarity(actual, expected)
    assert similarity >= threshold, (
        f"Markdown similarity {similarity:.4f} is below threshold {threshold:.4f}\n"
        f"Expected length: {len(expected)}\n"
        f"Actual length: {len(actual)}\n"
        f"First 200 chars of expected:\n{expected[:200]!r}\n"
        f"First 200 chars of actual:\n{actual[:200]!r}"
    )


def assert_files_similar(
    actual_path: Path,
    expected_path: Path,
    threshold: float = 0.95,
    encoding: str = "utf-8",
) -> None:
    """Assert that two markdown files are similar within a threshold.

    Reads both files and compares their content using the edit distance metric.

    Args:
        actual_path: Path to the actual markdown file
        expected_path: Path to the expected markdown file (ground truth)
        threshold: Minimum similarity score (0.0-1.0). Default 0.95
        encoding: File encoding. Default "utf-8"

    Raises:
        AssertionError: If similarity is below threshold
        FileNotFoundError: If either file does not exist

    Example:
        >>> actual = tmp_path / "output.md"
        >>> expected = Path("tests/fixtures/sample_ground_truth.md")
        >>> assert_files_similar(actual, expected, threshold=0.90)
    """
    actual_path = Path(actual_path)
    expected_path = Path(expected_path)

    if not actual_path.exists():
        raise FileNotFoundError(f"Actual file not found: {actual_path}")
    if not expected_path.exists():
        raise FileNotFoundError(f"Expected file not found: {expected_path}")

    actual_content = actual_path.read_text(encoding=encoding)
    expected_content = expected_path.read_text(encoding=encoding)

    try:
        assert_markdown_similar(actual_content, expected_content, threshold)
    except AssertionError as e:
        # Add file paths to error message for better debugging
        raise AssertionError(
            f"Files are not similar enough:\n"
            f"Actual: {actual_path}\n"
            f"Expected: {expected_path}\n"
            f"{str(e)}"
        ) from e


def get_fixture_path(filename: str) -> Path:
    """Get the absolute path to a fixture file.

    Args:
        filename: Name of the fixture file (e.g., "sample.pdf")

    Returns:
        Absolute path to the fixture file

    Raises:
        FileNotFoundError: If the fixture file does not exist

    Example:
        >>> sample_pdf = get_fixture_path("sample.pdf")
        >>> assert sample_pdf.exists()
    """
    fixture_path = Path(__file__).parent / "fixtures" / filename
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {filename}\nExpected at: {fixture_path}")
    return fixture_path


def get_test_output_dir(prefix: str = "pdfbench_test_") -> Path:
    """Create and return a temporary directory for test outputs.

    The directory is created in the system's temporary directory and
    will be automatically cleaned up by the OS eventually. For pytest,
    prefer using the tmp_path fixture instead.

    Args:
        prefix: Prefix for the temporary directory name. Default "pdfbench_test_"

    Returns:
        Path to the created temporary directory

    Example:
        >>> output_dir = get_test_output_dir()
        >>> output_file = output_dir / "result.md"
        >>> output_file.write_text("# Test")
    """
    import tempfile

    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    return temp_dir


def read_fixture(filename: str, encoding: str = "utf-8") -> str:
    """Read and return the contents of a fixture file.

    Convenience function that combines get_fixture_path() and read_text().

    Args:
        filename: Name of the fixture file
        encoding: File encoding. Default "utf-8"

    Returns:
        Contents of the fixture file as a string

    Example:
        >>> ground_truth = read_fixture("sample_ground_truth.md")
        >>> assert "# PDF Bench Sample Document" in ground_truth
    """
    fixture_path = get_fixture_path(filename)
    return fixture_path.read_text(encoding=encoding)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text for more lenient comparison.

    Strips leading/trailing whitespace from each line and converts
    multiple consecutive blank lines into a single blank line.

    Args:
        text: Text to normalize

    Returns:
        Text with normalized whitespace

    Example:
        >>> text = "  Line 1  \\n\\n\\n  Line 2  "
        >>> normalize_whitespace(text)
        'Line 1\\n\\nLine 2'
    """
    # Strip leading and trailing whitespace from each line
    lines = [line.strip() for line in text.splitlines()]

    # Remove multiple consecutive blank lines
    normalized_lines = []
    prev_blank = False
    for line in lines:
        is_blank = not line
        if is_blank and prev_blank:
            continue
        normalized_lines.append(line)
        prev_blank = is_blank

    return "\n".join(normalized_lines).strip()


def count_markdown_elements(text: str) -> dict[str, int]:
    """Count markdown elements in text for structural comparison.

    Counts headers, list items, code blocks, and paragraphs to enable
    structural comparison beyond simple text similarity.

    Args:
        text: Markdown text to analyze

    Returns:
        Dictionary with counts of markdown elements:
        - headers: Number of header lines (# ...)
        - list_items: Number of list items (- ..., * ..., 1. ...)
        - code_blocks: Number of code block delimiters (```)
        - paragraphs: Number of non-empty, non-header, non-list lines

    Example:
        >>> md = "# Title\\n\\nPara 1\\n\\n- Item 1\\n- Item 2"
        >>> counts = count_markdown_elements(md)
        >>> counts["headers"]
        1
        >>> counts["list_items"]
        2
    """
    lines = text.splitlines()

    counts = {
        "headers": 0,
        "list_items": 0,
        "code_blocks": 0,
        "paragraphs": 0,
    }

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("#"):
            counts["headers"] += 1
        elif stripped.startswith("```"):
            counts["code_blocks"] += 1
        elif stripped.startswith(("-", "*", "+")):
            counts["list_items"] += 1
        elif stripped[0].isdigit() and "." in stripped[:4]:
            counts["list_items"] += 1
        else:
            counts["paragraphs"] += 1

    return counts
