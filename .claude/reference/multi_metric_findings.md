# Multi-Metric Evaluation: Key Findings

**Date**: 2025-11-20
**Context**: PDF-Bench multi-metric implementation and evaluation

## Executive Summary

Multi-metric evaluation of PDF parsers reveals a **critical structure preservation gap**: all parsers achieve 70-90% text accuracy but lose 31-89% of document structure. Element-level detection (element_f1) shows similar patterns, with leading parsers at ~69% and others at 50-52%. This finding challenges the common practice of evaluating parsers solely on text similarity.

**Updated with complete benchmark results** (31 docs × 5 parsers, 150/155 successful).

## The Structure Preservation Gap

### Text vs Structure Performance

**Comprehensive Benchmark Results** (31 docs × 5 parsers):

| Parser | Docs | Text (edit) | Element (F1) | Structure (tree) | Tables (TEDS) |
|--------|------|-------------|--------------|------------------|---------------|
| **Marker+Ollama** | 26/31 | **89.9%** | **69.4%** | **49.3%** | 80.2% |
| **PDFPlumber** | 31/31 | 70.6% | **69.3%** | 38.7% | **93.4%** |
| PyMuPDF | 31/31 | 86.4% | 50.6% | 11.2% | N/A |
| PyPDFium2 | 31/31 | 88.3% | 49.9% | 26.8% | N/A |
| Unstructured | 31/31 | 75.9% | 51.7% | 26.6% | N/A |

**Gap Analysis**:
- Average text accuracy: 82.2%
- Average element detection: 58.2%
- Average structure preservation: 30.5%
- **Text-to-structure gap**: 51.7 percentage points
- **Element-to-structure gap**: 27.7 percentage points

### What Gets Lost

The structure preservation gap manifests as:

1. **Lists** → Plain paragraphs
   - Nested list hierarchies flattened
   - Bullet formatting lost
   - Indentation removed

2. **Tables** → Unstructured text
   - Cell boundaries lost
   - Column alignment missing
   - Header/data distinction gone

3. **Headings** → Regular text
   - Heading levels not detected
   - Document hierarchy flattened
   - Section structure lost

4. **Formatting** → Plain text
   - Multi-column layouts linearized
   - Text blocks reordered incorrectly
   - Visual structure ignored

## Metric-Specific Insights

### element_f1: Element Detection Accuracy

**Bug History**:
1. Initial "fix" (commit 104c5ab) claimed to remove buggy handler but code remained
2. Actual fix (commit 0f858e2): Removed special-case handler expecting ElementScores object
3. Wrapper correctly returns float directly, stored as-is in metrics dict

**Results** (comprehensive benchmark with fix):
- **Marker**: 69.4% F1 (best element detection)
- **PDFPlumber**: 69.3% F1 (nearly identical to Marker)
- Unstructured: 51.7% F1
- PyMuPDF: 50.6% F1
- PyPDFium2: 49.9% F1 (worst)

**Key Finding**: Marker and PDFPlumber both excel at element detection (~69%), significantly outperforming other parsers (50%). This contrasts with tree_similarity where Marker leads by wider margin (49% vs 39%).

**Interpretation**:
- **element_f1** measures element type detection (heading vs paragraph vs list)
- **tree_similarity** measures structural relationships and hierarchy
- High element_f1 + low tree_sim = detects elements but loses relationships
- PDFPlumber shows this pattern: 69% element detection, 39% structure preservation

### TEDS: Table Structure Evaluation

**Initial Bug**: Structure-only TEDS returned 1.0 for tables with correct structure but missing cell content.

**Root Cause**: `teds_score()` only compares table structure (rows/columns, not cell text):
- Ground truth: `<th>Sales Data</th>`
- Parser output: `<th></th>` (empty header)
- Structure-only TEDS: 1.0 (identical structure)
- Content-aware TEDS: 0.947 (penalizes missing content)

**Fix**: Switched to `teds_score_with_content()` which includes cell text in comparison.

**Results** (comprehensive benchmark):
- **PDFPlumber**: 93.4% (excellent table preservation)
- **Marker**: 80.2% (good table preservation)
- PyMuPDF/PyPDFium2/Unstructured: N/A (no table documents or failed extraction)

**Insight**: PDFPlumber leads table extraction by 13 percentage points over Marker. Content-aware TEDS correctly discriminates table quality, unlike structure-only variant which gave false 1.0 scores.

### tree_similarity: Markdown AST Comparison

**Performance Range**: 11.2% - 49.3%

**Marker Leadership**: Marker achieves 49.3% structure preservation through:
- Better heading detection (69% element F1)
- List hierarchy preservation
- Multi-column layout handling
- Table structure recognition (80% TEDS)

