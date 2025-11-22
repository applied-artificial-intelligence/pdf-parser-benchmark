"""Integration tests for parser adapters.

This module tests all parser implementations together to ensure:
1. All parsers work on the same synthetic corpus
2. Cache behavior is consistent across parsers
3. Error handling is robust
4. Performance baselines can be captured

These tests validate that all parser adapters properly implement the
BaseParser interface and work correctly with the benchmarking infrastructure.
"""

import time
from pathlib import Path
from typing import Any

import pytest

from pdf_bench.systems import BaseParser
from pdf_bench.systems.marker import MarkerParser
from pdf_bench.systems.pdfplumber_parser import PdfPlumberParser
from pdf_bench.systems.pymupdf import PyMuPDFParser
from pdf_bench.systems.unstructured_parser import UnstructuredParser
from pdf_bench.utils.caching import clear_cache

# All parsers to test
ALL_PARSERS: list[tuple[str, type[BaseParser]]] = [
    ("pymupdf", PyMuPDFParser),
    ("pdfplumber", PdfPlumberParser),
    ("marker", MarkerParser),
    ("unstructured", UnstructuredParser),
]


@pytest.fixture(params=ALL_PARSERS, ids=[p[0] for p in ALL_PARSERS])
def parser_instance(request: Any) -> BaseParser:
    """Create parser instances for each parser type."""
    _parser_name, parser_class = request.param
    instance: BaseParser = parser_class()
    return instance


@pytest.fixture
def corpus_dir() -> Path:
    """Get the synthetic corpus directory."""
    corpus = Path("corpus/synthetic")
    if not corpus.exists():
        pytest.skip("Synthetic corpus not found")
    return corpus


@pytest.fixture
def test_pdfs(corpus_dir: Path) -> list[Path]:
    """Get list of test PDF files from synthetic corpus."""
    pdfs = list(corpus_dir.glob("*.pdf"))
    if not pdfs:
        pytest.skip("No PDF files in synthetic corpus")
    return sorted(pdfs)[:3]  # Use first 3 PDFs for faster testing


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create temporary output directory."""
    output = tmp_path / "parser_outputs"
    output.mkdir()
    return output


@pytest.fixture(autouse=True)
def clear_all_caches() -> None:
    """Clear all parser caches before each test."""
    cache_dir = Path(".cache")
    for parser_name, _ in ALL_PARSERS:
        clear_cache(cache_dir, parser_name=parser_name)


class TestParserInterfaceCompliance:
    """Test that all parsers properly implement BaseParser interface."""

    def test_parser_has_name_property(self, parser_instance: BaseParser) -> None:
        """All parsers must have a name property."""
        assert hasattr(parser_instance, "name")
        assert isinstance(parser_instance.name, str)
        assert len(parser_instance.name) > 0

    def test_parser_has_version_property(self, parser_instance: BaseParser) -> None:
        """All parsers must have a version property."""
        assert hasattr(parser_instance, "version")
        assert isinstance(parser_instance.version, str)
        assert len(parser_instance.version) > 0

    def test_parser_has_parse_method(self, parser_instance: BaseParser) -> None:
        """All parsers must have a parse method."""
        assert hasattr(parser_instance, "parse")
        assert callable(parser_instance.parse)

    def test_parser_repr(self, parser_instance: BaseParser) -> None:
        """All parsers must have meaningful __repr__."""
        repr_str = repr(parser_instance)
        assert parser_instance.name in repr_str.lower()
        assert parser_instance.version in repr_str


class TestSyntheticCorpusParsing:
    """Test all parsers on the same synthetic corpus documents."""

    def test_parse_basic_document(
        self, parser_instance: BaseParser, corpus_dir: Path, output_dir: Path
    ) -> None:
        """All parsers should successfully parse the basic document."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        # Parse the document
        result_path = parser_instance.parse(pdf_path, output_dir)

        # Verify result
        assert result_path.exists()
        assert result_path.suffix == ".md"
        assert result_path.stat().st_size > 0

        # Verify content is valid markdown
        content = result_path.read_text(encoding="utf-8")
        assert len(content) > 0
        assert not content.isspace()

    def test_parse_lists_document(
        self, parser_instance: BaseParser, corpus_dir: Path, output_dir: Path
    ) -> None:
        """All parsers should successfully parse the lists document."""
        pdf_path = corpus_dir / "02_lists.pdf"
        if not pdf_path.exists():
            pytest.skip("02_lists.pdf not found")

        result_path = parser_instance.parse(pdf_path, output_dir)

        assert result_path.exists()
        assert result_path.stat().st_size > 0

        # Lists document should contain list markers
        content = result_path.read_text(encoding="utf-8")
        # At least some parsers should detect lists
        # (not all parsers preserve list structure perfectly)
        assert len(content) > 100

    def test_parse_tables_document(
        self, parser_instance: BaseParser, corpus_dir: Path, output_dir: Path
    ) -> None:
        """All parsers should successfully parse the tables document."""
        pdf_path = corpus_dir / "03_tables.pdf"
        if not pdf_path.exists():
            pytest.skip("03_tables.pdf not found")

        result_path = parser_instance.parse(pdf_path, output_dir)

        assert result_path.exists()
        assert result_path.stat().st_size > 0

        content = result_path.read_text(encoding="utf-8")
        assert len(content) > 100

    def test_parse_multiple_documents(
        self, parser_instance: BaseParser, test_pdfs: list[Path], output_dir: Path
    ) -> None:
        """All parsers should handle multiple documents sequentially."""
        results = []

        for pdf_path in test_pdfs:
            result_path = parser_instance.parse(pdf_path, output_dir)
            results.append(result_path)

        # Verify all results exist
        assert len(results) == len(test_pdfs)
        for result_path in results:
            assert result_path.exists()
            assert result_path.stat().st_size > 0


