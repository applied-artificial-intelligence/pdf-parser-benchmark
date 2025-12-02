# PDF Parser Benchmark: Content Marketing Framework

This document provides the conceptual framework for presenting pdf-bench results in content marketing materials. It explains the multi-dimensional nature of PDF parsing, our evaluation methodology, and how to present results fairly.

## The Core Insight: PDF Parsing is Not One Problem

The question "What's the best PDF parser?" is unanswerable because PDF parsing involves **multiple orthogonal capabilities**:

| Capability | What It Means | Who Needs It |
|------------|---------------|--------------|
| **Text Extraction** | Getting text from digital PDFs | Everyone |
| **OCR** | Reading scanned/image PDFs | Scanning workflows, legacy docs |
| **Structure Recovery** | Detecting headings, lists, sections | RAG pipelines, documentation |
| **Table Extraction** | Parsing tabular data | Financial, scientific, legal |
| **Output Quality** | Clean markdown, semantic markup | LLM input, publishing |

A parser can excel at one and fail at another. **The right parser depends on your use case.**

---

## Understanding Our Metrics

We use multiple metrics because each measures a different aspect of parsing quality:

### 1. Text Accuracy Metrics

These measure whether the parser extracted the **correct text content**.

| Metric | What It Measures | Interpretation |
|--------|------------------|----------------|
| **edit_similarity** | Levenshtein similarity (0-1) | Higher = more accurate text |
| **chrf++** | Character n-gram F-score (0-100) | Higher = better; more robust to formatting |
| **character_error_rate** | CER (0-∞) | Lower = better; 0 is perfect |

**When these matter:** Always. If the text is wrong, nothing else matters.

**What low scores mean:**
- On digital PDFs → Parser bug or poor text layer handling
- On scanned PDFs → OCR quality issue or missing OCR capability

### 2. Structure Recovery Metrics

These measure whether the parser correctly identified document **structure and layout**.

| Metric | What It Measures | Interpretation |
|--------|------------------|----------------|
| **tree_similarity** | AST comparison of document structure | Higher = better structure preservation |
| **element_f1** | Precision/recall of element types | Higher = correct element detection |

**When these matter:** RAG pipelines, semantic search, documentation systems, any use case where you need to know "this is a heading" vs "this is body text".

**What low scores mean:**
- Parser treats everything as flat text (no structure awareness)
- Heading levels are wrong
- Lists not detected as lists

**Key insight:** A parser can have HIGH edit_similarity but LOW tree_similarity. This means it got all the text but lost the structure—it's a "text dump" parser.

### 3. Table Extraction Metric

| Metric | What It Measures | Interpretation |
|--------|------------------|----------------|
| **teds** | Table Edit Distance Similarity (0-1) | Higher = better table structure |

**When this matters:** Financial documents, scientific papers, legal contracts, any document with important tabular data.

**What low scores mean:**
- Tables extracted as plain text (lost row/column structure)
- Cell contents merged or split incorrectly
- Table not detected at all

---

## Parser Capability Categories

Based on our research, parsers fall into distinct capability tiers:

### NEW: Tier 0: Frontier LLMs (Highest Quality, Highest Cost)

| Parser | Key Strengths | Key Weaknesses |
|--------|---------------|----------------|
| **GPT-5.1** | Best accuracy (92%), excellent structure | ~$0.05/page, API latency |
| **Gemini 3 Pro** | Strong accuracy (87%), good balance | ~$0.03/page |
| **Claude Sonnet 4.5** | Good accuracy (80%), Anthropic ecosystem | ~$0.04/page |

**Use when:** Maximum quality required, low volume, cost not primary concern

### Tier 0.5: Budget LLMs & LlamaParse (LLM Quality, Lower Cost)

| Parser | Key Strengths | Key Weaknesses |
|--------|---------------|----------------|
| **LlamaParse** | Purpose-built for PDF, 78% accuracy, $0.003/page | Cloud dependency |
| **Gemini 2.0 Flash** | Cheapest LLM (77%), ~$0.001/page | Lower than premium |
| **GPT-4o-mini** | Cheap but 13% tree similarity | **Destroys structure** |
| **Claude 3.5 Haiku** | Budget Anthropic option (68%) | Lowest accuracy |

**Use when:** Want LLM quality without premium costs. **LlamaParse is the sweet spot.**

**Warning:** GPT-4o-mini has only 13% tree similarity—avoid for RAG where structure matters.