**PDFPlumber Middle Ground**: 38.7% structure preservation despite:
- Excellent element detection (69% element F1)
- Best table extraction (93% TEDS)
- **Gap**: Detects elements correctly but loses hierarchical relationships

**PyMuPDF Failure Mode**: 11.2% structure preservation because:
- Extracts text in reading order but loses all structure (50% element F1)
- No list detection
- No table detection as markdown
- No heading recognition
- Pure text extraction optimized for speed, not structure

## Research Implications

### Current Evaluation Practice is Inadequate

Most PDF parser benchmarks use only text similarity (edit distance, BLEU, etc.). Our findings show this misses the majority of quality issues:

- **Text-only evaluation**: "Parser A and B both score 93% - they're equivalent"
- **Multi-metric evaluation**: "Parser A preserves 49% of structure, Parser B only 12% - they're vastly different"

### Why Structure Matters

Document structure is critical for:

1. **RAG Systems**: Need to preserve semantic boundaries (sections, lists, tables)
2. **Document Understanding**: Structure provides context for LLMs
3. **Search & Retrieval**: Headings and sections enable better chunking
4. **Data Extraction**: Tables and lists contain structured information
5. **Accessibility**: Screen readers depend on proper document structure

### The "Good Enough" Trap

Text similarity of 90%+ creates false confidence. Users assume parsers are "good enough" when they actually:
- Scramble list items
- Lose table structure
- Flatten heading hierarchies
- Break document flow

## Metric Implementation Lessons

### 1. Test in Isolation AND Integration

**TEDS Case Study**:
- Isolated test: Wrapper correctly returned 1.0, 0.75, NaN ✓
- Integration test: All real benchmarks returned 1.0 or NULL ✗
- **Lesson**: Always verify fixes with real parser outputs, not just unit tests

### 2. Understand What Metrics Actually Measure

**TEDS Structure-Only vs Content-Aware**:
- Structure-only: Perfect for OCR/detection evaluation
- Content-aware: Better for end-to-end parser evaluation
- **Lesson**: Choose metric variant based on what you're testing

### 3. Null/NaN Handling is Critical

**Common Pattern**:
```python
if gt_html is None or pred_html is None:
    return float("nan")  # Not 0.0 or 1.0!
```

**Lesson**: NaN preserves information ("metric not applicable") vs 0.0 ("metric computed, total failure")

### 4. Metadata Validation Can Hide Issues

**Our Bug**: Validation rejected 73% of corpus, silently reducing benchmark from 31 to 7 documents.

**Lesson**: Validation errors should be loud failures, not silent filtering.

## Recommendations

### For PDF-Bench Development

1. **Default to multi-metric evaluation**: Don't rely on text similarity alone
2. **Report structure gap explicitly**: Make it a first-class metric
3. **Create structure-focused benchmark**: Pure synthetic docs testing structure preservation
4. **Add visual diff tool**: Show side-by-side GT vs parsed markdown with structure highlighting

### For Parser Selection

1. **Match parser to use case**:
   - RAG/LLM: Choose high structure preservation (Marker, PyPDFium2)
   - Full-text search: Text accuracy sufficient (PyMuPDF, PDFPlumber)
   - Table extraction: Specialized tool (PDFPlumber) + post-processing
   - Speed critical: PyMuPDF acceptable if structure not needed

2. **Test on your document types**: Synthetic corpus may not reflect your PDFs

3. **Consider parser combination**: Use PyMuPDF for speed + Marker for structure on complex docs

### For Future Research

1. **Reading order metric**: Currently missing, manual analysis required
2. **Visual layout preservation**: How well does markdown reflect PDF visual structure?
3. **Error attribution**: Which PDF features cause structure loss?
4. **Parser combination strategies**: Can we merge outputs for best results?

## Conclusion

The structure preservation gap is the most significant finding from multi-metric evaluation. Text accuracy alone provides an incomplete and misleading view of parser quality. Future PDF parser development and evaluation must prioritize structural fidelity alongside text accuracy.

**Key Metric**: Structure Preservation Rate = tree_similarity / edit_similarity
- Ideal: 1.0 (structure preserved proportional to text)
- Current best: 0.55 (Marker: 49.3% / 89.9%)
- Current worst: 0.13 (PyMuPDF: 11.2% / 86.4%)
- Middle ground: 0.55 (PDFPlumber: 38.7% / 70.6% - lower text but better structure ratio)

**Element Detection Rate** = element_f1 / edit_similarity (measures type detection vs text accuracy):
- PDFPlumber: 0.98 (69.3% / 70.6%) - detects nearly all element types present in extracted text
- Marker: 0.77 (69.4% / 89.9%) - extracts more text but misses some element types
- PyMuPDF: 0.59 (50.6% / 86.4%) - extracts text but loses element types

These ratios reveal which parsers prioritize structure vs pure text extraction, and element type detection vs text completeness.
