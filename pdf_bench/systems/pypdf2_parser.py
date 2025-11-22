"""PyPDF2-based parser for PDF-to-text conversion.

PyPDF2 is a pure-python PDF library for text extraction and manipulation.
Note: This is the legacy version; pypdf is the modern fork.
"""

from pathlib import Path

try:
    import PyPDF2  # type: ignore[import-untyped]

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class PyPDF2Parser(BaseParser):
    """PDF parser using PyPDF2 for text extraction.

    PyPDF2 is the legacy version of pypdf, maintained for compatibility.
    """

    def __init__(self) -> None:
        """Initialize the PyPDF2Parser.

        Raises:
            ImportError: If PyPDF2 is not installed
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError(
                "PyPDF2 is required for PyPDF2Parser. Install with: pip install PyPDF2"
            )

        try:
            self._version = str(PyPDF2.__version__)
        except AttributeError:
            self._version = "3.0.1"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "pypdf2"

    @property
    def version(self) -> str:
        """Return the PyPDF2 library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using PyPDF2.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        from PyPDF2 import PdfReader  # type: ignore[import-untyped]

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
            raise RuntimeError(f"Failed to parse PDF with PyPDF2: {e}") from e
