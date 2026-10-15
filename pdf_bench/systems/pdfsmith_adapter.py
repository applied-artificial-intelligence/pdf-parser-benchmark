"""Adapter to use pdfsmith backends as pdf-bench parsers.

This module provides a bridge between pdfsmith's backend API (which returns
markdown strings) and pdf-bench's parser API (which writes files and returns paths).

The adapter handles:
- String to file conversion
- Version tracking via pdfsmith version
- Cost tracking forwarding for backends that support it
- Explicit uncached execution for benchmark measurements
- Image input support for backends that support it
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import pdfsmith
    from pdfsmith import IMAGE_CAPABLE_BACKENDS as PDFSMITH_IMAGE_BACKENDS
    from pdfsmith import get_backend

    PDFSMITH_AVAILABLE = True
except ImportError:
    PDFSMITH_AVAILABLE = False
    pdfsmith = None
    get_backend = None
    PDFSMITH_IMAGE_BACKENDS = set()

from pdf_bench.systems.base_parser import BaseParser

# Image extensions supported by image-capable backends
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".webp", ".bmp"}


class PdfsmithAdapter(BaseParser):
    """Adapter that wraps a pdfsmith backend as a pdf-bench parser.

    This allows pdf-bench to use any pdfsmith backend through a unified interface,
    handling the API differences between the two libraries.

    Examples:
        >>> adapter = PdfsmithAdapter("docling")
        >>> result = adapter.parse(Path("document.pdf"), Path("output"))
        >>> print(adapter.name)  # "pdfsmith-docling"

        >>> # With model selection for LLM backends
        >>> adapter = PdfsmithAdapter("anthropic", model="claude-3-5-haiku")
    """

    def __init__(self, backend_name: str, *, cache_mode: str = "bypass", **kwargs: Any) -> None:
        """Initialize pdfsmith adapter.

        Args:
            backend_name: Name of the pdfsmith backend (e.g., "docling", "marker")
            cache_mode: Only bypass is supported until full cache identity is verified.
            **kwargs: Additional options passed to the backend constructor

        Raises:
            ImportError: If pdfsmith is not installed
        """
        if not PDFSMITH_AVAILABLE:
            raise ImportError(
                "pdfsmith is required for PdfsmithAdapter. Install with: pip install pdfsmith"
            )

        if cache_mode != "bypass":
            raise ValueError("Adapter cache reuse is disabled until full identity is verified")
        self.cache_mode = cache_mode
        self._backend_name = backend_name
        self._kwargs = kwargs
        self._backend = None  # Lazy initialization
        self._pdfsmith_version = getattr(pdfsmith, "__version__", "0.1.0")
        # Build a unique name incorporating model kwarg (e.g., "pdfsmith-anthropic-claude-opus-4-6")
        model = kwargs.get("model")
        if model:
            self._name = f"pdfsmith-{backend_name}-{model}"
        else:
            self._name = f"pdfsmith-{backend_name}"

    def _get_backend(self) -> Any:
        """Get or create backend instance (lazy loading)."""
        if self._backend is None:
            # Get backend class from registry
            from pdfsmith.backends.registry import BACKEND_REGISTRY

            if self._backend_name not in BACKEND_REGISTRY:
                raise ValueError(
                    f"Unknown pdfsmith backend: {self._backend_name}. "
                    f"Available: {list(BACKEND_REGISTRY.keys())}"
                )

            backend_info = BACKEND_REGISTRY[self._backend_name]
            backend_class = backend_info.loader()

            # Instantiate with kwargs (for model selection etc.)
            self._backend = backend_class(**self._kwargs)

        return self._backend

    @property
    def name(self) -> str:
        """Return parser name with pdfsmith prefix and model variant."""
        return self._name

    @property
    def version(self) -> str:
        """Return pdfsmith version."""
        return self._pdfsmith_version

    @property
    def supports_images(self) -> bool:
        """Check if this backend supports image inputs."""
        return self._backend_name in PDFSMITH_IMAGE_BACKENDS

    def parse(self, input_path: Path, output_dir: Path) -> Path:
        """Parse a PDF or image file using pdfsmith backend.

        Args:
            input_path: Path to input file (PDF or image)
            output_dir: Directory for output markdown file

        Returns:
            Path to generated markdown file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If image input provided but backend doesn't support it
            RuntimeError: If parsing fails
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Check if this is an image file
        is_image = input_path.suffix.lower() in IMAGE_EXTENSIONS

        # Validate image support
        if is_image and not self.supports_images:
            raise ValueError(
                f"Backend '{self._backend_name}' does not support image inputs. "
                f"Image-capable backends: {sorted(PDFSMITH_IMAGE_BACKENDS)}"
            )

        # Get backend and parse
        backend = self._get_backend()
        try:
            markdown = backend.parse(input_path)
        except Exception as e:
            raise RuntimeError(f"pdfsmith {self._backend_name} failed: {e}") from e

        # Write to output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{input_path.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")

        return output_path

    def get_cost_info(self) -> dict[str, Any] | None:
        """Get cost information if backend supports it.

        Returns:
            Dictionary with cost information, or None if not supported
        """
        backend = self._get_backend()
        if hasattr(backend, "get_cost_info"):
            cost_info: dict[str, Any] = backend.get_cost_info()
            return cost_info
        return None

    def __repr__(self) -> str:
        """Return string representation."""
        return f"PdfsmithAdapter({self._backend_name})"
