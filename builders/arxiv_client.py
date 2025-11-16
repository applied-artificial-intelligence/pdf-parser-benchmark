"""
arXiv API Client for PDF-Bench.

This module provides a client for interacting with the arXiv API to:
- Fetch paper metadata
- Download PDFs
- Download LaTeX source files (.tar.gz)
- Download ar5iv HTML5 versions

The client implements rate limiting, retry logic, and comprehensive error handling.
"""

import logging
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ArxivClientError(Exception):
    """Base exception for ArxivClient errors."""

    pass


class ArxivMetadataError(ArxivClientError):
    """Raised when metadata cannot be fetched or parsed."""

    pass


class ArxivDownloadError(ArxivClientError):
    """Raised when a download fails."""

    pass


class ArxivClient:
    """
    Client for interacting with arXiv API and downloading papers.

    Implements:
    - Rate limiting (default 1 request/second)
    - Retry logic with exponential backoff
    - Polite User-Agent
    - arXiv ID versioning handling
    """

    # API endpoints
    API_BASE = "http://export.arxiv.org/api/query"
    PDF_BASE = "https://arxiv.org/pdf"
    SOURCE_BASE = "https://arxiv.org/e-print"
    AR5IV_BASE = "https://ar5iv.labs.arxiv.org/html"

    # Atom XML namespace
    ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
    ARXIV_NS = {"arxiv": "http://arxiv.org/schemas/atom"}

    def __init__(
        self,
        rate_limit: float = 1.0,
        max_retries: int = 3,
        timeout: int = 30,
        user_agent: str = "PDF-Bench/0.1 (research project)",
    ) -> None:
        """
        Initialize the arXiv client.

        Args:
            rate_limit: Minimum time between requests in seconds (default: 1.0)
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 30)
            user_agent: User-Agent header for requests
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.user_agent = user_agent
        self._last_request_time = 0.0

        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=2,  # Exponential backoff: 2s, 4s, 8s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({"User-Agent": self.user_agent})

    def _normalize_arxiv_id(self, arxiv_id: str) -> str:
        """
        Normalize arXiv ID by removing version suffix.

        Args:
            arxiv_id: arXiv ID (e.g., "2301.00001v2" or "2301.00001")

        Returns:
            Normalized arXiv ID without version (e.g., "2301.00001")
        """
        # Remove version suffix if present (e.g., v1, v2, etc.)
        if "v" in arxiv_id:
            return arxiv_id.split("v")[0]
        return arxiv_id

    def _rate_limit_wait(self) -> None:
        """Wait to enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            wait_time = self.rate_limit - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        self._last_request_time = time.time()

    def _make_request(self, url: str, stream: bool = False) -> requests.Response:
        """
        Make an HTTP request with rate limiting.

        Args:
            url: URL to request
            stream: Whether to stream the response

        Returns:
            Response object

        Raises:
            ArxivClientError: If request fails
        """
        self._rate_limit_wait()
        logger.info(f"Requesting: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout, stream=stream)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise ArxivClientError(f"Request failed: {e}") from e

    def get_paper_metadata(self, arxiv_id: str) -> dict[str, Any]:
        """
        Fetch paper metadata from arXiv API.

        Args:
            arxiv_id: arXiv ID (e.g., "2303.18223")

        Returns:
            Dictionary containing:
                - id: arXiv ID
                - title: Paper title
                - authors: List of author names
                - abstract: Paper abstract
                - categories: List of categories
                - published: Publication date (ISO format)
                - updated: Last update date (ISO format)
                - pdf_url: URL to PDF
                - source_url: URL to source .tar.gz
                - ar5iv_url: URL to ar5iv HTML5 version

        Raises:
            ArxivMetadataError: If metadata cannot be fetched or parsed
        """
        normalized_id = self._normalize_arxiv_id(arxiv_id)
        url = f"{self.API_BASE}?id_list={quote(normalized_id)}"

        try:
            response = self._make_request(url)
        except ArxivClientError as e:
            raise ArxivMetadataError(f"Failed to fetch metadata for {arxiv_id}: {e}") from e

        # Parse Atom XML response
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            raise ArxivMetadataError(f"Failed to parse XML response: {e}") from e

        # Find entry element
        entry = root.find("atom:entry", self.ATOM_NS)
        if entry is None:
            raise ArxivMetadataError(f"No entry found for arXiv ID: {arxiv_id}")

        # Extract metadata
        try:
            metadata = {
                "id": normalized_id,
                "title": self._get_text(entry, "atom:title"),
                "authors": self._get_authors(entry),
                "abstract": self._get_text(entry, "atom:summary"),
                "categories": self._get_categories(entry),
                "published": self._get_text(entry, "atom:published"),
                "updated": self._get_text(entry, "atom:updated"),
                "pdf_url": f"{self.PDF_BASE}/{normalized_id}.pdf",
                "source_url": f"{self.SOURCE_BASE}/{normalized_id}",
                "ar5iv_url": f"{self.AR5IV_BASE}/{normalized_id}",
            }
            logger.info(f"Successfully fetched metadata for {arxiv_id}")
            return metadata
        except Exception as e:
            raise ArxivMetadataError(f"Failed to extract metadata: {e}") from e

    def _get_text(self, element: ET.Element, tag: str) -> str:
        """Extract text from XML element, handling namespaces."""
        child = element.find(tag, self.ATOM_NS)
        if child is not None and child.text:
            return child.text.strip()
        return ""

    def _get_authors(self, entry: ET.Element) -> list[str]:
        """Extract author names from entry."""
        authors = []
        for author in entry.findall("atom:author", self.ATOM_NS):
            name = author.find("atom:name", self.ATOM_NS)
            if name is not None and name.text:
                authors.append(name.text.strip())
        return authors

    def _get_categories(self, entry: ET.Element) -> list[str]:
        """Extract categories from entry."""
        categories = []
        for category in entry.findall("atom:category", self.ATOM_NS):
            term = category.get("term")
            if term:
                categories.append(term)
        return categories

    def download_pdf(self, arxiv_id: str, output_path: Path) -> None:
        """
        Download PDF for a paper.

        Args:
            arxiv_id: arXiv ID (e.g., "2303.18223")
            output_path: Path to save PDF

        Raises:
            ArxivDownloadError: If download fails
        """
        normalized_id = self._normalize_arxiv_id(arxiv_id)
        url = f"{self.PDF_BASE}/{normalized_id}.pdf"

        try:
            self._download_file(url, output_path, expected_content_type="application/pdf")
            logger.info(f"Successfully downloaded PDF for {arxiv_id} to {output_path}")
        except Exception as e:
            raise ArxivDownloadError(f"Failed to download PDF for {arxiv_id}: {e}") from e

    def download_source(self, arxiv_id: str, output_path: Path) -> None:
        """
        Download LaTeX source (.tar.gz) for a paper.

        Args:
            arxiv_id: arXiv ID (e.g., "2303.18223")
            output_path: Path to save source file

        Raises:
            ArxivDownloadError: If download fails
        """
        normalized_id = self._normalize_arxiv_id(arxiv_id)
        url = f"{self.SOURCE_BASE}/{normalized_id}"

        try:
            # arXiv source endpoint returns .tar.gz but Content-Type may vary
            self._download_file(url, output_path, expected_content_type=None)
            logger.info(f"Successfully downloaded source for {arxiv_id} to {output_path}")
        except Exception as e:
            raise ArxivDownloadError(f"Failed to download source for {arxiv_id}: {e}") from e

    def download_ar5iv_html(self, arxiv_id: str, output_path: Path) -> None:
        """
        Download ar5iv HTML5 version of a paper.

        ar5iv provides experimental HTML5 conversions of arXiv papers.
        This is the preferred format for ground truth generation as it
        avoids LaTeX→Markdown conversion errors.

        Args:
            arxiv_id: arXiv ID (e.g., "2303.18223")
            output_path: Path to save HTML file

        Raises:
            ArxivDownloadError: If download fails or HTML not available
        """
        normalized_id = self._normalize_arxiv_id(arxiv_id)
        url = f"{self.AR5IV_BASE}/{normalized_id}"

        try:
            self._download_file(url, output_path, expected_content_type="text/html")
            logger.info(f"Successfully downloaded ar5iv HTML for {arxiv_id} to {output_path}")
        except Exception as e:
            raise ArxivDownloadError(
                f"Failed to download ar5iv HTML for {arxiv_id}: {e}"
            ) from e

    def _download_file(
        self, url: str, output_path: Path, expected_content_type: Optional[str] = None
    ) -> None:
        """
        Download a file with verification.

        Args:
            url: URL to download
            output_path: Path to save file
            expected_content_type: Expected Content-Type header (if specified)

        Raises:
            ArxivDownloadError: If download or verification fails
        """
        try:
            response = self._make_request(url, stream=True)

            # Verify Content-Type if specified
            if expected_content_type:
                content_type = response.headers.get("Content-Type", "")
                if not content_type.startswith(expected_content_type):
                    raise ArxivDownloadError(
                        f"Unexpected Content-Type: {content_type} "
                        f"(expected {expected_content_type})"
                    )

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file in chunks
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Verify file size
            file_size = output_path.stat().st_size
            if file_size == 0:
                raise ArxivDownloadError("Downloaded file is empty")

            logger.debug(f"Downloaded {file_size} bytes to {output_path}")

        except Exception as e:
            # Clean up partial download
            if output_path.exists():
                output_path.unlink()
            raise ArxivDownloadError(f"Download failed: {e}") from e