### Tier 1: Full-Featured (OCR + Tables + Structure + ML)

| Parser | Key Strengths | Key Weaknesses |
|--------|---------------|----------------|
| **marker** | Excellent OCR, formulas, structure | GPU recommended, slower |
| **docling** | IBM ML models, excellent tables (TableFormer) | Heavier dependencies |
| **Commercial APIs** | Best accuracy, forms extraction | Cost, latency, privacy |

**Use when:** Accuracy is critical, documents are complex (scanned, tables, formulas)

### Tier 2: Structure-Aware (Tables + Structure, Optional OCR)

| Parser | Key Strengths | Key Weaknesses |
|--------|---------------|----------------|
| **pymupdf4llm** | Fast, good markdown, LLM-optimized | No OCR |
| **unstructured** | Flexible, element types | Requires hi_res for tables |
| **pdfplumber** | Excellent table extraction | No OCR, no markdown |
| **kreuzberg** | Fast (Rust), multiple OCR backends | Newer, less tested |

**Use when:** Digital PDFs with tables, need structure, speed matters

### Tier 3: Text Extraction Only

| Parser | Key Strengths | Key Weaknesses |
|--------|---------------|----------------|
| **pymupdf** | Fastest by far | No structure, no tables, no OCR |
| **pypdf/pypdfium2** | Pure Python, fast | Minimal features |
| **extractous** | Very fast (Rust) | Basic text only |
| **pdfminer** | Detailed layout info | Raw output, no markdown |
| **tika** | Broad format support | Java dependency, basic PDF |

**Use when:** Just need text, speed is critical, digital PDFs only

---

## How to Present Results Fairly

### DO: Present Multiple Leaderboards

Instead of one "overall winner," show:

1. **Text Accuracy Leaderboard** (edit_similarity on digital PDFs)
   - Excludes OCR-required documents
   - Fair comparison for all parsers

2. **OCR Leaderboard** (edit_similarity on scanned PDFs)
   - Only includes OCR-capable parsers
   - Only on OCR-required documents

3. **Structure Recovery Leaderboard** (tree_similarity + element_f1)
   - Only for structure-aware parsers
   - Shows who preserves document organization

4. **Table Extraction Leaderboard** (teds)
   - Only for table-capable parsers
   - Only on documents with tables

5. **Speed Leaderboard** (parse time)
   - Important for high-volume processing
   - Separate local vs cloud

### DON'T: Compare Apples to Oranges

❌ **Wrong:** "pymupdf scored 0% on OmniDocBench"
- OmniDocBench requires OCR; pymupdf doesn't have OCR
- This comparison is meaningless

✅ **Right:** "On digital PDFs, pymupdf achieved 80% edit similarity while being 1000x faster than marker"
- Fair comparison on applicable documents
- Highlights the trade-off (speed vs features)

### DON'T: Use One Metric

❌ **Wrong:** "Parser X won with 85% accuracy"
- Which accuracy? Text? Structure? Tables?
- 85% text accuracy with 20% structure = probably not what users want

✅ **Right:** "Parser X achieved 85% text accuracy and 72% structure similarity, making it suitable for RAG pipelines that need document organization"
- Clear about what was measured
- Connects to use case

---

## Content Marketing Angles

### Blog Post Ideas

#### NEW: Frontier LLM Content (November 2025)

7. **"GPT-5.1 vs Open Source: The 14-Point Quality Gap"**
   - GPT-5.1 achieves 92% vs 78% for best open source
   - When is $0.05/page worth it?
   - Decision framework by use case and volume

8. **"LlamaParse: The $0.003/page Sweet Spot"**
   - Matches open-source quality at 1/10th the cost of frontier LLMs
   - Purpose-built vs general-purpose LLM comparison
   - When to use LlamaParse vs GPT-5.1 vs open source

9. **"Why GPT-4o-mini Destroys Your Document Structure"**
   - 13% tree similarity vs 35%+ for competitors
   - The hidden danger of cheap LLMs for RAG pipelines
   - Text extraction ≠ structure preservation

10. **"The Metric That Lies: ChrF++ vs Edit Similarity"**
    - Open source scores 90+ ChrF++ but 70s edit similarity
    - What each metric actually measures
    - Why you need multiple metrics

#### Original Content

1. **"The 5 Problems You're Actually Solving When Parsing PDFs"**
   - Introduce the capability framework
   - Help readers identify their actual needs

