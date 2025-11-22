"""Tests for PyMuPDF parser implementation."""

import shutil
from pathlib import Path

import fitz  # type: ignore[import-untyped]
import pytest

from pdf_bench.systems.pymupdf import PyMuPDFParser
from pdf_bench.utils.caching import clear_cache, get_cache_stats


@pytest.fixture
def parser() -> PyMuPDFParser:
    """Create a PyMuPDFParser instance."""
    return PyMuPDFParser()


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
    clear_cache(cache_dir, parser_name="pymupdf")


class TestPyMuPDFParserProperties:
    """Test parser properties (name, version)."""

    def test_parser_name(self, parser: PyMuPDFParser) -> None:
        """Test that parser name is correct."""
        assert parser.name == "pymupdf"

    def test_parser_version(self, parser: PyMuPDFParser) -> None:
        """Test that parser version matches PyMuPDF version."""
        assert parser.version == fitz.version[0]
        # Version should be a non-empty string
        assert isinstance(parser.version, str)
        assert len(parser.version) > 0

    def test_parser_repr(self, parser: PyMuPDFParser) -> None:
        """Test parser string representation."""
        repr_str = repr(parser)
        assert "PyMuPDFParser" in repr_str
        assert "pymupdf" in repr_str
        assert parser.version in repr_str


