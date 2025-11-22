# OmniDocBench Integration - Session Status

**Date**: 2025-11-20 (Updated 2025-11-21)
**Status**: Complete - Comprehensive Benchmark Finished

## Summary

Full 273-document benchmark completed across 10 open-source parsers with domain-specific analysis. Key findings:
- **2,730 runs** (273 docs × 10 parsers), 99.7% success rate
- **Legal documents "solved"**: 4 parsers achieve 98.8% accuracy
- **Invoices expose all parsers**: Best achieves only 49.9%
- **Table specialist confirmed**: pdfplumber leads with 93.4% TEDS
- Results file: `results/full_corpus_353docs.json`
- Analysis: `.claude/work/251120_001_review/273_doc_comprehensive_results.md`

## Completed (Updated 2025-11-21)

### 4. Full Corpus Benchmark (273 docs × 10 parsers) ✅ NEW
**Date**: 2025-11-21
**Results**: 2,730 runs, 99.7% success rate
**File**: `results/full_corpus_353docs.json`
**Analysis**: `.claude/work/251120_001_review/273_doc_comprehensive_results.md`

**Parser Rankings (by edit similarity)**:
| Rank | Parser | Edit Sim | TEDS | Success |
|------|--------|----------|------|---------|
| 1 | pypdfium2 | 78.3% | - | 100% |
| 2 | pypdf | 78.3% | - | 100% |
| 3 | extractous | 77.5% | - | 100% |
| 4 | pymupdf | 77.3% | - | 100% |
| 5 | kreuzberg | 74.9% | - | 100% |
| 6 | pymupdf4llm | 74.7% | 84.8% | 100% |
| 7 | docling | 71.3% | 84.5% | 97.4% |
| 8 | pdfplumber | 70.4% | **93.4%** | 100% |
| 9 | pdfminer | 68.2% | - | 100% |
| 10 | unstructured | 66.5% | - | 100% |

**Domain-Specific Findings**:
- Legal: 98.8% (pypdfium2/pypdf/pymupdf/pdfplumber tie)
- HR/Resumes: 87.8% (unstructured wins)
- Synthetic: 87.5% (kreuzberg/pypdfium2 tie)
- Invoices: 49.9% (all parsers struggle!)

**Metric Correlations**:
- edit_similarity vs CER: -0.978 (near-perfect inverse)
- edit_similarity vs chrF++: 0.739 (strong positive)
- edit_similarity vs tree_similarity: 0.174 (weak - text ≠ structure)

### 1. Fixed element_f1 Metric Bug
**Issue**: Previous "fix" commit didn't actually remove buggy handler code
**Solution**: Removed special-case handler expecting ElementScores object (commit 0f858e2)
**Verification**: Test benchmark (6/6 successful, all values valid 0.46-0.91)

### 2. Complete Multi-Metric Benchmark
**Results**: 31 docs × 5 parsers = 150/155 successful
**File**: `results/comprehensive_31docs_fixed_v2.json` (70KB)
**Duration**: ~24 minutes with 8 workers

**Key Findings**:
- Marker+Ollama: 89.9% text, 69.4% element, 49.3% structure, 80.2% tables
- PDFPlumber: 70.6% text, 69.3% element, 38.7% structure, 93.4% tables
- PyMuPDF: 86.4% text, 50.6% element, 11.2% structure (speed baseline)
- PyPDFium2: 88.3% text, 49.9% element, 26.8% structure
- Unstructured: 75.9% text, 51.7% element, 26.6% structure

**New Insight**: element_f1 measures element type detection, tree_similarity measures hierarchical relationships. PDFPlumber has high element detection (69%) but lower structure (39%) = detects types but loses hierarchy.

### 3. OmniDocBench Setup Complete
**Location**: `/home/stefan/projects/OmniDocBench/`
**Demo Data**: 18 images (JPEG, 200 DPI)
**Status**: ✅ Evaluation ran successfully on existing predictions

**Demo Results**:
- Text blocks: 65% accurate (edit distance 0.351)
- Formulas: 68% accurate (edit distance 0.319)
- Tables: 80% accurate (edit distance 0.203), 78% TEDS
- Reading order: 84% accurate (edit distance 0.161)