2. **"Why We Needed 6 Metrics to Benchmark PDF Parsers"**
   - Deep dive into evaluation methodology
   - Discuss why simple text comparison fails
   - Show examples of parsers that ace one metric but fail another

3. **"PDF Parser Showdown: OCR vs Text Extraction"**
   - Separate leaderboards for each capability
   - Decision tree for choosing

4. **"The Hidden Cost of PDF Table Extraction"**
   - Focus on TEDS metric
   - Show dramatic differences in table handling
   - Recommendations by document type

5. **"Speed vs Accuracy: The PDF Parser Trade-off"**
   - Scatter plot visualization
   - When to choose fast vs accurate
   - Cost analysis for cloud APIs

6. **"We Tested 17 PDF Parsers on 353+ Documents. Here's What We Learned."**
   - Comprehensive results summary
   - Key surprises and insights
   - Decision framework

### Key Data Visualizations

| Visualization | Data Source | Purpose |
|---------------|-------------|---------|
| Corpus composition bar chart | `corpus_breakdown.csv` | Show benchmark diversity |
| Text accuracy leaderboard | `parser_scores_text_extraction.csv` | Main comparison |
| Speed vs accuracy scatter | `parser_scores_text_extraction.csv` | Trade-off visualization |
| Parser × domain heatmap | `parser_domain_scores_text.csv` | "Which parser for which docs" |
| Capability matrix | `parser_capabilities_detailed.csv` | Feature comparison |
| OCR leaderboard | `parser_scores_ocr.csv` | OCR-specific comparison |

---

## Decision Framework for Users

Present this as an interactive decision tree or table:

```
START: What kind of PDFs do you have?

├── Mostly scanned/image-based
│   ├── Need best accuracy? → marker, docling, commercial APIs
│   ├── Need speed? → kreuzberg (with OCR)
│   └── Budget constrained? → extractous + Tesseract
│
├── Digital PDFs with embedded text
│   ├── Do you need document structure?
│   │   ├── Yes, for RAG/LLM → pymupdf4llm, marker
│   │   └── Yes, for tables → pdfplumber, docling
│   │
│   ├── Just need raw text?
│   │   ├── Speed critical → pymupdf (fastest)
│   │   ├── Pure Python needed → pypdf
│   │   └── Broad format support → tika
│   │
│   └── Need markdown output?
│       ├── High quality → marker, docling
│       └── Good enough → pymupdf4llm, kreuzberg
│
└── Mixed (some scanned, some digital)
    └── Need one solution → marker, docling (handle both)
```

---

## Data Files Reference

| File | Contents | Use For |
|------|----------|---------|
| `parser_capabilities_detailed.csv` | Full feature matrix (20 columns) | Feature comparison tables |
| `parser_scores_text_extraction.csv` | Performance on digital PDFs | Main accuracy leaderboard |
| `parser_scores_ocr.csv` | Performance on scanned PDFs | OCR comparison |
| `parser_domain_scores_text.csv` | Performance by document type | Heatmap, use-case selection |
| `parser_timing.csv` | Speed statistics | Speed comparison |
| `corpus_breakdown.csv` | Document counts by domain | Corpus composition chart |
| `detailed_results.csv` | 5,911 individual results | Custom analysis |

---

## Sources and References

### Parser Documentation
- [Marker GitHub](https://github.com/datalab-to/marker) - Deep learning PDF to markdown
- [Docling](https://www.docling.ai/) - IBM document understanding
- [pdfplumber](https://github.com/jsvine/pdfplumber) - Table extraction
- [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/) - LLM-optimized output
- [Unstructured](https://docs.unstructured.io/) - Document processing pipeline
- [Kreuzberg](https://github.com/Goldziher/kreuzberg) - Polyglot document parser
- [Extractous](https://lib.rs/crates/extractous) - Rust-based extraction
- [Apache Tika](https://tika.apache.org/) - Java document toolkit

### Our Benchmark
- 353+ documents across 7 domains
- 17 parsers tested (10 open source, 4 commercial APIs, 6 frontier LLMs, 1 LlamaParse)
- 6 evaluation metrics (edit_similarity, chrf++, tree_similarity, CER, TEDS, element_f1)
- Frontier LLM comparison: GPT-5.1, Gemini 3 Pro, Claude Sonnet 4.5, GPT-4o-mini, Gemini 2.0 Flash, Claude 3.5 Haiku
- Last updated: November 2025