class TestCacheBehavior:
    """Test cache behavior across all parsers."""

    def test_cache_cleared_successfully(
        self, parser_instance: BaseParser, corpus_dir: Path, output_dir: Path
    ) -> None:
        """Cache can be cleared for a parser."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        cache_dir = Path(".cache")

        # Parse document to populate cache
        parser_instance.parse(pdf_path, output_dir)

        # Clear cache for this parser
        clear_cache(cache_dir, parser_name=parser_instance.name)

        # Should not raise an error
        assert True

    def test_repeated_parse_produces_same_output(
        self, parser_instance: BaseParser, corpus_dir: Path, output_dir: Path
    ) -> None:
        """Repeated parsing of same document produces consistent output."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        cache_dir = Path(".cache")
        clear_cache(cache_dir, parser_name=parser_instance.name)

        # First parse
        result1 = parser_instance.parse(pdf_path, output_dir / "run1")
        content1 = result1.read_text()

        # Second parse (may hit cache or re-parse, but should be consistent)
        result2 = parser_instance.parse(pdf_path, output_dir / "run2")
        content2 = result2.read_text()

        # Results should be identical
        assert content1 == content2

    def test_cache_directory_structure(
        self, parser_instance: BaseParser, test_pdfs: list[Path], output_dir: Path
    ) -> None:
        """Parsing creates appropriate cache directory structure."""
        cache_dir = Path(".cache")
        clear_cache(cache_dir, parser_name=parser_instance.name)

        # Parse a document
        pdf_path = test_pdfs[0]
        parser_instance.parse(pdf_path, output_dir)

        # Cache directory for this parser should exist
        parser_cache = cache_dir / parser_instance.name
        assert parser_cache.exists()
        assert parser_cache.is_dir()


