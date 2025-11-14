# Requirements: PDF-Bench - A Benchmark for PDF-to-Markdown Conversion

## Source
- Type: Technical specification documents
- Reference: .claude/reference/specs_01.md (comprehensive PRD) and specs_02.md (executive summary)
- Date: 2025-11-14

## Project Overview

**PDF-Bench** is an open-source benchmarking suite for evaluating PDF-to-semantic-Markdown conversion systems. The goal is to create a practical, legally sound, and technically rigorous asset that:

1. Enables data-driven selection of PDF parsers for client projects
2. Establishes thought leadership in the document intelligence space
3. Provides a commercially permissive alternative to existing academic benchmarks

## Core Problem Statement

Existing PDF parsing benchmarks have critical limitations:
- **Academic-only focus** (arXiv, PubMed) - not representative of business documents
- **Layout-only evaluation** (DocLayNet) - no semantic content ground truth
- **Non-commercial licenses** (OmniDocBench: CC-BY-NC-4.0) - unusable for commercial consulting work
- **Shallow metrics** (text extraction only) - miss structural fidelity

## Functional Requirements

### 1. Corpus Creation (MVP v0.1: ~450 documents)

#### Track 1: Academic Corpus (~150 docs)
- **Source**: arXiv (cs.CL, cs.CV, math.AP, econ.EM)
- **Ground Truth Pipeline**: LaTeX source → LaTeXML → Custom MD converter
- **License**: CC-BY, arXiv perpetual license
- **Key Features**: Complex math, multi-column layouts, scientific tables

#### Track 2: Business/Institutional Corpus (~250 docs)

**Sub-Corpus A: Harvested Government/NGO Reports (~150 docs)**
- **GOV.UK**: Policy reports, whitepapers, annual reports (OGL v3.0 license)
- **EU Publications**: Technical briefs, policy reports (EU permissive license)
- **SEC EDGAR**: 10-K, 10-Q financial filings (public domain)
- **Ground Truth**: Paired HTML/XML source → normalized to Canonical Markdown

**Sub-Corpus B: Synthetic Enterprise Documents (~100 docs)**
- **DOCX-based**: Templates via python-docx-template → LibreOffice headless conversion
- **Markdown-based**: Source MD → Pandoc + Eisvogel template → PDF
- **License**: MIT (generated data)
- **Document Types**: Consulting whitepapers, financial statements, marketing materials

### 2. Ground Truth Specification: "Consulting Markdown" (CMD)

**Core Syntax (GitHub Flavored Markdown subset + extensions)**:
- Headings: `#`, `##`, `###` (hierarchical, sequential)
- Paragraphs: Double-newline separated
- Lists: Ordered/unordered with correct nesting
- **Tables**:
  - Simple: GFM table syntax
  - Complex (merged cells): Embedded HTML `<table>` blocks
- **Math**:
  - Inline: `$E=mc^2$`
  - Display: `$$\sum_{i=0}^{n}...$$`
- Figures: `![caption](image_filename.png)`
- Code blocks: GFM fenced blocks
- Footnotes: GFM-style `[^1]` and `[^1]: ...`
- **Exclusions**: Running headers, footers, page numbers (printing artifacts)

**Normalization Rules**:
- Unicode NFC normalization
- Collapse whitespace sequences (preserve semantic block separators)
- Normalize "smart" quotes and dashes
- LaTeX: remove redundant whitespace and grouping

**Metadata Schema** (per-file YAML):
```yaml
doc_id: gov_uk_env_plan_2023
source_url: https://www.gov.uk/...
pdf_url: https://assets.publishing...
pdf_hash_sha256: <hash>
ground_truth_file: gov_uk_report_001.md
license: Open Government Licence v3.0
source: GOV.UK
properties:
  category: "business_harvested"
  subcategory: "government_report"
  language: "en"
  layout: "mixed"
  page_count: 262
tags:
  - "has_complex_tables"
  - "has_figures"
  - "has_toc"
```

### 3. Evaluation Framework

#### Core Evaluation Tasks
1. **Task 1**: Full-document PDF→Markdown conversion (primary)
2. **Task 2** (Optional): Element-specific extraction (tables, math, layout)

#### Multi-Layered Metrics

**Text-Level Metrics**:
- **Normalized Edit Distance**: `1 - (Levenshtein / max_length)`
- **chrF++**: Robust, token-free text similarity (sacrebleu)

**Structure-Level Metrics** (Key Differentiator):
- **AST Tree-Edit Distance**: Zhang-Shasha on Markdown AST (using mistune/markdown-it-py)
- **Element F1 Score**: Precision/Recall on element type counts (H1, H2, Table, List, etc.)

