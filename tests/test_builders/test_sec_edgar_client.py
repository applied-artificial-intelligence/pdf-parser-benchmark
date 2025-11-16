"""Tests for SEC EDGAR client."""

import time
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

from builders.sec_edgar_client import SECEdgarClient


class TestSECEdgarClientInit:
    """Test client initialization."""

    def test_default_initialization(self) -> None:
        """Test client initializes with default values."""
        client = SECEdgarClient()
        assert client.user_agent == "PDF-Bench/0.1 (research@pdf-bench.org)"
        assert client.rate_limit_delay == 0.15
        assert client.max_retries == 3
        assert client.session is not None
        client.close()

    def test_custom_initialization(self) -> None:
        """Test client initializes with custom values."""
        client = SECEdgarClient(
            user_agent="Test/1.0 (test@example.com)",
            rate_limit_delay=0.2,
            max_retries=5,
        )
        assert client.user_agent == "Test/1.0 (test@example.com)"
        assert client.rate_limit_delay == 0.2
        assert client.max_retries == 5
        client.close()

    def test_session_headers(self) -> None:
        """Test that session has required headers."""
        client = SECEdgarClient(user_agent="Test/1.0")
        assert client.session.headers["User-Agent"] == "Test/1.0"
        assert "Accept" in client.session.headers
        client.close()

    def test_context_manager(self) -> None:
        """Test client works as context manager."""
        with SECEdgarClient() as client:
            assert client.session is not None
        # Session should be closed after context exit


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limiting_enforced(self) -> None:
        """Test that rate limiting delays requests."""
        client = SECEdgarClient(rate_limit_delay=0.1)

        start_time = time.time()
        client._rate_limit()
        first_request = time.time()
        client._rate_limit()
        second_request = time.time()

        # Second request should be delayed
        delay = second_request - first_request
        assert delay >= 0.1, f"Expected delay >= 0.1s, got {delay}s"

        client.close()

    def test_no_delay_on_first_request(self) -> None:
        """Test that first request has no delay."""
        client = SECEdgarClient(rate_limit_delay=0.1)

        start_time = time.time()
        client._rate_limit()
        elapsed = time.time() - start_time

        # First request should be immediate (or very fast)
        assert elapsed < 0.05

        client.close()


class TestMakeRequest:
    """Test HTTP request functionality."""

    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_successful_request(self, mock_get: Mock) -> None:
        """Test successful HTTP request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_get.return_value = mock_response

        client = SECEdgarClient()
        response = client._make_request("https://www.sec.gov/test")

        assert response.status_code == 200
        assert response.text == "Success"
        mock_get.assert_called_once()
        client.close()

    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_404_error(self, mock_get: Mock) -> None:
        """Test handling of 404 errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        client = SECEdgarClient(max_retries=1)  # Reduce retries for faster test

        with pytest.raises(requests.HTTPError):
            client._make_request("https://www.sec.gov/nonexistent")

        client.close()

    @patch('builders.sec_edgar_client.requests.Session.get')
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_403_retry_logic(self, mock_sleep: Mock, mock_get: Mock) -> None:
        """Test retry logic for 403 errors."""
        # First two attempts return 403, third succeeds
        mock_response_403 = Mock()
        mock_response_403.status_code = 403
        mock_response_403.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.text = "Success after retry"

        mock_get.side_effect = [mock_response_403, mock_response_403, mock_response_200]

        client = SECEdgarClient(max_retries=3, rate_limit_delay=0)
        response = client._make_request("https://www.sec.gov/test")

        assert response.status_code == 200
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep between retries
        client.close()

    @patch('builders.sec_edgar_client.requests.Session.get')
    @patch('time.sleep')
    def test_timeout_retry(self, mock_sleep: Mock, mock_get: Mock) -> None:
        """Test retry logic for timeouts."""
        # First attempt times out, second succeeds
        mock_get.side_effect = [
            requests.exceptions.Timeout("Request timeout"),
            Mock(status_code=200, text="Success"),
        ]

        client = SECEdgarClient(max_retries=3, rate_limit_delay=0)
        response = client._make_request("https://www.sec.gov/test")

        assert response.status_code == 200
        assert mock_get.call_count == 2
        client.close()

    @patch('builders.sec_edgar_client.requests.Session.get')
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep: Mock, mock_get: Mock) -> None:
        """Test that max retries is enforced."""
        mock_get.side_effect = requests.exceptions.Timeout("Always timeout")

        client = SECEdgarClient(max_retries=3, rate_limit_delay=0)

        with pytest.raises(requests.RequestException) as exc_info:
            client._make_request("https://www.sec.gov/test")

        assert "after 3 attempts" in str(exc_info.value)
        assert mock_get.call_count == 3
        client.close()


