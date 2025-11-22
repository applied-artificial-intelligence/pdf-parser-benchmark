"""Azure Document Intelligence parser for PDF-to-Markdown conversion with cost tracking.

This module implements a parser using Microsoft Azure Document Intelligence
(formerly Form Recognizer), a commercial ML-based document analysis service
that excels at OCR, layout analysis, and document understanding.

Azure Document Intelligence leverages deep learning models for:
- High-accuracy OCR and text extraction
- Layout and reading order detection
- Table structure recognition
- Handwriting and print recognition
- Multi-language document support

Key features:
- Cloud-based API (no local installation required)
- High accuracy (>99% on high-quality documents)
- Fast processing (typically <2 seconds/page)
- Built-in cost tracking ($1.50 per 1,000 pages for Read model)
- Prebuilt models for common document types

Cost Model:
    - Read Model (OCR): $1.50 per 1,000 pages (0-1M pages)
    - Read Model (OCR): $0.60 per 1,000 pages (>1M pages)
    This parser uses the Read model for cost-effective text extraction

API Limits:
    - Max file size: 500 MB
    - Max pages: 2,000 pages per document
    - Supported formats: PDF, JPEG, PNG, BMP, TIFF

Examples:
    >>> from pathlib import Path
    >>> parser = AzureDocumentIntelligenceParser(
    ...     endpoint="https://your-resource.cognitiveservices.azure.com/",
    ...     api_key="your-api-key"
    ... )
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")
    >>> print(result)
    PosixPath('output/document.md')

Environment Variables:
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: Azure endpoint URL (required)
    AZURE_DOCUMENT_INTELLIGENCE_KEY: Azure API key (required)
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import AnalyzeResult
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import (
        HttpResponseError,
        ResourceNotFoundError,
        ServiceRequestError,
    )
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    HttpResponseError = Exception  # type: ignore[misc]
    ResourceNotFoundError = Exception  # type: ignore[misc]
    ServiceRequestError = Exception  # type: ignore[misc]

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class AzureDocumentIntelligenceParser(BaseParser):
    """PDF parser using Azure Document Intelligence for commercial-grade text extraction.

    This parser uses Azure's Document Intelligence Read model to extract text
    from PDFs. It provides high accuracy, layout preservation, and includes
    cost tracking for benchmarking commercial parsers.

    The parser integrates with the caching system to avoid redundant API calls
    and provides comprehensive error handling for API failures, rate limits,
    and network issues.

    Attributes:
        name: Parser identifier ('azure_document_intelligence')
        version: azure-ai-documentintelligence package version
        last_parsing_cost: Cost of most recent parse() call in USD

    Examples:
        >>> parser = AzureDocumentIntelligenceParser(
        ...     endpoint="https://your-resource.cognitiveservices.azure.com/",
        ...     api_key="your-api-key"
        ... )
        >>> parser.name
        'azure_document_intelligence'
        >>> pdf = Path("document.pdf")
        >>> output = Path("output")
        >>> result = parser.parse(pdf, output)
        >>> print(f"Cost: ${parser.last_parsing_cost:.4f}")
    """

    # Pricing: $1.50 per 1,000 pages for Read model (0-1M pages)
    COST_PER_PAGE = 0.0015

    def __init__(
        self,
        endpoint: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the Azure Document Intelligence parser.

        Credentials are loaded from constructor arguments or environment variables.

        Args:
            endpoint: Azure Document Intelligence endpoint URL
                (defaults to AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT env var)
            api_key: Azure API key
                (defaults to AZURE_DOCUMENT_INTELLIGENCE_KEY env var)

        Raises:
            ImportError: If azure-ai-formrecognizer is not installed
            RuntimeError: If Azure credentials are not configured.
        """
        if not AZURE_AVAILABLE:
            raise ImportError(
                "azure-ai-formrecognizer is required for Azure Document Intelligence parser. "
                "Install with: pip install azure-ai-formrecognizer"
            )

        # Get credentials from args or environment
        self._endpoint = endpoint or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        self._api_key = api_key or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

        # Validate credentials
        if not self._endpoint or not self._api_key:
            raise RuntimeError(
                "Azure Document Intelligence credentials not found. "
                "Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and "
                "AZURE_DOCUMENT_INTELLIGENCE_KEY environment variables or pass them "
                "to the constructor."
            )

        # Initialize Azure client
        try:
            self._client = DocumentIntelligenceClient(
                endpoint=self._endpoint,
                credential=AzureKeyCredential(self._api_key),
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Azure Document Intelligence client: {e}"
            ) from e

        # Cost tracking
        self._total_cost = 0.0
        self._total_pages = 0
        self.last_parsing_cost = 0.0

        # Get package version
        try:
            from azure.ai.documentintelligence import __version__

            self._version: str = __version__
        except (ImportError, AttributeError):
            # Fallback if package doesn't have __version__
            self._version = "1.0.0"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier.

        Returns:
            str: Always returns 'azure_document_intelligence'.
        """
        return "azure_document_intelligence"

    @property
    def version(self) -> str:
        """Return the azure-ai-documentintelligence package version.

        Returns:
            str: Package version string (e.g., '1.0.0').
        """
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file using Azure Document Intelligence and generate Markdown.

        This method sends the PDF to Azure's Document Intelligence Read model
        and converts the response to Markdown format. The implementation:
        1. Checks cache for existing result
        2. If cache miss, reads PDF file
        3. Calls Azure Document Intelligence API
        4. Converts Azure response to Markdown
        5. Writes Markdown file
        6. Stores result in cache
        7. Updates cost tracking
        8. Returns path to generated file

        Args:
            pdf_path: Path to the input PDF file. Must exist and be readable.
            output_dir: Directory where the output Markdown file should be saved.
                Must exist and be writable.

        Returns:
            Path: Path to the generated Markdown file.

        Raises:
            FileNotFoundError: If pdf_path does not exist.
            PermissionError: If pdf_path is not readable or output_dir is not writable.
            RuntimeError: If Azure API call fails or produces no output.
            ValueError: If PDF exceeds size or page limits.

        Examples:
            >>> parser = AzureDocumentIntelligenceParser()
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

        # Check file size (500 MB limit)
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 500:
            raise ValueError(
                f"PDF file too large ({file_size_mb:.2f} MB). "
                "Azure Document Intelligence has a 500 MB limit."
            )

        # Generate cache key
        key = cache_key(pdf_path, self.name, self.version)

        # Check cache
        cache_dir = Path(".cache")
        cached = get_cached(key, cache_dir)
        if cached is not None:
            # Note: Cached results don't incur costs
            self.last_parsing_cost = 0.0
            return cached

        # Cache miss - parse the PDF using Azure Document Intelligence
        try:
            # Read PDF file
            pdf_bytes = pdf_path.read_bytes()

            # Call Azure Document Intelligence API
            # New SDK version uses 'body' parameter instead of 'analyze_request'
            poller = self._client.begin_analyze_document(
                model_id="prebuilt-read",
                body=pdf_bytes,
                content_type="application/pdf"
            )

            # Wait for result
            result: AnalyzeResult = poller.result()

            # Extract text from result
            markdown_text = self._extract_text(result)

            # Calculate cost
            page_count = len(result.pages) if result.pages else 1
            self.last_parsing_cost = page_count * self.COST_PER_PAGE
            self._total_cost += self.last_parsing_cost
            self._total_pages += page_count

            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write markdown file
            markdown_path = output_dir / f"{pdf_path.stem}.md"
            markdown_path.write_text(markdown_text, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, markdown_path, cache_dir)

            return cached_path

        except HttpResponseError as e:
            # Azure API errors
            status_code = e.status_code if hasattr(e, "status_code") else "Unknown"
            error_msg = str(e)

            if status_code == 429:
                raise RuntimeError(
                    f"Azure Document Intelligence rate limit exceeded: {error_msg}"
                ) from e
            elif status_code == 400:
                raise ValueError(f"Invalid PDF file: {error_msg}") from e
            else:
                raise RuntimeError(
                    f"Azure Document Intelligence API error ({status_code}): {error_msg}"
                ) from e

        except ResourceNotFoundError as e:
            raise RuntimeError(
                f"Azure Document Intelligence resource not found: {e}"
            ) from e

        except ServiceRequestError as e:
            raise RuntimeError(f"Azure service request error: {e}") from e

        except PermissionError as e:
            raise PermissionError(f"Permission denied: {e}") from e

        except Exception as e:
            raise RuntimeError(
                f"Failed to parse PDF with Azure Document Intelligence: {e}"
            ) from e

    def _extract_text(self, result: AnalyzeResult) -> str:
        """Extract text from Azure Document Intelligence AnalyzeResult.

        This method converts the Azure API response to Markdown format by
        extracting text lines from each page.

        Args:
            result: AnalyzeResult from Azure Document Intelligence API.

        Returns:
            str: Extracted text in Markdown format.
        """
        text_blocks = []

        if result.pages:
            for page in result.pages:
                if page.lines:
                    for line in page.lines:
                        text_blocks.append(line.content)

        # Convert to markdown (join lines with paragraph breaks)
        markdown = "\n\n".join(text_blocks)

        return markdown.strip()

    def get_total_cost(self) -> float:
        """Get total cost of all parsing operations in this session.

        Returns:
            float: Total cost in USD.

        Examples:
            >>> parser = AzureDocumentIntelligenceParser()
            >>> parser.parse(Path("doc1.pdf"), Path("output"))
            >>> parser.parse(Path("doc2.pdf"), Path("output"))
            >>> print(f"Total cost: ${parser.get_total_cost():.4f}")
        """
        return self._total_cost

    def get_total_pages(self) -> int:
        """Get total number of pages processed in this session.

        Returns:
            int: Total page count.

        Examples:
            >>> parser = AzureDocumentIntelligenceParser()
            >>> parser.parse(Path("doc1.pdf"), Path("output"))
            >>> print(f"Pages processed: {parser.get_total_pages()}")
        """
        return self._total_pages
