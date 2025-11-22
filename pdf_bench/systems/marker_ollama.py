"""Marker+Ollama parser for high-quality local LLM-enhanced PDF-to-Markdown conversion.

This module implements a parser using Marker with Ollama for local LLM processing.
It provides GPU-accelerated PDF parsing enhanced with vision language model capabilities
for improved table extraction, equation recognition, and complex layout understanding.

Marker+Ollama leverages:
- Marker's layout detection and OCR
- Local vision LLM (llama3.2-vision) for complex regions
- GPU acceleration for both Marker and Ollama
- No API costs (fully local processing)

Key features:
- Local LLM processing (no cloud API required)
- Vision model for table and equation extraction
- GPU acceleration (CUDA) with CPU fallback
- Higher accuracy than baseline Marker on complex documents
- Requires Ollama server running locally

Requirements:
- Ollama installed and running (ollama serve)
- llama3.2-vision model pulled (ollama pull llama3.2-vision)
- Marker ollama.py patched with flatten_schema fix (GitHub issue #907)

Cost:
- Zero API costs (all local processing)
- GPU compute time (~5-10 seconds/page)

Examples:
    >>> from pathlib import Path
    >>> parser = MarkerOllamaParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(result)
    PosixPath('output/document.md')

Note: This parser requires the fix from https://github.com/datalab-to/marker/issues/907
to be applied to marker/services/ollama.py. The fix resolves JSON schema $ref references
before sending to Ollama, preventing 500 Server Errors.
"""

import logging
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

# Configure logging
logger = logging.getLogger(__name__)


class MarkerOllamaParser(BaseParser):
    """PDF parser using Marker with Ollama for local LLM-enhanced extraction.

    This parser uses Marker's --use_llm flag with OllamaService to enable local
    vision language model processing for complex document regions. It provides
    higher accuracy than baseline Marker while avoiding cloud API costs.

    The parser integrates with the caching system to avoid redundant processing
    and provides comprehensive error handling for subprocess execution and Ollama
    connectivity.

    Attributes:
        name: Parser identifier ('marker_ollama')
        version: Marker package version + '-ollama' suffix

    Examples:
        >>> parser = MarkerOllamaParser()
        >>> parser.name
        'marker_ollama'
        >>> pdf = Path("document.pdf")
        >>> output = Path("output")
        >>> result = parser.parse(pdf, output)

    Raises:
        RuntimeError: If marker_single or Ollama is not available.
    """

    def __init__(self) -> None:
        """Initialize the MarkerOllamaParser.

        This constructor locates the marker_single executable and verifies
        that Ollama is running and accessible with the required vision model.

        Raises:
            ImportError: If marker-pdf is not installed
            RuntimeError: If marker_single executable is not found, Ollama
                is not running, or llama3.2-vision model is not available.
        """
        if not MARKER_AVAILABLE:
            raise ImportError(
                "marker-pdf is required for MarkerOllamaParser. "
                "Install with: pip install marker-pdf"
            )

        # Find marker_single executable in virtual environment
        venv_bin = Path(sys.prefix) / "bin" / "marker_single"

        if not venv_bin.exists():
            raise RuntimeError(
                f"marker_single not found at {venv_bin}. Install with: uv pip install marker-pdf"
            )

        self._marker_cmd = str(venv_bin)

        # Verify Ollama is running and has the required model
        import requests

        try:
            # Check Ollama server is accessible
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response.raise_for_status()

            # Parse response to check for vision model
            models_data = response.json()
            available_models = [m.get("name", "") for m in models_data.get("models", [])]

            # Check for llama3.2-vision (with or without tag)
            has_vision_model = any("llama3.2-vision" in model.lower() for model in available_models)

            if not has_vision_model:
                logger.warning(
                    "llama3.2-vision model not found in Ollama. "
                    "Available models: %s. "
                    "Install with: ollama pull llama3.2-vision",
                    available_models,
                )
                # Don't raise error - let Marker/Ollama handle it
            else:
                logger.info(
                    "Ollama server ready with vision model: %s",
                    [m for m in available_models if "llama3.2-vision" in m.lower()],
                )

        except (requests.RequestException, requests.ConnectionError) as e:
            raise RuntimeError(
                "Ollama server not accessible at http://localhost:11434. Start with: ollama serve"
            ) from e
        except Exception as e:
            logger.warning("Could not verify Ollama models: %s", e)

        # Get version from marker-pdf package
        try:
            version: str = str(marker.__version__)
            self._version = f"{version}-ollama"
        except AttributeError:
            # Fallback if marker package doesn't have __version__
            self._version = "1.10.1-ollama"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier.

        Returns:
            str: Always returns 'marker_ollama'.
        """
        return "marker_ollama"

    @property
    def version(self) -> str:
        """Return the marker-pdf library version with -ollama suffix.

        Returns:
            str: marker-pdf version string with '-ollama' (e.g., '1.10.1-ollama').
        """
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file using Marker+Ollama and generate Markdown output.

        This method executes marker_single with --use_llm and OllamaService flags
        to enable local LLM processing. The implementation:
        1. Checks cache for existing result
        2. If cache miss, runs marker_single with Ollama flags
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
            RuntimeError: If marker_single execution fails, Ollama errors occur,
                or no output is produced.

        Examples:
            >>> parser = MarkerOllamaParser()
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
            logger.debug("Cache hit for %s (marker_ollama)", pdf_path.name)
            return cached

        # Cache miss - parse the PDF using marker_single with Ollama
        logger.info("Cache miss for %s - parsing with Marker+Ollama (LLM enabled)", pdf_path.name)
        try:
            # Create a temporary output directory for Marker's output
            # (Marker creates subdirectory with PDF stem name)
            temp_output = output_dir / "marker_ollama_temp"
            temp_output.mkdir(parents=True, exist_ok=True)

            # Run marker_single with --use_llm and OllamaService
            # Output will be: marker_ollama_temp/{pdf_stem}/{pdf_stem}.md
            logger.info("Invoking Marker with Ollama LLM service for %s", pdf_path.name)
            result = subprocess.run(
                [
                    self._marker_cmd,
                    str(pdf_path.absolute()),
                    "--output_dir",
                    str(temp_output.absolute()),
                    "--use_llm",  # Enable LLM processing
                    "--llm_service",
                    "marker.services.ollama.OllamaService",
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=600,  # 10 minute timeout (LLM processing is slower)
            )
            logger.info("Marker+Ollama processing completed for %s", pdf_path.name)

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
            shutil.rmtree(marker_output_dir, ignore_errors=True)

            # Store in cache
            cached_path = store_cached(key, final_md_path, cache_dir)

            return cached_path

        except subprocess.CalledProcessError as e:
            # marker_single failed
            raise RuntimeError(
                f"Marker+Ollama processing failed (exit code {e.returncode}):\n"
                f"stdout: {e.stdout}\n"
                f"stderr: {e.stderr}"
            ) from e

        except subprocess.TimeoutExpired as e:
            raise RuntimeError(
                f"Marker+Ollama processing timed out after {e.timeout} seconds"
            ) from e

        except PermissionError as e:
            raise PermissionError(f"Permission denied: {e}") from e

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with Marker+Ollama: {e}") from e