class TestDownloadFilingHTML:
    """Test HTML filing download."""

    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_download_html_success(self, mock_get: Mock) -> None:
        """Test successful HTML download."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test filing content</body></html>"
        mock_get.return_value = mock_response

        client = SECEdgarClient(rate_limit_delay=0)
        html = client.download_filing_html("0000320193", "0000320193-24-000123")

        assert "Test filing content" in html
        assert mock_get.called
        client.close()

    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_download_html_with_leading_zeros(self, mock_get: Mock) -> None:
        """Test HTML download with CIK containing leading zeros."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Content</html>"
        mock_get.return_value = mock_response

        client = SECEdgarClient(rate_limit_delay=0)
        # CIK with leading zeros should be handled correctly
        html = client.download_filing_html("0000000001", "0000000001-24-000001")

        assert html == "<html>Content</html>"
        # Verify the URL used has CIK without leading zeros
        call_args = mock_get.call_args
        url = call_args[0][0]
        assert "cik=1&" in url or "cik=1" in url
        client.close()

    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_download_html_error(self, mock_get: Mock) -> None:
        """Test error handling in HTML download."""
        mock_get.side_effect = requests.RequestException("Network error")

        client = SECEdgarClient(max_retries=1, rate_limit_delay=0)

        with pytest.raises(requests.RequestException):
            client.download_filing_html("0000320193", "0000320193-24-000123")

        client.close()


class TestDownloadFilingPDF:
    """Test PDF filing download."""

    @patch.object(SECEdgarClient, 'find_pdf_url')
    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_download_pdf_success(self, mock_get: Mock, mock_find_pdf: Mock) -> None:
        """Test successful PDF download."""
        # Mock PDF URL discovery
        mock_find_pdf.return_value = "https://www.sec.gov/test.pdf"

        # Mock PDF download
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'%PDF-1.4\nTest PDF content'
        mock_get.return_value = mock_response

        client = SECEdgarClient(rate_limit_delay=0)
        pdf = client.download_filing_pdf("0000320193", "0000320193-24-000123")

        assert pdf is not None
        assert pdf.startswith(b'%PDF')
        assert b'Test PDF content' in pdf
        client.close()

    @patch.object(SECEdgarClient, 'find_pdf_url')
    def test_download_pdf_not_available(self, mock_find_pdf: Mock) -> None:
        """Test PDF download when no PDF available."""
        mock_find_pdf.return_value = None

        client = SECEdgarClient(rate_limit_delay=0)
        pdf = client.download_filing_pdf("0000320193", "0000320193-24-000123")

        assert pdf is None
        client.close()

    @patch.object(SECEdgarClient, 'find_pdf_url')
    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_download_pdf_invalid_format(self, mock_get: Mock, mock_find_pdf: Mock) -> None:
        """Test PDF download with invalid PDF format."""
        mock_find_pdf.return_value = "https://www.sec.gov/test.pdf"

        # Return HTML instead of PDF
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Not a PDF</html>'
        mock_get.return_value = mock_response

        client = SECEdgarClient(rate_limit_delay=0)
        pdf = client.download_filing_pdf("0000320193", "0000320193-24-000123")

        assert pdf is None  # Should return None for invalid PDF
        client.close()


