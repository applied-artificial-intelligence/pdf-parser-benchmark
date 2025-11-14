# PDF-Bench Implementation Plan Outline

## Overview

This is a high-level plan outline for implementing the PDF-Bench v0.1 MVP. Run `/plan` to expand this into detailed, actionable tasks with dependencies.

## Phase 1: Project Foundation (Week 1-2)

### 1.1 Project Structure & Configuration
- [ ] Initialize Poetry project (pyproject.toml)
- [ ] Create directory structure (pdf_bench/, builders/, ground_truth/, etc.)
- [ ] Configure development tools (ruff, mypy, pytest)
- [ ] Set up pre-commit hooks
- [ ] Initialize git repository
- [ ] Create GitHub repository with README skeleton

### 1.2 Core Abstractions
- [ ] Define BaseParser abstract class
- [ ] Implement caching system (hash-based, disk-backed)
- [ ] Create document metadata schema (YAML validation)
- [ ] Implement normalization utilities (text, whitespace)

### 1.3 Baseline Implementation
- [ ] Implement PyMuPDFParser (simple text extraction baseline)
- [ ] Create basic test PDF fixture
- [ ] Implement Normalized Edit Distance metric
- [ ] Write unit tests for core utilities

**Milestone**: Can parse a PDF with PyMuPDF, cache result, compute text similarity

---

## Phase 2: Synthetic Corpus Builder (Week 2-3)

### 2.1 Markdown→PDF Pipeline
- [ ] Create 5 test Markdown documents (simple → complex)
  - [ ] Basic text + headings
  - [ ] Lists (ordered, unordered, nested)
  - [ ] Simple tables (GFM syntax)
  - [ ] Math (inline and display)
  - [ ] Complex tables (HTML embedded)
- [ ] Implement Pandoc wrapper (MD → PDF via Eisvogel)
- [ ] Add PDF hash verification
- [ ] Create corresponding YAML metadata files

### 2.2 DOCX→PDF Pipeline
- [ ] Design 3 DOCX templates
  - [ ] Simple report (headings, paragraphs, lists)
  - [ ] Table-heavy document
  - [ ] Multi-column layout
- [ ] Implement python-docx-template integration
- [ ] Implement LibreOffice headless conversion
- [ ] Extract ground truth from DOCX structure
- [ ] Generate YAML metadata

### 2.3 Validation & Testing
- [ ] Implement GT validation script (schema check, file existence)
- [ ] Manual review checklist for synthetic docs
- [ ] Document corpus builder usage in README

**Milestone**: ~20 synthetic documents with validated ground truth

---

## Phase 3: Advanced Metrics (Week 3-4)

### 3.1 Structure Metrics
- [ ] Implement Markdown AST parser (using mistune)
- [ ] Integrate zss library for Tree-Edit Distance
- [ ] Implement AST-based structural comparison
- [ ] Implement Element F1 Score (node type counting)
- [ ] Write unit tests with known GT/prediction pairs

### 3.2 Table Metrics
- [ ] Integrate table-recognition-metric (TEDS)
- [ ] Implement HTML table normalization
- [ ] Implement GFM table parsing and comparison
- [ ] Implement cell content F1 score
- [ ] Test with complex table fixtures

### 3.3 Math Metrics
- [ ] Implement LaTeX normalization rules
- [ ] Implement normalized string matching
- [ ] Implement LaTeX extraction from Markdown
- [ ] Test with equation-heavy documents

**Milestone**: Full metric suite operational on synthetic corpus

---

## Phase 4: Open-Source Parser Adapters (Week 4)

### 4.1 Marker Adapter
- [ ] Install and test Marker locally
- [ ] Implement MarkerParser adapter
- [ ] Handle Marker-specific output format
- [ ] Integration tests

### 4.2 Nougat Adapter
- [ ] Install and test Nougat locally
- [ ] Implement NougatParser adapter
- [ ] Handle Nougat-specific LaTeX output
- [ ] Integration tests

### 4.3 Unstructured Adapter
- [ ] Install unstructured library
- [ ] Implement UnstructuredParser adapter
- [ ] Configure Unstructured for Markdown output
- [ ] Integration tests

**Milestone**: Can benchmark 4 parsers (PyMuPDF, Marker, Nougat, Unstructured) on synthetic corpus

---

## Phase 5: Benchmark Runner & Reporting (Week 4-5)

