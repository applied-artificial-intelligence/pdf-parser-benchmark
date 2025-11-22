# OmniDocBench Integration Plan

**Date**: 2025-11-20
**Status**: Exploration phase

## OmniDocBench Overview

**Publication**: CVPR 2025 (accepted)
**Dataset Size**: 1,355 PDF pages
**GitHub**: https://github.com/opendatalab/OmniDocBench
**HuggingFace**: opendatalab/OmniDocBench

### Coverage
- **9 document types**: Academic papers, financial reports, newspapers, textbooks, handwritten notes, slides, exams, books, research reports
- **4 layout types**: Single-column, double-column, complex multi-column, irregular
- **3 languages**: English, Chinese, mixed
- **15 block-level** annotations: text blocks, tables, formulas, figures, headers, footers, etc. (20K+)
- **4 span-level** annotations: text lines, inline formulas, subscripts, etc. (80K+)

### Key Differences from PDF-Bench

| Aspect | PDF-Bench | OmniDocBench |
|--------|-----------|--------------|
| **Ground Truth Format** | Markdown only | JSON with polygon coordinates + text/LaTeX/HTML |
| **Evaluation Level** | End-to-end (full document) | Multi-level (end-to-end, task-specific, attribute-based) |
| **Metrics** | 6 text/structure metrics | 19 layout categories + specialized metrics (TEDS-S, CDM, COCODet) |
| **Annotation Type** | Text-only | Spatial + text + recognition results |
| **Primary Use Case** | Parser comparison for RAG/LLM | Comprehensive document understanding |

## Integration Options

### Option 1: Full Integration (Convert OmniDocBench → PDF-Bench format)

**Approach**: Convert OmniDocBench JSON to markdown ground truth, run through PDF-Bench pipeline

**Pros**:
- Reuse all existing PDF-Bench infrastructure
- Get immediate parser comparisons on OmniDocBench data
- Consistent evaluation methodology

**Cons**:
- Loses spatial/polygon information
- Ignores layout detection capabilities
- Misses formula LaTeX and table HTML ground truth
- Significant information loss in conversion

**Effort**: Medium (1-2 days)

**Verdict**: ❌ Not recommended - wastes OmniDocBench's rich annotations

### Option 2: Dual Evaluation (Keep both frameworks)

**Approach**: Run PDF-Bench evaluation AND OmniDocBench evaluation separately, compare results

**Pros**:
- No information loss
- Can compare evaluation frameworks themselves
- Maintains strengths of both benchmarks
- Research value: "How do different evaluation methods affect parser rankings?"

**Cons**:
- Requires running two separate evaluation pipelines
- Different metrics make cross-comparison complex
- Duplicate effort for overlapping functionality

**Effort**: Low (setup only, ~half day)

**Verdict**: ✅ Good for research comparison

### Option 3: Extend PDF-Bench with OmniDocBench Metrics

**Approach**: Add OmniDocBench-style evaluation to PDF-Bench (TEDS-S, CDM, layout detection)

**Pros**:
- Single unified evaluation framework
- Best of both worlds
- More comprehensive parser assessment
- Publishable contribution to PDF-Bench

**Cons**:
- Significant engineering effort
- Requires spatial annotation pipeline
- May duplicate OmniDocBench work

**Effort**: High (1-2 weeks)

**Verdict**: ⚠️ Long-term goal, not immediate

### Option 4: Use OmniDocBench as Additional Corpus

**Approach**: Add OmniDocBench PDFs to PDF-Bench corpus, focus on end-to-end markdown evaluation only

**Pros**:
- Simple integration
- Expands PDF-Bench corpus significantly (1,355 pages)
- Diverse document types (newspapers, handwritten notes)
- Can still use our multi-metric framework

**Cons**:
- Need to generate markdown ground truth from OmniDocBench JSON
- Ignores most of OmniDocBench's rich annotations
- Redundant with existing synthetic/business corpora

**Effort**: Medium (conversion pipeline needed)

**Verdict**: ✅ Practical for immediate corpus expansion