## Currently Running

### 1. Marker on OmniDocBench Images
**Command**: `scripts/run_marker_on_omnidocbench.py`
**Status**: Background process abf1da (started 17:14 ET)
**Input**: 18 JPEG images from OmniDocBench demo
**Output**: `/home/stefan/projects/OmniDocBench/demo_data/pdfbench_marker_output/`
**Purpose**: Generate markdown from OmniDocBench images to compare evaluation frameworks

**Next Step**: Once complete, copy Marker outputs to OmniDocBench predictions directory and re-run OmniDocBench evaluation to compare:
- PDF-Bench metrics (edit_similarity, element_f1, tree_similarity)
- OmniDocBench metrics (Edit_dist, TEDS, CDM)

### 2. Remaining Parsers Benchmark (Ready to Run Overnight)
**Config**: `benchmarks/comprehensive_31docs_remaining.yaml`
**Parsers**: docling, extractous, pymupdf4llm, pdfminer, pypdf (5 parsers)
**Command**:
```bash
nohup uv run python pdf_bench/main.py run benchmarks/comprehensive_31docs_remaining.yaml -o results/comprehensive_31docs_remaining.json > /tmp/benchmark_remaining.log 2>&1 &
```
**Duration**: ~30-40 minutes (31 docs × 5 parsers)

## Next Steps

### Immediate (Tonight)
1. ✅ Wait for Marker to finish processing OmniDocBench images (~30-60 min)
2. Copy Marker outputs to OmniDocBench predictions format
3. Run OmniDocBench evaluation on Marker outputs
4. Compare PDF-Bench vs OmniDocBench rankings
5. Start overnight benchmark for remaining 5 parsers

### Short-Term (Tomorrow)
1. Analyze complete 10-parser benchmark results
2. Document framework comparison findings
3. Decide on integration strategy:
   - Option A: Keep separate (research comparison)
   - Option B: Add OmniDocBench as PDF-Bench corpus
   - Option C: Extend PDF-Bench with OmniDocBench metrics

### Research Questions

1. **Do evaluation frameworks rank parsers differently?**
   - PDF-Bench uses markdown-centric metrics (AST-based)
   - OmniDocBench uses document understanding metrics (spatial + content)

2. **Which metrics correlate? Which diverge?**
   - Hypothesis: edit_distance ≈ Edit_dist (text accuracy)
   - Hypothesis: element_f1 + tree_similarity ≈ reading_order (structure)
   - Hypothesis: TEDS consistent across frameworks

3. **Does spatial information change evaluation?**
   - OmniDocBench has polygon annotations
   - PDF-Bench only has text/markdown
   - Impact on parser rankings?

## Files Created/Modified

### Committed
- `pdf_bench/runner.py` - Actual element_f1 fix (0f858e2)
- `.claude/reference/multi_metric_findings.md` - Complete results (2bdf886)
- `benchmarks/element_f1_test.yaml` - Test config
- `benchmarks/comprehensive_31docs_remaining.yaml` - Remaining parsers config

### Uncommitted
- `results/comprehensive_31docs_fixed_v2.json` - Full benchmark results (gitignored)
- `scripts/run_marker_on_omnidocbench.py` - Marker runner for OmniDocBench

### External
- `/home/stefan/projects/OmniDocBench/` - Cloned repo with demo data and evaluation code

## Dependencies Installed

Added to pdf-bench environment for OmniDocBench support:
- tqdm, pycocotools, tabulate, sacrebleu, Levenshtein
- loguru, plotly, func-timeout, mmeval
- apted (tree edit distance for TEDS)
- scikit-image (for CDM formula metric)
- category-encoders

## Environment State

- **Working directory**: `/home/stefan/projects/pdf-bench`
- **Python**: 3.13 (uv environment)
- **OmniDocBench**: Fully functional, all dependencies installed
- **Background processes**:
  - Marker on OmniDocBench (abf1da)
  - Old benchmark runs (can be killed: 576d6e, 1a2c2b, 760137)
