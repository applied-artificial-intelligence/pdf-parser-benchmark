# PDF-Bench Repository Audit

**Date**: 2025-11-24
**Total Repository Size**: ~25MB (including results)

## Executive Summary

The pdf-bench repository contains:
- **386 files** in results/ (16MB) - mix of final results, checkpoints, and test outputs
- **61 benchmark configs** (19 active + 42 archived)
- **21 parser implementations** - some may be redundant given pdfsmith exists
- **13 metric files** - all actively used
- **34 builder scripts** - mixture of active and deprecated
- **10 documentation files** (117KB) - well-organized
- **9 test files** (119KB) - mostly stubs, not real tests

**Key Findings**:
1. Results directory needs significant cleanup (42 checkpoint files, 26 orphaned MD files, debug directories)
2. Benchmark configs are well-archived but could use consolidation
3. Parser systems are comprehensive but question remains: do we need individual files with pdfsmith?
4. Tests are skeletal - no actual test functions defined
5. Documentation is solid and well-structured

---

## 1. results/ Directory (386 files, 16MB)

### Overview
- **22 final JSON results** in root
- **42 checkpoint files** (.checkpoint.json)
- **26 markdown files** (.md) - appear to be test outputs from synthetic corpus
- **5 subdirectories**: archive/, debug_teds/, debug_element_f1/, quick/, tier1/

### Active/Important Results (KEEP)

**Primary Benchmarks** (22 JSON files in root):
```
full_corpus_353docs.json                    1.4MB  ✅ KEEP - Main comprehensive benchmark
comprehensive_278docs_all_parsers.json      329KB  ✅ KEEP - Multi-parser comparison
cuad_75docs_all_parsers.json               382KB  ✅ KEEP - Legal contracts
legal_108docs.json                          961KB  ✅ KEEP - Legal documents
invoices_100docs.json                       487KB  ✅ KEEP - Invoice benchmark
invoices_100docs_fresh.json                 172KB  ✅ KEEP - Updated invoice run
hr_34docs.json                              159KB  ✅ KEEP - HR documents
commercial_200docs.json                     293KB  ✅ KEEP - Commercial parsers
omnidocbench_english_252.json              452KB  ✅ KEEP - English OmniDoc subset
omnidocbench_english_ocr.json              224KB  ✅ KEEP - OCR-focused subset
academic_5docs.json                          27KB  ✅ KEEP - Small academic test
arxiv_10docs_full.json                       55KB  ✅ KEEP - ArXiv papers
arxiv_10docs_fixes.json                     7.5KB  ✅ KEEP - ArXiv with fixes
```

**Specialized Results**:
```
marker_gap_fill.json                         46KB  ⚠️  REVIEW - Gap filling for marker parser
pypdf2_gap_fill.json                         82KB  ⚠️  REVIEW - Gap filling for pypdf2
synthetic_missing_parsers.json              140KB  ⚠️  REVIEW - Synthetic corpus gaps
arxiv_1doc_test.json                        891B   ⚠️  REVIEW - Minimal test file
```

### Checkpoint Files (REMOVE - 42 files)

**Recommendation**: 🗑️ **DELETE ALL CHECKPOINT FILES**

These are intermediate saves that duplicate final results:
```
arxiv_10docs_fixes.checkpoint.json          7.4KB
arxiv_10docs_full.checkpoint.json            55KB
arxiv_1doc_test.checkpoint.json             821B
marker_gap_fill.checkpoint.json              46KB
pypdf2_gap_fill.checkpoint.json              82KB
```

**Action**: Remove all `*.checkpoint.json` files (saves ~200KB, reduces clutter)

### Markdown Files in results/ (REMOVE - 26 files)

**Recommendation**: 🗑️ **DELETE - These are parser outputs, not results**

These appear to be individual document outputs from synthetic corpus parsing:
```
07_docx_tables.md
08_docx_multicolumn.md
09_table_simple_grid.md
10_table_colspan.md
... (22 more files)
32_mixed_comprehensive.md
```

Total: 29,312 lines of parser output that shouldn't be in results/

**Action**: Delete all `*.md` files from results/ root (saves ~30KB, reduces confusion)

### Subdirectories

#### results/archive/ (75 files, 8MB)
**Recommendation**: ✅ **KEEP - Well-organized**

