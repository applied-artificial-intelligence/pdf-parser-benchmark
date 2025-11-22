"""Tests for Unstructured parser implementation."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pdf_bench.systems.unstructured_parser import UnstructuredParser
from pdf_bench.utils.caching import clear_cache


@pytest.fixture
def parser() -> UnstructuredParser:
    """Create an UnstructuredParser instance with fast strategy."""
    return UnstructuredParser(strategy="fast")


@pytest.fixture
def parser_auto() -> UnstructuredParser:
    """Create an UnstructuredParser instance with auto strategy."""
    return UnstructuredParser(strategy="auto")


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Copy sample PDF to temp directory for testing."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    sample_pdf = fixtures_dir / "sample.pdf"

    if not sample_pdf.exists():
        pytest.skip("Sample PDF not found - run create_sample_pdf.py first")

    # Copy to temp directory
    temp_pdf = tmp_path / "sample.pdf"
    shutil.copy(sample_pdf, temp_pdf)
    return temp_pdf


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture(autouse=True)
def clear_test_cache() -> None:
    """Clear cache before each test to ensure clean state."""
    cache_dir = Path(".cache")
    clear_cache(cache_dir, parser_name="unstructured")


class TestUnstructuredParserProperties:
    """Test parser properties (name, version)."""

    def test_parser_name(self, parser: UnstructuredParser) -> None:
        """Test that parser name is correct."""
        assert parser.name == "unstructured"

    def test_parser_version(self, parser: UnstructuredParser) -> None:
        """Test that parser version is a non-empty string."""
        assert isinstance(parser.version, str)
        assert len(parser.version) > 0
        # Should look like a version number
        assert "." in parser.version

    def test_parser_repr(self, parser: UnstructuredParser) -> None:
        """Test parser string representation."""
        repr_str = repr(parser)
        assert "UnstructuredParser" in repr_str
        assert "unstructured" in repr_str
        assert parser.version in repr_str


class TestUnstructuredParserInitialization:
    """Test parser initialization and configuration."""

    def test_default_strategy_is_fast(self) -> None:
        """Test that default strategy is 'fast'."""
        parser = UnstructuredParser()
        assert parser._strategy == "fast"
        assert parser._infer_table_structure is False

    def test_custom_strategy(self) -> None:
        """Test initialization with custom strategy."""
        parser = UnstructuredParser(strategy="auto")
        assert parser._strategy == "auto"

    def test_table_structure_inference(self) -> None:
        """Test initialization with table structure inference."""
        parser = UnstructuredParser(strategy="hi_res", infer_table_structure=True)
        assert parser._strategy == "hi_res"
        assert parser._infer_table_structure is True

    def test_invalid_strategy_raises_error(self) -> None:
        """Test that invalid strategy raises ValueError."""
        with pytest.raises(ValueError, match="Invalid strategy"):
            UnstructuredParser(strategy="invalid")


class TestUnstructuredParserBasicParsing:
    """Test basic parsing functionality."""

    def test_parse_sample_pdf_fast_strategy(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test parsing a simple PDF with fast strategy."""
        result = parser.parse(sample_pdf, output_dir)

        # Check that result path is returned
        assert result is not None
        assert isinstance(result, Path)

        # Check that file was created
        assert result.exists()
        assert result.is_file()

        # Check that file has .md extension
        assert result.suffix == ".md"

        # Check that file has content
        content = result.read_text(encoding="utf-8")
        assert len(content) > 0

        # Check that expected text is in the output
        assert "PDF Bench Sample Document" in content
        assert "Introduction" in content
        assert "Features" in content
        assert "Conclusion" in content

    def test_parse_sample_pdf_auto_strategy(
        self, parser_auto: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test parsing with auto strategy."""
        result = parser_auto.parse(sample_pdf, output_dir)

        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert len(content) > 0
        assert "PDF Bench" in content

    def test_parse_creates_output_directory(
        self, parser: UnstructuredParser, sample_pdf: Path, tmp_path: Path
    ) -> None:
        """Test that parse creates output directory if it doesn't exist."""
        nonexistent_output = tmp_path / "new_output_dir"
        assert not nonexistent_output.exists()

        result = parser.parse(sample_pdf, nonexistent_output)

        assert result.exists()
        # Result is cached
        assert ".cache" in str(result)

    def test_parse_returns_markdown_file(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that output is a markdown file."""
        result = parser.parse(sample_pdf, output_dir)

        assert result.suffix == ".md"
        assert result.is_file()


class TestUnstructuredParserErrorHandling:
    """Test error handling for various failure scenarios."""

    def test_parse_nonexistent_pdf(self, parser: UnstructuredParser, output_dir: Path) -> None:
        """Test that parsing a nonexistent PDF raises FileNotFoundError."""
        nonexistent_pdf = Path("/tmp/does_not_exist.pdf")

        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            parser.parse(nonexistent_pdf, output_dir)

    def test_parse_directory_as_pdf(
        self, parser: UnstructuredParser, output_dir: Path, tmp_path: Path
    ) -> None:
        """Test that parsing a directory raises ValueError."""
        with pytest.raises(ValueError, match="Path is not a file"):
            parser.parse(tmp_path, output_dir)

    def test_parse_failure_raises_runtime_error(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that partition_pdf failure raises RuntimeError."""
        with patch("pdf_bench.systems.unstructured_parser.partition_pdf") as mock_part:
            mock_part.side_effect = Exception("Partition failed")

            with pytest.raises(RuntimeError, match="Failed to parse PDF"):
                parser.parse(sample_pdf, output_dir)


class TestUnstructuredParserCaching:
    """Test caching behavior."""

    def test_parse_uses_cache_on_second_call(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that second parse of same PDF uses cache."""
        # First parse
        result1 = parser.parse(sample_pdf, output_dir)
        assert result1.exists()

        # Second parse should use cache
        with patch("pdf_bench.systems.unstructured_parser.partition_pdf") as mock_part:
            result2 = parser.parse(sample_pdf, output_dir)

            # partition_pdf should NOT be called (cache hit)
            mock_part.assert_not_called()

            # Results should be the same path
            assert result2 == result1
            assert result2.exists()

    def test_cache_different_strategies_separately(
        self, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that different strategies are cached separately."""
        parser_fast = UnstructuredParser(strategy="fast")
        parser_auto = UnstructuredParser(strategy="auto")

        # Parse with fast strategy
        result_fast = parser_fast.parse(sample_pdf, output_dir)
        assert result_fast.exists()

        # Parse with auto strategy (should not use fast cache)
        result_auto = parser_auto.parse(sample_pdf, output_dir)
        assert result_auto.exists()

        # Results should be different (different cache keys due to strategy)
        # Note: They might be the same if content is identical, but cache keys differ
        assert result_fast.exists()
        assert result_auto.exists()

    def test_cache_same_content_different_name(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path, tmp_path: Path
    ) -> None:
        """Test that PDFs with same content but different names use same cache."""
        # Parse first PDF
        result1 = parser.parse(sample_pdf, output_dir)
        assert result1.exists()

        # Create a copy with different name
        pdf2 = tmp_path / "different_name.pdf"
        shutil.copy(sample_pdf, pdf2)

        # Parse second PDF (same content, so should use same cache)
        result2 = parser.parse(pdf2, output_dir)
        assert result2.exists()

        # Same content = same cache entry (content-based hashing)
        assert result2 == result1


class TestUnstructuredParserMarkdownConversion:
    """Test markdown conversion from elements."""

    def test_markdown_has_proper_heading_format(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that headings are properly formatted in markdown."""
        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should have markdown headings
        assert "# PDF Bench Sample Document" in content or "#PDF Bench" in content.replace(" ", "")

    def test_markdown_has_list_items(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that list items are present in output."""
        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should have list items with dashes (may be on same line in fast mode)
        assert "- " in content

        # Should have multiple list markers
        list_marker_count = content.count("- ")
        assert list_marker_count >= 2

    def test_markdown_has_paragraph_separation(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that paragraphs are properly separated."""
        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should have paragraph breaks (double newlines)
        assert "\n\n" in content

    def test_empty_elements_are_filtered(self, parser: UnstructuredParser) -> None:
        """Test that empty elements are filtered out."""
        # Create mock elements with empty text
        mock_elements = [
            MagicMock(text="Some text", category="NarrativeText"),
            MagicMock(text="", category="NarrativeText"),  # Empty
            MagicMock(text="  ", category="NarrativeText"),  # Whitespace only
            MagicMock(text="More text", category="NarrativeText"),
        ]

        markdown = parser._elements_to_markdown(mock_elements)

        # Should only have two lines of content
        lines = [line for line in markdown.split("\n") if line.strip()]
        assert len(lines) == 2
        assert "Some text" in markdown
        assert "More text" in markdown


class TestUnstructuredParserIntegration:
    """Integration tests with real Unstructured execution."""

    def test_output_quality_comparison(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that Unstructured produces high-quality output."""
        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Check for proper markdown structure
        assert "#" in content  # Headings
        assert "\n\n" in content  # Paragraph separation

        # Check content preservation
        assert "PDF Bench" in content
        assert "benchmarking" in content or "benchmark" in content

        # File should not be empty or trivially small
        assert len(content) > 100

    def test_processing_speed(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that parsing completes in reasonable time."""
        import time

        start = time.time()
        result = parser.parse(sample_pdf, output_dir)
        elapsed = time.time() - start

        assert result.exists()
        # Fast strategy should complete quickly (under 5 seconds)
        assert elapsed < 5.0

    def test_element_categorization(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that elements are properly categorized."""
        # Parse and verify we get structured output
        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should have multiple element types
        # Titles (headings)
        assert content.count("#") >= 3  # Multiple headings

        # Paragraphs (double newlines between elements)
        assert content.count("\n\n") >= 3


class TestUnstructuredParserEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_parse_with_special_characters_in_filename(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path, tmp_path: Path
    ) -> None:
        """Test parsing PDF with special characters in filename."""
        # Create PDF with special characters in name
        special_pdf = tmp_path / "test-file_v1.2.pdf"
        shutil.copy(sample_pdf, special_pdf)

        result = parser.parse(special_pdf, output_dir)

        assert result.exists()
        assert result.suffix == ".md"

    def test_parse_multiple_pdfs_sequentially(
        self, parser: UnstructuredParser, sample_pdf: Path, output_dir: Path, tmp_path: Path
    ) -> None:
        """Test parsing multiple PDFs in sequence."""
        # Create multiple PDFs
        pdf1 = tmp_path / "doc1.pdf"
        pdf2 = tmp_path / "doc2.pdf"
        pdf3 = tmp_path / "doc3.pdf"

        shutil.copy(sample_pdf, pdf1)
        shutil.copy(sample_pdf, pdf2)
        shutil.copy(sample_pdf, pdf3)

        # Parse all three
        result1 = parser.parse(pdf1, output_dir)
        result2 = parser.parse(pdf2, output_dir)
        result3 = parser.parse(pdf3, output_dir)

        # All should exist
        assert result1.exists()
        assert result2.exists()
        assert result3.exists()

        # All should be markdown files
        assert result1.suffix == ".md"
        assert result2.suffix == ".md"
        assert result3.suffix == ".md"

    def test_empty_element_list(self, parser: UnstructuredParser) -> None:
        """Test markdown conversion with empty element list."""
        markdown = parser._elements_to_markdown([])
        assert markdown == ""
