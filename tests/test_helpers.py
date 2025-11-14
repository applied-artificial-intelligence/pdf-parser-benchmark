"""Tests for test helper utilities.

Validates that test helpers work correctly and provide useful
error messages when assertions fail.
"""

from pathlib import Path

import pytest

from tests.helpers import (
    assert_files_similar,
    assert_markdown_similar,
    count_markdown_elements,
    get_fixture_path,
    get_test_output_dir,
    normalize_whitespace,
    read_fixture,
)


class TestAssertMarkdownSimilar:
    """Tests for assert_markdown_similar helper."""

    def test_identical_strings_pass(self):
        """Identical strings should pass with any threshold."""
        text = "# Header\n\nSome text"
        assert_markdown_similar(text, text, threshold=1.0)
        assert_markdown_similar(text, text, threshold=0.0)

    def test_similar_strings_pass(self):
        """Similar strings should pass with appropriate threshold."""
        actual = "# Header\n\nSome text here"
        expected = "# Header\n\nSome text there"
        assert_markdown_similar(actual, expected, threshold=0.80)

    def test_different_strings_fail(self):
        """Very different strings should fail."""
        actual = "Completely different"
        expected = "# Header\n\nSome text"
        with pytest.raises(AssertionError, match="similarity.*below threshold"):
            assert_markdown_similar(actual, expected, threshold=0.95)

    def test_error_message_includes_details(self):
        """Error message should include helpful debugging info."""
        actual = "Short"
        expected = "Much longer expected text"
        with pytest.raises(AssertionError) as excinfo:
            assert_markdown_similar(actual, expected, threshold=0.95)

        error_msg = str(excinfo.value)
        assert "similarity" in error_msg.lower()
        assert "threshold" in error_msg.lower()
        assert "length" in error_msg.lower()

    def test_empty_strings(self):
        """Empty strings should raise ValueError (edit_distance requirement)."""
        with pytest.raises(ValueError, match="Both input texts are empty"):
            assert_markdown_similar("", "", threshold=1.0)


class TestAssertFilesSimilar:
    """Tests for assert_files_similar helper."""

    def test_identical_files_pass(self, sample_ground_truth, tmp_path):
        """Identical files should pass."""
        # Copy ground truth to temp location
        temp_file = tmp_path / "copy.md"
        temp_file.write_text(sample_ground_truth.read_text())

        assert_files_similar(temp_file, sample_ground_truth, threshold=1.0)

    def test_similar_files_pass(self, sample_ground_truth, tmp_path):
        """Similar files should pass with appropriate threshold."""
        # Create slightly modified version
        original = sample_ground_truth.read_text()
        modified = original.replace("PDF-Bench", "PDF Bench")  # Small change

        temp_file = tmp_path / "modified.md"
        temp_file.write_text(modified)

        assert_files_similar(temp_file, sample_ground_truth, threshold=0.90)

    def test_missing_actual_file_raises(self, sample_ground_truth):
        """Missing actual file should raise FileNotFoundError."""
        missing = Path("/nonexistent/file.md")
        with pytest.raises(FileNotFoundError, match="Actual file not found"):
            assert_files_similar(missing, sample_ground_truth)

    def test_missing_expected_file_raises(self, tmp_path):
        """Missing expected file should raise FileNotFoundError."""
        actual = tmp_path / "actual.md"
        actual.write_text("Test")
        missing = Path("/nonexistent/expected.md")

        with pytest.raises(FileNotFoundError, match="Expected file not found"):
            assert_files_similar(actual, missing)

    def test_error_includes_file_paths(self, tmp_path):
        """Error message should include file paths."""
        actual_file = tmp_path / "actual.md"
        expected_file = tmp_path / "expected.md"
        actual_file.write_text("Completely different content")
        expected_file.write_text("# Header\n\nLots of text here")

        with pytest.raises(AssertionError) as excinfo:
            assert_files_similar(actual_file, expected_file, threshold=0.95)

        error_msg = str(excinfo.value)
        assert "actual.md" in error_msg
        assert "expected.md" in error_msg


class TestGetFixturePath:
    """Tests for get_fixture_path helper."""

    def test_existing_fixture(self):
        """Should return path to existing fixture."""
        path = get_fixture_path("sample.pdf")
        assert path.exists()
        assert path.name == "sample.pdf"
        assert path.is_absolute()

    def test_missing_fixture_raises(self):
        """Should raise FileNotFoundError for missing fixture."""
        with pytest.raises(FileNotFoundError, match="Fixture file not found"):
            get_fixture_path("nonexistent.pdf")


class TestGetTestOutputDir:
    """Tests for get_test_output_dir helper."""

    def test_creates_directory(self):
        """Should create and return temp directory."""
        output_dir = get_test_output_dir()
        assert output_dir.exists()
        assert output_dir.is_dir()
        assert output_dir.is_absolute()

    def test_custom_prefix(self):
        """Should use custom prefix."""
        output_dir = get_test_output_dir(prefix="custom_test_")
        assert "custom_test_" in output_dir.name