### 5.1 Benchmark Configuration
- [ ] Design YAML config schema (benchmark definitions)
- [ ] Implement config loader and validator
- [ ] Support document filtering (by tag, category)
- [ ] Support parser selection and parameters

### 5.2 Execution Engine
- [ ] Implement BenchmarkRunner class
- [ ] Add parallel execution (multiprocessing)
- [ ] Implement progress tracking (rich progress bar)
- [ ] Error handling and retry logic
- [ ] Result persistence (JSON output)

### 5.3 CLI Interface
- [ ] Implement `pdfbench run` command (Typer)
- [ ] Implement `pdfbench list` commands (systems, benchmarks)
- [ ] Implement `pdfbench report` command
- [ ] Add --dry-run, --verbose flags
- [ ] Write CLI usage documentation

### 5.4 HTML Reporting
- [ ] Design HTML report template (Jinja2)
- [ ] Implement leaderboard generation
- [ ] Implement metric breakdown tables
- [ ] Implement per-document diff view (optional for v0.1)
- [ ] Add CSS styling (clean, professional)

**Milestone**: End-to-end benchmark run with HTML report

---

## Phase 6: Business Corpus - GOV.UK Track (Week 5-6)

### 6.1 GOV.UK Scraper
- [ ] Identify 30 target GOV.UK publications (varied topics/complexity)
- [ ] Implement HTML scraper (BeautifulSoup)
- [ ] Implement HTML→Markdown converter
  - [ ] Heading extraction
  - [ ] Table conversion (simple GFM, complex HTML)
  - [ ] List extraction
  - [ ] Figure/image handling
- [ ] Implement PDF downloader with retry logic
- [ ] Generate YAML metadata (OGL v3.0 license)

### 6.2 Quality Validation
- [ ] Implement HTML→MD validation script
- [ ] Manual spot-check (10 documents)
- [ ] Document known limitations (e.g., complex navigation menus)

**Milestone**: 20-30 GOV.UK documents in corpus

---

## Phase 7: Business Corpus - SEC EDGAR Track (Week 6)

### 7.1 SEC EDGAR Scraper
- [ ] Identify 20 target 10-K/10-Q filings (varied industries)
- [ ] Implement SEC EDGAR API integration
- [ ] Implement HTML/XBRL parser (focus on tables)
- [ ] Implement table extraction and normalization
- [ ] Download corresponding PDFs
- [ ] Generate YAML metadata (public domain)

### 7.2 Table-Focused Testing
- [ ] Validate table extraction quality
- [ ] Test TEDS metric on financial tables
- [ ] Document table extraction methodology

**Milestone**: 10-20 SEC filings in corpus

---

## Phase 8: Academic Corpus - arXiv Track (Week 7)

### 8.1 arXiv Pipeline
- [ ] Implement arXiv API client (metadata, downloads)
- [ ] Select 30-50 papers (varied: cs.CL, cs.CV, math, econ)
- [ ] Implement LaTeX source extractor (.tar.gz → .tex)
- [ ] Integrate LaTeXML subprocess wrapper
- [ ] Implement LaTeXML output → Markdown converter
- [ ] Add Pandoc fallback for LaTeXML failures
- [ ] Generate YAML metadata (arXiv licenses)

### 8.2 Academic Document Validation
- [ ] Test math extraction quality
- [ ] Test table extraction from LaTeX
- [ ] Manual review (10 papers)
- [ ] Document success rate and common failure modes

**Milestone**: 30-50 arXiv papers in corpus

---

## Phase 9: Commercial API Adapters (Week 7-8)

### 9.1 AWS Textract Adapter
- [ ] Implement AWSTextractParser (boto3)
- [ ] Add API key configuration (env vars)
- [ ] Implement cost estimation and tracking
- [ ] Add rate limiting and retry logic
- [ ] Integration tests (with mocked responses)

### 9.2 Azure Document Intelligence Adapter
- [ ] Implement AzureDocIntelParser (azure-ai-formrecognizer)
- [ ] Add API key configuration
- [ ] Implement cost tracking
- [ ] Add rate limiting
- [ ] Integration tests

### 9.3 Google Document AI Adapter (Optional)
- [ ] Implement GoogleDocAIParser
- [ ] Same configuration/testing pattern as above

**Milestone**: 2-3 commercial API adapters operational

