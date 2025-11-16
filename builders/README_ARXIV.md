# arXiv Corpus Builder

This directory contains tools for downloading arXiv papers for the PDF-Bench academic corpus.

## Components

### 1. `arxiv_client.py`
Main client for interacting with arXiv API.

**Features:**
- Fetch paper metadata from arXiv API (Atom XML)
- Download PDFs
- Download LaTeX source files (.tar.gz)
- Download ar5iv HTML5 versions (critical for ground truth generation)
- Rate limiting (1 request/second by default)
- Retry logic with exponential backoff
- Comprehensive error handling
- arXiv ID versioning handling (e.g., v1, v2)

**Usage:**
```python
from arxiv_client import ArxivClient

client = ArxivClient(rate_limit=1.0)

# Fetch metadata
metadata = client.get_paper_metadata("2303.18223")
print(metadata["title"])  # "A Survey of Large Language Models"

# Download files
from pathlib import Path
client.download_pdf("2303.18223", Path("paper.pdf"))
client.download_source("2303.18223", Path("paper.tar.gz"))
client.download_ar5iv_html("2303.18223", Path("paper.html"))
```

**API Endpoints:**
- Metadata: `http://export.arxiv.org/api/query?id_list={arxiv_id}`
- PDF: `https://arxiv.org/pdf/{arxiv_id}.pdf`
- Source: `https://arxiv.org/e-print/{arxiv_id}` (returns .tar.gz)
- ar5iv: `https://ar5iv.labs.arxiv.org/html/{arxiv_id}`

### 2. `download_arxiv_corpus.py`
Script to download all 40 papers from `corpus/academic/arxiv_targets.yaml`.

**Features:**
- Reads target papers from YAML
- Downloads PDF, LaTeX source, and ar5iv HTML for each paper
- Validates downloads against target metadata
- Logs all progress to `arxiv_download.log`
- Saves download results to JSON
- Handles interruptions gracefully

**Usage:**
```bash
cd builders
source ../.venv/bin/activate
python download_arxiv_corpus.py
```

**Output Structure:**
```
corpus/academic/arxiv/
├── pdfs/
│   ├── 2303.18223.pdf
│   ├── 2303.08774.pdf
│   └── ...
├── sources/
│   ├── 2303.18223.tar.gz
│   ├── 2303.08774.tar.gz
│   └── ...
├── ar5iv/
│   ├── 2303.18223.html
│   ├── 2303.08774.html
│   └── ...
└── download_results.json
```

**Download Results:**
The script generates `download_results.json` with:
- Summary statistics (total, successful, failed, success rate)
- List of successful downloads
- List of failed downloads with error details

### 3. `test_arxiv_client.py`
Comprehensive unit tests with 96% coverage.

**Test Coverage:**
- Client initialization
- arXiv ID normalization (handling versions)
- Rate limiting enforcement
- Metadata fetching and XML parsing
- PDF downloads with validation
- LaTeX source downloads
- ar5iv HTML5 downloads
- Error handling (network errors, invalid content, etc.)
- HTTP request handling

**Run Tests:**
```bash
source .venv/bin/activate
pytest tests/test_builders/test_arxiv_client.py -v
```

## ar5iv HTML5 Integration

**ar5iv** (https://ar5iv.labs.arxiv.org/) provides experimental HTML5 conversions of arXiv papers.

**Why ar5iv is Critical:**
- High-quality HTML5 rendering of LaTeX papers
- 100% availability verified for all 40 target papers
- Easier to convert HTML→Markdown than LaTeX→Markdown
- Preserves structure (sections, equations, tables, figures)
- Reduces conversion errors

**Ground Truth Strategy:**
1. **Primary:** ar5iv HTML5 → Markdown (high quality, fewer errors)
2. **Fallback:** LaTeX source → Markdown (if ar5iv fails)
3. **Validation:** Compare against PDF rendering

## Rate Limiting & Politeness

**arXiv API Guidelines:**
- Default: 1 request/second (configurable)
- arXiv is generous but recommend being polite
- Client implements exponential backoff on errors
- Retry on 429 (rate limit), 5xx errors

**Estimated Download Time:**
- 40 papers × 3 files = 120 downloads
- At 1 req/sec: ~2 minutes (excluding download time)
- Total with downloads: ~10-15 minutes (depends on file sizes)

## Error Handling

**Client Exceptions:**
- `ArxivClientError`: Base exception
- `ArxivMetadataError`: Metadata fetch/parse failure
- `ArxivDownloadError`: Download failure

**Common Errors:**
- Network timeouts: Automatic retry with backoff
- 404 Not Found: Paper doesn't exist or ar5iv unavailable
- Content-Type mismatch: Downloaded wrong file type
- Empty file: Download corrupted

**Recovery:**
- Script can be re-run safely (skips existing files)
- Failed downloads logged to `download_results.json`
- Individual papers can be retried

## License Compliance

All 40 target papers have permissive licenses:
- **arXiv non-exclusive license**: 32 papers
- **CC-BY-4.0**: 8 papers

Usage for research benchmarking is explicitly allowed.

## Testing

**Unit Tests:**
```bash
pytest tests/test_builders/test_arxiv_client.py -v --cov=builders.arxiv_client
```

**Real API Test:**
```bash
cd builders
python test_real_arxiv.py
```

**Download Corpus:**
```bash
python download_arxiv_corpus.py
```

## Dependencies

All dependencies already in `pyproject.toml`:
- `requests>=2.31.0` - HTTP client
- `pyyaml>=6.0` - YAML parsing

Standard library:
- `xml.etree.ElementTree` - Atom XML parsing
- `urllib3.util.retry` - Retry logic
- `pathlib` - File path handling
- `logging` - Logging
