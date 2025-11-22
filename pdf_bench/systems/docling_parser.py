"""Docling-based parser for PDF-to-Markdown conversion.

Docling is a modern document intelligence library from IBM that
converts PDFs to markdown with excellent structure preservation.
"""

from pathlib import Path

try:
    import docling  # type: ignore[import-untyped]
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class DoclingParser(BaseParser):
    """PDF parser using Docling for Markdown extraction.

    Docling provides high-quality PDF to markdown conversion with
    OCR support and structure preservation.
    """

    def __init__(self) -> None:
        """Initialize the DoclingParser.

        Raises:
            ImportError: If docling is not installed
        """
        if not DOCLING_AVAILABLE:
            raise ImportError(
                "docling is required for DoclingParser. "
                "Install with: pip install docling"
            )

        try:
            self._version = str(docling.__version__)
        except AttributeError:
            self._version = "2.62.0"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "docling"

    @property
    def version(self) -> str:
        """Return the docling library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using Docling.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        from docling.document_converter import DocumentConverter  # type: ignore[import-untyped]

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
            converter = DocumentConverter()
            result = converter.convert(str(pdf_path))
            markdown_text = result.document.export_to_markdown()

            # Write to output file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(markdown_text, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, output_path, cache_dir)
            return cached_path

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with Docling: {e}") from e