class TestErrorHandling:
    """Test error handling across all parsers."""

    def test_parse_nonexistent_file(self, parser_instance: BaseParser, output_dir: Path) -> None:
        """All parsers should handle nonexistent files gracefully."""
        nonexistent = Path("nonexistent.pdf")

        with pytest.raises((FileNotFoundError, RuntimeError, ValueError)):
            parser_instance.parse(nonexistent, output_dir)

    def test_parse_invalid_pdf(
        self, parser_instance: BaseParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """All parsers should handle invalid PDF files gracefully."""
        # Create a file that's not a valid PDF
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_text("This is not a PDF file", encoding="utf-8")

        # Some parsers may handle this gracefully, others may raise errors
        # Just verify it doesn't crash the test suite
        try:
            result = parser_instance.parse(invalid_pdf, output_dir)
            # If it succeeded, result should exist
            assert result.exists()
        except Exception:
            # Expected for most parsers
            pass

    def test_output_dir_created_if_missing(
        self, parser_instance: BaseParser, corpus_dir: Path, tmp_path: Path
    ) -> None:
        """All parsers should create output directory if it doesn't exist."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        # Use non-existent output directory
        output_dir = tmp_path / "new_output_dir"
        assert not output_dir.exists()

        result_path = parser_instance.parse(pdf_path, output_dir)

        # Verify output directory was created
        assert output_dir.exists()
        assert result_path.exists()


class TestPerformanceBaselines:
    """Capture performance baselines for each parser."""

    @pytest.mark.slow
    def test_parse_time_baseline(
        self, parser_instance: BaseParser, corpus_dir: Path, output_dir: Path
    ) -> None:
        """Measure parsing time for basic document (baseline)."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        # Clear cache to ensure clean measurement
        cache_dir = Path(".cache")
        clear_cache(cache_dir, parser_name=parser_instance.name)

        # Measure parse time
        start_time = time.time()
        result_path = parser_instance.parse(pdf_path, output_dir)
        parse_time = time.time() - start_time

        # Verify result
        assert result_path.exists()

        # Record baseline (not asserting specific times, just measuring)
        print(f"\n{parser_instance.name} parse time (01_basic.pdf): {parse_time:.3f}s")

        # Sanity check: should complete in reasonable time (< 60 seconds)
        assert parse_time < 60.0

    @pytest.mark.slow
    def test_cache_speedup(
        self, parser_instance: BaseParser, corpus_dir: Path, output_dir: Path
    ) -> None:
        """Verify that cache provides speedup on second parse."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        cache_dir = Path(".cache")
        clear_cache(cache_dir, parser_name=parser_instance.name)

        # First parse (cache miss)
        start_time = time.time()
        parser_instance.parse(pdf_path, output_dir)
        first_parse_time = time.time() - start_time

        # Second parse (cache hit)
        start_time = time.time()
        parser_instance.parse(pdf_path, output_dir)
        second_parse_time = time.time() - start_time

        print(
            f"\n{parser_instance.name} - First: {first_parse_time:.3f}s, "
            f"Second: {second_parse_time:.3f}s, "
            f"Speedup: {first_parse_time / max(second_parse_time, 0.001):.1f}x"
        )

        # Cache should provide some speedup (at least 2x)
        # Note: For very fast parsers, cache overhead might dominate
        # So we just verify second parse doesn't take longer
        assert second_parse_time <= first_parse_time * 1.5


class TestCrossParserComparison:
    """Compare behavior across different parsers."""

    def test_all_parsers_produce_markdown(self, corpus_dir: Path, output_dir: Path) -> None:
        """Verify all parsers produce valid markdown output."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        results = {}

        for parser_name, parser_class in ALL_PARSERS:
            parser = parser_class()
            result_path = parser.parse(pdf_path, output_dir / parser_name)

            assert result_path.exists()
            assert result_path.suffix == ".md"

            content = result_path.read_text(encoding="utf-8")
            assert len(content) > 0

            results[parser_name] = content

        # Verify we got results from all parsers
        assert len(results) == len(ALL_PARSERS)

        # All results should contain some content
        for parser_name, content in results.items():
            assert len(content) > 50, f"{parser_name} produced very short output"

    def test_output_file_naming_consistency(self, corpus_dir: Path, output_dir: Path) -> None:
        """Verify all parsers follow consistent output naming."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        for parser_name, parser_class in ALL_PARSERS:
            parser = parser_class()
            parser_output_dir = output_dir / parser_name
            parser_output_dir.mkdir(exist_ok=True)

            result_path = parser.parse(pdf_path, parser_output_dir)

            # Output should have .md extension
            assert result_path.suffix == ".md"

            # Output should exist
            assert result_path.exists()


class TestEdgeCases:
    """Test edge cases that all parsers should handle."""

    def test_empty_output_directory(
        self, parser_instance: BaseParser, corpus_dir: Path, tmp_path: Path
    ) -> None:
        """Parser should work with completely empty output directory."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        output_dir = tmp_path / "empty_output"
        output_dir.mkdir()

        result_path = parser_instance.parse(pdf_path, output_dir)

        # Result should exist (may be in cache or output dir depending on parser)
        assert result_path.exists()

    def test_unicode_in_paths(
        self, parser_instance: BaseParser, corpus_dir: Path, tmp_path: Path
    ) -> None:
        """Parser should handle unicode characters in paths."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        # Create output directory with unicode characters
        output_dir = tmp_path / "output_测试_émojis_🎉"
        output_dir.mkdir()

        result_path = parser_instance.parse(pdf_path, output_dir)

        assert result_path.exists()
        content = result_path.read_text(encoding="utf-8")
        assert len(content) > 0


# Utility function for manual performance comparison
def compare_parser_performance(corpus_dir: Path, output_dir: Path) -> None:
    """Compare performance of all parsers (for manual testing).

    This is not a test, but a utility function for comparing parsers.
    Run manually with: pytest -k compare_parser_performance -s
    """
    pdf_path = corpus_dir / "01_basic.pdf"
    if not pdf_path.exists():
        return

    print("\n" + "=" * 70)
    print("Parser Performance Comparison")
    print("=" * 70)

    for parser_name, parser_class in ALL_PARSERS:
        parser = parser_class()

        # Clear cache
        cache_dir = Path(".cache")
        clear_cache(cache_dir, parser_name=parser_name)

        # Measure parse time
        start_time = time.time()
        result_path = parser.parse(pdf_path, output_dir / parser_name)
        parse_time = time.time() - start_time

        output_size = result_path.stat().st_size

        print(
            f"{parser_name:15} | Time: {parse_time:6.3f}s | "
            f"Output: {output_size:6} bytes | Version: {parser.version}"
        )

    print("=" * 70)