class TestPyMuPDFParserBasicParsing:
    """Test basic parsing functionality."""

    def test_parse_sample_pdf(
        self, parser: PyMuPDFParser, sample_pdf: Path, output_dir: Path
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
        self, parser: PyMuPDFParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that parse creates a markdown file."""
        result = parser.parse(sample_pdf, output_dir)

        # File should have .md extension
        assert result.suffix == ".md"

        # File should be in cache directory (because of caching)
        assert ".cache" in str(result)
        assert "pymupdf" in str(result)

    def test_parse_extracts_text_content(
        self, parser: PyMuPDFParser, sample_pdf: Path, output_dir: Path
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


class TestPyMuPDFParserCaching:
    """Test cache integration."""

    def test_cache_miss_on_first_parse(
        self, parser: PyMuPDFParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that first parse is a cache miss."""
        # Clear cache to ensure clean state
        clear_cache(Path(".cache"), parser_name="pymupdf")

        # First parse should be a miss
        _ = parser.parse(sample_pdf, output_dir)

        # Check cache stats
        stats = get_cache_stats(Path(".cache"))
        assert "pymupdf" in stats["parsers"]
        parser_stats = stats["parsers"]["pymupdf"]

        # Should have at least one miss
        assert parser_stats["misses"] >= 1

        # Should have at least one entry
        assert parser_stats["entries"] >= 1

    def test_cache_hit_on_second_parse(
        self, parser: PyMuPDFParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that second parse of same PDF is a cache hit."""
        # Clear cache first
        clear_cache(Path(".cache"), parser_name="pymupdf")

        # First parse
        result1 = parser.parse(sample_pdf, output_dir)

        # Get stats after first parse
        stats1 = get_cache_stats(Path(".cache"))
        initial_misses = stats1["parsers"]["pymupdf"]["misses"]

        # Second parse (should hit cache)
        result2 = parser.parse(sample_pdf, output_dir)

        # Check that results are in cache directory
        assert ".cache" in str(result1)
        assert ".cache" in str(result2)

        # Both should return the same cached path
        assert result1 == result2

        # Get stats after second parse
        stats2 = get_cache_stats(Path(".cache"))
        final_hits = stats2["parsers"]["pymupdf"]["hits"]
        final_misses = stats2["parsers"]["pymupdf"]["misses"]

        # Misses should not have increased
        assert final_misses == initial_misses

        # Hits should have increased by 1
        assert final_hits >= 1

    def test_cache_stores_in_correct_directory(
        self, parser: PyMuPDFParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that cache stores files in correct directory."""
        result = parser.parse(sample_pdf, output_dir)

        # Result should be in .cache/pymupdf/
        assert ".cache" in str(result)
        assert "pymupdf" in str(result)
        assert result.parent.name == "pymupdf"


class TestPyMuPDFParserErrorHandling:
    """Test error handling for various edge cases."""

    def test_parse_nonexistent_file(self, parser: PyMuPDFParser, output_dir: Path) -> None:
        """Test that parsing nonexistent file raises FileNotFoundError."""
        nonexistent = Path("/tmp/nonexistent_file_12345.pdf")

        with pytest.raises(FileNotFoundError):
            parser.parse(nonexistent, output_dir)

    def test_parse_directory_instead_of_file(
        self, parser: PyMuPDFParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parsing a directory raises ValueError."""
        directory = tmp_path / "somedir"
        directory.mkdir()

        with pytest.raises(ValueError, match="not a file"):
            parser.parse(directory, output_dir)

    def test_parse_creates_output_dir_if_missing(
        self, parser: PyMuPDFParser, sample_pdf: Path, tmp_path: Path
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
        self, parser: PyMuPDFParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parsing invalid PDF raises RuntimeError."""
        # Create a file that's not a valid PDF
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_text("This is not a PDF file", encoding="utf-8")

        with pytest.raises(RuntimeError, match="corrupted or invalid"):
            parser.parse(invalid_pdf, output_dir)

    def test_parse_password_protected_pdf(
        self, parser: PyMuPDFParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parsing password-protected PDF raises RuntimeError."""
        # Create a password-protected PDF
        protected_pdf = tmp_path / "protected.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Protected content")

        # Save with password
        doc.save(protected_pdf, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="password")
        doc.close()

        # Attempt to parse should raise RuntimeError
        with pytest.raises(RuntimeError, match="password-protected"):
            parser.parse(protected_pdf, output_dir)


class TestPyMuPDFParserTextExtraction:
    """Test text extraction behavior."""

    def test_extract_preserves_paragraph_breaks(
        self, parser: PyMuPDFParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser preserves paragraph breaks."""
        # Create PDF with clear paragraph structure
        pdf_path = tmp_path / "paragraphs.pdf"
        doc = fitz.open()
        page = doc.new_page()

        text = """First paragraph.

Second paragraph after a blank line.

Third paragraph."""

        page.insert_textbox(fitz.Rect(50, 50, 545, 792), text, fontsize=12)
        doc.save(pdf_path)
        doc.close()

        # Parse and check output
        result = parser.parse(pdf_path, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should have paragraph breaks
        assert "First paragraph" in content
        assert "Second paragraph" in content
        assert "Third paragraph" in content

    def test_extract_handles_empty_pdf(
        self, parser: PyMuPDFParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser handles PDF with no text."""
        # Create empty PDF
        empty_pdf = tmp_path / "empty.pdf"
        doc = fitz.open()
        doc.new_page()  # Empty page
        doc.save(empty_pdf)
        doc.close()

        # Should parse without error
        result = parser.parse(empty_pdf, output_dir)

        # Result should exist but may be empty or have minimal content
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        # Content should be empty or just whitespace
        assert len(content.strip()) == 0

    def test_extract_handles_multipage_pdf(
        self, parser: PyMuPDFParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser handles multi-page PDFs."""
        # Create multi-page PDF
        multipage_pdf = tmp_path / "multipage.pdf"
        doc = fitz.open()

        # Page 1
        page1 = doc.new_page()
        page1.insert_textbox(fitz.Rect(50, 50, 545, 792), "Content on page 1", fontsize=12)

        # Page 2
        page2 = doc.new_page()
        page2.insert_textbox(fitz.Rect(50, 50, 545, 792), "Content on page 2", fontsize=12)

        # Page 3
        page3 = doc.new_page()
        page3.insert_textbox(fitz.Rect(50, 50, 545, 792), "Content on page 3", fontsize=12)

        doc.save(multipage_pdf)
        doc.close()

        # Parse and check output
        result = parser.parse(multipage_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # All pages should be in output
        assert "page 1" in content
        assert "page 2" in content
        assert "page 3" in content