class TestFindPDFURL:
    """Test PDF URL discovery."""

    @patch.object(SECEdgarClient, 'get_filing_index')
    def test_find_pdf_url_success(self, mock_get_index: Mock) -> None:
        """Test finding PDF URL in filing index."""
        mock_index_html = """
        <html>
            <table>
                <tr><td><a href="/Archives/edgar/data/320193/0000320193-24-000123/filing.pdf">PDF</a></td></tr>
                <tr><td><a href="/Archives/edgar/data/320193/0000320193-24-000123/filing.htm">HTML</a></td></tr>
            </table>
        </html>
        """
        mock_get_index.return_value = mock_index_html

        client = SECEdgarClient(rate_limit_delay=0)
        pdf_url = client.find_pdf_url("0000320193", "0000320193-24-000123")

        assert pdf_url is not None
        assert "filing.pdf" in pdf_url
        assert pdf_url.startswith("https://www.sec.gov")
        client.close()

    @patch.object(SECEdgarClient, 'get_filing_index')
    def test_find_pdf_url_not_found(self, mock_get_index: Mock) -> None:
        """Test when no PDF URL found in filing index."""
        mock_index_html = """
        <html>
            <table>
                <tr><td><a href="/filing.htm">HTML</a></td></tr>
            </table>
        </html>
        """
        mock_get_index.return_value = mock_index_html

        client = SECEdgarClient(rate_limit_delay=0)
        pdf_url = client.find_pdf_url("0000320193", "0000320193-24-000123")

        assert pdf_url is None
        client.close()

    @patch.object(SECEdgarClient, 'get_filing_index')
    def test_find_pdf_url_with_absolute_url(self, mock_get_index: Mock) -> None:
        """Test finding PDF URL when link is absolute."""
        mock_index_html = """
        <html>
            <table>
                <tr><td><a href="https://www.sec.gov/test.pdf">PDF</a></td></tr>
            </table>
        </html>
        """
        mock_get_index.return_value = mock_index_html

        client = SECEdgarClient(rate_limit_delay=0)
        pdf_url = client.find_pdf_url("0000320193", "0000320193-24-000123")

        assert pdf_url == "https://www.sec.gov/test.pdf"
        client.close()


class TestGetFilingMetadata:
    """Test filing metadata retrieval."""

    @patch.object(SECEdgarClient, 'get_filing_index')
    def test_get_metadata_success(self, mock_get_index: Mock) -> None:
        """Test successful metadata retrieval."""
        mock_index_html = """
        <html>
            <span class="companyName">APPLE INC</span>
            <table class="tableFile">
                <tr><th>Seq</th><th>Description</th><th>Document</th><th>Type</th></tr>
                <tr>
                    <td>1</td>
                    <td>10-K</td>
                    <td>aapl-20240928.htm</td>
                    <td>10-K</td>
                </tr>
            </table>
        </html>
        """
        mock_get_index.return_value = mock_index_html

        client = SECEdgarClient(rate_limit_delay=0)
        metadata = client.get_filing_metadata("0000320193", "0000320193-24-000123")

        assert metadata['cik'] == "0000320193"
        assert metadata['accession_number'] == "0000320193-24-000123"
        assert metadata['company_name'] == "APPLE INC"
        assert len(metadata['documents']) == 1
        assert metadata['documents'][0]['document'] == "aapl-20240928.htm"
        client.close()

    @patch.object(SECEdgarClient, 'get_filing_index')
    def test_get_metadata_error(self, mock_get_index: Mock) -> None:
        """Test metadata retrieval with error."""
        mock_get_index.side_effect = Exception("Network error")

        client = SECEdgarClient(rate_limit_delay=0)
        metadata = client.get_filing_metadata("0000320193", "0000320193-24-000123")

        assert 'error' in metadata
        assert metadata['cik'] == "0000320193"
        client.close()


class TestGetFilingIndex:
    """Test filing index retrieval."""

    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_get_index_success(self, mock_get: Mock) -> None:
        """Test successful index retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Filing Index</html>"
        mock_get.return_value = mock_response

        client = SECEdgarClient(rate_limit_delay=0)
        index_html = client.get_filing_index("0000320193", "0000320193-24-000123")

        assert "Filing Index" in index_html
        client.close()

    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_get_index_fallback_url(self, mock_get: Mock) -> None:
        """Test fallback to alternate index URL."""
        # First URL fails, second succeeds
        mock_response_404 = Mock()
        mock_response_404.status_code = 404
        mock_response_404.raise_for_status.side_effect = requests.HTTPError("404")

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.text = "<html>Alternate Index</html>"

        mock_get.side_effect = [mock_response_404, mock_response_200]

        client = SECEdgarClient(rate_limit_delay=0, max_retries=1)
        index_html = client.get_filing_index("0000320193", "0000320193-24-000123")

        assert "Alternate Index" in index_html
        assert mock_get.call_count == 2
        client.close()


class TestUserAgentHeader:
    """Test User-Agent header presence."""

    @patch('builders.sec_edgar_client.requests.Session.get')
    def test_user_agent_in_request(self, mock_get: Mock) -> None:
        """Test that User-Agent header is included in requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_get.return_value = mock_response

        client = SECEdgarClient(user_agent="TestAgent/1.0", rate_limit_delay=0)
        client._make_request("https://www.sec.gov/test")

        # Verify session has User-Agent header
        assert client.session.headers["User-Agent"] == "TestAgent/1.0"
        client.close()