**Table-Level Metrics**:
- **TEDS** (Tree-Edit-Distance-based Similarity): Industry standard, Python package `table-recognition-metric`
- **Cell Content F1**: F1 on cell text accuracy

**Equation-Level Metrics**:
- **v0**: Normalized LaTeX string F1 (exact match after normalization)
- **v1 (roadmap)**: CDM (Character Difference Metric) - image-based visual comparison

**Performance Metrics**:
- **Latency**: seconds/page
- **Throughput**: pages/second
- **Cost**: $/1k pages (for commercial APIs)

### 4. Library Architecture (pdfbench)

#### Repository Structure
```
/pdf-bench
├── datasets/
│   └── recipes/          # YAML metadata (URLs, hashes)
├── ground_truth/
│   ├── academic/
│   │   ├── arxiv_cs_cl_001.md
│   │   └── arxiv_cs_cl_001.yml
│   └── business/
│       ├── gov_uk_report_001.md
│       └── gov_uk_report_001.yml
├── builders/
│   ├── download_corpus.py
│   ├── build_academic.py
│   └── build_synthetic.py
├── pdf_bench/
│   ├── __init__.py
│   ├── systems/          # Parser adapters
│   │   ├── base_parser.py
│   │   ├── marker.py
│   │   └── aws_textract.py
│   ├── metrics/
│   │   ├── text_metrics.py
│   │   ├── table_metrics.py
│   │   └── struct_metrics.py
│   ├── core.py           # Benchmark runner
│   ├── cli.py            # CLI (Typer/Click)
│   └── report.py         # HTML/Markdown reports
├── benchmarks/
│   ├── academic_v0.yml
│   └── business_v0.yml
├── reports/
├── .cache/               # Cached parser outputs
├── DATASHEET.md          # Dataset governance
└── pyproject.toml
```

#### BaseParser Interface
```python
from abc import ABC, abstractmethod
from pathlib import Path

class BaseParser(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Return parser name and version."""
        pass

    @abstractmethod
    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """
        Process PDF, save Markdown to output_dir.
        Returns: Path to generated Markdown file.
        """
        pass
```

#### Supported Parsers (v0)
**Open Source**:
- Marker
- Nougat
- Unstructured
- PyMuPDF (baseline)

**Commercial**:
- AWS Textract
- Azure Document Intelligence
- Google Document AI

#### CLI Specification
```bash
# Build corpus
$ pdfbench build-corpus --track academic --track business

# List resources
$ pdfbench list benchmarks
$ pdfbench list systems

# Run benchmark
$ pdfbench run --benchmark business_v0 --systems marker,aws,azure

# Generate report
$ pdfbench report --run_id <run_id> --format html
```

#### Python API
```python
from pdfbench import Benchmark, run_benchmark
from pdfbench.systems import MarkerParser, AWSTextractParser

bench_spec = Benchmark.load("benchmarks/business_v0.yml")
systems_to_test = [MarkerParser(), AWSTextractParser()]
results = run_benchmark(bench_spec, systems_to_test, cache_dir=".cache")
results.save_report("reports/my_report.html")
```

### 5. Reporting and Error Analysis

**Generated Reports Include**:
- **Leaderboard**: Overall weighted score + category breakdowns (Academic, Government, Finance)
- **Metric Breakdown**: Structure, Table, Math, Speed/Cost comparison
- **Common Failure Modes**: Taxonomy (e.g., "Paragraph Merging", "Table Structure Collapse", "Dropped Math")
- **Per-Document Analysis**: Diff viewer for GT vs prediction

### 6. Legal and Governance

**Licenses**:
- **Library code**: MIT or Apache 2.0
- **Synthetic ground truth**: MIT or CC-BY-SA 4.0
- **Harvested documents**: "Recipes-only" approach (URLs + hashes, no redistribution)

**Documentation**:
- **DATASHEET.md**: Following "Datasheets for Datasets" framework
  - Motivation, composition, collection process
  - Full data provenance (source URLs, licenses per document)
  - Known limitations and biases (e.g., "English-only", "UK/EU report bias")

## Non-Functional Requirements

### Performance
- **Caching**: Robust caching mechanism using hash(parser_name, parser_version, pdf_hash, params)
- **Parallel Execution**: Support for concurrent parser execution
- **Rate Limiting**: For commercial API adapters
- **Cost Management**: `max_cost` parameter to prevent API overruns

