"""Integration tests for parser adapters.

This module tests parser implementations to ensure they work with the
benchmarking infrastructure. Tests use PdfsmithAdapter for pdfsmith backends
and native parsers for tika, marker_ollama, landing_ai.
"""

import time
from pathlib import Path
from typing import Any

import pytest

from pdf_bench.systems import BaseParser
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter
from pdf_bench.utils.caching import clear_cache

# Parsers to test - using pdfsmith backends
# We test a subset for speed; full coverage is in the benchmark itself
PDFSMITH_PARSERS: list[tuple[str, str]] = [
    ("pypdf", "pypdf"),
    ("pymupdf", "pymupdf"),
]


@pytest.fixture(params=PDFSMITH_PARSERS, ids=[p[0] for p in PDFSMITH_PARSERS])
def parser_instance(request: Any) -> BaseParser:
    """Create parser instances for each parser type."""
    _parser_name, backend = request.param
    return PdfsmithAdapter(backend)


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
    for parser_name, _ in PDFSMITH_PARSERS:
        clear_cache(cache_dir, parser_name=f"pdfsmith-{parser_name}")


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
        assert "pdfsmith" in repr_str.lower()


class TestSyntheticCorpusParsing:
    """Test parsers on synthetic corpus documents."""

    def test_parse_basic_document(
        self, parser_instance: BaseParser, corpus_dir: Path, output_dir: Path
    ) -> None:
        """All parsers should successfully parse the basic document."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        result_path = parser_instance.parse(pdf_path, output_dir)

        assert result_path.exists()
        assert result_path.suffix == ".md"
        assert result_path.stat().st_size > 0

        content = result_path.read_text(encoding="utf-8")
        assert len(content) > 0
        assert not content.isspace()

    def test_parse_multiple_documents(
        self, parser_instance: BaseParser, test_pdfs: list[Path], output_dir: Path
    ) -> None:
        """All parsers should handle multiple documents sequentially."""
        results = []

        for pdf_path in test_pdfs:
            result_path = parser_instance.parse(pdf_path, output_dir)
            results.append(result_path)

        assert len(results) == len(test_pdfs)
        for result_path in results:
            assert result_path.exists()
            assert result_path.stat().st_size > 0


class TestErrorHandling:
    """Test error handling across all parsers."""

    def test_parse_nonexistent_file(self, parser_instance: BaseParser, output_dir: Path) -> None:
        """All parsers should handle nonexistent files gracefully."""
        nonexistent = Path("nonexistent.pdf")

        with pytest.raises((FileNotFoundError, RuntimeError, ValueError)):
            parser_instance.parse(nonexistent, output_dir)

    def test_parse_returns_valid_path(
        self, parser_instance: BaseParser, corpus_dir: Path, tmp_path: Path
    ) -> None:
        """All parsers should return a valid result path."""
        pdf_path = corpus_dir / "01_basic.pdf"
        if not pdf_path.exists():
            pytest.skip("01_basic.pdf not found")

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result_path = parser_instance.parse(pdf_path, output_dir)

        # Result should exist (in cache or output)
        assert result_path.exists()
        assert result_path.suffix == ".md"


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

        cache_dir = Path(".cache")
        clear_cache(cache_dir, parser_name=parser_instance.name)

        start_time = time.time()
        result_path = parser_instance.parse(pdf_path, output_dir)
        parse_time = time.time() - start_time

        assert result_path.exists()
        print(f"\n{parser_instance.name} parse time (01_basic.pdf): {parse_time:.3f}s")
        assert parse_time < 60.0
