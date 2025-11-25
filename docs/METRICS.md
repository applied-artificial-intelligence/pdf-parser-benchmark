# PDF-Bench Metrics Guide

A practical guide to understanding evaluation metrics for PDF-to-Markdown conversion quality.

---

## Overview

PDF-Bench uses multiple complementary metrics because no single metric captures all aspects of conversion quality. Each metric answers a different question about the parser's output.

| Metric | Question Answered | Range | Best For |
|--------|------------------|-------|----------|
| **Edit Similarity** | How similar is the text overall? | 0.0-1.0 | General quality |
| **Edit Similarity Normalized** | How similar ignoring format? | 0.0-1.0 | Cross-parser comparison |
| **Token Recall** | Were all words extracted? | 0.0-1.0 | Content completeness |
| **ChrF++** | How well does character/word n-gram match? | 0-100 | Translation-style evaluation |
| **CER** | What percentage of characters are wrong? | 0.0-∞ | OCR evaluation |
| **Tree Similarity** | How well is structure preserved? | 0.0-1.0 | Document organization |
| **Element F1** | Are all document elements found? | 0.0-1.0 | Completeness checking |
| **TEDS** | How accurate is table extraction? | 0.0-1.0 | Table-heavy documents |

---

## 1. Edit Similarity (Primary Metric)

**Formula**: `1.0 - (levenshtein_distance / max(len(reference), len(hypothesis)))`

### What It Measures

Character-level similarity between ground truth and parser output after normalization. Intuitive interpretation: "88% edit similarity means 88% of characters match."

### Score Interpretation

| Score | Quality | Typical Issues |
|-------|---------|----------------|
| 95%+ | Excellent | Minor whitespace/punctuation differences |
| 85-95% | Very Good | Some formatting loss, minor text errors |
| 75-85% | Good | Noticeable structure loss, some missing content |
| 65-75% | Acceptable | Significant issues, but core content preserved |
| 50-65% | Poor | Major content loss or order problems |
| <50% | Unusable | Fundamental extraction failure |

### Real Examples from PDF-Bench

**95% Edit Similarity** (Excellent):
```
Ground Truth: "The company reported Q3 revenue of $1.2 billion."
Parser Output: "The company reported Q3 revenue of $1.2 billion"
Difference: Missing period only
```

**78% Edit Similarity** (Good):
```
Ground Truth: "## Financial Summary\n\n| Metric | Value |\n|--------|-------|\n| Revenue | $1.2B |"
Parser Output: "Financial Summary\n\nMetric Value\nRevenue $1.2B"
Difference: Lost heading markup, table structure broken
```

**52% Edit Similarity** (Poor - Multi-column):
```
Ground Truth: "First column text continues here. Second column has different content."
Parser Output: "First Second column column text has continues different here. content."
Difference: Reading order completely wrong (read across instead of down)
```

### When to Use

- **Primary metric** for overall quality assessment
- Good for comparing parsers on the same document
- Easy to communicate to stakeholders

### Limitations

- Doesn't distinguish content errors from formatting errors
- Multi-column reading order problems can tank scores
- Doesn't penalize missing structure (only missing text)

---

## 2. ChrF++ (Character n-gram F-score)

**Source**: Popovic, "chrF: character n-gram F-score for automatic MT evaluation" (2015)

### What It Measures

F-score based on character n-grams (1-6 characters) plus word n-grams. Originally designed for machine translation evaluation. More forgiving of word order variations than edit distance.

### Score Interpretation

| Score | Quality |
|-------|---------|
| 85+ | Excellent |
| 70-85 | Good |
| 55-70 | Acceptable |
| 40-55 | Poor |
| <40 | Unusable |

### When to Use

- Alternative view when edit similarity seems unfair
- Documents with flexible word order
- Comparing across languages (if applicable)

### Relationship to Edit Similarity

ChrF++ and Edit Similarity typically correlate strongly (r > 0.9) but can diverge when:
- Word order differs but content is complete
- Short vs. long n-gram matches differ
- Parser produces paraphrases (rare in extraction)

---

## 3. Character Error Rate (CER)

**Formula**: `levenshtein_distance / len(ground_truth)`

### What It Measures

