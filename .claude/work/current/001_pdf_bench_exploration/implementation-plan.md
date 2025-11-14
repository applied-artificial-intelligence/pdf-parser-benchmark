# PDF-Bench v0.1 MVP - Implementation Plan

**Project**: PDF-Bench - Open-Source Benchmarking Suite for PDF-to-Markdown Conversion
**Version**: v0.1 MVP
**Created**: 2025-11-14
**Total Estimated Effort**: ~255 hours (6-7 weeks full-time)
**Total Tasks**: 85 tasks across 11 phases

---

## Executive Summary

### Project Scope

**PDF-Bench** is a production-grade, open-source benchmarking suite for evaluating PDF-to-Markdown conversion systems. The v0.1 MVP will deliver:

- **~450 document corpus** across 3 tracks (academic, business/government, synthetic)
- **7+ parser adapters** (4 open-source, 3 commercial APIs)
- **Multi-layered evaluation metrics** (text, structure, tables, math, performance)
- **CLI and Python API** for running benchmarks
- **HTML report generation** with leaderboards and breakdowns
- **Complete documentation** (DATASHEET.md, README, CONTRIBUTING)

### Strategic Value

- **Thought Leadership**: Establishes firm as objective authority in document AI space
- **Client Tool**: Enables data-driven parser selection for projects
- **Community Asset**: Easy to extend (parsers, metrics, documents)
- **Content Marketing**: Platform for blog posts, leaderboards, technical analysis

### Success Criteria (MVP v0.1)

- ✅ ~450 documents with validated ground truth
- ✅ 7+ parser adapters operational
- ✅ 5 metric layers implemented and tested
- ✅ CLI for benchmark execution + HTML report generation
- ✅ DATASHEET.md with full data provenance
- ✅ PyPI package published
- ✅ Open-source repository public

### Timeline and Milestones

| Milestone | Phase | Tasks | Est. Hours | Target Week |
|-----------|-------|-------|------------|-------------|
| **M1**: Foundation Complete | Phase 1 | TASK-001 to TASK-010 | 30h | Week 1-2 |
| **M2**: Synthetic Corpus Ready | Phase 2 | TASK-011 to TASK-018 | 24h | Week 2-3 |
| **M3**: Metrics Suite Complete | Phase 3 | TASK-019 to TASK-028 | 30h | Week 3-4 |
| **M4**: Parsers Operational | Phase 4 | TASK-029 to TASK-036 | 24h | Week 4 |
| **M5**: E2E Benchmarking | Phase 5 | TASK-037 to TASK-046 | 30h | Week 4-5 |
| **M6**: Business Corpus Built | Phases 6-7 | TASK-047 to TASK-058 | 36h | Week 5-6 |
| **M7**: Academic Corpus Built | Phase 8 | TASK-059 to TASK-066 | 24h | Week 6-7 |
| **M8**: Commercial APIs Ready | Phase 9 | TASK-067 to TASK-072 | 18h | Week 7 |
| **M9**: Documentation Complete | Phase 10 | TASK-073 to TASK-080 | 24h | Week 7-8 |
| **M10**: v0.1 Launch | Phase 11 | TASK-081 to TASK-085 | 15h | Week 8 |

---

## Technical Architecture

### Technology Stack

**Core Dependencies** (using `uv` for package management):
```toml
[project]
name = "pdf-bench"
version = "0.1.0"
description = "Open-source benchmarking suite for PDF-to-Markdown conversion"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.9.0",           # CLI framework
    "rich>=13.0.0",            # Terminal output
    "beautifulsoup4>=4.12.0",  # HTML parsing
    "lxml>=4.9.0",             # XML processing
    "python-docx>=1.0.0",      # DOCX manipulation
    "python-docx-template>=0.16.0",
    "mistune>=3.0.0",          # Markdown AST parser
    "pyyaml>=6.0",             # Metadata
    "python-levenshtein>=0.21.0",  # Edit distance
    "sacrebleu>=2.3.0",        # chrF++ metric
    "zss>=1.2.0",              # Tree-edit distance
]

[project.optional-dependencies]
metrics = [
    "table-recognition-metric>=1.0.0",  # TEDS
]
parsers = [
    "pymupdf>=1.23.0",
    "unstructured>=0.10.0",
]
commercial = [
    "boto3>=1.28.0",           # AWS Textract
    "azure-ai-formrecognizer>=3.3.0",  # Azure DI
]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.6.0",
]

[project.scripts]
pdfbench = "pdf_bench.main:app"
```

**External Tools** (document in README):
- LaTeXML (`apt-get install latexml`)
- Pandoc (`apt-get install pandoc`)
- LibreOffice (`apt-get install libreoffice` - headless DOCX→PDF)

### Directory Structure

```
/pdf-bench
├── pdf_bench/              # Core Python library
│   ├── __init__.py
│   ├── main.py            # CLI entrypoint
│   ├── core.py            # BenchmarkRunner
│   ├── systems/           # Parser adapters
│   │   ├── base_parser.py
│   │   ├── marker.py
│   │   ├── nougat.py
│   │   ├── unstructured.py
│   │   ├── pymupdf.py
│   │   ├── aws_textract.py
│   │   └── azure_di.py
│   ├── metrics/           # Metric implementations
│   │   ├── text_metrics.py
│   │   ├── struct_metrics.py
│   │   ├── table_metrics.py
│   │   └── math_metrics.py
│   ├── utils/             # Utilities
│   │   ├── normalization.py
│   │   ├── caching.py
│   │   └── validation.py
│   └── report.py          # HTML report generation
├── builders/              # Corpus builder scripts
│   ├── download_corpus.py
│   ├── build_academic.py
│   ├── build_business.py
│   └── build_synthetic.py
├── corpus/                # Corpus metadata
│   ├── academic/
│   ├── business/
│   └── synthetic/
├── ground_truth/          # Canonical Markdown GT
│   ├── academic/
│   ├── business/
│   └── synthetic/
├── benchmarks/            # Benchmark configs
│   ├── mvp_all.yaml
│   ├── academic_v0.yaml
│   └── business_v0.yaml
├── reports/               # Generated reports (gitignored)
├── .cache/                # Cached parser outputs (gitignored)
├── tests/                 # Test suite
├── pyproject.toml
├── README.md
├── DATASHEET.md
├── CONTRIBUTING.md
└── LICENSE
```

### Key Abstractions

#### 1. BaseParser Interface

