# 10-Parser Comprehensive Evaluation Results

**Date**: 2025-11-20
**Benchmark**: 31 synthetic documents × 10 open-source parsers = 310 runs
**Success Rate**: 298/310 (96.1%)
**Results Files**:
- `results/comprehensive_31docs_fixed_v2.json` (5 parsers: marker_ollama, pdfplumber, pymupdf, pypdfium2, unstructured)
- `results/comprehensive_31docs_remaining.json` (5 parsers: docling, extractous, pymupdf4llm, pdfminer, pypdf)

---

## Executive Summary

**Docling** (IBM's parser) emerges as the **top overall performer**, leading in element detection (84.1%) and structure preservation (61.2%). However, parser selection depends on use case:

- **Best Overall**: docling (87.4% text, 84.1% element, 61.2% structure) - but 23% failure rate
- **Best Text**: marker_ollama (89.9%) - VLM-based, slower, 16% failure rate
- **Best Tables**: pdfplumber (93.4% TEDS) - specialized for tables
- **Best Speed/Reliability**: pymupdf, pypdfium2, pypdf - 100% success, fast, but weak structure

**Critical Finding**: All parsers show a **50% structure preservation gap** - they extract text well (83.2% avg) but struggle with document hierarchy (33.2% avg).

---

## Complete 10-Parser Rankings

| Rank | Parser | Success | Text Acc | Element F1 | Tree Sim | TEDS | Notes |
|------|--------|---------|----------|------------|----------|------|-------|
| 1 | **docling** | 24/31 (77%) | 87.4% | **84.1%** ✅ | **61.2%** ✅ | 84.5% | IBM, best structure |
| 2 | **marker_ollama** | 26/31 (84%) | **89.9%** ✅ | 69.4% | 49.3% | 80.2% | VLM-based, slow |
| 3 | **pymupdf4llm** | 31/31 (100%) | 86.2% | 68.5% | 47.3% | 84.8% | LLM-optimized |
| 4 | **pdfplumber** | 31/31 (100%) | 70.6% | 69.3% | 38.7% | **93.4%** ✅ | Table specialist |
| 5 | **pypdf** | 31/31 (100%) | 88.1% | 50.4% | 27.5% | N/A | Alternative lib |
| 6 | **pypdfium2** | 31/31 (100%) | 88.3% | 49.9% | 26.8% | N/A | Pure open-source |
| 7 | **extractous** | 31/31 (100%) | 84.3% | 50.1% | 24.6% | N/A | Rust-based |
| 8 | **unstructured** | 31/31 (100%) | 75.9% | 51.7% | 26.6% | N/A | ETL pipeline |
| 9 | **pymupdf** | 31/31 (100%) | 86.4% | 50.6% | 11.2% | N/A | Fast baseline |
| 10 | **pdfminer** | 31/31 (100%) | 74.7% | 51.1% | 19.0% | N/A | Classic Python |

✅ = Category winner

---

## Category Winners

### Text Extraction: marker_ollama (89.9%)
- VLM-based approach (Ollama) provides superior text accuracy
- Uses Llama vision model to understand document layout
- **Trade-off**: Slower (~6s/doc) and 16% failure rate (5/31 timeouts)

### Element Detection: docling (84.1%)
- IBM's recent parser excels at identifying document elements
- 15% better than nearest competitor (marker_ollama 69.4%)
- Accurately detects headings, paragraphs, lists, tables, code blocks

### Structure Preservation: docling (61.2%)
- Only parser above 50% tree similarity
- Preserves heading hierarchy, list nesting, section organization
- 12% better than runner-up (marker_ollama 49.3%)

### Table Extraction: pdfplumber (93.4%)
- Purpose-built table extraction beats general parsers
- 8.6% better than docling (84.5%), 13.2% better than marker (80.2%)
- **Trade-off**: Weak on text (70.6%) and structure (38.7%)

---

## Key Findings

### 1. Structure Preservation Gap: 50%

**All parsers struggle with document structure:**
- Average text accuracy: **83.2%**
- Average tree similarity: **33.2%**
- **Gap: 50 percentage points**

**What this means**: Parsers correctly extract most words but lose:
- Heading levels (H1 vs H2 vs H3)
- List nesting (nested bullets, numbered lists)
- Section hierarchy (document organization)
- Semantic relationships between elements

**Practical impact**:
- RAG systems lose context from document structure
- LLMs can't use headings to understand document organization
- Multi-column layouts often flattened incorrectly

### 2. Docling's Surprising Performance

**IBM's docling parser outperforms established parsers:**
- 84.1% element detection vs ~50% for most parsers (68% improvement!)
- 61.2% structure preservation vs 33.2% average (84% improvement!)
- Only major weakness: 23% failure rate (7/31 documents)

**Why it matters**: First open-source parser to break 60% structure preservation threshold.

**Reliability concern**: 7 failures across document types needs investigation:
- Which document types cause failures?
- Are failures predictable (e.g., multi-column)?
- Can they be caught and recovered?

### 3. VLM vs Traditional Approaches

**marker_ollama (VLM) vs docling (traditional CV/ML)**:

| Metric | marker_ollama | docling | Winner |
|--------|---------------|---------|--------|
| Text | 89.9% | 87.4% | marker (+2.5%) |
| Elements | 69.4% | 84.1% | docling (+14.7%) |
| Structure | 49.3% | 61.2% | docling (+11.9%) |
| Speed | ~6s | ~2s | docling (3× faster) |
| Reliability | 84% | 77% | marker (+7%) |

**Conclusion**: Docling's traditional CV/ML approach beats VLM on structure, loses on text.

### 4. Reliability vs Performance Trade-off

**Perfect reliability (31/31)**:
- pymupdf, pypdfium2, pypdf, extractous, pdfminer, unstructured, pdfplumber, pymupdf4llm
- All basic text extraction libraries

**Imperfect reliability**:
- docling: 24/31 (77%) - but best structure
- marker_ollama: 26/31 (84%) - but best text

**Use case decision**:
- **Production RAG system**: Use reliable parser (pypdfium2) + accept worse structure
- **Research corpus**: Use best quality (docling) + handle failures
- **Hybrid**: Try docling first, fall back to pypdfium2 on failure

### 5. Table Extraction Requires Specialization

**TEDS scores (Table Edit Distance-based Similarity)**:
- pdfplumber: 93.4% (table specialist)
- pymupdf4llm: 84.8% (LLM-optimized, includes table focus)
- docling: 84.5% (general parser)
- marker_ollama: 80.2% (VLM-based)
- Others: No table support

**Insight**: General parsers can't match specialized table extractors. If documents are table-heavy, use pdfplumber for tables + another parser for text/structure.

---

## Detailed Metric Analysis

### Text Accuracy (edit_similarity)

**Top 5**:
1. marker_ollama: 89.9%
2. pypdfium2: 88.3%
3. pypdf: 88.1%
4. docling: 87.4%
5. pymupdf: 86.4%

**Spread**: 89.9% - 70.6% = 19.3 percentage points

**Interpretation**: Most parsers (top 7) within 5% of each other on text. Character extraction is largely solved.

### Element Detection (element_f1)

**Top 5**:
1. docling: 84.1% ✅ (outlier)
2. marker_ollama: 69.4%
3. pdfplumber: 69.3%
4. pymupdf4llm: 68.5%
5. unstructured: 51.7%

**Spread**: 84.1% - 49.9% = 34.2 percentage points

**Interpretation**: Huge variance! Docling 15% ahead of nearest competitor. Element detection is **not solved**.

**What element_f1 measures**:
- Precision/recall of identifying element types (heading vs paragraph vs list vs table)
- Does NOT measure correctness of heading levels or list nesting
- Complements tree_similarity (which measures hierarchical relationships)

### Structure Preservation (tree_similarity)

**Top 5**:
1. docling: 61.2% ✅
2. marker_ollama: 49.3%
3. pymupdf4llm: 47.3%
4. pdfplumber: 38.7%
5. pypdf: 27.5%

**Spread**: 61.2% - 11.2% = 50 percentage points

**Interpretation**: Largest variance of any metric. Structure preservation is the **hardest unsolved problem**.

**What tree_similarity measures**:
- Tree edit distance on Markdown AST
- Heading hierarchy (H1 > H2 > H3)
- List nesting (bullets, numbered, nested)
- Section organization
- Structural relationships between elements

**Why it matters**:
- RAG retrieval quality depends on semantic chunks (sections)
- LLMs use heading structure for long-context reasoning
- Multi-column layouts require correct reading order

### Table Quality (TEDS)

**Parsers with table support** (12 documents with tables):
1. pdfplumber: 93.4% ✅ (37-100% range)
2. pymupdf4llm: 84.8% (63-100% range)
3. docling: 84.5% (59-100% range)
4. marker_ollama: 80.2% (46-100% range)

**What TEDS measures**:
- Table structure accuracy (rows, columns, cells)
- Cell content accuracy (text extraction)
- Weighted sum of structural and content similarity

**pdfplumber's advantage**:
- Purpose-built for table extraction
- Uses geometric analysis (text bounding boxes, line detection)
- Handles complex tables (merged cells, multi-line cells, nested headers)

---

## Parser Profiles

### docling (IBM)
**Best For**: Research, high-quality corpus creation
**Strengths**:
- Element detection: 84.1% (15% ahead of competition)
- Structure preservation: 61.2% (only parser above 60%)
- Balanced performance across text/elements/structure

**Weaknesses**:
- 23% failure rate (7/31 documents)
- Need fallback parser for production

**Use Case**: Corpus creation where quality > reliability

### marker_ollama
**Best For**: Maximum text accuracy with structure
**Strengths**:
- Text: 89.9% (VLM-based superior recognition)
- Structure: 49.3% (2nd best)
- Good tables: 80.2%

**Weaknesses**:
- Slow: ~6s/doc (3× slower than docling)
- 16% failure rate (5/31 timeouts)
- Requires Ollama + Llama vision model

**Use Case**: When text quality is critical and time is available

### pymupdf4llm
**Best For**: Production RAG systems
**Strengths**:
- 100% reliability (31/31)
- Good text: 86.2%
- Good structure: 47.3% (3rd best)
- Good tables: 84.8%
- Fast (~1s/doc)

**Weaknesses**:
- Not best at any single metric
- 16% behind docling on structure

**Use Case**: Balanced production parser with perfect reliability

### pdfplumber
**Best For**: Table-heavy documents
**Strengths**:
- Tables: 93.4% (8.6% ahead of nearest competitor)
- 100% reliability
- Element detection: 69.3% (tied for 2nd)

**Weaknesses**:
- Text: 70.6% (19% behind best)
- Structure: 38.7% (23% behind docling)

**Use Case**: Financial reports, data sheets, academic papers with complex tables

### pypdfium2 / pypdf
**Best For**: Fast, reliable text extraction
**Strengths**:
- Text: 88.1-88.3% (very good)
- 100% reliability
- Very fast (< 0.5s/doc)
- Pure Python, no dependencies

**Weaknesses**:
- Structure: 26-27% (poor)
- Element detection: 49-50% (poor)
- No table support

**Use Case**: Simple documents, speed-critical applications, fallback parser

### pymupdf
**Best For**: Speed baseline
**Strengths**:
- Fastest: < 0.5s/doc
- Good text: 86.4%
- 100% reliability

**Weaknesses**:
- Structure: 11.2% (worst of all parsers)
- Element detection: 50.6%
- No table support

**Use Case**: When speed is paramount and structure doesn't matter

---

## Comparison to OmniDocBench Results

**Framework differences**:
- PDF-Bench: PDF input, Markdown ground truth, 31 synthetic docs
- OmniDocBench: JPEG images, JSON ground truth, 18 real-world docs

**marker_ollama results**:

| Metric | PDF-Bench | OmniDocBench | Notes |
|--------|-----------|--------------|-------|
| Text | 89.9% | 91.1% | Consistent (+1.2%) |
| Structure | 49.3% tree_sim | 92.7% reading_order | Different metrics |
| Tables | 80.2% TEDS | 68.7% TEDS | Real-world harder (-11.5%) |
| Table content | N/A | 38.5% | Cell-level errors |

**Key insight**: Synthetic corpus (PDF-Bench) may be **easier than real-world** for table extraction:
- PDF-Bench TEDS: 80.2%
- OmniDocBench TEDS: 68.7%
- **Gap: 11.5 percentage points**

**Table content accuracy concern**: OmniDocBench shows 38.5% content accuracy despite 83.7% structure detection. This means:
- Table rows/columns correctly detected
- But **61.5% of cell text is wrong**
- Particularly bad on: full-line tables (54% TEDS), scanned notes (35% TEDS)

**Research question**: Is 38.5% content accuracy universal or marker-specific? Need to test pdfplumber (table specialist) on OmniDocBench.

---

## Recommendations

### For Production RAG Systems
1. **Primary**: pymupdf4llm (balanced, 100% reliable, good all-around)
2. **Fallback**: pypdfium2 (fast, reliable, good text)
3. **Tables**: pdfplumber (if table-heavy documents)

**Strategy**: Try pymupdf4llm → fallback to pypdfium2 on failure

### For Research Corpus Creation
1. **Primary**: docling (best structure/elements despite failures)
2. **Fallback**: marker_ollama (best text quality)
3. **Tables**: pdfplumber (best table extraction)

**Strategy**: Docling for most docs, marker_ollama for failed docs, pdfplumber for table-only extraction

### For Speed-Critical Applications
1. **Primary**: pymupdf (< 0.5s/doc, 86.4% text)
2. **Alternative**: pypdfium2 (< 0.5s/doc, 88.3% text, better structure)

**Trade-off**: Accept poor structure (11-27%) for 10× speed improvement

### For Table-Heavy Documents
1. **Primary**: pdfplumber (93.4% TEDS)
2. **Supplement**: docling or pymupdf4llm for text/structure

**Strategy**: Hybrid approach - pdfplumber for tables, docling for structure

---

## Next Steps

### Immediate
1. ✅ Analyze complete 10-parser results
2. ⏳ Investigate docling's 7 failures - which document types?
3. ⏳ Run pdfplumber on OmniDocBench to test 38.5% table accuracy hypothesis
4. ⏳ Update multi_metric_findings.md with docling insights

### Short-Term
1. Test docling + pdfplumber hybrid on table-heavy docs
2. Create failure analysis for marker_ollama and docling
3. Run commercial parsers (AWS Textract, Azure) for comparison
4. Benchmark on real-world corpus (business docs from SEC/GOV.UK)

### Medium-Term
1. Implement reading_order metric (OmniDocBench-style)
2. Create composite score with use-case weights
3. Generate parser selection decision tree
4. Build leaderboard website with filterable metrics

---

## Lessons Learned

### 1. Traditional CV/ML Can Beat VLMs
Docling's non-VLM approach beats marker_ollama (VLM) on structure and elements. VLMs aren't automatically superior for document understanding.

### 2. Perfect Reliability Requires Compromises
8/10 parsers have 100% success rate but weak structure (<28%). High-quality parsers (docling, marker) have 16-23% failure rates.

### 3. Table Extraction Needs Specialists
13% performance gap between pdfplumber (93.4%) and general parsers (~80%). Purpose-built tools still win for specialized tasks.

### 4. Synthetic ≠ Real-World
11.5% TEDS difference between PDF-Bench (synthetic) and OmniDocBench (real). Synthetic results may overestimate production performance.

### 5. Structure Is the Hard Problem
50-point structure preservation gap (83% text - 33% structure). Character extraction is solved, document understanding is not.

---

## Appendix: Raw Statistics

**Total runs**: 310
**Successful**: 298 (96.1%)
**Failed**: 12 (3.9%)

**Failure breakdown**:
- docling: 7 failures (22.6% of total, 2.3% of runs)
- marker_ollama: 5 timeouts (16.1% of total, 1.6% of runs)

**Average metrics** (all parsers):
- Text accuracy: 83.2%
- Element F1: 57.1%
- Tree similarity: 33.2%
- TEDS (4 parsers): 85.7%

**Metric ranges**:
- Text: 70.6% - 89.9% (19.3 point spread)
- Element: 49.9% - 84.1% (34.2 point spread)
- Structure: 11.2% - 61.2% (50.0 point spread)
- TEDS: 80.2% - 93.4% (13.2 point spread)

**Processing time** (31 docs):
- Fast parsers (pymupdf, pypdfium2, pypdf, pdfminer): < 30s total (< 1s/doc)
- Medium parsers (docling, pymupdf4llm, extractous, unstructured, pdfplumber): 30-90s total (1-3s/doc)
- Slow parsers (marker_ollama): ~180s total (~6s/doc)

**Benchmark runtime**:
- 5 parsers (fixed_v2): 24 minutes (8 parallel workers)
- 5 parsers (remaining): 39 minutes (8 parallel workers)
- Total: 63 minutes for 310 runs
- Average: 12 seconds per run (including failed runs)