Contains historical benchmark results. Good practice to preserve.

```
omnidocbench_ocr_4parsers_validation.json
business_fill_gaps.checkpoint.json
commercial_50doc_sample.json
legal_108docs.checkpoint.json
full_corpus_353docs.checkpoint.json
... (70+ more files)
```

**Note**: Contains many checkpoint files. Consider cleaning checkpoints from archive too.

#### results/debug_teds/ and results/debug_element_f1/ (empty, 4KB each)
**Recommendation**: 🗑️ **DELETE - Empty debug directories**

#### results/quick/ (10 files, 48KB)
**Recommendation**: ⚠️ **REVIEW - Appears to be test outputs**

Contains 10 markdown files from synthetic corpus. Similar to root MD files.
Likely temporary test outputs. Can be removed.

#### results/tier1/ (252 files, 2.3MB)
**Recommendation**: ⚠️ **REVIEW - Large collection of MD files**

Contains 252 markdown files. Appears to be parser outputs for a specific tier.
Question: Is this a deliberate organization or test outputs that should be cleaned?

---

## 2. benchmarks/ Directory (61 YAML files)

### Active Benchmarks (19 files)

**Recommendation**: ✅ **KEEP - Well-organized**

```
academic_5docs.yaml                  ✅ Small academic test set
arxiv_10docs.yaml                    ✅ 10 arXiv papers
arxiv_10docs_fixes.yaml              ✅ ArXiv with fixes
arxiv_1doc_test.yaml                 ✅ Minimal test
arxiv_complete_long.yaml             ✅ Long papers (>30 pages)
arxiv_complete_short.yaml            ✅ Short papers (<30 pages)
commercial_200docs.yaml              ✅ Commercial parser focus
comprehensive_278docs.yaml           ✅ Multi-corpus comprehensive
cuad_75docs.yaml                     ✅ Legal contracts
full_corpus_353docs.yaml             ✅ Main complete benchmark
hr_34docs.yaml                       ✅ HR documents
invoices_100docs.yaml                ✅ Invoice benchmark
invoices_100docs_fresh.yaml          ✅ Updated invoice config
legal_108docs.yaml                   ✅ Legal documents
marker_gap_fill.yaml                 ✅ Gap filling for marker
omnidocbench_english_252.yaml        ✅ English OmniDoc subset
omnidocbench_english_ocr.yaml        ✅ OCR-focused subset
pypdf2_gap_fill.yaml                 ✅ Gap filling for pypdf2
synthetic_missing_parsers.yaml       ✅ Synthetic gaps
```

### Archived Benchmarks (42 files in archive/)

**Recommendation**: ✅ **KEEP - Good archival practice**

Examples:
```
academic_only.yaml
commercial_quick.yaml
comprehensive_31docs_fixed.yaml
cuad_75docs_text_metrics.yaml
element_f1_test.yaml
omnidocbench_193docs.yaml
stratified_sample.yaml
... (35+ more)
```

These are historical/deprecated configs. Good to preserve for reference.

### Naming Convention Issues

**Observation**: Some configs have attribute-laden names that got moved to archive:
- `comprehensive_31docs_fixed.yaml`
- `comprehensive_31docs_remaining.yaml`
- `cuad_75docs_text_metrics.yaml`

Active configs are cleaner:
- `cuad_75docs.yaml`
- `full_corpus_353docs.yaml`
- `invoices_100docs.yaml`

**Recommendation**: Current naming is good. Archive handled the cleanup well.

---

## 3. pdf_bench/metrics/ (13 files)

### All Files (All KEEP)

**Recommendation**: ✅ **KEEP ALL - All actively used**

```
__init__.py                          ✅ Package init with all exports
ast_parser.py                        ✅ Markdown AST parsing for tree metrics
cell_content_f1.py                   ✅ Table cell F1 scoring
edit_distance.py                     ✅ Core edit distance metrics
element_f1.py                        ✅ Element-level F1 scoring
gfm_table_parser.py                  ✅ GitHub-flavored markdown table parsing
latex_matching.py                    ✅ LaTeX expression matching/scoring
latex_normalizer.py                  ✅ LaTeX normalization utilities
markdown_to_html.py                  ✅ Markdown table to HTML conversion
table_normalization.py               ✅ HTML table normalization
teds.py                              ✅ Table Edit Distance Similarity (TEDS)
text_metrics.py                      ✅ ChrF++ scoring
tree_edit_distance.py                ✅ Tree-based edit distance
```

