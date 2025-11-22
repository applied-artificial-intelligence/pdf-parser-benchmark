# Benchmark Organization

PDF-Bench organizes benchmarks across multiple dimensions to provide comprehensive parser evaluation. This guide explains the structure and how to interpret results.

## Benchmark Dimensions

### 1. Document Type (OCR Requirement)

| Tier | Description | Parsers | Speed |
|------|-------------|---------|-------|
| **Tier 1: Text-based** | PDFs with embedded text (machine-readable) | All parsers | Fast |
| **Tier 2: OCR-required** | Scanned documents, images | OCR-capable only | Slow |

**Tier 1 Parsers** (all):
- docling, marker, pymupdf, pymupdf4llm, pdfplumber, pypdf, pdfminer, kreuzberg, unstructured, etc.

**Tier 2 Parsers** (OCR-capable):
- docling-ocr, marker, unstructured (hi_res), kreuzberg (OCR), commercial APIs

### 2. Document Features

Structural elements that affect parsing difficulty:

| Feature | Description | Example Corpus |
|---------|-------------|----------------|
| `tables` | Tabular data | synthetic, CUAD |
| `multi_column` | Multi-column layouts | synthetic |
| `lists` | Bulleted/numbered lists | synthetic |
| `headers` | Document structure/hierarchy | all |
| `mixed_content` | Text + tables + images | OmniDocBench |
| `equations` | Mathematical formulas | OmniDocBench |
| `handwritten` | Handwritten content | OmniDocBench |

### 3. Domain

Business context affecting document style:

| Domain | Description | Corpus |
|--------|-------------|--------|
| `legal` | Contracts, agreements | CUAD |
| `academic` | Research papers, textbooks | OmniDocBench |
| `business` | Reports, invoices | synthetic |
| `presentation` | Slides converted to PDF | OmniDocBench |
| `education` | Exam papers, textbooks | OmniDocBench |

### 4. Corpus Source

| Corpus | Documents | Type | OCR Required |
|--------|-----------|------|--------------|
| **synthetic** | 31 | Generated test cases | No |
| **CUAD** | 75 | Real legal contracts | No |
| **OmniDocBench** | 193 | Academic/mixed documents | **Yes** |

## Benchmark Configurations

### Quick Benchmarks (Development)

```yaml
# benchmarks/quick_10docs.yaml
# Fast validation, ~5 minutes
corpus_dir: ../corpus
document_filter:
  max_documents: 10
parser_config:
  parsers: [pymupdf, pdfplumber, docling]
```

### Tier 1: Text-Based Documents

```yaml
# benchmarks/tier1_text_based.yaml
# All text-based corpora, all parsers
corpus_dir: ../corpus
document_filter:
  corpora: [synthetic, business]  # Excludes OmniDocBench
parser_config:
  parsers:
    - pymupdf
    - pymupdf4llm
    - pdfplumber
    - docling  # fast mode, no OCR
    - marker
    - kreuzberg
```

### Tier 2: OCR-Required Documents

```yaml
# benchmarks/tier2_ocr_required.yaml
# OmniDocBench with OCR-capable parsers
corpus_dir: ../corpus
document_filter:
  corpora: [academic]  # OmniDocBench only
parser_config:
  parsers:
    - docling-ocr
    - marker
  parser_options:
    docling-ocr:
      num_threads: 4
      device: cuda
```

### Domain-Specific Benchmarks

```yaml
# benchmarks/domain_legal.yaml
corpus_dir: ../corpus
document_filter:
  corpora: [business]
  domains: [legal]

# benchmarks/domain_academic.yaml
corpus_dir: ../corpus
document_filter:
  domains: [academic, education]
```

### Feature-Specific Benchmarks

```yaml
# benchmarks/feature_tables.yaml
corpus_dir: ../corpus
document_filter:
  features: [tables]

# benchmarks/feature_multi_column.yaml
corpus_dir: ../corpus
document_filter:
  features: [multi_column]
```

## Results Organization

Results are organized to support multiple views:

```
results/
├── tier1/                    # Text-based documents
│   ├── synthetic.json
│   ├── cuad.json
│   └── combined.json
├── tier2/                    # OCR-required documents
│   └── omnidocbench.json
├── by_domain/
│   ├── legal.json
│   ├── academic.json
│   └── business.json
├── by_feature/
│   ├── tables.json
│   ├── multi_column.json
│   └── lists.json
└── full/                     # Complete benchmark
    └── all_corpora.json
```

## Recommended Benchmark Workflow

### Phase 1: Quick Validation (5 min)
```bash
uv run python -m pdf_bench.main run benchmarks/quick_10docs.yaml
```

### Phase 2: Tier 1 Full Run (30-60 min)
```bash
# Text-based documents, all parsers
uv run python -m pdf_bench.main run benchmarks/tier1_text_based.yaml \
  --output results/tier1/combined.json --workers 4
```

### Phase 3: Tier 2 OCR Run (4-8 hours)
```bash
# Run overnight - OCR-required documents
uv run python -m pdf_bench.main run benchmarks/tier2_ocr_required.yaml \
  --output results/tier2/omnidocbench.json --workers 1
```

### Phase 4: Analysis
```bash
# Generate reports for each dimension
uv run python -m pdf_bench.report results/tier1/combined.json --by-feature
uv run python -m pdf_bench.report results/tier1/combined.json --by-domain
uv run python -m pdf_bench.report results/tier2/omnidocbench.json
```

## Interpreting Results

### Metrics by Use Case

| Use Case | Primary Metric | Secondary |
|----------|---------------|-----------|
| RAG/Search | ChrF++, Edit Similarity | Tree Similarity |
| Data extraction | Table F1, TEDS | Element F1 |
| Document conversion | Tree Similarity | ChrF++ |
| General quality | Edit Similarity | All metrics |

### Expected Performance Ranges

| Parser | Tier 1 (text) | Tier 2 (OCR) | Best For |
|--------|---------------|--------------|----------|
| docling | 0.85-0.95 | 0.75-0.85 | General, tables |
| marker | 0.80-0.90 | 0.70-0.85 | Academic, complex |
| pymupdf4llm | 0.75-0.85 | N/A | Speed, LLM |
| pdfplumber | 0.80-0.90 | N/A | Tables |

*Scores are approximate Edit Similarity ranges*
