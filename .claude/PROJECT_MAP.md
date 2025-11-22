# Project Map: pdf-bench

*Generated: 2025-11-22*
*Last Updated: 2025-11-22*

## Quick Overview
- **Type**: Benchmarking Suite / CLI Tool
- **Primary Language**: Python 3.10+
- **Frameworks**: Typer (CLI), Rich (output), pytest (testing)
- **Location**: `/home/stefan/applied-ai/pdf-bench`
- **License**: MIT

## Purpose

Open-source benchmarking suite for evaluating PDF-to-Markdown conversion parsers. Compares 17+ parsers (open source and commercial) against ground truth using multiple metrics.

## Directory Structure

### Core Application (`pdf_bench/`)
- `runner.py` - Main benchmark orchestration (parallel execution, checkpointing)
- `loader.py` - Document and config loading from YAML
- `report_generator.py` - Results reporting and visualization
- `metrics/` - Evaluation metrics (TEDS, ChrF++, Edit Distance, Tree Similarity)
- `systems/` - Parser adapters (17 parsers: docling, marker, pymupdf, commercial APIs)
- `utils/` - Caching, normalization, cost tracking

### Corpus (`corpus/`)
- `synthetic/` - 32 generated test documents (tables, lists, columns, mixed)
- `business/cuad/` - 75 legal contracts from CUAD dataset
- `business/invoices/` - Generated invoice documents
- `business/hr/` - HR documents (resumes, job applications)
- `business/legal/` - Legal contract templates
- `academic/omnidocbench/` - 193 documents (mixed types, mostly Chinese)
- `academic/sample/` - Sample academic papers

### Builders (`builders/`)
- Corpus generation scripts (CUAD, invoices, HR, legal, OmniDocBench)
- `generate_systematic_corpus.py` - Synthetic document generation
- `convert_omnidocbench.py` - Image to PDF conversion

### Benchmarks (`benchmarks/`)
- YAML config files defining document sets and metrics
- `full_corpus_353docs.yaml` - Complete benchmark
- `cuad_75docs.yaml` - Legal contracts only
- `omnidocbench_193docs.yaml` - OmniDocBench documents

### Results (`results/`)
- JSON benchmark results with checkpointing support
- `full_corpus_353docs.json` - Main results (~350 docs, 10 parsers)
- `comprehensive_278docs_all_parsers.json` - Multi-parser comparison

## Key Files

### Entry Points
- `pdf_bench/runner.py` - Benchmark execution engine
- `pdf_bench/loader.py` - Configuration and document loading

### Parser Systems (17 total)
**Open Source**: docling, marker, pymupdf, pymupdf4llm, pdfplumber, unstructured, kreuzberg, pdfminer, pypdf, pypdf2, pypdfium2, extractous, tika
**Commercial**: AWS Textract, Azure Document Intelligence, Google Document AI, Databricks (stubs)

### Metrics
- `metrics/teds.py` - Table Edit Distance Similarity
- `metrics/text_metrics.py` - ChrF++, Edit Similarity, CER
- `metrics/tree_edit_distance.py` - AST-based tree similarity
- `metrics/element_f1.py` - Element-level F1 scoring

## Patterns & Conventions

### Architecture
- **Parser Adapter Pattern**: All parsers inherit from `BaseParser`
- **Lazy Loading**: Parsers loaded on-demand to minimize memory
- **Checkpointing**: Results saved incrementally during long runs

### Configuration
- **YAML-based**: Benchmark configs and corpus metadata in YAML
- **Environment Variables**: API keys in `.env` (AWS, Azure, Google)

### Testing
- `tests/` - pytest-based tests organized by component
- Coverage reporting enabled via pytest-cov

### Code Style
- Ruff for linting (E, W, F, I, B, C4, UP, N rules)
- MyPy for type checking (strict mode)
- Line length: 100 characters

## Dependencies

### Core
- typer, rich - CLI and output
- beautifulsoup4, lxml - HTML/XML parsing
- pyyaml - Configuration
- python-levenshtein, sacrebleu, zss - Metrics

### Cloud APIs
- boto3 - AWS Textract
- azure-ai-documentintelligence - Azure
- google-cloud-documentai - Google

### Document Processing
- python-docx, docxtpl - DOCX generation
- datasets - HuggingFace datasets (CUAD)

## CLI Commands

```bash
# Run benchmark
pdfbench run benchmarks/full_corpus_353docs.yaml

# With specific parsers
pdfbench run config.yaml --parsers docling marker

# Generate report
pdfbench report results/benchmark.json
```

## Related Projects

- **pdfsmith**: `/home/stefan/applied-ai/pdfsmith/` - Unified PDF parsing library (extracted from this project)
- **enterprise-agents**: `/home/stefan/applied-ai/enterprise-agents/` - Uses benchmark data for content marketing

## Current State

### Completed
- 353+ documents in corpus (synthetic + real-world)
- 17 parser implementations
- 6 evaluation metrics
- Checkpointing support

### In Progress
- CUAD benchmark (started, needs restart)
- OmniDocBench benchmark (ready to run)

### Pending
- Additional corpora (financial, logistics, healthcare)
- Commercial parser testing (Databricks, Landing.AI need real implementations)
