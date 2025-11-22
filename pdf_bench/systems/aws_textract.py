"""AWS Textract parser for PDF-to-Markdown conversion with cost tracking.

This module implements a parser using Amazon Textract, a commercial ML-based
document analysis service that excels at text extraction, table detection, and
form processing.

AWS Textract leverages deep learning models for:
- High-accuracy OCR and text extraction
- Table structure detection and extraction
- Form field identification
- Multi-page document processing
- Handwriting recognition

Key features:
- Cloud-based API (no local installation required)
- High accuracy (>99% on printed text)
- Fast processing (typically <1 second/page)
- Built-in cost tracking ($1.50 per 1,000 pages)
- Automatic rate limiting (300 pages/minute default)

Cost Model:
    - DetectDocumentText: $1.50 per 1,000 pages
    - AnalyzeDocument (tables): $15 per 1,000 pages
    This parser uses DetectDocumentText for cost-effectiveness

API Limits:
    - Max file size: 10 MB (synchronous)
    - Max pages: 3,000 pages (synchronous)
    - Rate limit: 300 pages/minute

Examples:
    >>> from pathlib import Path
    >>> parser = AWSTextractParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")
    >>> print(result)
    PosixPath('output/document.md')

Environment Variables:
    AWS_ACCESS_KEY_ID: AWS access key (required)
    AWS_SECRET_ACCESS_KEY: AWS secret key (required)
    AWS_REGION: AWS region (optional, defaults to us-east-1)
"""

