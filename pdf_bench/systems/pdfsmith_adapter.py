"""Adapter to use pdfsmith backends as pdf-bench parsers.

This module provides a bridge between pdfsmith's backend API (which returns
markdown strings) and pdf-bench's parser API (which writes files and returns paths).

The adapter handles:
- String to file conversion
- Version tracking via pdfsmith version
- Cost tracking forwarding for backends that support it
- Caching integration with pdf-bench's caching system
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import pdfsmith
    from pdfsmith import get_backend

    PDFSMITH_AVAILABLE = True
except ImportError:
    PDFSMITH_AVAILABLE = False
    pdfsmith = None
    get_backend = None

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


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

    def __init__(self, backend_name: str, **kwargs: Any):
        """Initialize pdfsmith adapter.

        Args:
            backend_name: Name of the pdfsmith backend (e.g., "docling", "marker")
            **kwargs: Additional options passed to the backend constructor

        Raises:
            ImportError: If pdfsmith is not installed
        """
        if not PDFSMITH_AVAILABLE:
            raise ImportError(
                "pdfsmith is required for PdfsmithAdapter. "
                "Install with: pip install pdfsmith"
            )

        self._backend_name = backend_name
        self._kwargs = kwargs
        self._backend = None  # Lazy initialization
        self._pdfsmith_version = getattr(pdfsmith, "__version__", "0.1.0")

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
        """Return parser name with pdfsmith prefix."""
        return f"pdfsmith-{self._backend_name}"

    @property
    def version(self) -> str:
        """Return pdfsmith version."""
        return self._pdfsmith_version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file using pdfsmith backend.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output markdown file

        Returns:
            Path to generated markdown file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            RuntimeError: If parsing fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Check cache first
        cache_dir = Path(".cache")
        key = cache_key(pdf_path, self.name, self.version)
        cached = get_cached(key, cache_dir)
        if cached is not None:
            return cached

        # Get backend and parse
        backend = self._get_backend()
        try:
            markdown = backend.parse(pdf_path)
        except Exception as e:
            raise RuntimeError(f"pdfsmith {self._backend_name} failed: {e}") from e

        # Write to output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{pdf_path.stem}.md"
        output_path.write_text(markdown, encoding="utf-8")

        # Store in cache and return
        return store_cached(key, output_path, cache_dir)

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
