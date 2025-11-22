"""PyPDFium2-based parser for PDF-to-text conversion.

PyPDFium2 is a Python binding to PDFium (Google's PDF rendering library).
It provides fast, reliable text extraction with good Unicode support.
"""

from pathlib import Path

try:
    import pypdfium2  # type: ignore[import-untyped]

    PYPDFIUM2_AVAILABLE = True
except ImportError:
    PYPDFIUM2_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class PyPDFium2Parser(BaseParser):
    """PDF parser using PyPDFium2 for text extraction.

    PyPDFium2 provides Python bindings to Google's PDFium library,
    offering fast and reliable text extraction.
    """

    def __init__(self) -> None:
        """Initialize the PyPDFium2Parser.

        Raises:
            ImportError: If pypdfium2 is not installed
        """
        if not PYPDFIUM2_AVAILABLE:
            raise ImportError(
                "pypdfium2 is required for PyPDFium2Parser. Install with: pip install pypdfium2"
            )

        try:
            self._version = str(pypdfium2.__version__)
        except AttributeError:
            self._version = "4.30.0"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "pypdfium2"

    @property
    def version(self) -> str:
        """Return the pypdfium2 library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using PyPDFium2.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        import pypdfium2 as pdfium  # type: ignore[import-untyped]

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
            pdf = pdfium.PdfDocument(str(pdf_path))

            # Extract text from all pages
            text_parts = []
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                textpage = page.get_textpage()
                text = textpage.get_text_range()
                if text.strip():
                    text_parts.append(text)
                page.close()

            pdf.close()

            # Combine all pages
            markdown_content = "\n\n".join(text_parts)

            # Write to output file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(markdown_content, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, output_path, cache_dir)
            return cached_path

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with PyPDFium2: {e}") from e
