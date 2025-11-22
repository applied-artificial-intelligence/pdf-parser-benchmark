"""PyMuPDF4LLM-based parser for LLM-optimized PDF-to-Markdown conversion.

PyMuPDF4LLM is an extension of PyMuPDF specifically designed to produce
Markdown output optimized for LLM consumption, with better structure preservation.
"""

from pathlib import Path

try:
    import pymupdf4llm  # type: ignore[import-untyped]  # noqa: F401

    PYMUPDF4LLM_AVAILABLE = True
except ImportError:
    PYMUPDF4LLM_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class PyMuPDF4LLMParser(BaseParser):
    """PDF parser using PyMuPDF4LLM for LLM-optimized Markdown extraction.

    This parser uses pymupdf4llm which provides enhanced Markdown output
    with better structure preservation compared to basic PyMuPDF.
    """

    def __init__(self) -> None:
        """Initialize the PyMuPDF4LLMParser.

        Raises:
            ImportError: If pymupdf4llm is not installed
        """
        if not PYMUPDF4LLM_AVAILABLE:
            raise ImportError(
                "pymupdf4llm is required for PyMuPDF4LLMParser. "
                "Install with: pip install pymupdf4llm"
            )

        try:
            # pymupdf4llm doesn't have __version__, use pymupdf version
            import pymupdf

            self._version = str(pymupdf.VersionBind)
        except (ImportError, AttributeError):
            self._version = "0.2.2"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "pymupdf4llm"

    @property
    def version(self) -> str:
        """Return the pymupdf4llm library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using PyMuPDF4LLM.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        import pymupdf4llm  # type: ignore[import-untyped]

        # Validate input
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Generate cache key
        key = cache_key(pdf_path, self.name, self.version)

        # Check cache
        cache_dir = Path(".cache")
        cached = get_cached(key, cache_dir)
        if cached is not None:
            return cached

        # Parse the PDF
        try:
            # PyMuPDF4LLM to_markdown returns markdown string
            markdown_content = pymupdf4llm.to_markdown(str(pdf_path))

            # Write to output file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(markdown_content, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, output_path, cache_dir)
            return cached_path

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with PyMuPDF4LLM: {e}") from e