The percentage of character operations (insertions, deletions, substitutions) needed to transform parser output into ground truth. Standard OCR evaluation metric.

### Score Interpretation

| CER | Quality | Interpretation |
|-----|---------|----------------|
| <5% | Excellent | Near-perfect extraction |
| 5-10% | Good | Minor errors |
| 10-20% | Acceptable | Noticeable but usable |
| 20-40% | Poor | Significant correction needed |
| >40% | Unusable | More errors than correct text |
| >100% | Catastrophic | Output longer and wrong (hallucination) |

### Key Difference from Edit Similarity

CER can exceed 1.0 (100%) when parser output is longer than ground truth and mostly wrong. Edit Similarity is bounded 0.0-1.0.

```
Ground Truth: "Hello"
Parser Output: "Jello World Extra Text Here"
CER: 22/5 = 4.4 (440% error rate!)
Edit Similarity: 0.07 (7%)
```

### When to Use

- OCR quality assessment
- Documents with known text (scanned from digital source)
- Comparing against OCR-specific benchmarks

---

## 4. Tree Similarity (Structure Metric)

**Method**: Parse markdown to AST, compute tree edit distance, normalize

### What It Measures

Structural preservation: heading hierarchy, list nesting, paragraph organization. Two documents can have identical text but different tree similarity if structure differs.

### Score Interpretation

| Score | Quality | Typical Issues |
|-------|---------|----------------|
| 90%+ | Excellent | Structure fully preserved |
| 75-90% | Good | Minor nesting or heading level issues |
| 60-75% | Acceptable | Some structure lost but readable |
| 40-60% | Poor | Significant structure flattening |
| <40% | Unusable | Structure completely lost |

### Real Example

**Document with nested lists:**
```markdown
# Report

1. Introduction
   - Background
   - Objectives
2. Methods
   - Data collection
   - Analysis
```

**Parser A (Tree Similarity 92%)**:
```markdown
# Report

1. Introduction
   - Background
   - Objectives
2. Methods
   - Data collection
   - Analysis
```
(Perfect structure preservation)

**Parser B (Tree Similarity 61%)**:
```markdown
Report

Introduction
- Background
- Objectives
Methods
- Data collection
- Analysis
```
(Lost heading markup, numbered list became flat)

**Parser C (Tree Similarity 34%)**:
```markdown
Report Introduction Background Objectives Methods Data collection Analysis
```
(All structure lost, just text)

### When to Use

- Documents with complex hierarchy (legal, technical)
- RAG applications where structure aids chunking
- Comparing structure-aware vs. text-only parsers

### Limitations

- Computationally expensive for large documents
- Markdown AST may not capture all structure types
- Parser markdown formatting affects scores

---

## 5. Element F1 (Element-Level Precision/Recall)

**Method**: Count document elements by type, compute F1

### What It Measures

Element-level completeness: Did the parser find all headings? All tables? All lists?

### Elements Tracked

| Element | Detection Method |
|---------|------------------|
| Headings | `#`, `##`, etc. lines |
| Paragraphs | Text blocks |
| Lists | `-`, `*`, `1.` patterns |
| Tables | `|---|` patterns |
| Code blocks | Triple backticks |

### Score Components

```
Precision = correct_elements / parser_elements
Recall = correct_elements / ground_truth_elements
F1 = 2 * (precision * recall) / (precision + recall)
```

### Score Interpretation

| F1 | Interpretation |
|----|----------------|
| 95%+ | Found nearly all elements correctly |
| 80-95% | Found most elements, some missed |
| 60-80% | Significant element detection issues |
| <60% | Major element detection failures |

### Example Analysis

**Ground Truth**: 5 headings, 10 paragraphs, 3 tables, 2 lists
**Parser Output**: 4 headings, 12 paragraphs, 2 tables, 0 lists

```
Headings:    Precision=4/4=1.0   Recall=4/5=0.8   F1=0.89
Paragraphs:  Precision=10/12=0.83  Recall=10/10=1.0  F1=0.91
Tables:      Precision=2/2=1.0   Recall=2/3=0.67  F1=0.80
Lists:       Precision=0/0=N/A   Recall=0/2=0.0   F1=0.0
Overall:     Weighted F1 ≈ 0.65
```

**Diagnosis**: Parser converts lists to paragraphs and misses one table.

