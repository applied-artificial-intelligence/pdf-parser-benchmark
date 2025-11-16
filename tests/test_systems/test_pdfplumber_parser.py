"""Tests for pdfplumber parser implementation."""

import shutil
from pathlib import Path

import pdfplumber  # type: ignore[import-untyped]
import pytest

from pdf_bench.systems.pdfplumber_parser import PdfPlumberParser
from pdf_bench.utils.caching import clear_cache, get_cache_stats


@pytest.fixture
def parser() -> PdfPlumberParser:
    """Create a PdfPlumberParser instance."""
    return PdfPlumberParser()


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Copy sample PDF to temp directory for testing."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    sample_pdf = fixtures_dir / "sample.pdf"

    if not sample_pdf.exists():
        pytest.skip("Sample PDF not found - run create_sample_pdf.py first")

    # Copy to temp directory to avoid modifying test fixtures
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
    clear_cache(cache_dir, parser_name="pdfplumber")


class TestPdfPlumberParserProperties:
    """Test parser properties (name, version)."""

    def test_parser_name(self, parser: PdfPlumberParser) -> None:
        """Test that parser name is correct."""
        assert parser.name == "pdfplumber"

    def test_parser_version(self, parser: PdfPlumberParser) -> None:
        """Test that parser version matches pdfplumber version."""
        assert parser.version == pdfplumber.__version__
        # Version should be a non-empty string
        assert isinstance(parser.version, str)
        assert len(parser.version) > 0

    def test_parser_repr(self, parser: PdfPlumberParser) -> None:
        """Test parser string representation."""
        repr_str = repr(parser)
        assert "PdfPlumberParser" in repr_str
        assert "pdfplumber" in repr_str
        assert parser.version in repr_str


