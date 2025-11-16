"""Tests for GOV.UK PDF downloader."""

import hashlib
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from builders.download_govuk_pdfs import (
    FileValidationError,
    GovUKPDFDownloadError,
    NetworkError,
    calculate_sha256,
    download_pdf,
    download_with_rate_limit,
    is_non_pdf_url,
    is_pdf_url,
    verify_pdf_hash,
)

# Sample PDF content (minimal valid PDF)
SAMPLE_PDF_CONTENT = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000315 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
408
%%EOF
"""


@pytest.fixture
def temp_pdf_file(tmp_path: Path) -> Path:
    """Create a temporary PDF file for testing."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(SAMPLE_PDF_CONTENT)
    return pdf_file


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock requests Response object."""
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.headers = {"content-length": str(len(SAMPLE_PDF_CONTENT))}
    response.iter_content = Mock(
        return_value=[SAMPLE_PDF_CONTENT[i:i+8192]
                     for i in range(0, len(SAMPLE_PDF_CONTENT), 8192)]
    )
    return response


class TestCalculateSHA256:
    """Tests for calculate_sha256 function."""

    def test_calculate_sha256_success(self, temp_pdf_file: Path) -> None:
        """Test successful hash calculation."""
        expected_hash = hashlib.sha256(SAMPLE_PDF_CONTENT).hexdigest()
        result = calculate_sha256(temp_pdf_file)

        assert result == expected_hash
        assert len(result) == 64  # SHA256 is 64 hex characters

    def test_calculate_sha256_nonexistent_file(self, tmp_path: Path) -> None:
        """Test hash calculation with nonexistent file."""
        nonexistent = tmp_path / "nonexistent.pdf"

        with pytest.raises(OSError):
            calculate_sha256(nonexistent)

    def test_calculate_sha256_empty_file(self, tmp_path: Path) -> None:
        """Test hash calculation with empty file."""
        empty_file = tmp_path / "empty.pdf"
        empty_file.write_bytes(b"")

        # Hash of empty file
        expected_hash = hashlib.sha256(b"").hexdigest()
        result = calculate_sha256(empty_file)

        assert result == expected_hash


class TestDownloadPDF:
    """Tests for download_pdf function."""

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_success(
        self, mock_get: Mock, tmp_path: Path, mock_response: Mock
    ) -> None:
        """Test successful PDF download."""
        mock_get.return_value = mock_response
        output_path = tmp_path / "downloaded.pdf"

        result = download_pdf(
            url="https://example.gov.uk/test.pdf",
            output_path=output_path,
        )

        assert result["status"] == "success"
        assert result["url"] == "https://example.gov.uk/test.pdf"
        assert result["output_path"] == str(output_path)
        assert result["file_size"] == len(SAMPLE_PDF_CONTENT)
        assert "sha256" in result
        assert len(result["sha256"]) == 64
        assert result["skipped"] is False
        assert output_path.exists()
        assert output_path.read_bytes() == SAMPLE_PDF_CONTENT

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_skip_existing(
        self, mock_get: Mock, temp_pdf_file: Path
    ) -> None:
        """Test skipping download when file exists."""
        result = download_pdf(
            url="https://example.gov.uk/test.pdf",
            output_path=temp_pdf_file,
            skip_existing=True,
        )

        assert result["status"] == "skipped"
        assert result["skipped"] is True
        assert "sha256" in result
        assert not mock_get.called

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_timeout_with_retry(self, mock_get: Mock, tmp_path: Path) -> None:
        """Test timeout error with retry logic."""
        # First attempt times out, second succeeds
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "100"}
        mock_response.iter_content = Mock(return_value=[SAMPLE_PDF_CONTENT])

        mock_get.side_effect = [
            requests.exceptions.Timeout("Connection timeout"),
            mock_response,
        ]

        output_path = tmp_path / "downloaded.pdf"

        with patch("time.sleep"):  # Skip actual sleep during test
            result = download_pdf(
                url="https://example.gov.uk/test.pdf",
                output_path=output_path,
                max_retries=3,
            )

        assert result["status"] == "success"
        assert mock_get.call_count == 2

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_timeout_exhausted(self, mock_get: Mock, tmp_path: Path) -> None:
        """Test timeout error with all retries exhausted."""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")

        output_path = tmp_path / "downloaded.pdf"

        with patch("time.sleep"):  # Skip actual sleep during test
            with pytest.raises(NetworkError) as exc_info:
                download_pdf(
                    url="https://example.gov.uk/test.pdf",
                    output_path=output_path,
                    max_retries=3,
                )

        assert "Timeout after 3 attempts" in str(exc_info.value)
        assert mock_get.call_count == 3

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_404_error(self, mock_get: Mock, tmp_path: Path) -> None:
        """Test 404 error (should not retry)."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        output_path = tmp_path / "downloaded.pdf"

        with pytest.raises(NetworkError) as exc_info:
            download_pdf(
                url="https://example.gov.uk/test.pdf",
                output_path=output_path,
                max_retries=3,
            )

        assert "HTTP 404" in str(exc_info.value)
        # Should not retry on 4xx errors
        assert mock_get.call_count == 1

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_500_error_with_retry(self, mock_get: Mock, tmp_path: Path) -> None:
        """Test 500 error with retry (should retry)."""
        # First attempt fails with 500, second succeeds
        error_response = Mock(spec=requests.Response)
        error_response.status_code = 500
        error_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=error_response
        )

        success_response = Mock(spec=requests.Response)
        success_response.status_code = 200
        success_response.headers = {"content-length": "100"}
        success_response.iter_content = Mock(return_value=[SAMPLE_PDF_CONTENT])

        mock_get.side_effect = [error_response, success_response]

        output_path = tmp_path / "downloaded.pdf"

        with patch("time.sleep"):  # Skip actual sleep during test
            result = download_pdf(
                url="https://example.gov.uk/test.pdf",
                output_path=output_path,
                max_retries=3,
            )

        assert result["status"] == "success"
        assert mock_get.call_count == 2

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_connection_error(self, mock_get: Mock, tmp_path: Path) -> None:
        """Test connection error with retry."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        output_path = tmp_path / "downloaded.pdf"

        with patch("time.sleep"):  # Skip actual sleep during test
            with pytest.raises(NetworkError) as exc_info:
                download_pdf(
                    url="https://example.gov.uk/test.pdf",
                    output_path=output_path,
                    max_retries=3,
                )

        assert "Request failed after 3 attempts" in str(exc_info.value)
        assert mock_get.call_count == 3

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_creates_directories(
        self, mock_get: Mock, tmp_path: Path, mock_response: Mock
    ) -> None:
        """Test that download creates parent directories."""
        mock_get.return_value = mock_response

        # Create nested path that doesn't exist
        output_path = tmp_path / "nested" / "directories" / "test.pdf"

        result = download_pdf(
            url="https://example.gov.uk/test.pdf",
            output_path=output_path,
        )

        assert result["status"] == "success"
        assert output_path.exists()
        assert output_path.parent.exists()

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_pdf_user_agent_header(
        self, mock_get: Mock, tmp_path: Path, mock_response: Mock
    ) -> None:
        """Test that User-Agent header is set correctly."""
        mock_get.return_value = mock_response
        output_path = tmp_path / "downloaded.pdf"

        download_pdf(
            url="https://example.gov.uk/test.pdf",
            output_path=output_path,
        )

        # Check that User-Agent header was set
        call_args = mock_get.call_args
        assert "headers" in call_args.kwargs
        assert "User-Agent" in call_args.kwargs["headers"]
        assert "PDF-Bench" in call_args.kwargs["headers"]["User-Agent"]


class TestVerifyPDFHash:
    """Tests for verify_pdf_hash function."""

    def test_verify_hash_match(self, temp_pdf_file: Path) -> None:
        """Test hash verification with matching hash."""
        expected_hash = hashlib.sha256(SAMPLE_PDF_CONTENT).hexdigest()

        result = verify_pdf_hash(temp_pdf_file, expected_hash)

        assert result is True

    def test_verify_hash_mismatch(self, temp_pdf_file: Path) -> None:
        """Test hash verification with mismatched hash."""
        wrong_hash = "0" * 64

        result = verify_pdf_hash(temp_pdf_file, wrong_hash)

        assert result is False

    def test_verify_hash_case_insensitive(self, temp_pdf_file: Path) -> None:
        """Test that hash verification is case-insensitive."""
        expected_hash = hashlib.sha256(SAMPLE_PDF_CONTENT).hexdigest()

        # Test with uppercase
        result = verify_pdf_hash(temp_pdf_file, expected_hash.upper())
        assert result is True

        # Test with lowercase
        result = verify_pdf_hash(temp_pdf_file, expected_hash.lower())
        assert result is True


class TestDownloadWithRateLimit:
    """Tests for download_with_rate_limit function."""

    @patch("builders.download_govuk_pdfs.download_pdf")
    @patch("time.sleep")
    def test_download_with_rate_limit_success(
        self, mock_sleep: Mock, mock_download: Mock, tmp_path: Path
    ) -> None:
        """Test download with rate limiting."""
        mock_download.return_value = {
            "status": "success",
            "skipped": False,
            "file_size": 1000,
            "sha256": "abc123",
        }

        output_path = tmp_path / "test.pdf"

        result = download_with_rate_limit(
            url="https://example.gov.uk/test.pdf",
            output_path=output_path,
            rate_limit_delay=1.5,
        )

        assert result["status"] == "success"
        assert mock_download.called
        assert mock_sleep.called
        assert mock_sleep.call_args[0][0] == 1.5

    @patch("builders.download_govuk_pdfs.download_pdf")
    @patch("time.sleep")
    def test_download_with_rate_limit_skipped_no_delay(
        self, mock_sleep: Mock, mock_download: Mock, tmp_path: Path
    ) -> None:
        """Test that rate limiting is skipped when file is skipped."""
        mock_download.return_value = {
            "status": "skipped",
            "skipped": True,
        }

        output_path = tmp_path / "test.pdf"

        result = download_with_rate_limit(
            url="https://example.gov.uk/test.pdf",
            output_path=output_path,
            rate_limit_delay=1.5,
        )

        assert result["status"] == "skipped"
        assert mock_download.called
        # Should not sleep when file is skipped
        assert not mock_sleep.called


class TestURLValidation:
    """Tests for URL validation functions."""

    def test_is_pdf_url_direct_pdf(self) -> None:
        """Test is_pdf_url with direct PDF URLs."""
        assert is_pdf_url("https://example.gov.uk/document.pdf") is True
        assert is_pdf_url("https://example.gov.uk/document.PDF") is True
        assert is_pdf_url("https://example.gov.uk/path/to/file.pdf") is True

    def test_is_pdf_url_pdf_endpoint(self) -> None:
        """Test is_pdf_url with /pdf/ in path."""
        assert is_pdf_url("https://example.gov.uk/pdf/document") is True
        assert is_pdf_url("https://example.gov.uk/article/pdf") is True

    def test_is_pdf_url_non_pdf(self) -> None:
        """Test is_pdf_url with non-PDF URLs."""
        assert is_pdf_url("https://example.gov.uk/document.html") is False
        assert is_pdf_url("https://example.gov.uk/document.zip") is False
        assert is_pdf_url("https://example.gov.uk/document") is False
        assert is_pdf_url("") is False
        assert is_pdf_url(None) is False

    def test_is_non_pdf_url_zip(self) -> None:
        """Test is_non_pdf_url with ZIP files."""
        assert is_non_pdf_url("https://example.gov.uk/data.zip") is True
        assert is_non_pdf_url("https://example.gov.uk/data.tar.gz") is True

    def test_is_non_pdf_url_html(self) -> None:
        """Test is_non_pdf_url with HTML files."""
        assert is_non_pdf_url("https://example.gov.uk/page.html") is True
        assert is_non_pdf_url("https://example.gov.uk/page.htm") is True

    def test_is_non_pdf_url_spreadsheet(self) -> None:
        """Test is_non_pdf_url with spreadsheet files."""
        assert is_non_pdf_url("https://example.gov.uk/data.ods") is True
        assert is_non_pdf_url("https://example.gov.uk/data.xlsx") is True
        assert is_non_pdf_url("https://example.gov.uk/data.xls") is True

    def test_is_non_pdf_url_pdf(self) -> None:
        """Test is_non_pdf_url with PDF URLs (should return False)."""
        assert is_non_pdf_url("https://example.gov.uk/document.pdf") is False
        assert is_non_pdf_url("https://example.gov.uk/document") is False

    def test_is_non_pdf_url_empty(self) -> None:
        """Test is_non_pdf_url with empty/None URLs."""
        assert is_non_pdf_url("") is True
        assert is_non_pdf_url(None) is True


class TestErrorHandling:
    """Tests for error handling."""

    def test_govuk_pdf_download_error_inheritance(self) -> None:
        """Test exception hierarchy."""
        assert issubclass(NetworkError, GovUKPDFDownloadError)
        assert issubclass(FileValidationError, GovUKPDFDownloadError)

    def test_network_error_message(self) -> None:
        """Test NetworkError with custom message."""
        error = NetworkError("Test error message")
        assert str(error) == "Test error message"

    def test_file_validation_error_message(self) -> None:
        """Test FileValidationError with custom message."""
        error = FileValidationError("Validation failed")
        assert str(error) == "Validation failed"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_large_file_chunked(
        self, mock_get: Mock, tmp_path: Path
    ) -> None:
        """Test downloading large file in chunks."""
        # Create large content (1MB)
        large_content = b"x" * (1024 * 1024)

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-length": str(len(large_content))}
        # Split into chunks
        chunks = [large_content[i:i+8192] for i in range(0, len(large_content), 8192)]
        mock_response.iter_content = Mock(return_value=chunks)

        mock_get.return_value = mock_response

        output_path = tmp_path / "large.pdf"

        result = download_pdf(
            url="https://example.gov.uk/large.pdf",
            output_path=output_path,
        )

        assert result["status"] == "success"
        assert result["file_size"] == len(large_content)
        assert output_path.read_bytes() == large_content

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_with_keep_alive_chunks(
        self, mock_get: Mock, tmp_path: Path
    ) -> None:
        """Test that keep-alive chunks (empty) are filtered out."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"content-length": str(len(SAMPLE_PDF_CONTENT))}
        # Include empty chunks (keep-alive)
        mock_response.iter_content = Mock(
            return_value=[SAMPLE_PDF_CONTENT[:100], b"", SAMPLE_PDF_CONTENT[100:], b""]
        )

        mock_get.return_value = mock_response

        output_path = tmp_path / "test.pdf"

        result = download_pdf(
            url="https://example.gov.uk/test.pdf",
            output_path=output_path,
        )

        assert result["status"] == "success"
        assert output_path.read_bytes() == SAMPLE_PDF_CONTENT

    @patch("builders.download_govuk_pdfs.requests.get")
    def test_download_no_content_length_header(
        self, mock_get: Mock, tmp_path: Path
    ) -> None:
        """Test download when Content-Length header is missing."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {}  # No content-length
        mock_response.iter_content = Mock(return_value=[SAMPLE_PDF_CONTENT])

        mock_get.return_value = mock_response

        output_path = tmp_path / "test.pdf"

        result = download_pdf(
            url="https://example.gov.uk/test.pdf",
            output_path=output_path,
        )

        assert result["status"] == "success"
        assert output_path.exists()
