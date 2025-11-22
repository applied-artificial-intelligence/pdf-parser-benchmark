# The 50% Structure Gap: Why Your PDF Parser Extracts Text but Loses Meaning

**TL;DR**: Our benchmark reveals a critical gap in PDF extraction: parsers achieve 74% text accuracy but only 35% structure preservation. This 0.174 correlation means optimizing for text extraction provides almost no benefit for structure quality. For RAG and document understanding applications, this gap fundamentally limits system performance.

---

## The Problem Nobody Talks About

When evaluating PDF parsers, most benchmarks focus on a single question: *How accurately does this parser extract text?*

This seems reasonable. After all, if the text is correct, what more could you need?

But for modern document processing—RAG systems, document understanding pipelines, contract analysis—text accuracy tells only half the story. The other half is **structure**: headings, sections, lists, tables, and the hierarchical relationships that give documents meaning.

Our 273-document benchmark exposes an uncomfortable truth: **parsers optimized for text extraction don't preserve structure**.

---

## The Numbers

After processing 2,730 parser-document combinations across 10 open-source PDF parsers, we measured:

| Metric | Mean Score | What It Measures |
|--------|------------|------------------|
| **Edit Similarity** | 73.7% | Text accuracy (character-level) |
| **Tree Similarity** | 35.2% | Structure preservation (headings, hierarchy) |
| **Gap** | **~50%** | The structure preservation deficit |

The average parser extracts text at nearly 74% accuracy. That same parser preserves document structure at only 35%.

This isn't a minor discrepancy—it's a **50-point gap** that affects every downstream application.

---

## Why Does This Gap Exist?

### Different Optimization Targets

Most PDF parsers optimize for **text extraction fidelity**: getting every character correct, in the right order. This is the metric users complain about, the metric that appears in GitHub issues, and the metric that benchmarks typically report.

Structure preservation requires a different approach:
- Identifying heading levels (H1, H2, H3)
- Detecting section boundaries
- Recognizing list structures
- Preserving paragraph relationships
- Maintaining table layouts

These tasks require **semantic understanding**, not just character extraction.

### PDF Is a Visual Format

PDF was designed for printing, not for information extraction. A PDF file describes:
- Where to place text on a page
- Font sizes and styles
- Page coordinates

It does **not** describe:
- Document hierarchy
- Semantic sections
- Logical reading order

Extracting structure requires inference: "This text is bold and larger, so it's probably a heading." Parsers vary wildly in how they approach this inference.

---

## The Correlation Analysis

Our benchmark measured the relationship between metrics:

| Metric Pair | Correlation | Interpretation |
|-------------|-------------|----------------|
| edit_similarity ↔ CER | **-0.978** | Perfect inverse (expected) |
| edit_similarity ↔ chrF++ | **0.739** | Strong positive |
| edit_similarity ↔ tree_similarity | **0.174** | Almost no relationship |
| tree_similarity ↔ TEDS | -0.137 | No relationship |

The **0.174 correlation** between text accuracy (edit_similarity) and structure preservation (tree_similarity) is the key finding.

In statistical terms, this means:
- Knowing a parser's text accuracy tells you almost nothing about its structure preservation
- Improving text extraction doesn't improve structure preservation
- These are **separate problems requiring separate solutions**

---

## What This Looks Like in Practice

Consider a legal contract with this structure:

```
1. DEFINITIONS
   1.1 "Agreement" means this document...
   1.2 "Party" means either signatory...

2. OBLIGATIONS
   2.1 The Provider shall...
   2.2 The Client shall...
```

### Text-Optimized Parser Output

```
1. DEFINITIONS 1.1 "Agreement" means this document...
1.2 "Party" means either signatory... 2. OBLIGATIONS
2.1 The Provider shall... 2.2 The Client shall...
```

Text accuracy: 100% (every character preserved)
Structure accuracy: ~20% (hierarchy lost, sections merged)

### Structure-Aware Parser Output

```markdown
# 1. DEFINITIONS

## 1.1 "Agreement"
means this document...

## 1.2 "Party"
means either signatory...

# 2. OBLIGATIONS

## 2.1 The Provider
shall...

## 2.2 The Client
shall...
```

Text accuracy: 95% (minor formatting changes)
Structure accuracy: 90% (hierarchy preserved)

For a RAG system that needs to retrieve "Section 2.1 obligations," the first output is nearly useless. The second enables precise retrieval.

---

## Which Parsers Preserve Structure?

Our benchmark identified clear tiers:

### High Structure Preservation (>60% tree_similarity)

