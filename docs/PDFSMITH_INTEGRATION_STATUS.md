# pdfsmith Integration Status

**Date**: 2024-11-24
**Goal**: Ensure all pdf-bench parsers are available via pdfsmith unified library

## Current Status

### ✅ Implemented in pdfsmith (11/20 parsers)

**Light backends** (5):
- [x] `pypdf` - Pure Python, lightweight
- [x] `pdfplumber` - Excellent for tables
- [x] `pymupdf` - Fast MuPDF bindings
- [x] `pdfminer` - Mature extraction library
- [x] `pypdfium2` - Chrome's PDF engine

**Medium backends** (4):
- [x] `pymupdf4llm` - PyMuPDF for LLM consumption
- [x] `unstructured` - Document processing for LLMs
- [x] `kreuzberg` - Rust-based with OCR
- [x] `extractous` - Rust-based extraction

**Heavy backends** (2):
- [x] `docling` - IBM's document understanding (best quality)
- [x] `marker` - Deep learning, academic papers

### ❌ Missing from pdfsmith (9/20 parsers)

**Open-source (5)**:
- [ ] `pypdf2` - Deprecated fork of pypdf (likely not needed)
- [ ] `tika` - Apache Tika wrapper
- [ ] `marker_ollama` - Marker variant with Ollama models
- [ ] `landing_ai` - Partial implementation only

**Commercial (4)**:
- [ ] `aws_textract` - AWS Textract API
- [ ] `azure_document_intelligence` - Azure Document Intelligence API
- [ ] `google_document_ai` - Google Document AI API
- [ ] `databricks` - Databricks parser (via AI/BI platform)

## Priority Actions

### High Priority (Required for PyPI)

1. **Add commercial API backends**
   - AWS Textract
   - Azure Document Intelligence
   - Google Document AI
   - Databricks

2. **Add Apache Tika backend**
   - Widely used open-source option
   - Java-based (different from Python options)

3. **Document configuration for commercial APIs**
   - Google: sync vs async batch processing
   - AWS: region selection, pagination
   - Azure: endpoint configuration
   - API key management (environment variables)

### Medium Priority (Nice to have)

1. **marker_ollama backend**
   - Variant of marker using Ollama
   - Lower-cost alternative to marker

2. **landing_ai backend**
   - Currently partial implementation
   - May require API access

### Low Priority (Can skip)

1. **pypdf2 backend**
   - Deprecated fork of pypdf
   - pypdf (current version) already included
   - Only needed for legacy compatibility

## Implementation Plan

### Phase 1: Commercial APIs (Critical)

```python
# Add to pdfsmith/backends/

# aws_textract_backend.py
class AWSTextractBackend(BaseBackend):
    name = "aws_textract"
    # Requires: boto3, AWS credentials
    # Config: region, max_pages

# azure_document_intelligence_backend.py
class AzureDocIntelBackend(BaseBackend):
    name = "azure_document_intelligence"
    # Requires: azure-ai-documentintelligence, credentials
    # Config: endpoint, API key

# google_document_ai_backend.py
class GoogleDocAIBackend(BaseBackend):
    name = "google_document_ai"
    # Requires: google-cloud-documentai, credentials
    # Config: project_id, location, processor_id
    # Options: sync (15 pages) vs async (unlimited)

# databricks_backend.py
class DatabricksBackend(BaseBackend):
    name = "databricks"
    # Requires: databricks-sdk or requests
    # Config: workspace URL, token
```

### Phase 2: Tika (Open-source gap)

```python
# tika_backend.py
class TikaBackend(BaseBackend):
    name = "tika"
    # Requires: tika (Python wrapper)
    # Note: Requires Java runtime
```

### Phase 3: Optional variants

- marker_ollama (if Ollama adoption grows)
- landing_ai (if API access secured)

## Testing Requirements

**Before PyPI publication**:

1. **Unit tests**: Each backend has import + parse tests
2. **Integration tests**: Test with sample PDFs for each backend
3. **Commercial API tests**: Mock tests (avoid API costs in CI)
4. **Documentation**: Configuration examples for each backend
5. **Examples**: Sample code for commercial API setup

## Configuration Documentation Needed

### AWS Textract

```python
import os
from pdfsmith import parse

# Set AWS credentials
os.environ["AWS_ACCESS_KEY_ID"] = "..."
os.environ["AWS_SECRET_ACCESS_KEY"] = "..."
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Parse
markdown = parse("document.pdf", backend="aws_textract")
```

### Google Document AI

```python
# Sync mode (up to 15 pages)
markdown = parse("small.pdf", backend="google_document_ai",
                 config={"mode": "sync"})

# Async mode (unlimited pages, via GCS)
markdown = parse("large.pdf", backend="google_document_ai",
                 config={
                     "mode": "async",
                     "gcs_bucket": "my-bucket",
                     "project_id": "my-project"
                 })
```

### Azure Document Intelligence

```python
markdown = parse("document.pdf", backend="azure_document_intelligence",
                 config={
                     "endpoint": "https://....cognitiveservices.azure.com/",
                     "api_key": os.environ["AZURE_DOC_AI_KEY"]
                 })
```

## Viability Assessment

**Can we publish to PyPI now?**
- ❌ **No** - Missing 4 critical commercial backends
- ❌ **No** - Missing configuration documentation
- ✅ **Yes** - All open-source backends implemented and tested

**What's needed for 100% ready?**
1. Implement 4 commercial backend wrappers (2-3 days work)
2. Write configuration docs (1 day)
3. Add mock tests for commercial APIs (1 day)
4. Update README with commercial backend examples (0.5 day)

**Estimated effort**: 4-5 days to publication-ready

---

*This document tracks pdfsmith integration status for pdf-bench publication.*