```python
from abc import ABC, abstractmethod
from pathlib import Path

class BaseParser(ABC):
    """Abstract base class for all PDF parsers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return parser name and version (e.g., 'marker-v0.2.0')."""
        pass

    @abstractmethod
    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """
        Parse PDF and save Markdown output.

        Args:
            pdf_path: Path to input PDF
            output_dir: Directory to save output

        Returns:
            Path to generated Markdown file
        """
        pass
```

#### 2. Metric Framework

**Multi-layered evaluation**:
- **Text Level**: Normalized Edit Distance, chrF++
- **Structure Level**: AST Tree-Edit Distance, Element F1
- **Table Level**: TEDS, Cell Content F1
- **Math Level**: Normalized LaTeX matching, BLEU
- **Performance Level**: Latency, throughput, cost

#### 3. Caching System

**Hash-based caching**:
- Cache key: `sha256(parser_name + parser_version + pdf_hash + config)`
- Storage: `.cache/{parser_name}/{hash[:8]}/{doc_id}.md`
- Prevents re-running expensive API calls
- Automatic cache invalidation on version changes

#### 4. Ground Truth Schema

**Per-document metadata** (YAML):
```yaml
doc_id: "gov_uk_env_plan_2023"
source_url: "https://www.gov.uk/..."
pdf_url: "https://assets.publishing..."
pdf_hash_sha256: "<sha256>"
ground_truth_file: "gov_uk_report_001.md"
license: "Open Government Licence v3.0"
source: "GOV.UK"
properties:
  category: "business_harvested"
  subcategory: "government_report"
  language: "en"
  layout: "mixed"
  page_count: 262
tags:
  - "has_complex_tables"
  - "has_figures"
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2) - 10 Tasks, ~30 Hours

**Goal**: Establish project infrastructure and core abstractions

#### TASK-001: Initialize Project with uv
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: []
- **Acceptance Criteria**:
  - `pyproject.toml` created with dependencies (PEP 621 format)
  - `uv.lock` generated
  - Virtual environment created with `uv venv`
  - Dependencies installed successfully with `uv pip install`
  - `uv` project structure validated
- **Agent Recommendation**: None

#### TASK-002: Create Directory Structure
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-001]
- **Acceptance Criteria**:
  - All directories from architecture created
  - `.gitignore` configured (excludes `.cache/`, `reports/`, `*.pyc`)
  - README skeleton created
- **Agent Recommendation**: `/agent auditor` for structure validation

#### TASK-003: Configure Development Tools
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-001]
- **Acceptance Criteria**:
  - `ruff` configured for linting
  - `mypy` configured for type checking
  - `pytest` configured with coverage
  - Pre-commit hooks set up (optional)
- **Agent Recommendation**: None

#### TASK-004: Define BaseParser Abstract Class
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-002]
- **Acceptance Criteria**:
  - `pdf_bench/systems/base_parser.py` created
  - Abstract methods defined (`name`, `parse`)
  - Type hints complete
  - Docstrings written
  - Unit tests for interface validation
- **Agent Recommendation**: `/agent architect` for interface design review

#### TASK-005: Implement Caching System
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-002]
- **Acceptance Criteria**:
  - `pdf_bench/utils/caching.py` created
  - Hash-based key generation
  - Disk-backed storage (`.cache/`)
  - Cache hit/miss tracking
  - Unit tests with mock filesystem
- **Agent Recommendation**: None

#### TASK-006: Implement Document Metadata Schema
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-002]
- **Acceptance Criteria**:
  - YAML schema defined
  - Validation function created
  - Load/save utilities
  - Example metadata files
  - Unit tests for validation
- **Agent Recommendation**: None

#### TASK-007: Implement Text Normalization Utilities
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-002]
- **Acceptance Criteria**:
  - `pdf_bench/utils/normalization.py` created
  - Unicode NFC normalization
  - Whitespace collapsing
  - Smart quote normalization
  - Unit tests with edge cases
- **Agent Recommendation**: None

#### TASK-008: Implement PyMuPDFParser (Baseline)
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-004, TASK-005]
- **Acceptance Criteria**:
  - `pdf_bench/systems/pymupdf.py` created
  - Implements BaseParser interface
  - Simple text extraction (no structure)
  - Cache integration
  - Integration test with sample PDF
- **Agent Recommendation**: None

#### TASK-009: Implement Normalized Edit Distance Metric
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-007]
- **Acceptance Criteria**:
  - `pdf_bench/metrics/text_metrics.py` created
  - Levenshtein distance calculation
  - Normalization to 0-1 score
  - Handles empty strings
  - Unit tests with known distances
- **Agent Recommendation**: None

#### TASK-010: Create Basic Test Infrastructure
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-003, TASK-008, TASK-009]
- **Acceptance Criteria**:
  - `tests/` directory structure created
  - Fixtures for sample PDF + GT
  - Test utilities (comparison helpers)
  - CI configuration (GitHub Actions skeleton)
  - All existing tests passing
- **Agent Recommendation**: `/agent test-engineer` for test strategy

**Phase 1 Quality Gate**:
- ✅ Can parse a PDF with PyMuPDF
- ✅ Can compute normalized edit distance
- ✅ Result is cached correctly
- ✅ All tests passing

---

### Phase 2: Synthetic Corpus Builder (Week 2-3) - 8 Tasks, ~24 Hours

**Goal**: Create reproducible ground truth documents

#### TASK-011: Create Markdown Test Documents
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-002]
- **Acceptance Criteria**:
  - 5 Markdown files created with increasing complexity:
    1. Basic (text + headings)
    2. Lists (ordered, unordered, nested)
    3. Simple tables (GFM)
    4. Math (inline + display)
    5. Complex (tables with HTML, footnotes)
  - Saved in `corpus/synthetic/`
  - Corresponding YAML metadata created
- **Agent Recommendation**: None

#### TASK-012: Implement Pandoc Wrapper for MD→PDF
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-011]
- **Acceptance Criteria**:
  - `builders/build_synthetic.py` created
  - Pandoc subprocess integration
  - Eisvogel template configuration
  - PDF hash verification
  - Error handling for Pandoc failures
- **Agent Recommendation**: None

#### TASK-013: Generate PDF from Markdown Test Docs
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-012]
- **Acceptance Criteria**:
  - All 5 Markdown files converted to PDF
  - PDFs saved with SHA256 hashes
  - Visual inspection confirms quality
  - Metadata updated with pdf_hash
- **Agent Recommendation**: None

#### TASK-014: Design DOCX Templates
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 3
- **Dependencies**: [TASK-002]
- **Acceptance Criteria**:
  - 3 DOCX templates created:
    1. Simple report
    2. Table-heavy document
    3. Multi-column layout
  - Templates use Jinja2 syntax for variables
  - Saved in `corpus/synthetic/templates/`
- **Agent Recommendation**: None

#### TASK-015: Implement DOCX→PDF Pipeline
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 4
- **Dependencies**: [TASK-014]
- **Acceptance Criteria**:
  - `python-docx-template` integration
  - LibreOffice headless conversion
  - Ground truth extraction from DOCX structure
  - PDF hash verification
  - Error handling for conversion failures
- **Agent Recommendation**: None

#### TASK-016: Generate Synthetic DOCX Documents
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 3
- **Dependencies**: [TASK-015]
- **Acceptance Criteria**:
  - 3 DOCX documents generated from templates
  - Converted to PDF successfully
  - Ground truth Markdown created
  - Metadata YAML files created
  - Visual inspection confirms quality
- **Agent Recommendation**: None

#### TASK-017: Implement Ground Truth Validation Script
- **Type**: testing
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-006, TASK-013, TASK-016]
- **Acceptance Criteria**:
  - Validation script checks:
    - YAML schema compliance
    - PDF file existence
    - Hash verification
    - GT file existence
    - Markdown syntax validity
  - Generates validation report
  - Fails loudly on errors
- **Agent Recommendation**: None

#### TASK-018: Manual Review and Documentation
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-017]
- **Acceptance Criteria**:
  - All 8 synthetic documents manually reviewed
  - Review checklist completed:
    - PDF renders correctly
    - GT accurately represents PDF content
    - Metadata is complete
  - Corpus builder usage documented in README
  - Known limitations documented
- **Agent Recommendation**: None

**Phase 2 Quality Gate**:
- ✅ 8 synthetic documents with validated GT
- ✅ Validation script confirms corpus integrity
- ✅ Manual review confirms quality

---

### Phase 3: Advanced Metrics (Week 3-4) - 10 Tasks, ~30 Hours

**Goal**: Implement multi-layered evaluation metrics

#### TASK-019: Implement Markdown AST Parser
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-002]
- **Acceptance Criteria**:
  - `pdf_bench/metrics/struct_metrics.py` created
  - mistune integration for AST generation
  - AST node type extraction
  - Handles malformed Markdown gracefully
  - Unit tests with sample Markdown
- **Agent Recommendation**: None

#### TASK-020: Implement AST Tree-Edit Distance
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-019]
- **Acceptance Criteria**:
  - zss library integration
  - AST-to-tree conversion
  - Tree-edit distance calculation
  - Normalization to 0-1 score
  - Unit tests with known tree pairs
- **Agent Recommendation**: `/agent architect` for algorithm review

#### TASK-021: Implement Element F1 Score
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-019]
- **Acceptance Criteria**:
  - Node type counting (H1, H2, List, Table, etc.)
  - Precision/Recall/F1 calculation
  - Per-element-type breakdown
  - Handles empty documents
  - Unit tests with varied documents
- **Agent Recommendation**: None

#### TASK-022: Implement HTML Table Normalization
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-007]
- **Acceptance Criteria**:
  - Lowercase tags and attributes
  - Sort attributes alphabetically
  - Normalize whitespace inside tags
  - Extract to canonical 2D array
  - Unit tests with complex tables
- **Agent Recommendation**: None

#### TASK-023: Integrate TEDS Metric
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-022]
- **Acceptance Criteria**:
  - `table-recognition-metric` library integrated
  - Wrapper function in `table_metrics.py`
  - HTML table comparison
  - Score normalization
  - Integration tests with table fixtures
- **Agent Recommendation**: None

#### TASK-024: Implement GFM Table Parser
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 3
- **Dependencies**: [TASK-019]
- **Acceptance Criteria**:
  - GFM table syntax parsing
  - Conversion to 2D array
  - Handles alignment markers
  - Malformed table handling
  - Unit tests with varied GFM tables
- **Agent Recommendation**: None

#### TASK-025: Implement Cell Content F1
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 2
- **Dependencies**: [TASK-024]
- **Acceptance Criteria**:
  - Cell-by-cell text comparison
  - Precision/Recall/F1 calculation
  - Handles mismatched table dimensions
  - Unit tests
- **Agent Recommendation**: None

#### TASK-026: Implement LaTeX Normalization
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-007]
- **Acceptance Criteria**:
  - Whitespace collapsing
  - Remove `\left`, `\right`
  - Remove redundant grouping `{{a}}` → `{a}`
  - Handles inline and display math
  - Unit tests with complex equations
- **Agent Recommendation**: None

#### TASK-027: Implement LaTeX String Matching
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-026]
- **Acceptance Criteria**:
  - Extract LaTeX from Markdown
  - Normalize both GT and prediction
  - Exact string match
  - F1 score calculation
  - Unit tests with math-heavy documents
- **Agent Recommendation**: None

#### TASK-028: Implement chrF++ Metric
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 2
- **Dependencies**: [TASK-007]
- **Acceptance Criteria**:
  - sacrebleu library integration
  - Wrapper in `text_metrics.py`
  - Handles empty strings
  - Unit tests
- **Agent Recommendation**: None

**Phase 3 Quality Gate**:
- ✅ All metric layers implemented
- ✅ Unit tests passing for each metric
- ✅ Can evaluate synthetic corpus with all metrics
- ✅ Results are sensible (e.g., identical docs score ~1.0)

---

### Phase 4: Open-Source Parser Adapters (Week 4) - 8 Tasks, ~24 Hours

**Goal**: Implement adapters for open-source parsers

#### TASK-029: Install and Test Marker Locally
- **Type**: integration
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-001]
- **Acceptance Criteria**:
  - Marker installed from GitHub
  - Can run `marker_single` CLI
  - Test on sample PDF
  - Output quality inspected
- **Agent Recommendation**: None

#### TASK-030: Implement MarkerParser Adapter
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-029, TASK-004, TASK-005]
- **Acceptance Criteria**:
  - `pdf_bench/systems/marker.py` created
  - Implements BaseParser interface
  - Subprocess integration with `marker_single`
  - Output format handling
  - Cache integration
  - Error handling
  - Integration test
- **Agent Recommendation**: None

#### TASK-031: Install and Test Nougat Locally
- **Type**: integration
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-001]
- **Acceptance Criteria**:
  - Nougat installed from GitHub
  - Model downloaded
  - Can run Nougat CLI
  - Test on academic PDF
  - LaTeX output inspected
- **Agent Recommendation**: None

#### TASK-032: Implement NougatParser Adapter
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-031, TASK-004, TASK-005]
- **Acceptance Criteria**:
  - `pdf_bench/systems/nougat.py` created
  - Implements BaseParser interface
  - Subprocess integration
  - LaTeX-to-Markdown conversion
  - Cache integration
  - Integration test
- **Agent Recommendation**: None

#### TASK-033: Install and Test Unstructured Library
- **Type**: integration
- **Priority**: medium
- **Estimated Hours**: 2
- **Dependencies**: [TASK-001]
- **Acceptance Criteria**:
  - `unstructured` library installed
  - API exploration completed
  - Test on sample PDF
  - Markdown output inspected
- **Agent Recommendation**: None

#### TASK-034: Implement UnstructuredParser Adapter
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 4
- **Dependencies**: [TASK-033, TASK-004, TASK-005]
- **Acceptance Criteria**:
  - `pdf_bench/systems/unstructured.py` created
  - Implements BaseParser interface
  - Configure for Markdown output
  - Cache integration
  - Integration test
- **Agent Recommendation**: None

#### TASK-035: Create Parser Adapter Test Suite
- **Type**: testing
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-008, TASK-030, TASK-032, TASK-034]
- **Acceptance Criteria**:
  - Integration tests for all 4 parsers
  - Test on same synthetic corpus
  - Verify cache behavior
  - Error handling tested
  - Performance baseline captured
- **Agent Recommendation**: `/agent test-engineer` for test coverage

#### TASK-036: Document Parser Installation and Usage
- **Type**: documentation
- **Priority**: medium
- **Estimated Hours**: 3
- **Dependencies**: [TASK-035]
- **Acceptance Criteria**:
  - README updated with installation instructions
  - Per-parser setup documented
  - Known limitations documented
  - Example usage provided
- **Agent Recommendation**: None

**Phase 4 Quality Gate**:
- ✅ 4 parsers operational (PyMuPDF, Marker, Nougat, Unstructured)
- ✅ Can benchmark all 4 on synthetic corpus
- ✅ Cache system working correctly
- ✅ Integration tests passing

---

### Phase 5: Benchmark Runner & Reporting (Week 4-5) - 10 Tasks, ~30 Hours

**Goal**: Implement end-to-end benchmarking infrastructure

#### TASK-037: Design Benchmark Configuration Schema
- **Type**: foundation
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-006]
- **Acceptance Criteria**:
  - YAML schema defined for benchmarks
  - Includes: document filters, parser selection, metric config
  - Example configs created (`benchmarks/mvp_all.yaml`)
  - Validation function
- **Agent Recommendation**: `/agent architect` for schema design

#### TASK-038: Implement Config Loader
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-037]
- **Acceptance Criteria**:
  - Load YAML config
  - Validate schema
  - Resolve document paths
  - Load parser classes
  - Unit tests
- **Agent Recommendation**: None

#### TASK-039: Implement BenchmarkRunner Core
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-038, TASK-009, TASK-020]
- **Acceptance Criteria**:
  - `pdf_bench/core.py` created
  - BenchmarkRunner class
  - Task orchestration (parser × document)
  - Metric computation per result
  - Error handling and logging
  - Unit tests with mocks
- **Agent Recommendation**: `/agent architect` for orchestration design

#### TASK-040: Implement Parallel Execution
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 4
- **Dependencies**: [TASK-039]
- **Acceptance Criteria**:
  - Multiprocessing integration
  - Configurable worker count
  - Progress tracking with Rich
  - Proper error propagation
  - Unit tests
- **Agent Recommendation**: None

#### TASK-041: Implement Result Persistence
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-039]
- **Acceptance Criteria**:
  - Save results to JSON
  - Schema: per-document, per-parser, per-metric scores
  - Include metadata (timestamps, versions)
  - Load results from JSON
  - Unit tests
- **Agent Recommendation**: None

#### TASK-042: Implement CLI with Typer
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-038, TASK-039]
- **Acceptance Criteria**:
  - `pdf_bench/main.py` created
  - Commands: `run`, `list`, `report`
  - `pdfbench run --config <yaml>` works
  - `pdfbench list systems` shows parsers
  - Progress bar during execution
  - Error messages are clear
- **Agent Recommendation**: None

#### TASK-043: Design HTML Report Template
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-041]
- **Acceptance Criteria**:
  - Jinja2 template created
  - Sections: Leaderboard, metric breakdown, category breakdown
  - Clean, professional CSS
  - Mobile-responsive
  - Chart placeholders (optional for v0.1)
- **Agent Recommendation**: None

#### TASK-044: Implement Report Generation
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-043]
- **Acceptance Criteria**:
  - `pdf_bench/report.py` created
  - Load results JSON
  - Calculate aggregate scores
  - Render Jinja2 template
  - Save HTML report
  - Integration test
- **Agent Recommendation**: None

#### TASK-045: Create Example Benchmark Configs
- **Type**: documentation
- **Priority**: medium
- **Estimated Hours**: 2
- **Dependencies**: [TASK-037]
- **Acceptance Criteria**:
  - `benchmarks/mvp_all.yaml` (all docs, all parsers)
  - `benchmarks/quick_test.yaml` (10 docs, 2 parsers)
  - `benchmarks/academic_only.yaml`
  - `benchmarks/business_only.yaml`
- **Agent Recommendation**: None

#### TASK-046: End-to-End Integration Test
- **Type**: testing
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-042, TASK-044]
- **Acceptance Criteria**:
  - Run full benchmark on synthetic corpus
  - All 4 parsers tested
  - All metrics computed
  - HTML report generated
  - Manual review of report quality
  - CI integration
- **Agent Recommendation**: `/agent test-engineer` for E2E testing

**Phase 5 Quality Gate**:
- ✅ Can run `pdfbench run --config benchmarks/quick_test.yaml`
- ✅ HTML report generated successfully
- ✅ Report includes leaderboard and metric breakdown
- ✅ E2E test passes in CI

---

### Phase 6: Business Corpus - GOV.UK Track (Week 5-6) - 6 Tasks, ~18 Hours

**Goal**: Build business document corpus from GOV.UK

#### TASK-047: Identify GOV.UK Target Documents
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: []
- **Acceptance Criteria**:
  - 30 GOV.UK publications identified
  - Varied topics (environment, economy, health, etc.)
  - Varied complexity (simple reports to complex multi-part)
  - Both HTML and PDF URLs confirmed accessible
  - OGL v3.0 license confirmed
  - List saved in `corpus/business/gov_uk_targets.yaml`
- **Agent Recommendation**: None

#### TASK-048: Implement GOV.UK HTML Scraper
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-047]
- **Acceptance Criteria**:
  - BeautifulSoup integration
  - Download HTML content
  - Strip navigation, headers, footers
  - Extract main content area
  - Retry logic for network errors
  - Unit tests with mock HTML
- **Agent Recommendation**: None

#### TASK-049: Implement HTML→Markdown Converter
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-048]
- **Acceptance Criteria**:
  - Heading extraction (h1→#, h2→##, etc.)
  - Paragraph extraction
  - List extraction (nested)
  - Table conversion (simple→GFM, complex→HTML)
  - Figure/image handling
  - Applies normalization rules
  - Unit tests
- **Agent Recommendation**: None

#### TASK-050: Implement GOV.UK PDF Downloader
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 2
- **Dependencies**: [TASK-047]
- **Acceptance Criteria**:
  - Download PDFs from URLs
  - Verify with SHA256 hash
  - Retry logic
  - Save to corpus directory
  - Unit tests with mock downloads
- **Agent Recommendation**: None

#### TASK-051: Build GOV.UK Corpus
- **Type**: integration
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-049, TASK-050]
- **Acceptance Criteria**:
  - 20-30 GOV.UK documents processed
  - HTML→Markdown GT generated
  - PDFs downloaded
  - Metadata YAML files created (OGL v3.0 license)
  - Validation script confirms integrity
- **Agent Recommendation**: None

#### TASK-052: GOV.UK Corpus Quality Review
- **Type**: testing
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-051]
- **Acceptance Criteria**:
  - Manual review of 10 documents
  - GT accuracy spot-checked
  - Common failure modes documented
  - Known limitations documented
  - Refinements applied if needed
- **Agent Recommendation**: None

**Phase 6 Milestone**:
- ✅ 20-30 GOV.UK documents in corpus
- ✅ Validation confirms quality
- ✅ Can benchmark parsers on GOV.UK track

---

### Phase 7: Business Corpus - SEC EDGAR Track (Week 6) - 6 Tasks, ~18 Hours

**Goal**: Build financial document corpus from SEC filings

#### TASK-053: Identify SEC EDGAR Target Filings
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: []
- **Acceptance Criteria**:
  - 20 target 10-K/10-Q filings identified
  - Varied industries (tech, finance, manufacturing, etc.)
  - CIK numbers and filing dates documented
  - Both HTML and PDF URLs confirmed
  - Public domain status confirmed
  - List saved in `corpus/business/sec_targets.yaml`
- **Agent Recommendation**: None

#### TASK-054: Implement SEC EDGAR API Client
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-053]
- **Acceptance Criteria**:
  - Fetch filing metadata via SEC API
  - Download HTML/XBRL source
  - Download PDF version
  - Rate limiting (SEC requires user-agent)
  - Error handling
  - Unit tests with mock API
- **Agent Recommendation**: None

#### TASK-055: Implement Financial Table Extraction
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-054]
- **Acceptance Criteria**:
  - Parse HTML/XBRL tables
  - Handle nested tables
  - Extract multi-level headers
  - Convert to Markdown (GFM or HTML)
  - Apply normalization
  - Unit tests with complex financial tables
- **Agent Recommendation**: None

#### TASK-056: Implement SEC→Markdown Converter
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-055]
- **Acceptance Criteria**:
  - Full document HTML→Markdown
  - Focus on table accuracy
  - Handle SEC-specific formatting
  - Unit tests
- **Agent Recommendation**: None

#### TASK-057: Build SEC EDGAR Corpus
- **Type**: integration
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-056]
- **Acceptance Criteria**:
  - 10-20 SEC filings processed
  - HTML→Markdown GT generated
  - PDFs downloaded
  - Metadata YAML files created (public domain)
  - Validation confirms integrity
- **Agent Recommendation**: None

#### TASK-058: SEC Corpus Quality Review
- **Type**: testing
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-057]
- **Acceptance Criteria**:
  - Manual review of 5 filings
  - Table extraction quality verified
  - TEDS metric tested on SEC tables
  - Known limitations documented
- **Agent Recommendation**: None

**Phase 7 Milestone**:
- ✅ 10-20 SEC filings in corpus
- ✅ Complex financial tables extracted
- ✅ Can evaluate table metrics on SEC track

---

### Phase 8: Academic Corpus - arXiv Track (Week 6-7) - 8 Tasks, ~24 Hours

**Goal**: Build academic document corpus from arXiv

#### TASK-059: Identify arXiv Target Papers
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: []
- **Acceptance Criteria**:
  - 30-50 arXiv papers identified
  - Categories: cs.CL, cs.CV, math.AP, econ.EM
  - Varied complexity (math-heavy, table-heavy, multi-column)
  - arXiv IDs documented
  - Licenses verified (CC-BY, arXiv license)
  - List saved in `corpus/academic/arxiv_targets.yaml`
- **Agent Recommendation**: None

#### TASK-060: Implement arXiv API Client
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-059]
- **Acceptance Criteria**:
  - Fetch paper metadata via arXiv API
  - Download source .tar.gz
  - Download PDF
  - Rate limiting
  - Error handling
  - Unit tests with mock API
- **Agent Recommendation**: None

#### TASK-061: Implement LaTeX Source Extractor
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-060]
- **Acceptance Criteria**:
  - Extract .tar.gz
  - Identify main .tex file (heuristics)
  - Handle multi-file LaTeX projects
  - Copy dependencies (images, .bib, etc.)
  - Unit tests with sample tarballs
- **Agent Recommendation**: None

#### TASK-062: Integrate LaTeXML
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-061]
- **Acceptance Criteria**:
  - Subprocess wrapper for LaTeXML
  - Convert .tex to HTML/XML
  - Error handling for LaTeXML failures
  - Timeout for long conversions
  - Unit tests with sample .tex
- **Agent Recommendation**: None

#### TASK-063: Implement LaTeXML→Markdown Converter
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-062]
- **Acceptance Criteria**:
  - Parse LaTeXML HTML/XML output
  - Extract headings, paragraphs, lists
  - Extract math (preserve LaTeX)
  - Extract tables
  - Convert to CMD specification
  - Unit tests
- **Agent Recommendation**: None

#### TASK-064: Implement Pandoc Fallback
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 3
- **Dependencies**: [TASK-062]
- **Acceptance Criteria**:
  - If LaTeXML fails, try Pandoc
  - Subprocess wrapper
  - Same output format as LaTeXML converter
  - Unit tests
- **Agent Recommendation**: None

#### TASK-065: Build arXiv Corpus
- **Type**: integration
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-063, TASK-064]
- **Acceptance Criteria**:
  - 30-50 arXiv papers processed
  - LaTeX→Markdown GT generated
  - 80%+ success rate (some failures acceptable)
  - PDFs downloaded
  - Metadata YAML files created
  - Validation confirms integrity
- **Agent Recommendation**: None

#### TASK-066: arXiv Corpus Quality Review
- **Type**: testing
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-065]
- **Acceptance Criteria**:
  - Manual review of 10 papers
  - Math extraction quality verified
  - Table extraction quality verified
  - Common failure modes documented (e.g., custom macros)
  - Success rate calculated
- **Agent Recommendation**: None

**Phase 8 Milestone**:
- ✅ 30-50 arXiv papers in corpus
- ✅ Math and table extraction working
- ✅ 80%+ LaTeX conversion success rate
- ✅ Full corpus now ~400-450 documents

---

### Phase 9: Commercial API Adapters (Week 7) - 6 Tasks, ~18 Hours

**Goal**: Implement adapters for commercial parsing APIs

#### TASK-067: Implement AWS Textract Adapter
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-004, TASK-005]
- **Acceptance Criteria**:
  - `pdf_bench/systems/aws_textract.py` created
  - boto3 integration
  - API key from environment variables
  - Markdown output formatting
  - Cost tracking (per-page pricing)
  - Rate limiting
  - Cache integration
  - Integration test (mock API)
- **Agent Recommendation**: `/agent code-reviewer` for security review (API keys)

#### TASK-068: Implement Azure Document Intelligence Adapter
- **Type**: feature
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-004, TASK-005]
- **Acceptance Criteria**:
  - `pdf_bench/systems/azure_di.py` created
  - azure-ai-formrecognizer integration
  - API key from environment variables
  - Configure for Markdown output
  - Cost tracking
  - Rate limiting
  - Cache integration
  - Integration test (mock API)
- **Agent Recommendation**: `/agent code-reviewer` for security review

#### TASK-069: Implement Google Document AI Adapter (Optional)
- **Type**: feature
- **Priority**: low
- **Estimated Hours**: 4
- **Dependencies**: [TASK-004, TASK-005]
- **Acceptance Criteria**:
  - `pdf_bench/systems/google_docai.py` created
  - Google Cloud client library integration
  - API key configuration
  - Markdown output formatting
  - Cost tracking
  - Integration test
- **Agent Recommendation**: None

#### TASK-070: Implement Cost Estimation System
- **Type**: feature
- **Priority**: medium
- **Estimated Hours**: 3
- **Dependencies**: [TASK-067, TASK-068]
- **Acceptance Criteria**:
  - Cost calculator for commercial APIs
  - Per-page pricing configuration
  - Pre-run cost estimate (CLI flag)
  - Post-run cost report
  - `max_cost` parameter to prevent overruns
  - Unit tests
- **Agent Recommendation**: None

#### TASK-071: Commercial Adapter Integration Tests
- **Type**: testing
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-067, TASK-068]
- **Acceptance Criteria**:
  - Mock API responses for tests
  - Test error handling (API failures)
  - Test rate limiting
  - Test cost tracking
  - Test cache behavior
- **Agent Recommendation**: `/agent test-engineer`

#### TASK-072: Document Commercial API Setup
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 1
- **Dependencies**: [TASK-071]
- **Acceptance Criteria**:
  - README updated with API setup instructions
  - Environment variable configuration documented
  - Pricing information linked
  - Example usage provided
  - Security best practices noted
- **Agent Recommendation**: None

**Phase 9 Milestone**:
- ✅ 7+ parsers operational (4 OS + 3 commercial)
- ✅ Cost tracking and estimation working
- ✅ Can run full benchmark on complete corpus

---

### Phase 10: Documentation & Release Prep (Week 7-8) - 8 Tasks, ~24 Hours

**Goal**: Complete all documentation for v0.1 release

#### TASK-073: Create DATASHEET.md
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-065, TASK-051, TASK-057]
- **Acceptance Criteria**:
  - "Datasheets for Datasets" framework followed
  - Sections complete:
    - Motivation and composition
    - Collection process per track
    - Full data provenance (URLs, licenses)
    - Known limitations and biases
    - Recommended uses
    - Ethical considerations
  - Per-document license tracking verified
- **Agent Recommendation**: None

#### TASK-074: Complete README.md
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-046, TASK-072]
- **Acceptance Criteria**:
  - Sections complete:
    - Project overview and motivation
    - Features
    - Installation instructions (Poetry, external tools)
    - Quick start guide
    - Usage examples (CLI and Python API)
    - Corpus overview
    - Metric descriptions
    - Parser list
    - Troubleshooting
    - FAQ
    - Contributing
    - License
  - Code examples tested
  - Screenshots/example output included
- **Agent Recommendation**: None

#### TASK-075: Create CONTRIBUTING.md
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: []
- **Acceptance Criteria**:
  - Sections complete:
    - Code of Conduct
    - How to add a new parser adapter
    - How to contribute documents
    - How to add metrics
    - Development setup
    - Testing requirements
    - PR process
  - Examples provided
  - Clear, welcoming tone
- **Agent Recommendation**: None

#### TASK-076: Create LICENSE and Legal Files
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 1
- **Dependencies**: []
- **Acceptance Criteria**:
  - LICENSE file (MIT or Apache 2.0)
  - NOTICE file if using Apache
  - License headers in source files
  - Third-party license attributions
- **Agent Recommendation**: None

#### TASK-077: Create GitHub Issue/PR Templates
- **Type**: documentation
- **Priority**: medium
- **Estimated Hours**: 2
- **Dependencies**: []
- **Acceptance Criteria**:
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - Clear, structured templates
- **Agent Recommendation**: None

#### TASK-078: Create Example Jupyter Notebook
- **Type**: documentation
- **Priority**: low
- **Estimated Hours**: 3
- **Dependencies**: [TASK-046]
- **Acceptance Criteria**:
  - Notebook demonstrates:
    - Loading a benchmark config
    - Running evaluation
    - Analyzing results
    - Visualizing metrics
  - Runs without errors
  - Included in repository
- **Agent Recommendation**: None

#### TASK-079: Complete API Documentation
- **Type**: documentation
- **Priority**: medium
- **Estimated Hours**: 3
- **Dependencies**: [TASK-046]
- **Acceptance Criteria**:
  - All public classes/functions documented
  - Docstrings follow NumPy/Google style
  - Type hints complete
  - Sphinx setup (optional for v0.1)
  - Examples in docstrings
- **Agent Recommendation**: None

#### TASK-080: Create Release Checklist
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-073, TASK-074, TASK-075]
- **Acceptance Criteria**:
  - Checklist includes:
    - All tests passing
    - Full corpus built and validated
    - Sample benchmark run completed
    - HTML report manually reviewed
    - Documentation complete
    - License files in place
    - GitHub repository configured
    - PyPI package metadata complete
    - Version tagged
  - Saved in `.claude/work/` for reference
- **Agent Recommendation**: None

**Phase 10 Quality Gate**:
- ✅ DATASHEET.md complete with full provenance
- ✅ README.md with installation and usage
- ✅ CONTRIBUTING.md with clear guidelines
- ✅ All documentation reviewed for accuracy

---

### Phase 11: Launch & Community Engagement (Week 8+) - 5 Tasks, ~15 Hours

**Goal**: Prepare for and execute v0.1 launch

#### TASK-081: Configure PyPI Package
- **Type**: integration
- **Priority**: high
- **Estimated Hours**: 3
- **Dependencies**: [TASK-001, TASK-080]
- **Acceptance Criteria**:
  - `pyproject.toml` complete with metadata (PEP 621 format)
  - Package description, keywords, classifiers
  - Entry points for CLI configured
  - Build with `uv build`
  - Test PyPI upload
  - Production PyPI upload
  - `pip install pdf-bench` works
- **Agent Recommendation**: None

#### TASK-082: Run Full Benchmark on Complete Corpus
- **Type**: testing
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-065, TASK-051, TASK-057, TASK-072]
- **Acceptance Criteria**:
  - Benchmark run on all ~450 documents
  - All 7 parsers tested
  - All metrics computed
  - Results saved to JSON
  - HTML report generated
  - Manual quality review of report
  - Leaderboard results sensible
  - Performance metrics captured
- **Agent Recommendation**: None

#### TASK-083: Write Launch Blog Post
- **Type**: documentation
- **Priority**: high
- **Estimated Hours**: 4
- **Dependencies**: [TASK-082]
- **Acceptance Criteria**:
  - Blog post drafted (1500-2000 words)
  - Sections:
    - Problem statement (licensing gap)
    - Solution overview
    - Corpus design
    - Key results from leaderboard
    - Call to action (GitHub, PyPI)
  - Includes charts/visualizations
  - Edited and proofread
- **Agent Recommendation**: None

#### TASK-084: Prepare GitHub Repository for Public Release
- **Type**: integration
- **Priority**: high
- **Estimated Hours**: 2
- **Dependencies**: [TASK-080, TASK-081]
- **Acceptance Criteria**:
  - Repository description and topics set
  - README renders correctly on GitHub
  - All sensitive data removed
  - CI/CD badges added
  - Social preview image configured
  - Repository made public
  - Initial release tagged (v0.1.0)
- **Agent Recommendation**: None

#### TASK-085: Launch and Community Outreach
- **Type**: documentation
- **Priority**: medium
- **Estimated Hours**: 2
- **Dependencies**: [TASK-083, TASK-084]
- **Acceptance Criteria**:
  - Blog post published on firm website
  - GitHub repository announced
  - PyPI package announced
  - Shared on:
    - Hacker News
    - Reddit (r/MachineLearning, r/Python)
    - Twitter/X
    - LinkedIn
  - Initial issues/PRs monitored and responded to
- **Agent Recommendation**: None

**Phase 11 Milestone**:
- ✅ v0.1 released to PyPI
- ✅ GitHub repository public
- ✅ Launch blog post published
- ✅ Community engagement initiated

---

## Critical Path Analysis

### Minimum Viable Sequence to Working System

The following tasks represent the **critical path** - the minimum sequence required to achieve a working MVP:

1. **Foundation** (TASK-001 → TASK-010): 30 hours
2. **Synthetic Corpus** (TASK-011 → TASK-018): 24 hours
3. **Core Metrics** (TASK-019 → TASK-023, TASK-026 → TASK-027): 21 hours
4. **First Parser** (TASK-029 → TASK-030): 6 hours
5. **Benchmark Runner** (TASK-037 → TASK-046): 30 hours
6. **One Corpus Track** (TASK-047 → TASK-052 OR TASK-059 → TASK-066): 18-24 hours
7. **Documentation** (TASK-073 → TASK-080): 24 hours
8. **Release** (TASK-081 → TASK-084): 9 hours

**Critical Path Total**: ~162-168 hours (4-5 weeks)

### Parallel Opportunities

The following tasks can be executed in parallel to compress timeline:

**Parallel Track 1**: Corpus Builders (Weeks 5-7)
- GOV.UK scraper (TASK-047 → TASK-052)
- SEC EDGAR scraper (TASK-053 → TASK-058)
- arXiv pipeline (TASK-059 → TASK-066)

**Parallel Track 2**: Parser Adapters (Week 4)
- Marker (TASK-029 → TASK-030)
- Nougat (TASK-031 → TASK-032)
- Unstructured (TASK-033 → TASK-034)

**Parallel Track 3**: Commercial APIs (Week 7)
- AWS Textract (TASK-067)
- Azure DI (TASK-068)
- Google DocAI (TASK-069)

**Parallel Track 4**: Documentation (Throughout)
- Can write docs incrementally alongside implementation

---

## Risk Mitigation Strategies

### Risk 1: LaTeX Conversion Failures
**Impact**: High - Affects 30-50 documents in academic corpus
**Probability**: Medium - LaTeX is complex and fragile

**Mitigation**:
- Multi-stage fallback: LaTeXML → Pandoc → Skip document
- Conservative paper selection (avoid custom macro-heavy papers)
- Acceptance criterion: 80% success rate (not 100%)
- Detailed logging of failures for post-mortem

**Contingency**:
- If success rate < 60%, reduce academic corpus to 20 papers
- Focus on simpler papers (recent arXiv submissions with standard templates)

### Risk 2: Metric Implementation Complexity
**Impact**: Medium - May delay Phase 3
**Probability**: Low - Well-documented libraries exist

**Mitigation**:
- Use established libraries (zss, table-recognition-metric)
- Make advanced metrics "optional extras" in Poetry groups
- Implement simple fallbacks (e.g., exact string match for tables)

**Contingency**:
- If TEDS integration fails, use simple cell-by-cell comparison
- If AST-TED is too complex, rely on Element F1 for structure

### Risk 3: Commercial API Changes
**Impact**: Medium - Adapter breakage after release
**Probability**: Medium - APIs evolve frequently

**Mitigation**:
- Pin API client library versions
- Comprehensive integration tests with recorded responses
- Version compatibility matrix in documentation
- Adapter versioning (e.g., `AWSTextractParserV2`)

**Contingency**:
- Community contributions for updated adapters
- Maintain multiple adapter versions for same API

### Risk 4: Dataset Licensing Ambiguity
**Impact**: High - Legal risk, blocks commercial use
**Probability**: Low - Conservative sourcing strategy

**Mitigation**:
- Only use explicitly permissive sources (OGL v3.0, CC-BY, public domain)
- Per-document license tracking in YAML
- Legal review before v0.1 release
- "Recipes-only" distribution (no PDF redistribution)

**Contingency**:
- If any source is legally questionable, remove immediately
- Synthetic corpus can expand to compensate

### Risk 5: Table Ground Truth Inconsistency
**Impact**: Medium - Affects metric reliability
**Probability**: Medium - Tables have multiple valid representations

**Mitigation**:
- Canonical HTML table normalization (lowercase, sorted attrs)
- TEDS metric (structural similarity) vs exact match
- Document normalization rules clearly
- Manual validation of complex tables

**Contingency**:
- If TEDS scores seem unreliable, add manual validation subset
- Provide "table quality" flag in metadata for filtering

---

## Quality Assurance Strategy

### Testing Approach

**Unit Tests** (Throughout all phases):
- Coverage target: 80%+
- Focus: Individual functions, edge cases
- Tools: pytest, pytest-cov
- Run on every commit (CI)

**Integration Tests** (Phases 4-9):
- Focus: Parser adapters, corpus builders, metric computation
- Mock external dependencies (APIs, Pandoc, LaTeXML)
- Verify error handling and retry logic

**End-to-End Tests** (Phase 5, 10):
- Run full benchmark on small subset (10 docs, 2 parsers)
- Verify HTML report generation
- Performance regression checks
- Run in CI before release

### Code Quality Standards

**Linting and Formatting**:
- Tool: ruff (replaces flake8, black, isort)
- Config: `pyproject.toml`
- Auto-fix on commit (pre-commit hook)

**Type Checking**:
- Tool: mypy
- Strict mode enabled
- All public APIs fully typed

**Code Review**:
- All PRs require review
- Focus: security (API keys), correctness, performance
- Use `/agent code-reviewer` for complex logic

### Documentation Requirements

**Code Documentation**:
- Docstrings: NumPy/Google style
- Type hints: All public APIs
- Examples: In docstrings for complex functions

**User Documentation**:
- README: Installation, quick start, examples
- DATASHEET: Full dataset governance
- CONTRIBUTING: Clear extension guidelines

**Technical Documentation**:
- Metric definitions: Mathematical formulas, normalization rules
- Corpus builder: Step-by-step pipeline explanation
- Architecture: Diagrams (optional), key abstractions

### Performance Benchmarks

**Targets** (v0.1):
- Benchmark 100 documents in < 10 minutes (with caching)
- HTML report generation: < 5 seconds
- Memory usage: < 2GB for full corpus

**Monitoring**:
- Track execution time per parser per document
- Track metric computation time
- Identify bottlenecks for optimization in v1.0

---

## Success Indicators

### Functional Completeness
- ✅ All 85 tasks completed
- ✅ All acceptance criteria met
- ✅ All quality gates passed

### Technical Quality
- ✅ 80%+ test coverage
- ✅ All linting/type checks passing
- ✅ No critical security vulnerabilities

### Corpus Quality
- ✅ ~450 documents with validated GT
- ✅ Corpus diversity across 3 tracks
- ✅ Validation script confirms integrity

### Usability
- ✅ CLI works as documented
- ✅ Python API is intuitive
- ✅ HTML reports are clear and actionable

### Community Readiness
- ✅ Documentation complete
- ✅ Easy to install (`pip install pdf-bench`)
- ✅ Easy to extend (clear CONTRIBUTING.md)
- ✅ Responsive to initial issues/PRs

---

## Post-MVP Roadmap (v1.0+)

### v1.0 Features (Extended Corpus)
- 400+ documents
- Multi-language support (3-5 languages)
- CDM metric for math (image-based)
- Scanned/OCR track (~50 degraded documents)
- **Estimated**: +4 weeks

### v2.0 Features (Advanced)
- Forms/invoice track
- Presentation (.pptx) track
- Interactive web-based report viewer
- Continuous leaderboard updates
- **Estimated**: +6 weeks

### Community Contributions
- Additional parser adapters
- New metric implementations
- Expanded corpus (user-contributed documents)
- Translations and internationalization

---

## Appendix: Agent Recommendations Summary

The following tasks have specialist agent recommendations for enhanced quality:

### Architecture Agent (`/agent architect`)
- TASK-004: BaseParser interface design
- TASK-020: AST Tree-Edit Distance algorithm
- TASK-037: Benchmark config schema
- TASK-039: BenchmarkRunner orchestration

### Test Engineer Agent (`/agent test-engineer`)
- TASK-010: Test infrastructure and strategy
- TASK-035: Parser adapter test suite
- TASK-046: End-to-end integration testing
- TASK-071: Commercial adapter testing

### Code Reviewer Agent (`/agent code-reviewer`)
- TASK-067: AWS Textract security review (API keys)
- TASK-068: Azure DI security review (API keys)

### Auditor Agent (`/agent auditor`)
- TASK-002: Directory structure validation

**Note**: Agent use is **recommended but optional**. All tasks can be completed without agents.

---

## Next Actions

After reviewing this implementation plan:

1. **Approve the plan** - Confirm scope, effort estimates, and approach
2. **Create state.json** - Generate task tracking file for `/next` command
3. **Start TASK-001** - Run `/next` to begin with Poetry project initialization
4. **Track progress** - Use `/workflow:status` to monitor task completion
5. **Adapt as needed** - Adjust plan based on implementation learnings

**The plan is comprehensive, phased, and accounts for technical complexity while maintaining a clear path to a valuable MVP.**

---

**Plan Created**: 2025-11-14
**Ready for Execution**: Yes
**Next Command**: `/next` to begin TASK-001