class TestReadFixture:
    """Tests for read_fixture helper."""

    def test_reads_ground_truth(self):
        """Should read ground truth fixture."""
        content = read_fixture("sample_ground_truth.md")
        assert "PDF Bench Sample Document" in content
        assert "Introduction" in content
        assert len(content) > 100

    def test_missing_fixture_raises(self):
        """Should raise FileNotFoundError for missing fixture."""
        with pytest.raises(FileNotFoundError):
            read_fixture("nonexistent.md")


class TestNormalizeWhitespace:
    """Tests for normalize_whitespace helper."""

    def test_strips_leading_trailing(self):
        """Should strip leading and trailing whitespace."""
        text = "  Line 1  \n  Line 2  "
        result = normalize_whitespace(text)
        assert result == "Line 1\nLine 2"

    def test_removes_multiple_blank_lines(self):
        """Should collapse multiple blank lines."""
        text = "Line 1\n\n\n\nLine 2"
        result = normalize_whitespace(text)
        assert result == "Line 1\n\nLine 2"

    def test_preserves_single_blank_lines(self):
        """Should preserve single blank lines."""
        text = "Line 1\n\nLine 2"
        result = normalize_whitespace(text)
        assert result == "Line 1\n\nLine 2"

    def test_empty_string(self):
        """Should handle empty string."""
        assert normalize_whitespace("") == ""
        assert normalize_whitespace("   \n\n   ") == ""


class TestCountMarkdownElements:
    """Tests for count_markdown_elements helper."""

    def test_counts_headers(self):
        """Should count header lines."""
        text = "# H1\n## H2\n### H3"
        counts = count_markdown_elements(text)
        assert counts["headers"] == 3

    def test_counts_list_items(self):
        """Should count list items."""
        text = "- Item 1\n- Item 2\n* Item 3\n1. Numbered"
        counts = count_markdown_elements(text)
        assert counts["list_items"] == 4

    def test_counts_code_blocks(self):
        """Should count code block delimiters."""
        text = "```python\ncode\n```\n\n```\nmore\n```"
        counts = count_markdown_elements(text)
        assert counts["code_blocks"] == 4  # 2 opening + 2 closing

    def test_counts_paragraphs(self):
        """Should count paragraph lines."""
        text = "Para 1\n\nPara 2\n\nPara 3"
        counts = count_markdown_elements(text)
        assert counts["paragraphs"] == 3

    def test_complex_document(self, sample_ground_truth_text):
        """Should correctly count elements in ground truth."""
        counts = count_markdown_elements(sample_ground_truth_text)

        # Ground truth should have:
        # - Multiple headers (# and ##)
        # - List items (Features section)
        # - Paragraphs
        assert counts["headers"] > 0
        assert counts["list_items"] > 0
        assert counts["paragraphs"] > 0

    def test_empty_document(self):
        """Should return zero counts for empty document."""
        counts = count_markdown_elements("")
        assert counts["headers"] == 0
        assert counts["list_items"] == 0
        assert counts["code_blocks"] == 0
        assert counts["paragraphs"] == 0


class TestGroundTruthFixture:
    """Validate the ground truth fixture itself."""

    def test_ground_truth_exists(self, sample_ground_truth):
        """Ground truth file should exist."""
        assert sample_ground_truth.exists()
        assert sample_ground_truth.is_file()

    def test_ground_truth_content(self, sample_ground_truth_text):
        """Ground truth should have expected content."""
        assert "PDF Bench Sample Document" in sample_ground_truth_text
        assert "Introduction" in sample_ground_truth_text
        assert "Features" in sample_ground_truth_text
        assert "Conclusion" in sample_ground_truth_text

    def test_ground_truth_structure(self, sample_ground_truth_text):
        """Ground truth should have proper markdown structure."""
        counts = count_markdown_elements(sample_ground_truth_text)

        # Should have at least:
        # - 1 main header (# Title)
        # - 3 section headers (## Introduction, Features, Conclusion)
        # - 4 list items (Features section)
        assert counts["headers"] >= 4
        assert counts["list_items"] >= 4
        assert counts["paragraphs"] >= 3

    def test_ground_truth_matches_pdf_content(self, sample_ground_truth_text):
        """Ground truth should match key content from sample PDF."""
        # These are key phrases from the PDF that should be in ground truth
        expected_phrases = [
            "PDF-Bench is an open-source benchmarking suite",
            "Support for multiple parser systems",
            "Comprehensive evaluation metrics",
            "Caching system for performance",
            "Extensible architecture",
        ]

        for phrase in expected_phrases:
            assert phrase in sample_ground_truth_text, f"Expected phrase not found: {phrase}"