### Usage Analysis

All metrics are imported in `__init__.py` and used throughout:
- **edit_distance.py**: Core metric used in all benchmarks
- **text_metrics.py**: ChrF++ used in most configs
- **tree_edit_distance.py**: Tree similarity metric
- **element_f1.py**: Element-level F1 scoring
- **teds.py**: Table-specific evaluation
- **cell_content_f1.py**: Table cell accuracy
- **latex_matching.py**: Academic paper evaluation

**Verdict**: All 13 files are actively used. No redundancy.

---

## 4. pdf_bench/systems/ (21 files)

### Parser Implementations

**Total**: 21 files (20 parsers + base class)

```
base_parser.py                       ✅ KEEP - Abstract base class
__init__.py                          ✅ KEEP - Registry

Open Source (13):
docling_parser.py                    ⚠️  REVIEW - In pdfsmith?
marker.py                            ⚠️  REVIEW - In pdfsmith?
pymupdf.py                           ⚠️  REVIEW - In pdfsmith?
pymupdf4llm_parser.py                ⚠️  REVIEW - In pdfsmith?
pdfplumber_parser.py                 ⚠️  REVIEW - In pdfsmith?
pypdf_parser.py                      ⚠️  REVIEW - In pdfsmith?
pypdf2_parser.py                     ⚠️  REVIEW - In pdfsmith?
pypdfium2_parser.py                  ⚠️  REVIEW - In pdfsmith?
pdfminer_parser.py                   ⚠️  REVIEW - In pdfsmith?
extractous_parser.py                 ⚠️  REVIEW - In pdfsmith?
unstructured_parser.py               ⚠️  REVIEW - In pdfsmith?
tika_parser.py                       ⚠️  REVIEW - In pdfsmith?
kreuzberg_parser.py                  ⚠️  REVIEW - In pdfsmith?
marker_ollama.py                     ⚠️  REVIEW - Variant of marker

Commercial (4):
aws_textract.py                      ✅ KEEP - Cloud API adapter
azure_document_intelligence.py       ✅ KEEP - Cloud API adapter
google_document_ai.py                ✅ KEEP - Cloud API adapter
databricks_parser.py                 ✅ KEEP - Has real implementation
landing_ai_parser.py                 ✅ KEEP - Has real implementation
```

### Critical Question: PDFSMITH RELATIONSHIP

**From PROJECT_MAP.md**:
> **pdfsmith**: `/home/stefan/applied-ai/pdfsmith/` - Unified PDF parsing library (extracted from this project)

**Key Questions**:
1. Was pdfsmith extracted FROM pdf-bench?
2. Does pdfsmith contain all 13 open-source parsers?
3. Should pdf-bench USE pdfsmith instead of individual implementations?
4. OR are these intentionally separate (pdf-bench = benchmark harness, pdfsmith = library)?

**Current State Analysis**:
- No `pdfsmith` imports found in pdf_bench code
- Each parser is a separate adapter implementing `BaseParser`
- Parsers include cost tracking, caching, metadata specific to benchmarking

**Recommendation**: ⚠️ **INVESTIGATE THEN DECIDE**

**If pdfsmith is the extraction**:
- Consider replacing individual parsers with pdfsmith imports
- Keep only benchmark-specific adapters (BaseParser wrappers)
- Reduces duplication, maintains single source of truth

**If pdfsmith is different**:
- Keep current structure
- These are benchmark adapters with specific requirements (cost tracking, caching)

**Commercial parsers (4)**: ✅ KEEP ALL - These are cloud API adapters not in pdfsmith

---

## 5. builders/ Directory (34 files)

### Corpus Builders (KEEP - Active)

```
build_cuad_corpus.py                 ✅ KEEP - Generates CUAD legal contracts
build_hr_corpus.py                   ✅ KEEP - Generates HR documents
build_legal_corpus.py                ✅ KEEP - Generates legal templates
generate_invoice_corpus.py           ✅ KEEP - Generates invoices
generate_systematic_corpus.py        ✅ KEEP - Generates synthetic test docs
```

### Document Utilities (KEEP - Active)