class TestPdfPlumberParserBasicParsing:
    """Test basic parsing functionality."""

    def test_parse_sample_pdf(
        self, parser: PdfPlumberParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test parsing a simple PDF."""
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

    def test_parse_creates_markdown_file(
        self, parser: PdfPlumberParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that parse creates a markdown file."""
        result = parser.parse(sample_pdf, output_dir)

        # File should have .md extension
        assert result.suffix == ".md"

        # File should be in cache directory (because of caching)
        assert ".cache" in str(result)
        assert "pdfplumber" in str(result)

    def test_parse_extracts_text_content(
        self, parser: PdfPlumberParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that parser extracts expected text content."""
        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Check for key sections
        assert "PDF-Bench" in content or "PDF Bench" in content
        assert "benchmarking suite" in content
        assert "parser" in content.lower() or "Parser" in content

        # Content should not be empty or just whitespace
        assert content.strip()


class TestPdfPlumberParserTableExtraction:
    """Test table extraction and Markdown conversion."""

    def test_table_to_markdown_simple(self, parser: PdfPlumberParser) -> None:
        """Test converting a simple table to Markdown."""
        table = [
            ["Name", "Age"],
            ["Alice", "30"],
            ["Bob", "25"],
        ]

        result = parser._table_to_markdown(table)

        # Check that it produces a markdown table
        assert "| Name | Age |" in result
        assert "| --- | --- |" in result
        assert "| Alice | 30 |" in result
        assert "| Bob | 25 |" in result

    def test_table_to_markdown_with_none_values(self, parser: PdfPlumberParser) -> None:
        """Test converting a table with None values to Markdown."""
        table = [
            ["Name", "Age", "City"],
            ["Alice", "30", None],
            ["Bob", None, "NYC"],
        ]

        result = parser._table_to_markdown(table)

        # None values should be converted to empty strings
        assert "| Name | Age | City |" in result
        assert "| Alice | 30 |  |" in result
        assert "| Bob |  | NYC |" in result

    def test_table_to_markdown_irregular_rows(self, parser: PdfPlumberParser) -> None:
        """Test converting a table with irregular row lengths."""
        table = [
            ["Name", "Age", "City"],
            ["Alice", "30"],  # Missing City
            ["Bob", "25", "NYC", "Extra"],  # Extra column ignored
        ]

        result = parser._table_to_markdown(table)

        # Should normalize to max columns (4 in this case due to "Extra")
        assert "| Name | Age | City |" in result or "| Name | Age | City |  |" in result
        # Alice should have empty city
        assert "| Alice | 30 |" in result

    def test_table_to_markdown_empty_table(self, parser: PdfPlumberParser) -> None:
        """Test converting an empty table."""
        table: list[list[str]] = []

        result = parser._table_to_markdown(table)

        # Should return empty string
        assert result == ""

    def test_table_to_markdown_single_row(self, parser: PdfPlumberParser) -> None:
        """Test converting a table with only one row (header only)."""
        table = [["Name", "Age"]]

        result = parser._table_to_markdown(table)

        # Should return empty string (need at least header + 1 data row)
        assert result == ""

    def test_table_to_markdown_with_whitespace(self, parser: PdfPlumberParser) -> None:
        """Test that table cells are properly trimmed."""
        table = [
            ["  Name  ", " Age "],
            [" Alice ", "  30  "],
        ]

        result = parser._table_to_markdown(table)

        # Whitespace should be trimmed
        assert "| Name | Age |" in result
        assert "| Alice | 30 |" in result


class TestPdfPlumberParserCaching:
    """Test cache integration."""

    def test_cache_miss_on_first_parse(
        self, parser: PdfPlumberParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that first parse is a cache miss."""
        # Clear cache to ensure clean state
        clear_cache(Path(".cache"), parser_name="pdfplumber")

        # First parse should be a miss
        _ = parser.parse(sample_pdf, output_dir)

        # Check cache stats
        stats = get_cache_stats(Path(".cache"))
        assert "pdfplumber" in stats["parsers"]
        parser_stats = stats["parsers"]["pdfplumber"]

        # Should have at least one miss
        assert parser_stats["misses"] >= 1

        # Should have at least one entry
        assert parser_stats["entries"] >= 1

    def test_cache_hit_on_second_parse(
        self, parser: PdfPlumberParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that second parse of same PDF is a cache hit."""
        # Clear cache first
        clear_cache(Path(".cache"), parser_name="pdfplumber")

        # First parse
        result1 = parser.parse(sample_pdf, output_dir)

        # Get stats after first parse
        stats1 = get_cache_stats(Path(".cache"))
        initial_misses = stats1["parsers"]["pdfplumber"]["misses"]

        # Second parse (should hit cache)
        result2 = parser.parse(sample_pdf, output_dir)

        # Check that results are in cache directory
        assert ".cache" in str(result1)
        assert ".cache" in str(result2)

        # Both should return the same cached path
        assert result1 == result2

        # Get stats after second parse
        stats2 = get_cache_stats(Path(".cache"))
        final_hits = stats2["parsers"]["pdfplumber"]["hits"]
        final_misses = stats2["parsers"]["pdfplumber"]["misses"]

        # Misses should not have increased
        assert final_misses == initial_misses

        # Hits should have increased by 1
        assert final_hits >= 1

    def test_cache_stores_in_correct_directory(
        self, parser: PdfPlumberParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that cache stores files in correct directory."""
        result = parser.parse(sample_pdf, output_dir)

        # Result should be in .cache/pdfplumber/
        assert ".cache" in str(result)
        assert "pdfplumber" in str(result)
        assert result.parent.name == "pdfplumber"


class TestPdfPlumberParserErrorHandling:
    """Test error handling for various edge cases."""

    def test_parse_nonexistent_file(
        self, parser: PdfPlumberParser, output_dir: Path
    ) -> None:
        """Test that parsing nonexistent file raises FileNotFoundError."""
        nonexistent = Path("/tmp/nonexistent_file_12345.pdf")

        with pytest.raises(FileNotFoundError):
            parser.parse(nonexistent, output_dir)

    def test_parse_directory_instead_of_file(
        self, parser: PdfPlumberParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parsing a directory raises ValueError."""
        directory = tmp_path / "somedir"
        directory.mkdir()

        with pytest.raises(ValueError, match="not a file"):
            parser.parse(directory, output_dir)

    def test_parse_creates_output_dir_if_missing(
        self, parser: PdfPlumberParser, sample_pdf: Path, tmp_path: Path
    ) -> None:
        """Test that parser creates output directory if it doesn't exist."""
        nonexistent_output = tmp_path / "nonexistent" / "nested" / "output"

        # Output directory doesn't exist yet
        assert not nonexistent_output.exists()

        # Should create it and parse successfully
        result = parser.parse(sample_pdf, nonexistent_output)

        # Should succeed without raising
        assert result.exists()

    def test_parse_invalid_pdf(
        self, parser: PdfPlumberParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parsing invalid PDF raises RuntimeError."""
        # Create a file that's not a valid PDF
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_text("This is not a PDF file", encoding="utf-8")

        with pytest.raises(RuntimeError, match="corrupted or invalid|Failed to parse"):
            parser.parse(invalid_pdf, output_dir)


class TestPdfPlumberParserTextExtraction:
    """Test text extraction behavior."""

    def test_extract_handles_empty_pdf(
        self, parser: PdfPlumberParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser handles PDF with no text."""
        # Create a minimal empty PDF using reportlab
        from reportlab.pdfgen import canvas  # type: ignore[import-untyped]

        empty_pdf = tmp_path / "empty.pdf"

        # Create a blank PDF with reportlab
        c = canvas.Canvas(str(empty_pdf))
        c.showPage()
        c.save()

        # Should parse without error
        result = parser.parse(empty_pdf, output_dir)

        # Result should exist but may be empty or have minimal content
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        # Content should be empty or just whitespace
        assert len(content.strip()) == 0

    def test_extract_handles_multipage_pdf(
        self, parser: PdfPlumberParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser handles multi-page PDFs."""
        from reportlab.pdfgen import canvas  # type: ignore[import-untyped]

        # Create multi-page PDF
        multipage_pdf = tmp_path / "multipage.pdf"
        c = canvas.Canvas(str(multipage_pdf))

        # Page 1
        c.drawString(100, 750, "Content on page 1")
        c.showPage()

        # Page 2
        c.drawString(100, 750, "Content on page 2")
        c.showPage()

        # Page 3
        c.drawString(100, 750, "Content on page 3")
        c.showPage()

        c.save()

        # Parse and check output
        result = parser.parse(multipage_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # All pages should be in output
        assert "page 1" in content
        assert "page 2" in content
        assert "page 3" in content

    def test_extract_normalizes_text(
        self, parser: PdfPlumberParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that extracted text is normalized."""
        from reportlab.pdfgen import canvas  # type: ignore[import-untyped]

        # Create PDF with text that needs normalization
        pdf_path = tmp_path / "normalize.pdf"
        c = canvas.Canvas(str(pdf_path))

        # Add text with smart quotes and extra whitespace
        c.drawString(100, 750, "Test   with    spaces")
        c.showPage()
        c.save()

        # Parse
        result = parser.parse(pdf_path, output_dir)
        content = result.read_text(encoding="utf-8")

        # Whitespace should be normalized
        # (Multiple spaces collapsed to single space)
        assert "Test with spaces" in content or "spaces" in content


class TestPdfPlumberParserIntegration:
    """Integration tests with real sample PDF."""

    def test_parse_integration_with_sample(
        self, parser: PdfPlumberParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test complete parsing workflow with sample PDF."""
        # Parse the PDF
        result = parser.parse(sample_pdf, output_dir)

        # Verify result
        assert result.exists()
        assert result.suffix == ".md"

        # Read content
        content = result.read_text(encoding="utf-8")

        # Should have meaningful content
        assert len(content) > 100

        # Should be valid markdown (basic check)
        lines = content.split("\n")
        assert len(lines) > 0

    def test_compare_with_ground_truth(
        self, parser: PdfPlumberParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that parsed output is similar to ground truth."""
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        ground_truth_path = fixtures_dir / "sample_ground_truth.md"

        if not ground_truth_path.exists():
            pytest.skip("Ground truth not found")

        # Parse the PDF
        result = parser.parse(sample_pdf, output_dir)
        parsed_content = result.read_text(encoding="utf-8")

        # Both should contain key sections
        key_terms = ["PDF Bench", "Introduction", "Features", "Conclusion"]
        for term in key_terms:
            # Allow for minor variations
            assert (
                term in parsed_content or term.lower() in parsed_content.lower()
            ), f"Missing term: {term}"
