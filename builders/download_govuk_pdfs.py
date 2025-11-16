"""GOV.UK PDF downloader.

This module provides functions to download PDFs from GOV.UK publication pages.
It handles direct PDF links, retry logic, hash verification, and rate limiting.

License: Open Government Licence v3.0
See: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
"""

import hashlib
import logging
import time
from pathlib import Path

import requests  # type: ignore[import-untyped]

# Configure logging
logger = logging.getLogger(__name__)

# User-Agent for polite scraping
USER_AGENT = "PDF-Bench/0.1.0 (https://github.com/pdf-bench/pdf-bench; research project)"

# Default configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 2.0  # Exponential backoff multiplier
DEFAULT_REQUEST_TIMEOUT = 30  # seconds for PDFs (can be large)
DEFAULT_RATE_LIMIT_DELAY = 1.5  # seconds between requests


class GovUKPDFDownloadError(Exception):
    """Base exception for GOV.UK PDF download errors."""

    pass


class NetworkError(GovUKPDFDownloadError):
    """Exception raised for network-related errors."""

    pass


class FileValidationError(GovUKPDFDownloadError):
    """Exception raised when file validation fails."""

    pass


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file.

    Args:
        file_path: Path to file to hash

    Returns:
        Hexadecimal SHA256 hash string

    Raises:
        OSError: If file cannot be read
    """
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def download_pdf(
    url: str,
    output_path: Path,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    timeout: int = DEFAULT_REQUEST_TIMEOUT,
    skip_existing: bool = False,
) -> dict[str, str | int | bool]:
    """Download a PDF from a URL with retry logic.

    Args:
        url: The URL to download PDF from
        output_path: Path where to save the PDF
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff (seconds)
        timeout: Request timeout in seconds
        skip_existing: If True, skip download if file already exists

    Returns:
        Dictionary with download metadata:
            - url: Source URL
            - output_path: Where file was saved
            - file_size: Size in bytes
            - sha256: SHA256 hash of downloaded file
            - status: "success", "skipped", or "error"
            - error: Error message if status is "error" (optional)
            - skipped: True if file was skipped

    Raises:
        NetworkError: If download fails after all retries
        OSError: If file cannot be written
    """
    # Check if file exists and skip if requested
    if skip_existing and output_path.exists():
        logger.info(f"File already exists, skipping: {output_path}")
        file_size = output_path.stat().st_size
        try:
            sha256 = calculate_sha256(output_path)
        except Exception as e:
            logger.warning(f"Could not calculate hash for existing file: {e}")
            sha256 = ""

        return {
            "url": url,
            "output_path": str(output_path),
            "file_size": file_size,
            "sha256": sha256,
            "status": "skipped",
            "skipped": True,
        }

    headers = {"User-Agent": USER_AGENT}

    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading PDF from {url} (attempt {attempt + 1}/{max_retries})")

            # Stream download for large files
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.raise_for_status()

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Download with progress tracking
            total_size = int(response.headers.get("content-length", 0))
            logger.debug(f"Downloading {total_size:,} bytes to {output_path}")

            downloaded_size = 0
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
                        downloaded_size += len(chunk)

            logger.info(
                f"Successfully downloaded {downloaded_size:,} bytes to {output_path.name}"
            )

            # Calculate hash for verification
            sha256 = calculate_sha256(output_path)
            logger.debug(f"SHA256: {sha256}")

            return {
                "url": url,
                "output_path": str(output_path),
                "file_size": downloaded_size,
                "sha256": sha256,
                "status": "success",
                "skipped": False,
            }

        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                sleep_time = backoff_factor**attempt
                logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
            else:
                raise NetworkError(f"Timeout after {max_retries} attempts: {url}") from e

        except requests.exceptions.HTTPError as e:
            # Don't retry on 4xx errors (client errors)
            if e.response is not None and 400 <= e.response.status_code < 500:
                raise NetworkError(
                    f"HTTP {e.response.status_code} error for {url}: {e}"
                ) from e
            # Retry on 5xx errors (server errors)
            logger.warning(f"HTTP error on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                sleep_time = backoff_factor**attempt
                logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
            else:
                raise NetworkError(
                    f"HTTP error after {max_retries} attempts: {url}"
                ) from e

        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                sleep_time = backoff_factor**attempt
                logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
            else:
                raise NetworkError(f"Request failed after {max_retries} attempts: {url}") from e

    # Should never reach here, but for type safety
    raise NetworkError(f"Download failed for unknown reason: {url}")


def verify_pdf_hash(file_path: Path, expected_hash: str) -> bool:
    """Verify a PDF file's SHA256 hash.

    Args:
        file_path: Path to PDF file
        expected_hash: Expected SHA256 hash (hexadecimal)

    Returns:
        True if hash matches, False otherwise

    Raises:
        OSError: If file cannot be read
    """
    actual_hash = calculate_sha256(file_path)
    matches = actual_hash.lower() == expected_hash.lower()

    if matches:
        logger.info(f"Hash verification successful: {file_path.name}")
    else:
        logger.error(
            f"Hash mismatch for {file_path.name}:\n"
            f"  Expected: {expected_hash}\n"
            f"  Actual:   {actual_hash}"
        )

    return matches


def download_with_rate_limit(
    url: str,
    output_path: Path,
    max_retries: int = DEFAULT_MAX_RETRIES,
    rate_limit_delay: float = DEFAULT_RATE_LIMIT_DELAY,
    skip_existing: bool = False,
) -> dict[str, str | int | bool]:
    """Download PDF with rate limiting.

    This is the main entry point that combines download_pdf with rate limiting.

    Args:
        url: URL to download from
        output_path: Path where to save the PDF
        max_retries: Maximum number of retry attempts
        rate_limit_delay: Delay in seconds after download (rate limiting)
        skip_existing: If True, skip download if file exists

    Returns:
        Dictionary with download metadata (see download_pdf for details)

    Raises:
        NetworkError: If download fails
        OSError: If file cannot be written
    """
    result = download_pdf(
        url,
        output_path,
        max_retries=max_retries,
        skip_existing=skip_existing,
    )

    # Rate limiting - be polite to GOV.UK servers
    # Only delay if we actually downloaded (not skipped)
    if not result.get("skipped", False) and rate_limit_delay > 0:
        logger.debug(f"Rate limiting: waiting {rate_limit_delay} seconds")
        time.sleep(rate_limit_delay)

    return result


def is_pdf_url(url: str) -> bool:
    """Check if a URL appears to be a PDF file.

    Args:
        url: URL to check

    Returns:
        True if URL appears to be a PDF, False otherwise
    """
    if not url:
        return False

    url_lower = url.lower()

    # Direct PDF URL
    if url_lower.endswith(".pdf"):
        return True

    # GOV.UK PDF download endpoint
    if "/pdf" in url_lower:
        return True

    return False


def is_non_pdf_url(url: str) -> bool:
    """Check if a URL is definitely not a PDF.

    Args:
        url: URL to check

    Returns:
        True if URL is definitely not a PDF (e.g., ZIP, HTML)
    """
    if not url:
        return True

    url_lower = url.lower()

    # Known non-PDF formats
    non_pdf_extensions = [".zip", ".tar.gz", ".html", ".htm", ".ods", ".xlsx", ".xls"]

    for ext in non_pdf_extensions:
        if url_lower.endswith(ext):
            return True

    return False
