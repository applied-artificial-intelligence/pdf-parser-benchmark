# Document Metadata Schema

This document describes the YAML metadata schema used for documents in the PDF-Bench corpus. Each PDF in the corpus must have an associated `.yaml` metadata file with the same base filename.

## File Naming Convention

Metadata files must match their corresponding PDF files:

```
corpus/academic/
├── arxiv_1706_03762.pdf
└── arxiv_1706_03762.yaml

corpus/business/
├── govuk_env_plan_2023.pdf
└── govuk_env_plan_2023.yaml

corpus/synthetic/
├── synthetic_pandoc_001.pdf
└── synthetic_pandoc_001.yaml
```

## Schema Definition

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `doc_id` | string | Unique identifier for the document | `"arxiv_1706_03762"` |
| `source_url` | string | URL to download the original PDF (must start with http:// or https://) | `"https://arxiv.org/pdf/1706.03762.pdf"` |
| `corpus` | string | Corpus category: `"academic"`, `"business"`, or `"synthetic"` | `"academic"` |
| `domain` | string | Subcategory within corpus (see valid domains below) | `"arxiv"` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | Document title | `"Attention Is All You Need"` |
| `authors` | list[string] | List of author names | `["Ashish Vaswani", "Noam Shazeer"]` |
| `publication_date` | string | Publication date in ISO 8601 format (YYYY-MM-DD) | `"2017-06-12"` |
| `page_count` | integer | Number of pages (must be >= 1) | `15` |
| `file_size_bytes` | integer | PDF file size in bytes (must be >= 0) | `2155905` |
| `features` | list[string] | List of features present in document (see valid features below) | `["tables", "math", "figures"]` |
| `language` | string | 2-letter ISO 639-1 language code | `"en"` (default) |
| `license` | string | License information | `"CC-BY-4.0"` |
| `notes` | string | Free-form notes about the document | `"Seminal transformer paper"` |

## Valid Values

### Corpus and Domain Combinations

The `domain` field must be valid for the specified `corpus`:

**Academic Corpus**:
- `arxiv`: Papers from arXiv.org

**Business Corpus**:
- `gov-uk`: GOV.UK government publications
- `sec-edgar`: SEC EDGAR financial filings

**Synthetic Corpus**:
- `pandoc`: Documents generated via Pandoc (Markdown → PDF)
- `libreoffice`: Documents generated via LibreOffice (DOCX → PDF)

### Valid Features

Documents can be tagged with the following feature tags:

| Feature | Description |
|---------|-------------|
| `tables` | Contains data tables |
| `math` | Contains mathematical notation (LaTeX, equations) |
| `figures` | Contains images, diagrams, or charts |
| `code` | Contains code blocks or listings |
| `lists` | Contains bullet points or numbered lists |
| `footnotes` | Contains footnotes or citations |
| `multi-column` | Multi-column layout (e.g., two-column papers) |
| `headers-footers` | Page headers and/or footers |

## Example Metadata Files

### Academic Paper (arXiv)

```yaml
doc_id: arxiv_1706_03762
source_url: https://arxiv.org/pdf/1706.03762.pdf
corpus: academic
domain: arxiv
title: Attention Is All You Need
authors:
  - Ashish Vaswani
  - Noam Shazeer
  - Niki Parmar
  - Jakob Uszkoreit
  - Llion Jones
  - Aidan N. Gomez
  - Lukasz Kaiser
  - Illia Polosukhin
publication_date: '2017-06-12'
page_count: 15
file_size_bytes: 2155905
features:
  - tables
  - math
  - figures
  - lists
language: en
license: arXiv.org perpetual non-exclusive license
notes: Seminal paper introducing the Transformer architecture. Contains complex mathematical notation and architecture diagrams.
```

### Government Report (GOV.UK)

```yaml
doc_id: govuk_env_plan_2023
source_url: https://www.gov.uk/government/publications/environmental-improvement-plan
corpus: business
domain: gov-uk
title: Environmental Improvement Plan 2023
authors:
  - UK Department for Environment, Food & Rural Affairs
publication_date: '2023-01-31'
page_count: 262
file_size_bytes: 8457216
features:
  - tables
  - figures
  - lists
  - headers-footers
  - multi-column
language: en
license: Open Government Licence v3.0
notes: Complex government report with multiple tables, figures, and multi-column layouts. Good test for structure extraction.
```

### Synthetic Document (Pandoc)

```yaml
doc_id: synthetic_pandoc_001
source_url: https://github.com/pdf-bench/corpus-builders/synthetic/basic_doc.md
corpus: synthetic
domain: pandoc
title: Basic Synthetic Document with Tables and Math
publication_date: '2024-11-01'
page_count: 5
file_size_bytes: 87432
features:
  - tables
  - math
  - lists
  - code
language: en
license: CC0-1.0
notes: Synthetic document generated from Markdown using Pandoc with Eisvogel template. Ground truth is the original Markdown source. Designed to test basic structure, simple tables, and inline/display math.
```

## Validation Rules

The metadata validation enforces the following rules:

1. **Required fields** must be present and non-empty
2. **Corpus** must be one of: `academic`, `business`, `synthetic`
3. **Domain** must be valid for the specified corpus
4. **URLs** must start with `http://` or `https://`
5. **Page count** must be >= 1 (if provided)
6. **File size** must be >= 0 (if provided)
7. **Features** must be from the valid features list
8. **Language** must be a 2-letter ISO 639-1 code
9. **Publication date** must be in YYYY-MM-DD format (if provided)

## Usage Examples

### Python API

```python
from pathlib import Path
from pdf_bench.utils.metadata import DocumentMetadata, load_metadata, save_metadata

# Create metadata programmatically
metadata = DocumentMetadata(
    doc_id="test_001",
    source_url="https://example.com/doc.pdf",
    corpus="academic",
    domain="arxiv",
    title="Test Document",
    authors=["Author One", "Author Two"],
    features=["tables", "math"]
)

# Validate metadata
metadata.validate()  # Raises ValueError if invalid

# Save to YAML file
yaml_path = Path("corpus/academic/test_001.yaml")
save_metadata(metadata, yaml_path)

# Load from YAML file
loaded = load_metadata(yaml_path)
print(f"Loaded: {loaded.title}")

# Convert to/from dict
data_dict = metadata.to_dict()
reconstructed = DocumentMetadata.from_dict(data_dict)
```

### Validation Script

```python
from pathlib import Path
from pdf_bench.utils.metadata import load_metadata

def validate_corpus(corpus_dir: Path) -> None:
    """Validate all metadata files in a corpus directory."""
    for yaml_file in corpus_dir.glob("**/*.yaml"):
        try:
            metadata = load_metadata(yaml_file)
            print(f"✓ {yaml_file.name}: Valid")
        except Exception as e:
            print(f"✗ {yaml_file.name}: {e}")

# Run validation
validate_corpus(Path("corpus/academic"))
```

## Extending the Schema

### Adding New Domains

To add a new domain to an existing corpus:

1. Update `VALID_DOMAINS` in `pdf_bench/utils/metadata.py`:
   ```python
   VALID_DOMAINS = {
       "academic": ["arxiv", "new_domain"],
       # ...
   }
   ```

2. Add tests for the new domain in `tests/test_utils/test_metadata.py`

3. Update this documentation

### Adding New Features

To add a new feature tag:

1. Update `VALID_FEATURES` in `pdf_bench/utils/metadata.py`:
   ```python
   VALID_FEATURES = [
       "tables",
       "math",
       # ...
       "new_feature",
   ]
   ```

2. Add tests for the new feature

3. Update this documentation

### Adding New Corpora

To add a completely new corpus (e.g., `"legal"`, `"medical"`):

1. Update `VALID_CORPORA` in `pdf_bench/utils/metadata.py`
2. Add corresponding domains to `VALID_DOMAINS`
3. Create directory structure: `corpus/new_corpus/`
4. Add comprehensive tests
5. Update documentation and examples

## Best Practices

1. **Be Thorough**: Include as much metadata as possible, especially `title`, `authors`, and `features`
2. **Verify URLs**: Ensure `source_url` is accessible and points to the correct document
3. **License Compliance**: Always specify the license, especially for harvested documents
4. **Descriptive Notes**: Use the `notes` field to document special characteristics, known issues, or processing details
5. **Consistent Naming**: Use snake_case for `doc_id` (e.g., `arxiv_2301_12345`)
6. **Feature Tags**: Be conservative - only tag features that are significant and testable
7. **Date Format**: Always use ISO 8601 format (YYYY-MM-DD) for dates

## Error Handling

The metadata utilities provide clear error messages for common issues:

```python
# Missing required field
KeyError: "Missing required field: 'domain'"

# Invalid corpus
ValueError: "corpus must be one of ['academic', 'business', 'synthetic'], got 'invalid'"

# Invalid URL
ValueError: "source_url must start with http:// or https://, got 'ftp://example.com/doc.pdf'"

# Multiple errors
ValueError: "Metadata validation failed with 3 error(s):
  - doc_id is required and cannot be empty
  - source_url must start with http:// or https://
  - page_count must be >= 1, got 0"
```

## License Tracking

Proper license attribution is critical for corpus distribution:

### Common Licenses

| License | Description | Usage |
|---------|-------------|-------|
| `CC0-1.0` | Public domain dedication | Synthetic documents |
| `CC-BY-4.0` | Creative Commons Attribution | arXiv papers |
| `Open Government Licence v3.0` | UK government data | GOV.UK publications |
| `Public Domain` | No copyright restrictions | SEC filings, US government |
| `arXiv.org perpetual non-exclusive license` | arXiv default license | arXiv papers |

### License Compliance Checklist

- [ ] Every document has a license specified
- [ ] License allows redistribution and derivative works
- [ ] Attribution requirements are documented
- [ ] Commercial use restrictions are noted
- [ ] License text is included in DATASHEET.md

## Version History

- **v0.1** (2024-11-14): Initial schema definition
  - Required fields: doc_id, source_url, corpus, domain
  - Optional fields: title, authors, publication_date, page_count, file_size_bytes, features, language, license, notes
  - 3 corpora: academic, business, synthetic
  - 8 feature tags

## See Also

- [DATASHEET.md](../DATASHEET.md) - Full dataset documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute documents
- [README.md](../README.md) - Project overview