---

## Phase 10: Documentation & Release Preparation (Week 8)

### 10.1 Dataset Documentation (DATASHEET.md)
- [ ] Document motivation and composition
- [ ] Full data provenance (per-document licenses)
- [ ] Known limitations and biases
- [ ] Collection methodology
- [ ] Recommended uses and ethical considerations

### 10.2 User Documentation
- [ ] README.md with installation instructions
- [ ] Usage examples (CLI and Python API)
- [ ] Troubleshooting guide
- [ ] FAQ

### 10.3 Contributor Documentation
- [ ] CONTRIBUTING.md
  - [ ] How to add a new parser adapter
  - [ ] How to contribute documents
  - [ ] How to add metrics
- [ ] CODE_OF_CONDUCT.md
- [ ] Issue templates (bug, feature request)
- [ ] PR template

### 10.4 Release Checklist
- [ ] All tests passing
- [ ] Full corpus built and validated
- [ ] Sample benchmark run on full corpus
- [ ] HTML report reviewed
- [ ] Documentation complete
- [ ] License files in place (MIT/Apache)
- [ ] GitHub repository public
- [ ] PyPI package published

**Milestone**: v0.1 MVP ready for public release

---

## Phase 11: Launch & Community Engagement (Week 9+)

### 11.1 Content Marketing
- [ ] Write launch blog post
- [ ] Write technical deep dive #1 (GOV.UK corpus)
- [ ] Write technical deep dive #2 (AST metrics)
- [ ] Write leaderboard comparison post
- [ ] Submit to HN, Reddit, relevant communities

### 11.2 Community Building
- [ ] Monitor GitHub issues
- [ ] Respond to pull requests
- [ ] Engage with users on social media
- [ ] Present at relevant conferences/meetups

---

## Dependencies & Constraints

### Critical Path
1. Foundation → Synthetic Corpus → Metrics → Parsers → Runner/Reporting
2. Cannot test parsers without metrics
3. Cannot build business corpus without HTML→MD converter
4. Cannot benchmark without runner infrastructure

### Parallelizable Work
- GOV.UK scraper can be developed in parallel with arXiv pipeline
- Commercial adapters can be developed after open-source adapters
- Documentation can be written incrementally

### External Dependencies
- LaTeXML installation (apt/brew)
- Pandoc installation
- LibreOffice installation (for DOCX→PDF)
- API keys for commercial services (user-provided)

### Risk Mitigation
- Start with synthetic corpus (known-good ground truth)
- Implement metrics incrementally (text → structure → domain-specific)
- Test each corpus source independently before integration
- Manual validation checkpoints throughout

---

## Success Criteria (v0.1 MVP)

### Functional
- ✅ ~450 documents across 3 tracks (academic, business, synthetic)
- ✅ 7+ parser adapters (4 OS, 3 commercial)
- ✅ 5 metric categories (text, structure, table, math, performance)
- ✅ CLI operational for full benchmark runs
- ✅ HTML reports generated with leaderboards and breakdowns

### Quality
- ✅ 80%+ success rate on LaTeX→MD conversion
- ✅ All synthetic documents pass validation
- ✅ Manual review confirms ground truth quality
- ✅ Metrics produce sensible results on test cases

### Documentation
- ✅ DATASHEET.md complete with provenance
- ✅ README.md with installation and usage
- ✅ CONTRIBUTING.md with clear guidelines
- ✅ All code has docstrings and type hints

### Community
- ✅ Open-source repository public
- ✅ Launch blog post published
- ✅ PyPI package available
- ✅ Initial community feedback collected

---

## Post-MVP Roadmap

### v1.0 (Extended Corpus)
- 400+ documents
- Multi-language support
- CDM metric for math
- Scanned/OCR track

### v2.0 (Advanced Features)
- Forms/invoice track
- Presentation (.pptx) track
- Interactive web-based report viewer
- Continuous leaderboard updates

---

## Next Action

**This outline is ready to be expanded into detailed tasks.**

Run `/plan` to:
1. Break down each phase into specific, actionable tasks
2. Define task dependencies and ordering
3. Estimate effort per task
4. Create a state.json file for `/next` command execution
5. Identify potential blockers and mitigation strategies

The plan is comprehensive, phased, and accounts for the technical complexity of the project while maintaining a clear path to a valuable MVP.
