# Metadata Quick Start Guide

Quick reference for working with document metadata in PDF-Bench.

## Basic Usage

### Import

```python
from pathlib import Path
from pdf_bench.utils.metadata import DocumentMetadata, load_metadata, save_metadata
```

### Create Metadata

```python
metadata = DocumentMetadata(
    doc_id="arxiv_1706_03762",
    source_url="https://arxiv.org/pdf/1706.03762.pdf",
    corpus="academic",
    domain="arxiv",
    title="Attention Is All You Need",
    authors=["Ashish Vaswani", "Noam Shazeer"],
    features=["tables", "math", "figures"]
)
```

### Validate

```python
try:
    metadata.validate()
    print("Valid!")
except ValueError as e:
    print(f"Invalid: {e}")
```

### Save to File

```python
yaml_path = Path("corpus/academic/arxiv_1706_03762.yaml")
save_metadata(metadata, yaml_path)
```

### Load from File

```python
yaml_path = Path("corpus/academic/arxiv_1706_03762.yaml")
metadata = load_metadata(yaml_path)
print(f"Loaded: {metadata.title}")
```

## Required Fields

| Field | Values |
|-------|--------|
| `doc_id` | Any non-empty string |
| `source_url` | URL starting with http:// or https:// |
| `corpus` | `"academic"`, `"business"`, `"synthetic"` |
| `domain` | See corpus/domain table below |

## Corpus/Domain Combinations

| Corpus | Valid Domains |
|--------|---------------|
| `academic` | `arxiv` |
| `business` | `gov-uk`, `sec-edgar` |
| `synthetic` | `pandoc`, `libreoffice` |

## Optional Fields Reference

```python
title: str | None = None                  # Document title
authors: list[str] = []                  # List of authors
publication_date: str | None = None     # YYYY-MM-DD format
page_count: int | None = None           # Number of pages (>= 1)
file_size_bytes: int | None = None      # File size (>= 0)
features: list[str] = []                 # Feature tags (see below)
language: str = "en"                     # ISO 639-1 code
license: str | None = None               # License string
notes: str | None = None                 # Free-form notes
```

## Valid Feature Tags

- `tables` - Data tables
- `math` - Mathematical notation
- `figures` - Images/diagrams
- `code` - Code blocks
- `lists` - Bullet/numbered lists
- `footnotes` - Footnotes/citations
- `multi-column` - Multi-column layout
- `headers-footers` - Page headers/footers

## Common Patterns

### Validate All Metadata in Directory

```python
from pathlib import Path
from pdf_bench.utils.metadata import load_metadata

corpus_dir = Path("corpus/academic")
for yaml_file in corpus_dir.glob("*.yaml"):
    try:
        metadata = load_metadata(yaml_file)
        print(f"✓ {yaml_file.name}")
    except Exception as e:
        print(f"✗ {yaml_file.name}: {e}")
```

### Convert to/from Dictionary

```python
# To dict
data = metadata.to_dict()

# From dict
metadata = DocumentMetadata.from_dict(data)
```

### Bulk Create from CSV

```python
import csv
from pathlib import Path
from pdf_bench.utils.metadata import DocumentMetadata, save_metadata

with open("documents.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        metadata = DocumentMetadata(
            doc_id=row["id"],
            source_url=row["url"],
            corpus=row["corpus"],
            domain=row["domain"],
            title=row.get("title"),
            page_count=int(row["pages"]) if row.get("pages") else None
        )
        metadata.validate()
        save_metadata(metadata, Path(f"corpus/{metadata.corpus}/{metadata.doc_id}.yaml"))
```

## Common Errors

### Missing Required Field

```python
KeyError: "Missing required field: 'domain'"
```

**Fix**: Ensure all required fields are provided.

### Invalid Corpus

```python
ValueError: "corpus must be one of ['academic', 'business', 'synthetic'], got 'papers'"
```

**Fix**: Use one of the valid corpus values.

### Domain Mismatch

```python
ValueError: "domain 'gov-uk' is not valid for corpus 'academic'. Valid domains: ['arxiv']"
```

**Fix**: Use correct domain for the corpus (see combinations table above).

### Invalid URL

```python
ValueError: "source_url must start with http:// or https://, got 'ftp://example.com/doc.pdf'"
```

**Fix**: Use http:// or https:// URLs only.

### Invalid Date Format

```python
ValueError: "publication_date must be in YYYY-MM-DD format, got '2023/01/15'"
```

**Fix**: Use ISO 8601 format (YYYY-MM-DD).

### Unknown Feature

```python
ValueError: "Unknown feature 'images'. Valid features: ['tables', 'math', ...]"
```

**Fix**: Use `figures` instead of `images` (see valid features list).

## Tips

1. **Always validate** before saving to catch errors early
2. **Use Path objects** for file paths, not strings
3. **Check example files** in `corpus/` for reference
4. **Read full docs** in `docs/METADATA_SCHEMA.md` for details
5. **Test validation** with invalid data to understand error messages

## See Also

- [METADATA_SCHEMA.md](METADATA_SCHEMA.md) - Complete schema documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute documents
- [API Documentation](../README.md#api-documentation) - Full API reference
