"""SEC EDGAR API client for downloading SEC filings.

This module provides a client for downloading SEC EDGAR filings (HTML and PDF versions)
with proper rate limiting, error handling, and retry logic as required by SEC.gov.

SEC Requirements:
- User-Agent header is MANDATORY (SEC blocks requests without it)
- Rate limit: Be conservative (5-10 req/sec max)
- Respect robots.txt
"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SECEdgarClient:
    """Client for downloading SEC EDGAR filings.

    This client handles:
    - HTML filing downloads
    - PDF filing downloads (when available)
    - Filing metadata retrieval
    - Rate limiting (10 requests/second max)
    - Retry logic with exponential backoff
    - Proper User-Agent headers

    Attributes:
        user_agent: User-Agent string for SEC compliance
        rate_limit_delay: Minimum seconds between requests
        max_retries: Maximum retry attempts for failed requests
        session: Requests session for connection pooling
    """

    BASE_URL = "https://www.sec.gov"
    ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"

    def __init__(
        self,
        user_agent: str = "PDF-Bench/0.1 (research@pdf-bench.org)",
        rate_limit_delay: float = 0.15,  # ~6.7 req/sec (conservative)
        max_retries: int = 3,
    ) -> None:
        """Initialize SEC EDGAR client.

        Args:
            user_agent: User-Agent string (required by SEC)
            rate_limit_delay: Minimum seconds between requests (default: 0.15s = ~6.7 req/s)
            max_retries: Maximum number of retry attempts
        """
        self.user_agent = user_agent
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.last_request_time = 0.0

        # Create session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
        })

        logger.info(f"Initialized SEC EDGAR client with User-Agent: {self.user_agent}")

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _make_request(
        self,
        url: str,
        timeout: int = 30,
        allow_redirects: bool = True,
    ) -> requests.Response:
        """Make HTTP request with retry logic.

        Args:
            url: URL to request
            timeout: Request timeout in seconds
            allow_redirects: Whether to follow redirects

        Returns:
            Response object

        Raises:
            requests.RequestException: On persistent request failures
        """
        self._rate_limit()

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Request attempt {attempt + 1}/{self.max_retries}: {url}")
                response = self.session.get(
                    url,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                )

                # Handle specific HTTP errors
                if response.status_code == 403:
                    logger.warning(f"403 Forbidden - possible rate limiting or User-Agent issue: {url}")
                    if attempt < self.max_retries - 1:
                        backoff = 2 ** attempt
                        logger.info(f"Retrying after {backoff}s backoff")
                        time.sleep(backoff)
                        continue
                    response.raise_for_status()
                elif response.status_code == 404:
                    logger.error(f"404 Not Found: {url}")
                    response.raise_for_status()
                else:
                    response.raise_for_status()

                logger.debug(f"Request successful: {url} (status={response.status_code})")
                return response

            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries}): {url}")
                if attempt < self.max_retries - 1:
                    backoff = 2 ** attempt
                    time.sleep(backoff)
                    continue
                raise requests.RequestException(f"Request timeout after {self.max_retries} attempts") from e

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {url}")
                if attempt < self.max_retries - 1:
                    backoff = 2 ** attempt
                    time.sleep(backoff)
                    continue
                raise requests.RequestException(f"Connection error after {self.max_retries} attempts") from e

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {url} - {e}")
                if attempt < self.max_retries - 1:
                    backoff = 2 ** attempt
                    time.sleep(backoff)
                    continue
                raise

        raise requests.RequestException(f"Failed after {self.max_retries} attempts")

    def download_filing_html(self, cik: str, accession_number: str) -> str:
        """Download HTML version of SEC filing.

        Args:
            cik: Company CIK number (with or without leading zeros)
            accession_number: Filing accession number (e.g., "0000320193-24-000123")

        Returns:
            HTML content as string

        Raises:
            requests.RequestException: On download failure
        """
        # Clean CIK (remove leading zeros for URL)
        cik_clean = cik.lstrip('0') or '0'

        # Clean accession number (remove dashes for URL path)
        accession_clean = accession_number.replace('-', '')

        # Try direct document URL first (most common)
        # Format: https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_doc}.htm
        # We need to construct the primary document filename
        # Typically it's the company ticker symbol + filing date, but we'll try the viewer URL first

        # Use EDGAR viewer URL
        viewer_url = (
            f"{self.BASE_URL}/cgi-bin/viewer"
            f"?action=view&cik={cik_clean}&accession_number={accession_number}&xbrl_type=v"
        )

        logger.info(f"Downloading HTML filing: CIK={cik}, Accession={accession_number}")
        logger.debug(f"Viewer URL: {viewer_url}")

        try:
            response = self._make_request(viewer_url)
            html_content = response.text

            # Verify we got actual content (not an error page)
            if len(html_content) < 100 or "error" in html_content.lower()[:500]:
                logger.warning("Response may be an error page, checking content...")

            logger.info(f"Successfully downloaded HTML ({len(html_content)} bytes)")
            return html_content

        except requests.RequestException as e:
            logger.error(f"Failed to download HTML filing: {e}")
            raise

    def get_filing_index(self, cik: str, accession_number: str) -> str:
        """Download filing index page to find available documents.

        Args:
            cik: Company CIK number
            accession_number: Filing accession number

        Returns:
            HTML content of filing index page

        Raises:
            requests.RequestException: On download failure
        """
        cik_clean = cik.lstrip('0') or '0'
        accession_clean = accession_number.replace('-', '')

        # Filing index URL
        index_url = f"{self.ARCHIVES_URL}/{cik_clean}/{accession_clean}/{accession_number}-index.htm"

        logger.info(f"Fetching filing index: {index_url}")

        try:
            response = self._make_request(index_url)
            return response.text
        except requests.RequestException:
            # Try without -index.htm suffix
            index_url_alt = f"{self.ARCHIVES_URL}/{cik_clean}/{accession_clean}/"
            logger.info(f"Trying alternate index URL: {index_url_alt}")
            response = self._make_request(index_url_alt)
            return response.text

    def find_pdf_url(self, cik: str, accession_number: str) -> Optional[str]:
        """Find PDF document URL from filing index.

        Args:
            cik: Company CIK number
            accession_number: Filing accession number

        Returns:
            PDF URL if found, None otherwise
        """
        try:
            index_html = self.get_filing_index(cik, accession_number)
            soup = BeautifulSoup(index_html, 'html.parser')

            # Look for PDF links in the filing index
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    # Construct full URL
                    if href.startswith('http'):
                        pdf_url = href
                    else:
                        pdf_url = urljoin(self.BASE_URL, href)
                    logger.info(f"Found PDF URL: {pdf_url}")
                    return pdf_url

            logger.info("No PDF document found in filing index")
            return None

        except Exception as e:
            logger.warning(f"Error finding PDF URL: {e}")
            return None

    def download_filing_pdf(self, cik: str, accession_number: str) -> Optional[bytes]:
        """Download PDF version of SEC filing if available.

        Args:
            cik: Company CIK number
            accession_number: Filing accession number

        Returns:
            PDF content as bytes, or None if no PDF available

        Raises:
            requests.RequestException: On download failure (if PDF found but download fails)
        """
        logger.info(f"Attempting to download PDF: CIK={cik}, Accession={accession_number}")

        # Find PDF URL
        pdf_url = self.find_pdf_url(cik, accession_number)
        if not pdf_url:
            logger.info("No PDF available for this filing")
            return None

        # Download PDF
        try:
            response = self._make_request(pdf_url)
            pdf_content = response.content

            # Verify it's actually a PDF
            if not pdf_content.startswith(b'%PDF'):
                logger.warning("Downloaded file does not appear to be a PDF")
                return None

            logger.info(f"Successfully downloaded PDF ({len(pdf_content)} bytes)")
            return pdf_content

        except requests.RequestException as e:
            logger.error(f"Failed to download PDF: {e}")
            raise

    def get_filing_metadata(self, cik: str, accession_number: str) -> Dict[str, Any]:
        """Get filing metadata from SEC.

        Args:
            cik: Company CIK number
            accession_number: Filing accession number

        Returns:
            Dictionary with filing metadata
        """
        logger.info(f"Fetching metadata: CIK={cik}, Accession={accession_number}")

        try:
            index_html = self.get_filing_index(cik, accession_number)
            soup = BeautifulSoup(index_html, 'html.parser')

            metadata: Dict[str, Any] = {
                'cik': cik,
                'accession_number': accession_number,
                'documents': [],
            }

            # Extract company name
            company_name_tag = soup.find('span', class_='companyName')
            if company_name_tag:
                metadata['company_name'] = company_name_tag.get_text(strip=True)

            # Extract filing type and date from the page
            # Look for table rows with document information
            table = soup.find('table', class_='tableFile')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        doc_info = {
                            'sequence': cols[0].get_text(strip=True),
                            'description': cols[1].get_text(strip=True),
                            'document': cols[2].get_text(strip=True),
                            'type': cols[3].get_text(strip=True),
                        }
                        metadata['documents'].append(doc_info)

            logger.info(f"Retrieved metadata: {len(metadata.get('documents', []))} documents")
            return metadata

        except Exception as e:
            logger.warning(f"Error fetching metadata: {e}")
            return {
                'cik': cik,
                'accession_number': accession_number,
                'error': str(e),
            }

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
        logger.info("Closed SEC EDGAR client session")

    def __enter__(self) -> "SECEdgarClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
