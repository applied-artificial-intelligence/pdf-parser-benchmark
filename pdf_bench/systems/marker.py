"""Marker-based parser for high-quality PDF-to-Markdown conversion.

This module implements a parser using Marker, a GPU-accelerated ML-based PDF parser
that excels at complex document layouts, tables, and mathematical equations.

Marker leverages deep learning models for:
- Layout detection and analysis
- OCR error detection and correction
- Table structure recognition
- Mathematical equation extraction
- Figure and image handling

Key features:
- GPU acceleration (CUDA) with CPU fallback
- High accuracy (99%+ text extraction)
- Fast processing (~1.5 seconds/page with GPU)
- Excellent structure preservation
- Minimal dependencies (subprocess-based)

Examples:
    >>> from pathlib import Path
    >>> parser = MarkerParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(result)
    PosixPath('output/document.md')
"""

import shutil
import subprocess
import sys
from pathlib import Path

try:
    import marker  # type: ignore[import-untyped]

    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class MarkerParser(BaseParser):
    """PDF parser using Marker for high-quality PDF-to-Markdown conversion.

    This parser uses the Marker CLI tool (marker_single) via subprocess to convert
    PDFs to Markdown. Marker is an ML-based parser that provides superior accuracy
    for complex documents including tables, equations, and multi-column layouts.

    The parser integrates with the caching system to avoid redundant processing
    and provides comprehensive error handling for subprocess execution.

    Attributes:
        name: Parser identifier ('marker')
        version: Marker package version string

    Examples:
        >>> parser = MarkerParser()
        >>> parser.name
        'marker'
        >>> pdf = Path("document.pdf")
        >>> output = Path("output")
        >>> result = parser.parse(pdf, output)
    """

    def __init__(self) -> None:
        """Initialize the MarkerParser.

        This constructor locates the marker_single executable in the virtual
        environment and verifies it's available.

        Raises:
            ImportError: If marker-pdf is not installed
            RuntimeError: If marker_single executable is not found in the venv.
        """
        if not MARKER_AVAILABLE:
            raise ImportError(
                "marker-pdf is required for MarkerParser. Install with: pip install marker-pdf"
            )

        # Find marker_single executable in virtual environment
        venv_bin = Path(sys.prefix) / "bin" / "marker_single"

        if not venv_bin.exists():
            raise RuntimeError(
                f"marker_single not found at {venv_bin}. Install with: uv pip install marker-pdf"
            )

        self._marker_cmd = str(venv_bin)

        # Get version from marker-pdf package
        try:
            version: str = str(marker.__version__)
            self._version = version
        except AttributeError:
            # Fallback if marker package doesn't have __version__
            self._version = "1.10.1"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier.

        Returns:
            str: Always returns 'marker'.
        """
        return "marker"

    @property
    def version(self) -> str:
        """Return the marker-pdf library version.

        Returns:
            str: marker-pdf version string (e.g., '1.10.1').
        """
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using Marker.

        This method executes the marker_single CLI tool to convert the PDF to Markdown.
        The implementation:
        1. Checks cache for existing result
        2. If cache miss, runs marker_single subprocess
        3. Extracts the generated markdown from Marker's output structure
        4. Copies result to the requested output directory
        5. Stores result in cache
        6. Returns path to generated file

        Note: Marker outputs to a subdirectory structure:
            {output_dir}/{pdf_stem}/{pdf_stem}.md

        Args:
            pdf_path: Path to the input PDF file. Must exist and be readable.
            output_dir: Directory where the output Markdown file should be saved.
                Must exist and be writable.

        Returns:
            Path: Path to the generated Markdown file.

        Raises:
            FileNotFoundError: If pdf_path does not exist.
            PermissionError: If pdf_path is not readable or output_dir is not writable.
            RuntimeError: If marker_single execution fails or produces no output.

        Examples:
            >>> parser = MarkerParser()
            >>> pdf = Path("document.pdf")
            >>> output = Path("output")
            >>> result = parser.parse(pdf, output)
            >>> result.exists()
            True
        """
        # Validate input
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not pdf_path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")

        # Generate cache key
        key = cache_key(pdf_path, self.name, self.version)

        # Check cache
        cache_dir = Path(".cache")
        cached = get_cached(key, cache_dir)
        if cached is not None:
            return cached

        # Cache miss - parse the PDF using marker_single
        try:
            # Create a temporary output directory for Marker's output
            # (Marker creates subdirectory with PDF stem name)
            temp_output = output_dir / "marker_temp"
            temp_output.mkdir(parents=True, exist_ok=True)

            # Run marker_single
            # Output will be: marker_temp/{pdf_stem}/{pdf_stem}.md
            result = subprocess.run(
                [
                    self._marker_cmd,
                    str(pdf_path.absolute()),
                    "--output_dir",
                    str(temp_output.absolute()),
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=300,  # 5 minute timeout
            )

            # Find the generated markdown file
            # Marker creates: {output_dir}/{pdf_stem}/{pdf_stem}.md
            pdf_stem = pdf_path.stem
            marker_output_dir = temp_output / pdf_stem
            marker_md_file = marker_output_dir / f"{pdf_stem}.md"

            if not marker_md_file.exists():
                raise RuntimeError(
                    f"Marker did not generate expected output file: {marker_md_file}\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )

            # Copy markdown to final output location
            output_dir.mkdir(parents=True, exist_ok=True)
            final_md_path = output_dir / f"{pdf_stem}.md"
            shutil.copy2(marker_md_file, final_md_path)

            # Clean up temporary Marker output directory
            shutil.rmtree(temp_output)

            # Store in cache
            cached_path = store_cached(key, final_md_path, cache_dir)

            return cached_path

        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"Marker processing timed out after 300 seconds: {e}") from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Marker execution failed with exit code {e.returncode}\n"
                f"stdout: {e.stdout}\n"
                f"stderr: {e.stderr}"
            ) from e
        except PermissionError as e:
            raise PermissionError(f"Permission denied: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with Marker: {e}") from e
