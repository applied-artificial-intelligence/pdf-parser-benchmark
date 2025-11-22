"""PyPDF-based parser for PDF-to-text conversion.

PyPDF is a pure-python PDF library capable of text extraction,
merging, splitting, and basic PDF manipulation.
"""

from pathlib import Path

try:
    import pypdf  # type: ignore[import-untyped]

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class PyPDFParser(BaseParser):
    """PDF parser using PyPDF for text extraction.

    PyPDF (formerly PyPDF2) is a pure-python library for PDF operations
    including text extraction.
    """

    def __init__(self) -> None:
        """Initialize the PyPDFParser.

        Raises:
            ImportError: If pypdf is not installed
        """
        if not PYPDF_AVAILABLE:
            raise ImportError("pypdf is required for PyPDFParser. Install with: pip install pypdf")

        try:
            self._version = str(pypdf.__version__)
        except AttributeError:
            self._version = "5.1.0"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "pypdf"

    @property
    def version(self) -> str:
        """Return the pypdf library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using PyPDF.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        from pypdf import PdfReader  # type: ignore[import-untyped]

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
            reader = PdfReader(str(pdf_path))

            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)

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
            raise RuntimeError(f"Failed to parse PDF with PyPDF: {e}") from e
