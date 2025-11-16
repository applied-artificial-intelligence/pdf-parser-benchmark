"""GOV.UK HTML content scraper.

This module provides functions to download and extract clean HTML content from GOV.UK
publication pages. It handles the specific HTML structure of GOV.UK websites,
extracting main content while stripping navigation, headers, and footers.

License: Open Government Licence v3.0
See: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
"""

import logging
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

# Configure logging
logger = logging.getLogger(__name__)

# User-Agent for polite scraping
USER_AGENT = "PDF-Bench/0.1.0 (https://github.com/pdf-bench/pdf-bench; research project)"

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 2.0  # Exponential backoff multiplier
DEFAULT_REQUEST_TIMEOUT = 30  # seconds


class GovUKScraperError(Exception):
    """Base exception for GOV.UK scraper errors."""

    pass


class NetworkError(GovUKScraperError):
    """Exception raised for network-related errors."""

    pass


class ContentExtractionError(GovUKScraperError):
    """Exception raised when content extraction fails."""

    pass


def download_html(
    url: str,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    timeout: int = DEFAULT_REQUEST_TIMEOUT,
) -> str:
    """Download HTML content from a URL with retry logic.

    Args:
        url: The URL to download from
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff (seconds)
        timeout: Request timeout in seconds

    Returns:
        Raw HTML content as string

    Raises:
        NetworkError: If download fails after all retries
    """
    headers = {"User-Agent": USER_AGENT}

    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading HTML from {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            logger.info(f"Successfully downloaded {len(response.text)} bytes from {url}")
            return response.text

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
            if 400 <= e.response.status_code < 500:
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


def extract_main_content(html: str, url: str = "") -> str:
    """Extract main content from GOV.UK HTML page.

    This function identifies and extracts the main content area from GOV.UK pages,
    removing navigation, headers, footers, and other non-content elements while
    preserving semantic HTML structure (headings, lists, tables, paragraphs).

    GOV.UK pages typically use:
    - <main id="content"> for main content area
    - <div class="publication-content"> for publication content
    - <article> for article content
    - <nav>, <header>, <footer> for elements to remove

    Args:
        html: Raw HTML content as string
        url: Optional URL for logging/debugging purposes

    Returns:
        Cleaned HTML content as string

    Raises:
        ContentExtractionError: If main content cannot be found
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove script and style elements entirely
    for element in soup(["script", "style"]):
        element.decompose()

    # Try to find main content area using various selectors
    content = None
    selectors = [
        ("main#content", "main tag with id='content'"),
        ("main", "main tag"),
        (".publication-content", "publication-content class"),
        ("article.publication", "article.publication"),
        ("article", "article tag"),
        (".govuk-main-wrapper", "govuk-main-wrapper class"),
    ]

    for selector, description in selectors:
        content = soup.select_one(selector)
        if content:
            logger.info(f"Found main content using selector: {description}")
            break

    if not content:
        logger.error(f"Could not find main content area for {url}")
        raise ContentExtractionError(
            f"Could not find main content area. Tried selectors: "
            f"{', '.join(s[0] for s in selectors)}"
        )

    # Remove unwanted elements from within the content
    # These are elements that appear within the main content but aren't content themselves
    unwanted_selectors = [
        "nav",  # Navigation menus
        "header",  # Headers
        "footer",  # Footers
        ".gem-c-breadcrumbs",  # Breadcrumbs
        ".gem-c-related-navigation",  # Related links
        ".app-c-print-link",  # Print buttons
        ".govuk-button-group",  # Button groups
        ".gem-c-share-links",  # Share links
        "[role='navigation']",  # Navigation roles
        ".attachment-details",  # Attachment metadata (keep the attachments, not metadata)
    ]

    for selector in unwanted_selectors:
        for element in content.select(selector):
            logger.debug(f"Removing element: {selector}")
            element.decompose()

    # Extract the cleaned HTML
    cleaned_html = str(content)

    # Check if content is effectively empty (no text content)
    if not content.get_text(strip=True):
        raise ContentExtractionError("Extracted content is empty")

    logger.info(f"Extracted {len(cleaned_html)} bytes of cleaned content")
    return cleaned_html


def scrape_govuk_content(
    url: str,
    max_retries: int = DEFAULT_MAX_RETRIES,
    rate_limit_delay: float = 1.5,
) -> str:
    """Download and extract main content from a GOV.UK URL.

    This is the main entry point that combines download_html and extract_main_content.
    It includes rate limiting to be respectful to GOV.UK servers.

    Args:
        url: GOV.UK URL to scrape
        max_retries: Maximum number of retry attempts for download
        rate_limit_delay: Delay in seconds after successful download (rate limiting)

    Returns:
        Cleaned HTML content as string

    Raises:
        NetworkError: If download fails
        ContentExtractionError: If content extraction fails
    """
    logger.info(f"Scraping GOV.UK content from: {url}")

    # Download HTML
    html = download_html(url, max_retries=max_retries)

    # Extract main content
    content = extract_main_content(html, url=url)

    # Rate limiting - be polite to GOV.UK servers
    if rate_limit_delay > 0:
        logger.debug(f"Rate limiting: waiting {rate_limit_delay} seconds")
        time.sleep(rate_limit_delay)

    return content


def save_html_content(content: str, output_path: Path) -> None:
    """Save HTML content to a file.

    Creates parent directories if they don't exist.

    Args:
        content: HTML content to save
        output_path: Path where to save the file

    Raises:
        OSError: If file cannot be written
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"Saved HTML content to {output_path} ({len(content)} bytes)")


def scrape_and_save(
    url: str,
    output_path: Path,
    max_retries: int = DEFAULT_MAX_RETRIES,
    rate_limit_delay: float = 1.5,
) -> dict[str, str | int]:
    """Download, extract, and save GOV.UK content.

    Convenience function that combines scraping and saving.

    Args:
        url: GOV.UK URL to scrape
        output_path: Path where to save the cleaned HTML
        max_retries: Maximum number of retry attempts
        rate_limit_delay: Delay in seconds after successful download

    Returns:
        Dictionary with metadata about the operation:
            - url: Source URL
            - output_path: Where content was saved
            - content_size: Size of saved content in bytes
            - status: "success" or "error"
            - error: Error message if status is "error" (optional)

    Raises:
        GovUKScraperError: If scraping or saving fails
    """
    try:
        content = scrape_govuk_content(url, max_retries=max_retries, rate_limit_delay=rate_limit_delay)
        save_html_content(content, output_path)

        return {
            "url": url,
            "output_path": str(output_path),
            "content_size": len(content),
            "status": "success",
        }

    except GovUKScraperError as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return {
            "url": url,
            "output_path": str(output_path),
            "content_size": 0,
            "status": "error",
            "error": str(e),
        }
