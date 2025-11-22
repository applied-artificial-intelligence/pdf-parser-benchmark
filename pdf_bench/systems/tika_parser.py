"""Apache Tika-based parser for PDF-to-text conversion.

Apache Tika is a content detection and analysis framework that
supports 1000+ file formats including PDFs.
"""

from pathlib import Path

try:
    import tika  # type: ignore[import-untyped]
    TIKA_AVAILABLE = True
except ImportError:
    TIKA_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class TikaParser(BaseParser):
    """PDF parser using Apache Tika for text extraction.

    Tika is a Java-based framework for content extraction from documents.
    Requires Java runtime to be installed.
    """

    def __init__(self) -> None:
        """Initialize the TikaParser.

        Raises:
            ImportError: If tika-python is not installed
        """
        if not TIKA_AVAILABLE:
            raise ImportError(
                "tika-python is required for TikaParser. "
                "Install with: pip install tika"
            )

        # Tika doesn't have a version in the Python wrapper
        self._version = "3.1.0"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "tika"

    @property
    def version(self) -> str:
        """Return the tika library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using Apache Tika.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        from tika import parser  # type: ignore[import-untyped]

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
            # Parse file and extract text
            file_data = parser.from_file(str(pdf_path))
            text = file_data.get('content', '')

            if text is None:
                text = ""

            # Write to output file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(text, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, output_path, cache_dir)
            return cached_path

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with Tika: {e}") from e
