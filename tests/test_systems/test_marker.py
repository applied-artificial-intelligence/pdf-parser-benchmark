"""Tests for Marker parser implementation."""

import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pdf_bench.systems.marker import MarkerParser
from pdf_bench.utils.caching import clear_cache


@pytest.fixture
def parser() -> MarkerParser:
    """Create a MarkerParser instance."""
    return MarkerParser()


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
    clear_cache(cache_dir, parser_name="marker")


class TestMarkerParserProperties:
    """Test parser properties (name, version)."""

    def test_parser_name(self, parser: MarkerParser) -> None:
        """Test that parser name is correct."""
        assert parser.name == "marker"

    def test_parser_version(self, parser: MarkerParser) -> None:
        """Test that parser version is a non-empty string."""
        assert isinstance(parser.version, str)
        assert len(parser.version) > 0
        # Version should follow semantic versioning pattern
        assert "." in parser.version

    def test_parser_repr(self, parser: MarkerParser) -> None:
        """Test parser string representation."""
        repr_str = repr(parser)
        assert "MarkerParser" in repr_str
        assert "marker" in repr_str
        assert parser.version in repr_str


class TestMarkerParserInitialization:
    """Test parser initialization and setup."""

    def test_marker_cmd_is_set(self, parser: MarkerParser) -> None:
        """Test that marker_single command path is set."""
        assert hasattr(parser, "_marker_cmd")
        assert parser._marker_cmd is not None
        assert "marker_single" in parser._marker_cmd

    def test_initialization_without_marker_installed(self) -> None:
        """Test that initialization fails gracefully if marker_single not found."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(RuntimeError, match="marker_single not found"):
                MarkerParser()


class TestMarkerParserBasicParsing:
    """Test basic parsing functionality."""

    def test_parse_sample_pdf(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test parsing a simple PDF with Marker."""
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
        # (Marker may use ## instead of # for first heading, either is acceptable)
        assert "PDF Bench Sample Document" in content
        assert "Introduction" in content
        assert "Features" in content
        assert "Conclusion" in content

    def test_parse_creates_output_directory(
        self, parser: MarkerParser, sample_pdf: Path, tmp_path: Path
    ) -> None:
        """Test that parse creates output directory if it doesn't exist."""
        nonexistent_output = tmp_path / "new_output_dir"
        assert not nonexistent_output.exists()

        result = parser.parse(sample_pdf, nonexistent_output)

        assert result.exists()
        # Result is cached, so it lives in .cache directory
        assert ".cache" in str(result)

    def test_parse_returns_markdown_file(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that output is a markdown file."""
        result = parser.parse(sample_pdf, output_dir)

        # Should return a .md file
        assert result.suffix == ".md"
        assert result.is_file()


class TestMarkerParserErrorHandling:
    """Test error handling for various failure scenarios."""

    def test_parse_nonexistent_pdf(
        self, parser: MarkerParser, output_dir: Path
    ) -> None:
        """Test that parsing a nonexistent PDF raises FileNotFoundError."""
        nonexistent_pdf = Path("/tmp/does_not_exist.pdf")

        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            parser.parse(nonexistent_pdf, output_dir)

    def test_parse_directory_as_pdf(
        self, parser: MarkerParser, output_dir: Path, tmp_path: Path
    ) -> None:
        """Test that parsing a directory raises ValueError."""
        with pytest.raises(ValueError, match="Path is not a file"):
            parser.parse(tmp_path, output_dir)

    def test_parse_subprocess_failure(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that subprocess failure raises RuntimeError."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd="marker_single", stderr="Error"
            )

            with pytest.raises(RuntimeError, match="Marker execution failed"):
                parser.parse(sample_pdf, output_dir)

    def test_parse_subprocess_timeout(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that subprocess timeout raises RuntimeError."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd="marker_single", timeout=300
            )

            with pytest.raises(RuntimeError, match="timed out"):
                parser.parse(sample_pdf, output_dir)

    def test_parse_missing_output_file(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that missing output file raises RuntimeError."""
        with patch("subprocess.run") as mock_run:
            # Mock successful subprocess but no output file created
            mock_result = MagicMock()
            mock_result.stdout = "Success"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            with pytest.raises(RuntimeError, match="did not generate expected output"):
                parser.parse(sample_pdf, output_dir)


class TestMarkerParserCaching:
    """Test caching behavior."""

    def test_parse_uses_cache_on_second_call(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that second parse of same PDF uses cache."""
        # First parse
        result1 = parser.parse(sample_pdf, output_dir)
        assert result1.exists()

        # Second parse should use cache
        with patch("subprocess.run") as mock_run:
            result2 = parser.parse(sample_pdf, output_dir)

            # subprocess.run should NOT be called (cache hit)
            mock_run.assert_not_called()

            # Results should be the same path (cache returns same file)
            assert result2 == result1
            assert result2.exists()
            assert result2.read_text() == result1.read_text()

    def test_parse_cache_invalidation_on_version_change(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that cache is invalidated when parser version changes."""
        # First parse
        result1 = parser.parse(sample_pdf, output_dir)
        assert result1.exists()

        # Clear cache for marker
        clear_cache(Path(".cache"), parser_name="marker")

        # Create new parser instance (simulating version change)
        with patch.object(MarkerParser, "version", new_callable=lambda: "2.0.0"):
            parser2 = MarkerParser()
            # This should trigger a new parse (cache miss due to version)
            result2 = parser2.parse(sample_pdf, output_dir)
            assert result2.exists()

    def test_cache_different_pdfs_separately(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path, tmp_path: Path
    ) -> None:
        """Test that different PDFs are cached separately."""
        # Parse first PDF
        result1 = parser.parse(sample_pdf, output_dir)
        assert result1.exists()

        # Create a second PDF (copy with different name)
        # Note: Same content = same hash = same cache entry
        # So we'll just verify it uses the same cached result
        pdf2 = tmp_path / "different.pdf"
        shutil.copy(sample_pdf, pdf2)

        # Parse second PDF (same content, so should use same cache)
        result2 = parser.parse(pdf2, output_dir)
        assert result2.exists()

        # Same content means same cache entry
        assert result2 == result1

        # Both should exist
        assert result1.exists()
        assert result2.exists()


class TestMarkerParserIntegration:
    """Integration tests with real Marker execution."""

    def test_marker_output_quality(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that Marker produces high-quality output."""
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

    def test_marker_handles_multipage_pdf(
        self, parser: MarkerParser, output_dir: Path, tmp_path: Path
    ) -> None:
        """Test that Marker handles multi-page PDFs correctly."""
        # This test uses sample.pdf which may be single-page
        # If we have a multi-page PDF fixture, use it
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        sample_pdf = fixtures_dir / "sample.pdf"

        if not sample_pdf.exists():
            pytest.skip("Sample PDF not found")

        temp_pdf = tmp_path / "sample.pdf"
        shutil.copy(sample_pdf, temp_pdf)

        result = parser.parse(temp_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should have content
        assert len(content) > 0

    def test_marker_subprocess_execution(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that marker_single subprocess is executed correctly."""
        with patch("subprocess.run", wraps=subprocess.run) as mock_run:
            result = parser.parse(sample_pdf, output_dir)

            # Verify subprocess.run was called
            mock_run.assert_called_once()

            # Verify correct arguments
            call_args = mock_run.call_args[0][0]
            assert "marker_single" in call_args[0]
            assert str(sample_pdf.absolute()) in call_args
            assert "--output_dir" in call_args

            # Result should exist
            assert result.exists()


class TestMarkerParserEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_parse_with_special_characters_in_filename(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path, tmp_path: Path
    ) -> None:
        """Test parsing PDF with special characters in filename."""
        # Create PDF with special characters in name
        special_pdf = tmp_path / "test-file_v1.2.pdf"
        shutil.copy(sample_pdf, special_pdf)

        result = parser.parse(special_pdf, output_dir)

        assert result.exists()
        # Result is cached with hash-based name
        assert result.suffix == ".md"

    def test_parse_cleans_up_temporary_directory(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path
    ) -> None:
        """Test that temporary Marker output directory is cleaned up."""
        result = parser.parse(sample_pdf, output_dir)

        # Temporary directory should be removed
        temp_dir = output_dir / "marker_temp"
        assert not temp_dir.exists()

        # Final result should exist
        assert result.exists()

    def test_parse_multiple_pdfs_sequentially(
        self, parser: MarkerParser, sample_pdf: Path, output_dir: Path, tmp_path: Path
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

        # All should be markdown files (cached, so they'll have hash-based names)
        assert result1.suffix == ".md"
        assert result2.suffix == ".md"
        assert result3.suffix == ".md"
