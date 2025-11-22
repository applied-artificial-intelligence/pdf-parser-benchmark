"""
Unit tests for ArxivClient.

Tests cover:
- Metadata fetching and parsing
- PDF downloads
- LaTeX source downloads
- ar5iv HTML5 downloads
- Rate limiting
- Error handling
"""

import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from builders.arxiv_client import (
    ArxivClient,
    ArxivClientError,
    ArxivDownloadError,
    ArxivMetadataError,
)

# Sample Atom XML response from arXiv API
SAMPLE_ATOM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2303.18223v1</id>
    <published>2023-03-31T17:59:59Z</published>
    <updated>2023-03-31T17:59:59Z</updated>
    <title>A Survey of Large Language Models</title>
    <summary>This paper surveys recent advances in large language models.</summary>
    <author>
      <name>Wayne Xin Zhao</name>
    </author>
    <author>
      <name>Kun Zhou</name>
    </author>
    <category term="cs.CL" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>
"""

EMPTY_ATOM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>
"""


@pytest.fixture
def client() -> ArxivClient:
    """Create ArxivClient instance with minimal rate limiting for tests."""
    return ArxivClient(rate_limit=0.01)  # Fast rate limit for testing


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock requests.Response object."""
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.headers = {"Content-Type": "application/pdf"}
    return response


class TestArxivClientInitialization:
    """Test ArxivClient initialization."""

    def test_default_initialization(self) -> None:
        """Test client initializes with default parameters."""
        client = ArxivClient()
        assert client.rate_limit == 1.0
        assert client.timeout == 30
        assert "PDF-Bench" in client.user_agent

    def test_custom_initialization(self) -> None:
        """Test client initializes with custom parameters."""
        client = ArxivClient(
            rate_limit=0.5,
            max_retries=5,
            timeout=60,
            user_agent="TestAgent/1.0",
        )
        assert client.rate_limit == 0.5
        assert client.timeout == 60
        assert client.user_agent == "TestAgent/1.0"


class TestArxivIdNormalization:
    """Test arXiv ID normalization."""

    def test_normalize_id_without_version(self, client: ArxivClient) -> None:
        """Test normalization of ID without version."""
        assert client._normalize_arxiv_id("2303.18223") == "2303.18223"

    def test_normalize_id_with_version(self, client: ArxivClient) -> None:
        """Test normalization of ID with version."""
        assert client._normalize_arxiv_id("2303.18223v1") == "2303.18223"
        assert client._normalize_arxiv_id("2303.18223v2") == "2303.18223"

    def test_normalize_old_id_format(self, client: ArxivClient) -> None:
        """Test normalization of old arXiv ID format."""
        assert client._normalize_arxiv_id("math/0601001") == "math/0601001"
        assert client._normalize_arxiv_id("math/0601001v1") == "math/0601001"


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limiting_enforced(self, client: ArxivClient) -> None:
        """Test that rate limiting is enforced."""
        client.rate_limit = 0.1  # 100ms between requests

        start_time = time.time()
        client._rate_limit_wait()
        client._rate_limit_wait()
        elapsed = time.time() - start_time

        # Second call should have waited ~100ms
        assert elapsed >= 0.1, f"Rate limiting not enforced: {elapsed}s < 0.1s"

    def test_no_wait_on_first_request(self, client: ArxivClient) -> None:
        """Test that first request doesn't wait."""
        start_time = time.time()
        client._rate_limit_wait()
        elapsed = time.time() - start_time

        # First call should be immediate
        assert elapsed < 0.01, f"First request waited unnecessarily: {elapsed}s"


class TestMetadataFetching:
    """Test metadata fetching from arXiv API."""

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_get_metadata_success(self, mock_request: Mock, client: ArxivClient) -> None:
        """Test successful metadata fetching."""
        mock_response = Mock()
        mock_response.content = SAMPLE_ATOM_XML.encode("utf-8")
        mock_request.return_value = mock_response

        metadata = client.get_paper_metadata("2303.18223")

        assert metadata["id"] == "2303.18223"
        assert metadata["title"] == "A Survey of Large Language Models"
        assert "Wayne Xin Zhao" in metadata["authors"]
        assert "Kun Zhou" in metadata["authors"]
        assert "cs.CL" in metadata["categories"]
        assert "cs.AI" in metadata["categories"]
        assert metadata["published"] == "2023-03-31T17:59:59Z"
        assert metadata["pdf_url"] == "https://arxiv.org/pdf/2303.18223.pdf"
        assert metadata["source_url"] == "https://arxiv.org/e-print/2303.18223"
        assert metadata["ar5iv_url"] == "https://ar5iv.labs.arxiv.org/html/2303.18223"

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_get_metadata_normalizes_id(self, mock_request: Mock, client: ArxivClient) -> None:
        """Test that metadata fetching normalizes arXiv ID."""
        mock_response = Mock()
        mock_response.content = SAMPLE_ATOM_XML.encode("utf-8")
        mock_request.return_value = mock_response

        metadata = client.get_paper_metadata("2303.18223v2")

        assert metadata["id"] == "2303.18223"  # Version stripped

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_get_metadata_no_entry(self, mock_request: Mock, client: ArxivClient) -> None:
        """Test error handling when no entry is found."""
        mock_response = Mock()
        mock_response.content = EMPTY_ATOM_XML.encode("utf-8")
        mock_request.return_value = mock_response

        with pytest.raises(ArxivMetadataError, match="No entry found"):
            client.get_paper_metadata("9999.99999")

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_get_metadata_invalid_xml(self, mock_request: Mock, client: ArxivClient) -> None:
        """Test error handling for invalid XML."""
        mock_response = Mock()
        mock_response.content = b"invalid xml content"
        mock_request.return_value = mock_response

        with pytest.raises(ArxivMetadataError, match="Failed to parse XML"):
            client.get_paper_metadata("2303.18223")

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_get_metadata_request_failure(self, mock_request: Mock, client: ArxivClient) -> None:
        """Test error handling when request fails."""
        mock_request.side_effect = ArxivClientError("Network error")

        with pytest.raises(ArxivMetadataError, match="Failed to fetch metadata"):
            client.get_paper_metadata("2303.18223")


