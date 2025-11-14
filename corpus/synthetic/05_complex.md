# PDF-Bench: Comprehensive Evaluation Document

This document combines all Markdown features to provide a comprehensive test of PDF parsing capabilities. It includes headings, paragraphs, lists, tables, math, code blocks, and various formatting.

## Executive Summary

PDF parsing systems face the fundamental challenge of extracting structured content from a format designed for visual presentation. The **PDF-Bench** project addresses this by providing:

1. A diverse, openly-licensed corpus of ~150 documents
2. Multiple evaluation metrics (character, structure, and domain-specific)
3. Standardized benchmarking infrastructure
4. Support for both open-source and commercial parsers

## Background and Motivation

### The PDF Parsing Problem

PDFs store content as positioned *glyphs* rather than structured text. Consider the implications:

- **Reading order**: Not explicitly encoded, must be inferred from coordinates
- **Tables**: Just positioned text cells, require sophisticated detection
- **Math**: May be images, text, or embedded fonts
- **Multi-column layouts**: Require column detection before text ordering

### Existing Solutions

Current PDF parsing approaches:

| Approach | Examples | Strengths | Limitations |
|----------|----------|-----------|-------------|
| Rule-based | PyMuPDF, pdfplumber | Fast, deterministic | Poor structure detection |
| Vision-based | Marker, Nougat | Good layout analysis | Requires GPU, slower |
| Commercial API | Textract, Azure DI | High accuracy | Cost, privacy concerns |

## Methodology

### Corpus Design

Our corpus spans three categories:

1. **Synthetic** (50 docs)
   - Created from Markdown via Pandoc
   - Perfect ground truth
   - Controlled feature coverage
2. **Business** (50 docs)
   - GOV.UK publications: $n=30$
   - SEC EDGAR filings: $n=20$
   - Real-world structure complexity
3. **Academic** (50 docs)
   - arXiv papers from cs.CL, cs.CV, math
   - Heavy math and tables
   - Multi-column layouts

### Evaluation Metrics

We employ a multi-level evaluation framework:

#### Character-Level Metrics

**Normalized Edit Distance**: Measures character-level similarity after normalization (Unicode NFC, whitespace collapsing, smart quote conversion).

$$\text{similarity} = 1 - \frac{\text{edit\_distance}(s_1, s_2)}{\max(\text{len}(s_1), \text{len}(s_2))}$$

**chrF++**: Character n-gram F-score from machine translation:

$$\text{chrF++} = (1 + \beta^2) \cdot \frac{\text{Precision} \cdot \text{Recall}}{\beta^2 \cdot \text{Precision} + \text{Recall}}$$

#### Structure-Level Metrics

**AST Tree-Edit Distance**: Compares Markdown AST structure:

1. Parse both documents to AST using `mistune`
2. Convert AST to `zss` tree representation
3. Calculate tree-edit distance
4. Normalize to $[0, 1]$ similarity score

**Element F1 Score**: Precision and recall of Markdown elements:

$$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

#### Domain-Specific Metrics

**TEDS (Table Edit Distance Score)**: For table structure:

- Converts tables to HTML
- Calculates tree-edit distance on DOM
- Normalizes attributes and whitespace

**LaTeX String Matching**: For mathematical notation:

```python
def latex_f1(ground_truth: str, prediction: str) -> float:
    gt_math = extract_latex(ground_truth)
    pred_math = extract_latex(prediction)

    gt_normalized = normalize_latex(gt_math)
    pred_normalized = normalize_latex(pred_math)

    matches = sum(1 for eq in gt_normalized if eq in pred_normalized)
    precision = matches / len(pred_normalized) if pred_normalized else 0
    recall = matches / len(gt_normalized) if gt_normalized else 0

    return 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
```

## Baseline Results

### Overall Performance

Aggregate scores across full corpus (mean ± std):

| Parser | Edit Similarity | AST-TED | Element F1 | TEDS | LaTeX F1 |
|--------|---------------:|--------:|-----------:|-----:|---------:|
| PyMuPDF | 0.89 ± 0.12 | 0.65 ± 0.18 | 0.72 ± 0.15 | 0.42 ± 0.23 | 0.38 ± 0.31 |
| Marker | 0.93 ± 0.08 | 0.81 ± 0.12 | 0.85 ± 0.11 | 0.76 ± 0.15 | 0.71 ± 0.19 |
| Nougat | 0.91 ± 0.11 | 0.79 ± 0.14 | 0.82 ± 0.13 | 0.68 ± 0.19 | 0.83 ± 0.12 |
| AWS Textract | 0.95 ± 0.06 | 0.87 ± 0.09 | 0.89 ± 0.08 | 0.84 ± 0.11 | 0.76 ± 0.16 |

### Category Breakdown

Performance varies by document category:

1. **Synthetic**: All parsers >0.90 (controlled complexity)
2. **Business**: Wide variation (0.75-0.92) due to complex tables
3. **Academic**: Nougat excels (0.88) vs PyMuPDF (0.73) on math-heavy content

### Cost Analysis

For commercial APIs processing the full corpus:

- **AWS Textract**: ~$600 (150 docs × 15.6 avg pages × $0.25/page)
- **Azure DI**: ~$525 (volume discount tier)
- **Total runtime**: 3.2 hours (parallelized on 8 cores)

## Discussion

### Key Findings

Our benchmark reveals several insights:

- **No universal winner**: Best parser depends on document type
- **Open-source competitive**: Marker approaches commercial quality on many documents
- **Math is hard**: LaTeX extraction remains challenging for most parsers
- **Tables critical**: TEDS scores show table extraction is a major differentiator

### Limitations

This benchmark has limitations:

1. Corpus size (150 docs) is modest compared to vision benchmarks
2. Ground truth quality varies by source
3. Metrics don't capture semantic meaning
4. Limited coverage of non-Latin scripts

### Future Work

Planned enhancements:

- [ ] Expand corpus to 500+ documents
- [ ] Add image caption evaluation
- [ ] Include non-English documents
- [ ] Semantic similarity metrics
- [ ] Interactive error analysis tool

## Conclusion

**PDF-Bench** provides a rigorous, reproducible framework for evaluating PDF-to-Markdown conversion systems. By combining diverse corpora, multi-level metrics, and standardized infrastructure, we enable:

- **Developers** to benchmark and improve parsing systems
- **Researchers** to measure progress on document understanding
- **Practitioners** to select appropriate tools for their use cases

The project is open-source (MIT license) and available at: `https://github.com/example/pdf-bench`

## References

1. Gebru, T., et al. (2018). "Datasheets for datasets." *Communications of the ACM*, 64(12), 86-92.
2. Graliński, F., et al. (2019). "chrF++: words helping character n-grams." *WMT 2019*.
3. Zhong, X., et al. (2020). "Image-based table recognition: data, model, and evaluation." *ECCV 2020*.

## Appendix: Code Example

Basic usage example:

```python
from pdf_bench.core import BenchmarkRunner
from pdf_bench.systems import PyMuPDFParser, MarkerParser

# Load configuration
config = BenchmarkRunner.load_config("benchmarks/quick_test.yaml")

# Initialize runner
runner = BenchmarkRunner(
    parsers=[PyMuPDFParser(), MarkerParser()],
    metrics=["edit_similarity", "ast_ted", "element_f1"],
    output_dir="results/"
)

# Run benchmark
results = runner.run(config)

# Generate report
runner.generate_report(results, "report.html")
```

---

*This document exercises all major Markdown features for comprehensive PDF parser evaluation.*