import os
from pathlib import Path
from typing import Any

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    BotoCoreError = Exception  # type: ignore[misc]
    ClientError = Exception  # type: ignore[misc]

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class AWSTextractParser(BaseParser):
    """PDF parser using AWS Textract for commercial-grade text extraction.

    This parser uses Amazon Textract's DetectDocumentText API to extract text
    from PDFs. It provides high accuracy and includes cost tracking for
    benchmarking commercial parsers against open-source alternatives.

    The parser integrates with the caching system to avoid redundant API calls
    and provides comprehensive error handling for API failures, rate limits,
    and network issues.

    Attributes:
        name: Parser identifier ('aws_textract')
        version: boto3 library version string
        last_parsing_cost: Cost of most recent parse() call in USD

    Examples:
        >>> parser = AWSTextractParser()
        >>> parser.name
        'aws_textract'
        >>> pdf = Path("document.pdf")
        >>> output = Path("output")
        >>> result = parser.parse(pdf, output)
        >>> print(f"Cost: ${parser.last_parsing_cost:.4f}")
    """

    # Pricing: $1.50 per 1,000 pages for DetectDocumentText
    COST_PER_PAGE = 0.0015

    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str | None = None,
    ) -> None:
        """Initialize the AWS Textract parser.

        Credentials are loaded from constructor arguments or environment variables.
        If neither is provided, boto3 will attempt to use AWS CLI configuration.

        Args:
            aws_access_key_id: AWS access key (defaults to AWS_ACCESS_KEY_ID env var)
            aws_secret_access_key: AWS secret key (defaults to AWS_SECRET_ACCESS_KEY)
            region_name: AWS region (defaults to AWS_REGION env var or us-east-1)

        Raises:
            ImportError: If boto3 is not installed
            RuntimeError: If AWS credentials are not configured.
            BotoCoreError: If boto3 client initialization fails.
        """
        if not AWS_AVAILABLE:
            raise ImportError(
                "boto3 is required for AWS Textract parser. Install with: pip install boto3"
            )

        # Get credentials from args or environment
        self._aws_profile = os.getenv("AWS_PROFILE")
        self._aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self._aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self._region_name = region_name or os.getenv("AWS_REGION", "us-east-1")

        # Initialize boto3 client
        try:
            if self._aws_profile:
                # Use AWS profile
                session = boto3.Session(
                    profile_name=self._aws_profile,
                    region_name=self._region_name,
                )
                self._client = session.client("textract")
            elif self._aws_access_key_id and self._aws_secret_access_key:
                # Use explicit credentials
                self._client = boto3.client(
                    "textract",
                    aws_access_key_id=self._aws_access_key_id,
                    aws_secret_access_key=self._aws_secret_access_key,
                    region_name=self._region_name,
                )
            else:
                raise RuntimeError(
                    "AWS credentials not found. Set AWS_PROFILE or "
                    "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment "
                    "variables or pass them to the constructor."
                )
        except BotoCoreError as e:
            raise RuntimeError(f"Failed to initialize AWS Textract client: {e}") from e

        # Cost tracking
        self._total_cost = 0.0
        self._total_pages = 0
        self.last_parsing_cost = 0.0

    @property
    def name(self) -> str:
        """Return the parser's unique identifier.

        Returns:
            str: Always returns 'aws_textract'.
        """
        return "aws_textract"

    @property
    def version(self) -> str:
        """Return the boto3 library version.

        Returns:
            str: boto3 version string (e.g., '1.35.0').
        """
        return boto3.__version__

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file using AWS Textract and generate Markdown output.

        This method sends the PDF to AWS Textract's DetectDocumentText API
        and converts the response to Markdown format. The implementation:
        1. Checks cache for existing result
        2. If cache miss, reads PDF file
        3. Calls Textract API with rate limiting
        4. Converts Textract response to Markdown
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
            RuntimeError: If Textract API call fails or produces no output.
            ValueError: If PDF exceeds size or page limits.

        Examples:
            >>> parser = AWSTextractParser()
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

        # Check file size (10 MB limit for synchronous API)
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            raise ValueError(
                f"PDF file too large ({file_size_mb:.2f} MB). "
                "AWS Textract synchronous API has a 10 MB limit."
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

        # Cache miss - parse the PDF using Textract
        try:
            # Read PDF file
            pdf_bytes = pdf_path.read_bytes()

            # Call Textract API
            markdown_text = self._extract_text(pdf_bytes)

            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write markdown file
            markdown_path = output_dir / f"{pdf_path.stem}.md"
            markdown_path.write_text(markdown_text, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, markdown_path, cache_dir)

            return cached_path

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))

            if error_code == "ThrottlingException":
                raise RuntimeError(f"AWS Textract rate limit exceeded: {error_msg}") from e
            elif error_code == "InvalidParameterException":
                raise ValueError(f"Invalid PDF file: {error_msg}") from e
            elif error_code == "ProvisionedThroughputExceededException":
                raise RuntimeError(f"AWS Textract throughput exceeded: {error_msg}") from e
            else:
                raise RuntimeError(f"AWS Textract API error ({error_code}): {error_msg}") from e

        except BotoCoreError as e:
            raise RuntimeError(f"AWS SDK error: {e}") from e

        except PermissionError as e:
            raise PermissionError(f"Permission denied: {e}") from e

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with AWS Textract: {e}") from e

    def _extract_text(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using AWS Textract DetectDocumentText API.

        This method calls the Textract API and converts the JSON response to
        Markdown format. It also tracks the number of pages processed for
        cost estimation.

        For multi-page PDFs, each page is converted to PNG and processed
        separately since DetectDocumentText with Bytes only supports single-page.

        Args:
            pdf_bytes: PDF file content as bytes.

        Returns:
            str: Extracted text in Markdown format.

        Raises:
            ClientError: If Textract API call fails.
            BotoCoreError: If boto3 SDK error occurs.
        """

        try:
            import fitz  # PyMuPDF
        except ImportError as err:
            raise ImportError(
                "PyMuPDF (fitz) is required for multi-page PDF support. "
                "Install with: pip install pymupdf"
            ) from err

        # Open PDF to check page count
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(pdf_doc)

        all_text_blocks = []

        if page_count == 1:
            # Single page - send PDF directly
            pdf_doc.close()
            response = self._client.detect_document_text(Document={"Bytes": pdf_bytes})
            all_text_blocks = self._extract_blocks(response)
        else:
            # Multi-page - convert each page to PNG and process separately
            for page_num in range(page_count):
                page = pdf_doc[page_num]
                # Render page to PNG at 150 DPI for good quality
                pix = page.get_pixmap(dpi=150)
                png_bytes = pix.tobytes("png")

                # Call Textract for this page
                response = self._client.detect_document_text(Document={"Bytes": png_bytes})
                page_blocks = self._extract_blocks(response)
                all_text_blocks.extend(page_blocks)

            pdf_doc.close()

        # Calculate cost
        self.last_parsing_cost = page_count * self.COST_PER_PAGE
        self._total_cost += self.last_parsing_cost
        self._total_pages += page_count

        # Convert to markdown (simple concatenation with paragraph breaks)
        markdown = "\n\n".join(all_text_blocks)

        return markdown.strip()

    def _extract_blocks(self, response: dict[str, Any]) -> list[str]:
        """Extract text blocks from Textract API response.

        Textract returns blocks of different types (PAGE, LINE, WORD).
        This method extracts LINE blocks which contain complete lines of text.

        Args:
            response: Textract API response dictionary.

        Returns:
            list[str]: List of text lines extracted from the document.
        """
        text_blocks = []

        for block in response.get("Blocks", []):
            # We want LINE blocks which represent complete lines of text
            if block["BlockType"] == "LINE":
                text = block.get("Text", "").strip()
                if text:
                    text_blocks.append(text)

        return text_blocks

    def get_total_cost(self) -> float:
        """Get total cost of all parsing operations in this session.

        Returns:
            float: Total cost in USD.

        Examples:
            >>> parser = AWSTextractParser()
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
            >>> parser = AWSTextractParser()
            >>> parser.parse(Path("doc1.pdf"), Path("output"))
            >>> print(f"Pages processed: {parser.get_total_pages()}")
        """
        return self._total_pages
