"""Docling-based parser for PDF-to-Markdown conversion.

Docling is a modern document intelligence library from IBM that
converts PDFs to markdown with excellent structure preservation.

Resource Requirements:
    - Fast mode (no OCR): ~2-4GB RAM, ~2-5 sec/doc
    - Accurate mode (with OCR): ~8-12GB RAM, ~30-60 sec/doc
    - GPU recommended for OCR mode (CUDA or MPS)

Configuration (in order of precedence):
    1. Constructor arguments: DoclingParser(do_ocr=True)
    2. Environment variables: DOCLING_OCR=true
    3. Config file: .pdfbench/docling.yaml or ~/.config/pdfbench/docling.yaml
    4. Built-in defaults

See config/parsers/docling.yaml for all available options.
"""

from pathlib import Path
from typing import Any

try:
    import docling  # noqa: F401

    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached
from pdf_bench.utils.parser_config import get_parser_defaults, load_parser_config

# Known configuration options for environment variable lookup
KNOWN_OPTIONS = [
    "do_ocr",
    "do_table_structure",
    "num_threads",
    "device",
    "ocr_languages",
    "table_mode",
    "generate_page_images",
    "generate_picture_images",
    "images_scale",
]


class DoclingParser(BaseParser):
    """PDF parser using Docling for Markdown extraction.

    Docling provides high-quality PDF to markdown conversion with
    optional OCR support and table structure extraction.

    Configuration sources (in precedence order):
        1. Constructor arguments
        2. Environment variables (DOCLING_<OPTION>)
        3. Config files (.pdfbench/docling.yaml, ~/.config/pdfbench/docling.yaml)
        4. Built-in defaults

    By default, OCR is DISABLED for performance. Enable via:
        - Constructor: DoclingParser(do_ocr=True)
        - Environment: DOCLING_OCR=true
        - Config file: do_ocr: true

    Resource estimates:
        - Fast mode (no OCR): 2-4GB RAM, 2-5 sec/doc
        - Accurate mode (OCR): 8-12GB RAM, 30-60 sec/doc, GPU recommended
    """

    def __init__(
        self,
        do_ocr: bool | None = None,
        do_table_structure: bool | None = None,
        num_threads: int | None = None,
        device: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the DoclingParser.

        Args:
            do_ocr: Enable OCR for scanned documents. Default: False
            do_table_structure: Enable table structure extraction. Default: True
            num_threads: Number of CPU threads. Default: 4
            device: Device selection ("auto", "cpu", "cuda", "mps"). Default: "auto"
            **kwargs: Additional options (see config/parsers/docling.yaml)

        Raises:
            ImportError: If docling is not installed
        """
        if not DOCLING_AVAILABLE:
            raise ImportError(
                "docling is required for DoclingParser. Install with: pip install docling"
            )

        # Try to get version from importlib.metadata
        try:
            from importlib.metadata import version

            self._version = version("docling")
        except Exception:
            self._version = "unknown"

        # Build explicit options from constructor args
        explicit_options = {k: v for k, v in kwargs.items() if v is not None}
        if do_ocr is not None:
            explicit_options["do_ocr"] = do_ocr
        if do_table_structure is not None:
            explicit_options["do_table_structure"] = do_table_structure
        if num_threads is not None:
            explicit_options["num_threads"] = num_threads
        if device is not None:
            explicit_options["device"] = device

        # Load configuration from all sources
        defaults = get_parser_defaults("docling")
        config = load_parser_config("docling", explicit_options, KNOWN_OPTIONS)

        # Apply defaults, then loaded config
        self._config = {**defaults, **config.options}
        self._config_source = config.source

        # Extract commonly used options
        self._do_ocr = self._config.get("do_ocr", False)
        self._do_table_structure = self._config.get("do_table_structure", True)
        self._num_threads = self._config.get("num_threads", 4)
        self._device = self._config.get("device", "auto")

        # Lazy-loaded converter (created on first use)
        self._converter: Any = None

    def _get_converter(self) -> Any:
        """Get or create the document converter with configured options."""
        if self._converter is not None:
            return self._converter

        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            PdfPipelineOptions,
        )
        from docling.document_converter import (
            DocumentConverter,
            PdfFormatOption,
        )

        # Configure pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = self._do_ocr
        pipeline_options.do_table_structure = self._do_table_structure

        # Configure additional options from config
        if self._config.get("generate_page_images"):
            pipeline_options.generate_page_images = True
        if self._config.get("generate_picture_images"):
            pipeline_options.generate_picture_images = True
        if self._config.get("images_scale"):
            pipeline_options.images_scale = float(self._config["images_scale"])

        # Configure accelerator options
        try:
            from docling.datamodel.accelerator_options import (
                AcceleratorDevice,
                AcceleratorOptions,
            )

            # Map device string to AcceleratorDevice enum
            device_map = {
                "auto": AcceleratorDevice.AUTO,
                "cpu": AcceleratorDevice.CPU,
                "cuda": AcceleratorDevice.CUDA,
                "mps": AcceleratorDevice.MPS,
            }
            device = device_map.get(self._device.lower(), AcceleratorDevice.AUTO)

            pipeline_options.accelerator_options = AcceleratorOptions(
                num_threads=self._num_threads,
                device=device,
            )
        except ImportError:
            pass  # Older docling version without accelerator options

        # Create converter with configured options
        self._converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

        return self._converter

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        # Include mode in name for differentiation in benchmarks
        mode = "ocr" if self._do_ocr else "fast"
        return f"docling-{mode}"

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
        # Validate input
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Generate cache key (includes mode in name)
        key = cache_key(pdf_path, self.name, self.version)

        # Check cache
        cache_dir = Path(".cache")
        cached = get_cached(key, cache_dir)
        if cached is not None:
            return cached

        # Parse the PDF
        try:
            converter = self._get_converter()
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


# Convenience factory functions for benchmark configurations
def create_docling_fast() -> DoclingParser:
    """Create Docling parser optimized for speed (no OCR)."""
    return DoclingParser(do_ocr=False, do_table_structure=True, num_threads=4)


def create_docling_accurate() -> DoclingParser:
    """Create Docling parser optimized for accuracy (with OCR)."""
    return DoclingParser(do_ocr=True, do_table_structure=True, num_threads=4)
