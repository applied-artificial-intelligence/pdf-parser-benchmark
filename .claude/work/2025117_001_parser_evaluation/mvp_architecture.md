# PubTabNet MVP Architecture

**Status**: Design Phase
**Goal**: Quality-only leaderboard for table extraction using PubTabNet + TEDS metric

## Components

### 1. Data Pipeline

```
PubTabNet Dataset (HuggingFace)
└─> Download validation split (9,115 samples)
    └─> Each sample contains:
        - image: PNG of table (from PDF)
        - html: Ground truth HTML table structure
        - metadata: source info, bounding boxes, etc.
```

### 2. Parser Interface

**Current parsers** (all output Markdown):
- PyMuPDF (text-based, fast)
- PDFPlumber (layout-aware, good for tables)
- Marker (ML-based, slow but accurate)
- Unstructured (hybrid approach)
- AWS Textract (commercial, requires API key)
- Azure Document Intelligence (commercial, requires API key)

**Parser flow**:
```
PNG image → Parser → Markdown output → Extract tables → Convert to HTML → TEDS score
```

### 3. Table Extraction & Conversion

**Problem**: Parsers output Markdown, TEDS needs HTML

**Solution**:
1. **GFMTableParser** (exists) - Extract Markdown tables from parser output
2. **MarkdownTableToHTML** (new) - Convert GFM table to HTML `<table>` structure
3. **TEDS** (exists) - Compute similarity between pred_html and gt_html

**Conversion logic**:
```python
from pdf_bench.metrics.gfm_table_parser import GFMTableParser

# Extract
parser = GFMTableParser()
tables = parser.extract_tables(markdown_output)

# Convert
for table in tables:
    html = markdown_table_to_html(table)
    score = teds_score(html, ground_truth_html)
```

### 4. Benchmark Runner

```
BenchmarkRunner
├─> Load PubTabNet validation split
├─> For each sample:
│   ├─> Run parser on image
│   ├─> Extract tables from output
│   ├─> Convert to HTML
│   ├─> Compute TEDS score vs ground truth
│   └─> Record result
└─> Generate leaderboard
```

### 5. Results & Leaderboard

**Metrics per parser**:
- Mean TEDS score (structure-only)
- Mean TEDS score (with content)
- Table detection rate (% of samples with ≥1 table extracted)
- Average inference time per image
- Success rate (% without errors)

**Leaderboard format** (quality-only):
```
| Rank | Parser               | TEDS  | TEDS+Content | Detection | Time/img |
|------|---------------------|-------|--------------|-----------|----------|
| 1    | Marker              | 0.85  | 0.78         | 95%       | 2.3s     |
| 2    | PDFPlumber          | 0.72  | 0.65         | 88%       | 0.4s     |
| 3    | AWS Textract        | 0.81  | 0.74         | 92%       | 0.8s     |
...
```

## Implementation Plan

### Phase 1: Core Infrastructure (Today)
1. ✅ Verify TEDS implementation
2. ⏳ Implement MarkdownTableToHTML converter
3. ⏳ Download PubTabNet validation subset (100 samples for testing)
4. ⏳ Implement PubTabNetLoader

### Phase 2: Parser Integration (Next session)
5. Test each parser on sample images
6. Implement BenchmarkRunner
7. Run benchmark on 100 samples

### Phase 3: Full Evaluation & Analysis
8. Run full validation set (9,115 samples)
9. Generate leaderboard
10. Analyze failure modes
11. Write initial findings document

### Phase 4: Cost Analysis (After quality validation)
12. Add cost tracking for commercial APIs
13. Generate cost-quality Pareto frontier
14. Produce quality-per-dollar leaderboard

## Technical Decisions

### Why start with PubTabNet?
- **Focused scope**: Tables only, not full documents
- **We have TEDS**: Metric is already implemented
- **Clear ground truth**: HTML structure is canonical format
- **Validate approach**: If this works, expand to DocLayNet/OmniDocBench

### Why validation split?
- **Manageable size**: 9,115 samples vs 568K full dataset
- **Standard practice**: Validation split is for model evaluation
- **Faster iteration**: Can run full benchmark in hours, not days

### What about parsers that don't detect images?
- PyMuPDF, PDFPlumber work on text-based PDFs
- PubTabNet provides PNG images, not PDFs
- **Solution**: Need OCR layer OR use parsers that support images:
  - Marker (supports images)
  - AWS Textract (image input)
  - Azure Document Intelligence (image input)
  - Unstructured (has image support)

**Decision**: Start with image-capable parsers only, add OCR layer later for text-only parsers

## Open Questions

1. **Image format**: PubTabNet is PNG images. Do all parsers accept PNG, or need PDF conversion?
2. **Multi-table documents**: PubTabNet is single-table images. How to handle multiple tables in output?
3. **API rate limits**: AWS/Azure have rate limits. Need throttling?
4. **GPU usage**: Marker uses GPU. Can we batch process for efficiency?

## Next Steps

1. Implement MarkdownTableToHTML converter
2. Download 100 PubTabNet samples
3. Test one parser end-to-end (Marker or AWS Textract)
4. Validate the full pipeline works
5. Then scale to all parsers

---

**Last Updated**: 2025-11-17
**Author**: Claude
**Status**: Ready for implementation