### When to Use

- Debugging why text metrics are low
- Understanding parser failure modes
- Documents with specific element requirements

---

## 6. TEDS (Tree Edit Distance Similarity)

**Source**: Zhong et al., "Image-based Table Recognition: Data, Model, and Evaluation" (PubTabNet, 2019)

### What It Measures

Table structure accuracy using tree representation. The gold standard for table extraction evaluation.

### How It Works

1. Parse table to tree structure:
   - Root → rows → cells
   - Includes rowspan/colspan attributes
2. Compute tree edit distance between predicted and ground truth
3. Normalize to 0.0-1.0 similarity

### Score Interpretation

| TEDS | Quality | Typical Issues |
|------|---------|----------------|
| 90%+ | Excellent | Minor cell content differences |
| 75-90% | Good | Some structure errors, content mostly correct |
| 60-75% | Acceptable | Noticeable structure problems |
| 40-60% | Poor | Significant row/column errors |
| <40% | Unusable | Table structure not recognized |

### Real Example

**Ground Truth Table**:
```
| Product | Q1 | Q2 | Q3 |
|---------|-----|-----|-----|
| Widget A | 100 | 150 | 200 |
| Widget B | 80 | 90 | 110 |
```

**Parser A (TEDS 98%)**:
```
| Product | Q1 | Q2 | Q3 |
|---------|-----|-----|-----|
| Widget A | 100 | 150 | 200 |
| Widget B | 80 | 90 | 110 |
```
(Perfect extraction)

**Parser B (TEDS 72%)**:
```
| Product Q1 Q2 Q3 |
|------------------|
| Widget A 100 150 200 |
| Widget B 80 90 110 |
```
(Header row merged, columns lost)

**Parser C (TEDS 31%)**:
```
Product Q1 Q2 Q3
Widget A 100 150 200
Widget B 80 90 110
```
(No table structure at all)

### When to Use

- Documents with important tables (invoices, financial reports)
- Comparing table extraction capabilities
- Any document where tabular data matters

### Limitations

- Only measures tables, ignores rest of document
- Complex tables (merged cells, nested headers) are challenging for all parsers
- Requires table detection first

---

## Metric Selection Guide

### By Document Type

| Document Type | Primary Metric | Secondary Metrics |
|---------------|----------------|-------------------|
| **General text** | Edit Similarity | ChrF++ |
| **Legal contracts** | Edit Similarity | Tree Similarity |
| **Financial reports** | TEDS | Edit Similarity |
| **Invoices** | TEDS | Element F1 |
| **Resumes** | Element F1 | Tree Similarity |
| **Academic papers** | Edit Similarity | Tree Similarity |
| **Scanned documents** | CER | Edit Similarity |

### By Use Case

| Use Case | Recommended Metrics |
|----------|---------------------|
| **RAG pipelines** | Edit Similarity, Tree Similarity |
| **Data extraction** | TEDS, Element F1 |
| **Document search** | Edit Similarity, ChrF++ |
| **Compliance/legal** | Edit Similarity, Tree Similarity |
| **OCR comparison** | CER, Edit Similarity |

---

## Aggregation Methods

### Per-Document vs. Aggregate Scores

PDF-Bench computes both:
1. **Per-document scores**: Individual scores for each document
2. **Aggregate scores**: Mean across all documents

### Handling Edge Cases

| Situation | Handling |
|-----------|----------|
| Parser timeout | Score = 0.0, flagged as failure |
| Empty output | Score = 0.0 (or normalized appropriately) |
| No tables (for TEDS) | Excluded from TEDS average |
| Parser crash | Score = 0.0, logged as error |

### Weighted Averages

For mixed corpora, consider document-weighted averages:
- Complex documents shouldn't dominate scores
- Balance representation across document types

---

## 7. Format-Agnostic Metrics (NEW)

**Critical Discovery**: Standard edit distance metrics can **penalize parsers for helpful formatting**.

### The Problem

When comparing parser output to ground truth, traditional metrics measure character-level similarity. But parsers produce different output formats:

| Parser | Output Format | Example |
|--------|--------------|---------|
| Azure Document Intelligence | Plain text | `Invoice Item 1 $100` |
| Databricks | Markdown headers | `## INVOICE\n\n### Item 1\n$100` |
| Google Document AI | Markdown headers | `# Invoice\n## Item 1\n$100` |
| AWS Textract | Plain text | `INVOICE Item 1 $100` |

**The result**: Parsers that add structure (headers, tables, bullets) score **lower** even if content extraction is perfect.

### Real-World Impact

From our commercial parser benchmark:

| Parser | Raw Score | Format-Agnostic | Delta | Interpretation |
|--------|-----------|-----------------|-------|----------------|
| Azure | 87.6% | 88.4% | +0.8% | Already plain text |
| **Databricks** | 73.8% | **87.5%** | **+13.7%** | Markdown adds structure |
| AWS | 76.5% | 77.3% | +0.8% | Plain text output |
| Google | 75.2% | 76.8% | +1.6% | Light markdown |

**Key insight**: Databricks jumped **+13.7 points** when measuring content instead of format. The parser was being penalized for adding markdown headers like `## PROFESSIONAL SUMMARY`.

### Format-Agnostic Metrics

**Edit Similarity Normalized** (`edit_similarity_normalized`)
- Strips markdown syntax before comparison
- Removes: headers (`#`), bullets (`-`, `*`), tables, emphasis
- Measures content accuracy independent of formatting

**Token Recall** (`token_recall`)
- Extracts words/tokens from both texts
- Computes: `|ground_truth_tokens ∩ parser_tokens| / |ground_truth_tokens|`
- Answers: "Did the parser extract all the words?"

### Implementation

```python
from pdf_bench.metrics import edit_similarity_normalized, token_recall

ground_truth = "Invoice\nItem 1\n$100"
parser_output = "## Invoice\n\n### Item 1\n\n$100"

# Raw edit similarity: ~70% (penalized for markdown)
# Format-agnostic: ~95% (content matches)
normalized = edit_similarity_normalized(ground_truth, parser_output)
recall = token_recall(ground_truth, parser_output)
```

### When to Use

| Metric | Use When |
|--------|----------|
| **Raw Edit Similarity** | Ground truth format matches expected output format |
| **Format-Agnostic** | Comparing parsers with different output styles |
| **Token Recall** | Only care about content extraction, not structure |

### Important Caveat

Format-agnostic metrics **don't measure structure quality**. A parser that flattens all structure to plain text will score the same as one that preserves hierarchy. Use Tree Similarity (Section 4) for structure evaluation.

---

## Normalization Applied

Before computing metrics, both ground truth and parser output undergo normalization:

1. **Unicode NFC**: Canonical character composition
2. **Whitespace**:
   - CRLF/CR → LF
   - Tabs → spaces
   - Multiple spaces → single space
   - Trim line whitespace
   - Collapse multiple blank lines
3. **Quotes**: Smart quotes → straight quotes

### Why Normalize?

PDFs can encode the same character differently. Parsers produce varying whitespace. Without normalization, superficial differences inflate error rates.

**Example**:
```
Ground Truth: "The company's revenue..." (smart quote)
Parser Output: "The company's revenue..." (straight quote)

Without normalization: Different characters → penalized
With normalization: Same characters → no penalty
```

---

## References

### Academic Papers

- **TEDS**: Zhong et al., "Image-based Table Recognition: Data, Model, and Evaluation" (PubTabNet, 2019)
- **ChrF++**: Popovic, "chrF: character n-gram F-score for automatic MT evaluation" (2015)
- **Tree Edit Distance**: Zhang & Shasha algorithm (1989)

### Benchmark Standards

- **PubTabNet**: Table structure evaluation (TEDS origin)
- **DocLayNet**: Layout analysis evaluation
- **OmniDocBench**: Comprehensive document parsing evaluation

### Implementation

See `pdf_bench/metrics/` for implementation details:
- `text_metrics.py`: Edit Similarity, ChrF++, CER
- `teds.py`: Table Edit Distance Similarity
- `tree_edit_distance.py`: Tree Similarity
- `element_f1.py`: Element-level F1

---

*This guide accompanies the PDF-Bench benchmarking framework. For methodology details, see [METHODOLOGY.md](METHODOLOGY.md). For parser comparisons, see [PARSERS.md](PARSERS.md).*