### Extensibility
- **Plugin Architecture**: Easy to add new parsers via BaseParser interface
- **Metric Extension**: Clear process to add new metrics (e.g., CDM)
- **Corpus Contributions**: CONTRIBUTING.md for submitting new documents/sources

### Quality
- **Reproducibility**: All results tied to specific benchmark version and code
- **Fairness**: Latest stable versions of parsers, transparent parameters
- **Transparency**: All costs, parameters, and limitations disclosed

## Acceptance Criteria

### v0.1 MVP
- ✅ Corpus builder scripts for ~450 documents (academic, business, synthetic)
- ✅ Ground truth Markdown + YAML metadata files
- ✅ Python evaluation library with core metrics (Edit Distance, TEDS, Element-F1, AST-Edit-Distance)
- ✅ Parser adapters for 3-5 open-source systems + 2-3 commercial APIs
- ✅ CLI for running benchmarks and generating static HTML/Markdown reports
- ✅ DATASHEET.md for dataset governance
- ✅ README.md with installation, usage examples
- ✅ CONTRIBUTING.md with clear extension guidelines

### v1.0 Roadmap
- Scanned/OCR track (~50 degraded documents)
- Multi-language track
- CDM metric implementation for math
- Extended corpus (~400 documents)

### v2.0 Roadmap
- Forms/transactional track
- Presentation (.pptx) track
- Interactive report viewer

## Out of Scope (v0.1)
- Model training
- GUI or web application (reports are static files)
- Manual annotation tooling
- OCR/scanned document track

## Dependencies

### Python Libraries
- **Core**: pathlib, typing, abc
- **Parsing**: markdown-it-py or mistune (AST generation)
- **Metrics**:
  - python-Levenshtein (edit distance)
  - sacrebleu (chrF++)
  - table-recognition-metric (TEDS)
  - zss or apted (tree-edit distance)
- **Document Processing**:
  - LaTeXML (academic corpus)
  - BeautifulSoup4 (HTML scraping)
  - python-docx-template (synthetic generation)
  - Pandoc (LaTeX/MD conversion)
- **CLI**: typer or click
- **Reporting**: jinja2 (HTML templates)
- **Parsers**:
  - marker (datalab-to/marker)
  - nougat (facebookresearch/nougat)
  - unstructured
  - PyMuPDF
  - boto3 (AWS Textract)
  - azure-ai-formrecognizer (Azure DI)

### External Tools
- LaTeXML (Perl-based)
- LibreOffice (headless DOCX→PDF conversion)
- Pandoc (universal document converter)

## Risks and Assumptions

### Risks
1. **License Ambiguity**: Some GOV.UK/EU documents may have unclear derivative work terms
   - *Mitigation*: Only use explicitly OGL v3.0 or public domain sources
2. **Ground Truth Quality**: Automated LaTeX→MD conversion may have errors
   - *Mitigation*: Manual spot-checking, validation scripts
3. **Parser API Changes**: Commercial APIs may change output formats
   - *Mitigation*: Version pinning, adapter abstraction layer
4. **Metric Selection**: Weighted scores may not reflect all use cases
   - *Mitigation*: Provide metric breakdown, allow custom weighting

### Assumptions
1. Users will provide their own API keys for commercial parsers
2. LaTeXML can handle majority of arXiv papers without manual intervention
3. GFM + HTML tables are sufficient for complex table representation
4. AST-based structural metrics correlate with real-world parsing quality

## Success Indicators

- ✅ Work unit created and activated
- ✅ Requirements clearly documented
- ✅ Corpus sourcing strategy legally validated
- ✅ Metric framework comprehensively specified
- ✅ Parser adapter interface defined
- ✅ Clear v0.1 MVP scope established
- ✅ Thought leadership positioning articulated

## Strategic Positioning

**Key Message**: "The Practitioner's Benchmark for Real-World Documents"

**Differentiation**:
- vs. DocLayNet: Semantic content, not just layout
- vs. \readoc: Business documents, not just academic
- vs. OmniDocBench: Commercially permissive, practitioner-focused

**Community Engagement**:
- Launch blog: Announce project, highlight licensing gap
- Technical deep dives: GOV.UK harvesting, AST metrics
- Leaderboard post: Neutral, reproducible parser comparison
- Contribution guide: Easy parser/document/metric additions

**Responsible Communication**:
- Neutral, trusted arbiter (not partisan)
- Reproducible results (exact versions, parameters)
- Fair comparisons (latest stable versions)
- Transparent costs and limitations
- Nuanced analysis (not "Parser X destroys Parser Y")