| Parser | Tree Similarity | Trade-off |
|--------|-----------------|-----------|
| docling | 61.2% | 2.6% failure rate |
| pymupdf4llm | 60.8% | Markdown-focused output |

### Average Structure Preservation (~35%)

| Parser | Tree Similarity |
|--------|-----------------|
| kreuzberg | 38.4% |
| unstructured | 36.1% |
| extractous | 34.2% |

### Low Structure Preservation (<30%)

| Parser | Tree Similarity |
|--------|-----------------|
| pypdfium2 | 28.1% |
| pypdf | 27.9% |
| pdfplumber | 25.3% |

**Note**: The "best" text extraction parsers (pypdfium2, pypdf) have the **worst** structure preservation. This isn't coincidence—they optimize for different objectives.

---

## Implications for Production Systems

### RAG Systems

Retrieval-Augmented Generation depends on meaningful chunks. If your parser flattens document structure, you lose:

- **Section context**: Which part of the document is this from?
- **Hierarchical relationships**: Is this a main point or a sub-point?
- **Semantic boundaries**: Where does one topic end and another begin?

Chunking strategies (by token count, by paragraph) can't recover structure that was never extracted.

### Document Classification

Classifying documents by type often depends on structural patterns:
- Contracts have numbered clauses
- Invoices have line-item tables
- Reports have executive summaries and appendices

Without structure, classification relies solely on keyword matching.

### Question Answering

"What are the client's obligations under Section 2?" requires:
1. Finding Section 2
2. Identifying the obligations subsection
3. Extracting relevant text

If the parser merged Section 2 into a text blob, step 1 already fails.

---

## The Industry-Wide Challenge

This isn't a problem unique to open-source parsers. Our analysis suggests it's an **industry-wide limitation**:

1. **Benchmark focus**: Most PDF extraction benchmarks measure text accuracy only
2. **User expectations**: Developers primarily complain about text errors, not structure loss
3. **Optimization pressure**: Parser maintainers prioritize reported issues
4. **Evaluation difficulty**: Structure quality is harder to measure than text accuracy

The result is an ecosystem optimized for the wrong metric.

---

## What Can You Do?

### 1. Choose Structure-Aware Parsers for Structure-Dependent Tasks

If your application needs document hierarchy:
- **docling**: Best structure preservation (61.2%), but 2.6% failure rate
- **pymupdf4llm**: Second-best (60.8%), 100% reliability

If you only need text:
- **pypdfium2** or **pymupdf**: Fast, reliable, high text accuracy

### 2. Evaluate on Structure Metrics

Add tree_similarity or similar metrics to your evaluation suite. Don't rely solely on text accuracy.

### 3. Consider Multi-Parser Pipelines

For critical applications:
- Primary: Structure-aware parser (docling)
- Fallback: Reliable text parser (pypdfium2)

This captures structure when possible while ensuring reliability.

### 4. Post-Process for Structure

If your parser doesn't preserve structure:
- Use LLMs to infer section boundaries
- Apply heuristics (font size → heading level)
- Implement custom chunking strategies

These add complexity but can recover some structural information.

### 5. Advocate for Better Benchmarks

When evaluating parsers, request structure metrics. When reporting issues, mention structure loss. Market demand drives development priorities.

---

## Measuring Structure Preservation

We used **tree_similarity** to measure structure preservation:

1. Convert document to tree representation (headings → nodes)
2. Extract ground truth tree from source HTML/LaTeX
3. Compare trees using edit distance
4. Normalize to 0-1 scale

This captures:
- Heading detection accuracy
- Hierarchy depth preservation
- Section boundary identification

It does not capture:
- List structure within sections
- Inline formatting
- Table cell relationships (use TEDS for tables)

---

## Conclusion

The 50% structure gap reveals a fundamental limitation in current PDF extraction technology. Parsers optimized for text accuracy achieve 74% on average—but structure preservation lags at 35%.

This gap matters because:
1. **RAG systems need structure** for meaningful retrieval
2. **Document understanding requires hierarchy** for classification and QA
3. **The gap isn't closing**—text and structure optimization are independent problems

For practitioners building document processing pipelines:
- Don't assume text accuracy implies structure quality
- Evaluate parsers on the metrics that matter for your use case
- Consider structure-aware parsers when hierarchy matters

The "best" parser for text extraction may be the worst choice for document understanding.

---

*This is part of a series on PDF parser evaluation. See also: [Comprehensive Evaluation of 10 PDF Parsers](#) | [Why Parser Rankings Change by Document Type](#)*