class TestPDFDownload:
    """Test PDF downloading."""

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_pdf_success(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test successful PDF download."""
        # Mock streaming response
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = Mock(return_value=[b"PDF content"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.pdf"
        client.download_pdf("2303.18223", output_path)

        assert output_path.exists()
        assert output_path.read_bytes() == b"PDF content"

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_pdf_creates_directories(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test that download creates necessary directories."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = Mock(return_value=[b"PDF"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "subdir" / "test.pdf"
        client.download_pdf("2303.18223", output_path)

        assert output_path.exists()
        assert output_path.parent.exists()

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_pdf_wrong_content_type(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test error handling for wrong Content-Type."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.iter_content = Mock(return_value=[b"HTML"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.pdf"

        with pytest.raises(ArxivDownloadError, match="Unexpected Content-Type"):
            client.download_pdf("2303.18223", output_path)

        # Verify partial download is cleaned up
        assert not output_path.exists()

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_pdf_empty_file(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test error handling for empty file download."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = Mock(return_value=[])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.pdf"

        with pytest.raises(ArxivDownloadError, match="Downloaded file is empty"):
            client.download_pdf("2303.18223", output_path)

        # Verify empty file is cleaned up
        assert not output_path.exists()


class TestSourceDownload:
    """Test LaTeX source downloading."""

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_source_success(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test successful source download."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/gzip"}
        mock_response.iter_content = Mock(return_value=[b"tar.gz content"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.tar.gz"
        client.download_source("2303.18223", output_path)

        assert output_path.exists()
        assert output_path.read_bytes() == b"tar.gz content"

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_source_normalizes_id(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test that source download normalizes arXiv ID."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/gzip"}
        mock_response.iter_content = Mock(return_value=[b"content"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.tar.gz"
        client.download_source("2303.18223v2", output_path)

        # Verify request was made with normalized ID
        mock_request.assert_called_once()
        call_args = mock_request.call_args[0]
        assert "2303.18223" in call_args[0]
        assert "v2" not in call_args[0]


class TestAr5ivDownload:
    """Test ar5iv HTML5 downloading."""

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_ar5iv_success(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test successful ar5iv HTML download."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_response.iter_content = Mock(return_value=[b"<html>content</html>"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.html"
        client.download_ar5iv_html("2303.18223", output_path)

        assert output_path.exists()
        assert output_path.read_bytes() == b"<html>content</html>"

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_ar5iv_wrong_content_type(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test error handling for wrong Content-Type."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.iter_content = Mock(return_value=[b"{}"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.html"

        with pytest.raises(ArxivDownloadError, match="Unexpected Content-Type"):
            client.download_ar5iv_html("2303.18223", output_path)

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_ar5iv_request_failure(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test error handling when ar5iv request fails."""
        mock_request.side_effect = ArxivClientError("404 Not Found")

        output_path = tmp_path / "test.html"

        with pytest.raises(ArxivDownloadError, match="Failed to download ar5iv HTML"):
            client.download_ar5iv_html("2303.18223", output_path)


class TestMakeRequest:
    """Test HTTP request handling."""

    @patch("builders.arxiv_client.requests.Session.get")
    def test_make_request_success(self, mock_get: Mock, client: ArxivClient) -> None:
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = client._make_request("https://example.com")

        assert response == mock_response
        mock_get.assert_called_once()

    @patch("builders.arxiv_client.requests.Session.get")
    def test_make_request_raises_for_status(self, mock_get: Mock, client: ArxivClient) -> None:
        """Test that failed requests raise exceptions."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        mock_get.return_value = mock_response

        with pytest.raises(ArxivClientError, match="Request failed"):
            client._make_request("https://example.com")

    @patch("builders.arxiv_client.requests.Session.get")
    def test_make_request_timeout(self, mock_get: Mock, client: ArxivClient) -> None:
        """Test timeout handling."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        with pytest.raises(ArxivClientError, match="Request failed"):
            client._make_request("https://example.com")

    @patch("builders.arxiv_client.requests.Session.get")
    def test_make_request_includes_user_agent(self, mock_get: Mock, client: ArxivClient) -> None:
        """Test that User-Agent header is set."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client._make_request("https://example.com")

        # Verify User-Agent was set in session headers
        assert "User-Agent" in client.session.headers
        assert "PDF-Bench" in client.session.headers["User-Agent"]


class TestDownloadFile:
    """Test generic file download functionality."""

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_file_chunked(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test that files are downloaded in chunks."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = Mock(return_value=[b"chunk1", b"chunk2", b"chunk3"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.pdf"
        client._download_file(
            "https://example.com/test.pdf",
            output_path,
            expected_content_type="application/pdf",
        )

        assert output_path.exists()
        assert output_path.read_bytes() == b"chunk1chunk2chunk3"

    @patch("builders.arxiv_client.ArxivClient._make_request")
    def test_download_file_no_content_type_check(
        self, mock_request: Mock, client: ArxivClient, tmp_path: Path
    ) -> None:
        """Test download without Content-Type verification."""
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "application/x-tar"}
        mock_response.iter_content = Mock(return_value=[b"content"])
        mock_request.return_value = mock_response

        output_path = tmp_path / "test.tar"
        # No expected_content_type specified
        client._download_file("https://example.com/test.tar", output_path)

        assert output_path.exists()