```
build_docx.py                        ✅ KEEP - DOCX generation utilities
create_docx_templates.py             ✅ KEEP - Template creation
convert_omnidocbench.py              ✅ KEEP - OmniDocBench conversion
pdf_utils.py                         ✅ KEEP - PDF utilities
```

### ArXiv Builders (REVIEW - Partially Active)

```
arxiv_client.py                      ✅ KEEP - ArXiv API client
download_arxiv_corpus.py             ✅ KEEP - Downloads arXiv papers
ar5iv_to_markdown.py                 ⚠️  REVIEW - ArXiv HTML conversion
omnidocbench_to_markdown.py          ⚠️  REVIEW - OmniDoc conversion
improved_txt_to_markdown.py          ⚠️  REVIEW - Text to markdown
test_real_arxiv.py                   ⚠️  REVIEW - Test script
```

### Synthetic Corpus Scripts

```
build_synthetic.py                   ⚠️  REVIEW - Older synthetic builder?
convert_systematic_to_pdf.py         ⚠️  REVIEW - Converts systematic to PDF
generate_docx_corpus.py              ⚠️  REVIEW - DOCX corpus generation
```

**Questions**:
1. `build_synthetic.py` vs `generate_systematic_corpus.py` - Same purpose?
2. Are the ArXiv converters still needed or were they one-time use?
3. `test_real_arxiv.py` - Is this a builder or a test?

**Recommendation**: ⚠️ **CONSOLIDATE**

Keep active builders, archive or remove one-time scripts:
- **KEEP**: CUAD, HR, legal, invoice, systematic corpus builders
- **KEEP**: PDF/DOCX utilities
- **REVIEW**: ArXiv converters - move to archive if one-time use
- **REVIEW**: `build_synthetic.py` - redundant with `generate_systematic_corpus.py`?

---

## 6. docs/ Directory (10 MD files + 1 JSON, 117KB)

### All Files

**Recommendation**: ✅ **KEEP ALL - Well-structured documentation**

```
CORPORA.md                           543 lines  ✅ Corpus descriptions
FINDINGS.md                          432 lines  ✅ Benchmark findings
GROUND_TRUTH_METHODOLOGY.md          261 lines  ✅ GT creation methodology
LAYOUT_STRUCTURE_EVALUATION_STRATEGY.md  274 lines  ✅ Evaluation strategy
LEADERBOARDS.md                      270 lines  ✅ Parser rankings
METHODOLOGY.md                       319 lines  ✅ Benchmark methodology
METRICS.md                           536 lines  ✅ Metric descriptions
PARSER_COVERAGE.md                    58 lines  ✅ Parser coverage matrix
PARSER_COVERAGE.json                          ✅ Machine-readable coverage
PARSERS.md                           513 lines  ✅ Parser descriptions
RESULTS.md                           394 lines  ✅ Results summary
```

### Archive Subdirectory (4 files)

**Recommendation**: ✅ **KEEP - Good archival**

Contains deprecated/historical documentation.

### Documentation Quality

**Strengths**:
- Clear separation of concerns (corpora, parsers, metrics, results)
- Good balance of technical and methodology docs
- Machine-readable + human-readable formats (PARSER_COVERAGE)
- Archived obsolete docs rather than deleting

**No changes needed** - This is well-organized.

---

## 7. tests/ Directory (9 files, 119KB)

### Test Files

```
conftest.py                          3.3KB  ✅ pytest configuration
helpers.py                           7.6KB  ✅ Test helper utilities
__init__.py                            32B  ✅ Package marker
test_config.py                        22KB  ⚠️  NO TEST FUNCTIONS
test_helpers.py                       11KB  ⚠️  NO TEST FUNCTIONS
test_integration.py                   16KB  ⚠️  NO TEST FUNCTIONS
test_loader.py                        20KB  ⚠️  NO TEST FUNCTIONS
test_persistence.py                   19KB  ⚠️  NO TEST FUNCTIONS
test_runner.py                        21KB  ⚠️  NO TEST FUNCTIONS
```

### Analysis

**Found**: 0 `def test_*` functions in all test files

**What's in the files?**:
- `test_runner.py`: Mock classes (`MockParser`) and fixtures
- Other files: Likely similar setup code without actual tests

**Recommendation**: ⚠️ **SKELETAL TESTS - DECIDE TO COMPLETE OR REMOVE**