## Recommended Approach

**Start with Option 2 (Dual Evaluation)** + Plan for **Option 4 (Corpus Expansion)**

### Phase 1: Dual Evaluation (Immediate - 1 day)

1. Download OmniDocBench dataset (Hugging Face or OpenDataLab)
2. Run PDF-Bench parsers on OmniDocBench PDFs
3. Run OmniDocBench evaluation on same results
4. Compare parser rankings across frameworks
5. Document differences in evaluation methodologies

**Deliverable**: Research document comparing PDF-Bench vs OmniDocBench evaluation results

### Phase 2: Selective Corpus Integration (Short-term - 2-3 days)

1. Identify high-value OmniDocBench document types missing from PDF-Bench:
   - Newspapers (complex multi-column)
   - Handwritten notes (OCR challenge)
   - Exam papers (mixed content)
2. Create JSON → Markdown converter for OmniDocBench ground truth
3. Add selected documents to PDF-Bench corpus
4. Run full multi-metric evaluation

**Deliverable**: Expanded PDF-Bench corpus with challenging real-world documents

### Phase 3: Metric Enhancement (Future - optional)

1. Add layout detection evaluation (COCODet)
2. Add formula-specific metrics (CDM)
3. Add table structure metrics (TEDS-S)
4. Create spatial annotation support

**Deliverable**: Enhanced PDF-Bench with layout-aware evaluation

## Implementation: Phase 1 (Dual Evaluation)

### Step 1: Setup OmniDocBench

```bash
# Clone repo
git clone https://github.com/opendatalab/OmniDocBench.git
cd OmniDocBench

# Install dependencies
conda create -n omnidocbench python=3.10
conda activate omnidocbench
pip install -r requirements.txt

# Download dataset
huggingface-cli download opendatalab/OmniDocBench --repo-type dataset
```

### Step 2: Run PDF-Bench Parsers

```bash
# Create config for OmniDocBench PDFs
cat > benchmarks/omnidocbench_test.yaml <<EOF
name: OmniDocBench Test
corpus_dir: ../OmniDocBench/pdfs
parser_config:
  parsers:
    - pdfplumber
    - pymupdf
    - pypdfium2
    - marker_ollama
metric_config:
  metrics:
    - edit_similarity
    - tree_similarity
    - element_f1
EOF

# Run benchmark
python pdf_bench/main.py run benchmarks/omnidocbench_test.yaml
```

### Step 3: Convert PDF-Bench Results to OmniDocBench Format

Create adapter script:
```python
# scripts/convert_to_omnidocbench.py
def pdfbench_md_to_omnidocbench_json(md_path):
    """Convert PDF-Bench markdown to OmniDocBench JSON format."""
    # Extract text blocks, tables, formulas from markdown
    # Create layout_dets with minimal spatial info
    # Output OmniDocBench-compatible JSON
    pass
```

### Step 4: Run OmniDocBench Evaluation

```bash
cd OmniDocBench
# Configure end2end.yaml to point at converted results
python pdf_validation.py --config configs/end2end.yaml
```

### Step 5: Compare Results

Create comparison analysis:
- Parser rankings in PDF-Bench vs OmniDocBench
- Which metrics correlate? Which diverge?
- Does spatial information change evaluation significantly?

## Open Questions

1. **Ground truth format**: Can we preserve OmniDocBench's rich annotations while using PDF-Bench's markdown format?
2. **Metric alignment**: How do edit_similarity and OmniDocBench's text Edit Distance compare?
3. **TEDS variants**: We use content-aware TEDS, they use structure-only - which is better?
4. **Evaluation philosophy**: End-to-end vs task-specific - which approach better predicts real-world performance?

## Next Steps

1. Download OmniDocBench dataset
2. Inspect actual JSON ground truth format
3. Run 5-10 sample PDFs through PDF-Bench parsers
4. Attempt manual conversion to OmniDocBench format
5. Run OmniDocBench evaluation
6. Compare with PDF-Bench scores

**Time estimate**: 4-6 hours for initial exploration
