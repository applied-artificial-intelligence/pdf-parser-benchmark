# GOV.UK PDF Downloader

This module provides tools for downloading PDF documents from GOV.UK publications.

## Features

- **PDF Downloads**: Download PDFs from `url_pdf` field in target YAML
- **Hash Verification**: SHA256 hash calculation for downloaded files
- **Retry Logic**: Exponential backoff retry on network failures (3 attempts)
- **Rate Limiting**: 1.5s delay between downloads (polite scraping)
- **Resume Support**: Skip already downloaded files
- **Error Handling**: Comprehensive error handling for network, HTTP, and file I/O errors
- **Format Detection**: Automatically skip non-PDF formats (ZIP, HTML, ODS, etc.)
- **Progress Tracking**: Detailed logging and progress indicators
- **Metadata**: JSON metadata file with download results and hashes

## Files

- **`download_govuk_pdfs.py`**: Core PDF download module (316 lines)
- **`download_govuk_pdf_corpus.py`**: CLI tool for batch downloads (425 lines)
- **`tests/test_download_govuk_pdfs.py`**: Comprehensive test suite (560 lines, 95% coverage)

## Usage

### Basic Download

```bash
# Download all PDFs
python builders/download_govuk_pdf_corpus.py

# Download with limit (for testing)
python builders/download_govuk_pdf_corpus.py --limit 5

# Dry run (show what would be downloaded)
python builders/download_govuk_pdf_corpus.py --dry-run
```

### Advanced Options

```bash
# Skip existing files
python builders/download_govuk_pdf_corpus.py --skip-existing

# Custom rate limiting
python builders/download_govuk_pdf_corpus.py --rate-limit 2.0

# Custom retry count
python builders/download_govuk_pdf_corpus.py --max-retries 5

# Verbose output
python builders/download_govuk_pdf_corpus.py --verbose
```

### Custom Paths

```bash
# Custom targets file
python builders/download_govuk_pdf_corpus.py \
  --targets /path/to/targets.yaml \
  --output /path/to/output/dir
```

## Output

- **PDFs**: `corpus/business/govuk/pdfs/*.pdf`
- **Metadata**: `corpus/business/govuk/pdfs/download_metadata.json`

### Metadata Format

```json
{
  "targets_file": "corpus/business/gov_uk_targets.yaml",
  "output_dir": "corpus/business/govuk/pdfs",
  "statistics": {
    "total": 30,
    "processed": 24,
    "successful": 24,
    "failed": 0,
    "skipped": 6,
    "no_pdf_url": 6,
    "non_pdf_format": 1
  },
  "downloads": [
    {
      "id": "govuk_001",
      "title": "NHS England Annual Report...",
      "url": "https://assets.publishing.service.gov.uk/...",
      "output_path": "corpus/business/govuk/pdfs/govuk_001.pdf",
      "file_size": 2297415,
      "sha256": "3ea850a600bc503001dbd5e9ea92b9e07ac78a7f30a5494ba2370ffdc4dfd802",
      "status": "success",
      "skipped": false
    }
  ]
}
```

## API Usage

```python
from pathlib import Path
from builders.download_govuk_pdfs import download_pdf, verify_pdf_hash

# Download a single PDF
result = download_pdf(
    url="https://example.gov.uk/document.pdf",
    output_path=Path("output/doc.pdf"),
    max_retries=3,
    skip_existing=True,
)

print(f"Downloaded {result['file_size']} bytes")
print(f"SHA256: {result['sha256']}")

# Verify hash
is_valid = verify_pdf_hash(
    Path("output/doc.pdf"),
    expected_hash="abc123..."
)
```

## Error Handling

The downloader handles:

- **Network Errors**: Timeout, connection refused, DNS errors
- **HTTP Errors**: 404 (not retried), 500 (retried with backoff)
- **File I/O Errors**: Permission denied, disk full
- **Invalid Formats**: ZIP, HTML, ODS files are skipped with warnings

### Exit Codes

- `0`: Success (all downloads completed)
- `1`: Partial failure (some downloads failed)
- `130`: Interrupted by user (Ctrl+C)

## Testing

```bash
# Run tests
pytest tests/test_builders/test_download_govuk_pdfs.py -v

# With coverage
pytest tests/test_builders/test_download_govuk_pdfs.py \
  --cov=builders.download_govuk_pdfs \
  --cov-report=term-missing

# Code quality
ruff check builders/download_govuk_pdfs.py
mypy builders/download_govuk_pdfs.py --check-untyped-defs
```

## Notes

### HTML-Only Documents

Some GOV.UK documents (6 out of 30 in current targets) are HTML-only:
- `govuk_012`: Housing Supply (null PDF URL)
- `govuk_017`: Education and Training Statistics (null PDF URL)
- `govuk_023`: UK Milk Prices (null PDF URL)
- `govuk_024`: Light Rail and Tram Statistics (null PDF URL)
- `govuk_028`: Police Powers and Procedures (null PDF URL)
- `govuk_030`: R&D Tax Credits Statistics (null PDF URL)

These documents may require HTML→PDF conversion using the GOV.UK HTML converter.

### Non-PDF Formats

Some documents have non-PDF URLs:
- `govuk_011`: Road Traffic Estimates (ZIP file)

These are automatically skipped with informational messages.

## Integration

This module integrates with:
- **`gov_uk_targets.yaml`**: Source of PDF URLs
- **`scrape_govuk.py`**: HTML scraping module (similar patterns)
- **`govuk_html_to_markdown.py`**: For HTML-only documents

## Performance

- **Rate Limit**: 1.5s between downloads (polite to GOV.UK servers)
- **Timeout**: 30s per PDF (handles large files)
- **Retry**: Exponential backoff (1s, 2s, 4s)
- **Throughput**: ~40 PDFs/minute with rate limiting

## License

Open Government Licence v3.0
See: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