Options:
1. **Complete the tests** - Add actual test functions to validate components
2. **Remove test files** - If not planning to write tests, remove to avoid confusion
3. **Keep as stubs** - If planning to add tests later

Current state suggests these were scaffolded but never completed.

**Verdict**: Keep `conftest.py` and `helpers.py` (useful infrastructure).
For `test_*.py` files: Either complete them or archive them.

---

## Summary of Recommendations

### Immediate Actions (Quick Wins)

1. **results/ cleanup** - Remove:
   - 42 checkpoint files (`*.checkpoint.json`) - saves 200KB
   - 26 markdown files in root (`*.md`) - saves 30KB, reduces confusion
   - 2 empty debug directories (`debug_teds/`, `debug_element_f1/`)
   - **Potential savings**: ~250KB, -70 files

2. **results/ organization** - Review:
   - `quick/` directory (10 MD files) - likely test outputs
   - `tier1/` directory (252 MD files, 2.3MB) - verify if intentional or cleanup needed

### Investigation Needed

3. **pdfsmith relationship** - Critical decision:
   - Understand extraction: Did pdfsmith come FROM pdf-bench?
   - If yes: Refactor to use pdfsmith, keep only benchmark adapters
   - If no: Document why separate implementations exist
   - Commercial parsers: Keep regardless

4. **builders/ consolidation**:
   - Identify redundant builders (`build_synthetic.py` vs `generate_systematic_corpus.py`)
   - Archive one-time conversion scripts (ArXiv converters)
   - Keep active corpus generators

### Optional Improvements

5. **tests/ completion**:
   - Decide: Complete tests or archive skeletal files
   - Keep: `conftest.py`, `helpers.py`
   - Review: 6 test files with no test functions

6. **benchmarks/archive cleanup**:
   - Archive contains checkpoint files too
   - Consider removing checkpoints from archive (saves ~4MB)

### Keep As-Is

7. **docs/** - ✅ Well-organized, no changes needed
8. **metrics/** - ✅ All actively used, no redundancy
9. **benchmarks/** (active) - ✅ Good organization
10. **results/archive/** - ✅ Good archival practice

---

## File Count Summary

| Directory | Total Files | Keep | Remove | Review |
|-----------|-------------|------|--------|--------|
| results/ | 386 | 22 | 70 | 294 |
| benchmarks/ | 61 | 61 | 0 | 0 |
| metrics/ | 13 | 13 | 0 | 0 |
| systems/ | 21 | 21 | 0 | 13* |
| builders/ | 34 | 10 | 0 | 24 |
| docs/ | 11 | 11 | 0 | 0 |
| tests/ | 9 | 2 | 0 | 7 |

*Systems: All keep, but 13 need investigation re: pdfsmith

---

## Disk Space Analysis

| Directory | Current Size | After Cleanup |
|-----------|--------------|---------------|
| results/ | 16MB | ~13MB (remove checkpoints, MDs, debug) |
| benchmarks/archive/ | 196KB | 196KB (or ~50KB if remove checkpoints) |
| Total savings | - | ~3MB |

---

## Next Steps

### Phase 1: Safe Cleanup (Do Now)
```bash
# Remove checkpoint files
find results/ -name "*.checkpoint.json" -delete

# Remove orphaned MD files from results root
rm results/*.md

# Remove empty debug directories
rmdir results/debug_teds results/debug_element_f1
```

### Phase 2: Investigation (Before Cleanup)
1. Review `results/quick/` and `results/tier1/` - are these intentional?
2. Investigate pdfsmith relationship - check `/home/stefan/applied-ai/pdfsmith/`
3. Review builders/ - identify one-time vs. maintained scripts

### Phase 3: Consolidation (After Investigation)
1. Refactor parser systems based on pdfsmith findings
2. Consolidate or archive builders
3. Complete or archive test files

---

## Questions for User

1. **results/tier1/** (252 MD files, 2.3MB) - Is this intentional organization or test output?
2. **pdfsmith** - Was it extracted from pdf-bench? Should pdf-bench use it?
3. **builders/** - Which ArXiv converters are still needed vs. one-time scripts?
4. **tests/** - Plan to complete tests or remove skeletal files?
5. **Aggressive cleanup** - Remove checkpoints from archive/ too? (saves 4MB)

---

End of audit.
