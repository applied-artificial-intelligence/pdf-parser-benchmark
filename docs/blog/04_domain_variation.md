# Why PDF Parser Rankings Change by Document Type: A Data-Driven Analysis

**TL;DR**: Parser rankings aren't stable. pypdfium2 leads on legal documents (98.8%) but drops to 49.9% on invoices—a 49-point swing. unstructured ranks last overall but wins on HR documents. We analyze why this happens and provide a decision framework for parser selection based on your document types.

---

## The Assumption That Breaks Down

Most parser comparisons present a single leaderboard: "Parser A is best, Parser B is second, etc."

This assumes performance is **transitive**—if A beats B overall, A should beat B on any document type.

Our 273-document benchmark shows this assumption is wrong. **Parser rankings are domain-specific**, and the "best" parser depends entirely on what you're extracting.

---

## The Evidence: Domain-Specific Performance

We evaluated 10 parsers across four business document types:

### Overall Rankings (Edit Similarity)

| Rank | Parser | Score |
|------|--------|-------|
| 1 | pypdfium2 | 78.3% |
| 2 | pypdf | 78.3% |
| 3 | extractous | 77.5% |
| 4 | pymupdf | 77.3% |
| 5 | kreuzberg | 74.9% |
| ... | ... | ... |
| 10 | unstructured | 66.5% |

### Domain-Specific Rankings

| Domain | Winner | Score | Runner-up |
|--------|--------|-------|-----------|
| **Legal** | pypdfium2/pypdf/pymupdf/pdfplumber | 98.8% | extractous (98.5%) |
| **Invoices** | kreuzberg/pypdfium2/pypdf | 49.9% | pymupdf (47.7%) |
| **HR/Resumes** | unstructured | 87.8% | extractous (87.7%) |
| **Synthetic** | kreuzberg | 87.5% | pypdfium2 (87.5%) |

**unstructured** ranks 10th overall but **1st on HR documents**.
**pdfplumber** ranks 8th overall but **ties for 1st on legal documents**.

---

## The 49-Point Gap: Within-Parser Variance

The most striking finding isn't the ranking shifts—it's the variance within individual parsers.

### pypdfium2 Performance by Domain

| Domain | Score | Gap from Best |
|--------|-------|---------------|
| Legal | 98.8% | — |
| Synthetic | 87.5% | -11.3 |
| HR/Resumes | 87.3% | -11.5 |
| **Invoices** | **49.9%** | **-48.9** |

The same parser—with the same code, same parameters—varies **49 percentage points** across document types.

### All Parsers Show Similar Patterns

| Parser | Best Domain | Worst Domain | Gap |
|--------|-------------|--------------|-----|
| pypdfium2 | Legal (98.8%) | Invoices (49.9%) | 48.9 |
| pdfplumber | Legal (98.8%) | Invoices (33.8%) | 65.0 |
| unstructured | Legal (98.7%) | Invoices (21.7%) | 77.0 |
| pdfminer | Legal (98.5%) | Invoices (27.1%) | 71.4 |

**Every parser struggles with invoices.** The legal-to-invoice gap ranges from 41 to 77 percentage points.

---

## Why Do Rankings Change?

### 1. Document Complexity Profiles Differ

| Domain | Text Density | Table Complexity | Layout Variation |
|--------|--------------|------------------|------------------|
| Legal | High | Low | Low |
| HR/Resumes | Medium | Low | High |
| Synthetic | Variable | Medium | Medium |
| Invoices | Low | High | High |

**Legal documents** are parser-friendly:
- Dense, flowing text
- Consistent formatting
- Few tables, simple layouts
- Predictable structure

**Invoices** are parser-hostile:
- Sparse text among visual elements
- Complex tables with merged cells
- Variable layouts across vendors
- Mixed content (logos, barcodes, stamps)

### 2. Parser Design Targets Specific Use Cases

| Parser | Design Focus | Excels At | Struggles With |
|--------|--------------|-----------|----------------|
| pypdfium2 | Fast text extraction | Text-heavy docs | Complex layouts |
| pdfplumber | Table extraction | Structured tables | Running text |
| unstructured | Document understanding | Layout-rich docs | Dense text |
| docling | Enterprise docs | Complex formatting | Simple extraction |

**unstructured** uses layout detection optimized for varied document types—but this adds overhead that hurts performance on simple documents where basic text extraction suffices.

**pdfplumber** focuses on table detection, which is overkill for contracts but critical for invoices (though even it achieves only 33.8% on invoices).

### 3. Optimization Metrics Vary

Most parsers optimize for:
- Text accuracy on benchmark datasets
- Processing speed
- Memory efficiency

Few optimize for:
- Invoice-specific layouts
- Multi-column text flow
- Embedded table extraction

---

## The Invoice Problem: An Industry-Wide Challenge

### No Parser Exceeds 50% on Invoices

| Rank | Parser | Invoice Score |
|------|--------|---------------|
| 1 | kreuzberg | 49.9% |
| 1 | pypdfium2 | 49.9% |
| 1 | pypdf | 49.9% |
| 4 | extractous | 49.2% |
| 5 | pymupdf | 47.7% |
| 6 | docling | 46.6% |
| ... | ... | ... |
| 10 | unstructured | 21.7% |

**This is not a parser selection problem—it's a fundamental limitation.**

Invoices combine multiple extraction challenges:
1. **Table extraction**: Line items in varied formats
2. **Field extraction**: Vendor info, totals, dates in unpredictable locations
3. **Visual elements**: Logos, stamps, watermarks
4. **Multi-format**: PDF generated from different sources

Generic PDF parsers weren't designed for this. Invoice processing requires specialized solutions:
- Dedicated invoice ML models (LayoutLM, Donut)
- Commercial OCR/extraction APIs
- LLM-based field extraction
- Template-matching approaches

---

## Parser Consistency: A Hidden Quality Dimension

Beyond average performance, **consistency matters**.

### Cross-Domain Variance Rankings

| Parser | Variance | Assessment |
|--------|----------|------------|
| kreuzberg | 16.7% | Most consistent |
| docling | 16.9% | Very consistent |
| extractous | 18.4% | Consistent |
| pypdfium2 | 18.5% | Consistent |
| pymupdf | 19.2% | Moderate |
| unstructured | **29.7%** | Highly variable |
| pdfminer | 27.7% | Variable |

**Why consistency matters**:
- A 75% average with 10% variance → reliable 65-85% performance
- A 75% average with 30% variance → unpredictable 45-100% performance

For production systems, the second scenario means:
- More edge cases
- More manual review
- Less predictable quality

**kreuzberg** and **docling** maintain relatively stable performance across document types, making them safer choices when you can't fully predict your document mix.

---

## Decision Framework: Choosing a Parser

### Step 1: Identify Your Primary Document Type

| If Your Documents Are... | Consider |
|--------------------------|----------|
| Legal contracts, NDAs | pypdfium2, pymupdf |
| Invoices, receipts | Custom solution required |
| Resumes, HR documents | unstructured, extractous |
| Mixed/unknown | kreuzberg, docling |
| Table-heavy | pdfplumber (for table structure) |

### Step 2: Evaluate Trade-offs

| Parser | Strength | Trade-off |
|--------|----------|-----------|
| pypdfium2 | Fast, reliable, good text | Poor structure preservation |
| docling | Best structure, consistent | 2.6% failure rate |
| pdfplumber | Best table extraction | Slower, lower text accuracy |
| unstructured | Good on varied layouts | Lowest overall accuracy |

### Step 3: Benchmark on Your Documents

Generic benchmarks (including ours) can only guide initial selection. For production systems:

1. **Collect representative samples** (20-50 documents minimum)
2. **Create ground truth** (manually verify extracted text)
3. **Run candidate parsers** (top 3 from our results)
4. **Measure domain-specific accuracy**
5. **Select based on your data**

### Step 4: Plan for the Unexpected

Document populations change:
- New document types enter your pipeline
- Vendor formats evolve
- Acquisition brings new document sources

Build flexibility:
- Monitor extraction quality over time
- Implement fallback parsers
- Alert on degraded performance

---

## Multi-Parser Strategies

For robust production systems, consider multiple parsers:

### Strategy 1: Domain-Specific Routing

```
IF document_type == "legal":
    use pypdfium2  # 98.8% accuracy
ELIF document_type == "hr":
    use unstructured  # 87.8% accuracy
ELIF document_type == "invoice":
    use specialized_invoice_model
ELSE:
    use kreuzberg  # most consistent
```

Requires document classification before extraction.

### Strategy 2: Ensemble Extraction

```
results = [parser.extract(doc) for parser in [pypdfium2, docling]]
final = select_best(results)  # by confidence, length, etc.
```

Higher computational cost but catches individual parser failures.

### Strategy 3: Primary + Fallback

```
try:
    result = docling.extract(doc)  # best structure
except:
    result = pypdfium2.extract(doc)  # reliable fallback
```

Captures structure when possible while ensuring reliability.

---

## When to Ignore Generic Benchmarks

Our benchmark provides guidance, but you should ignore it when:

1. **Your documents are highly specialized**
   - Medical records, engineering drawings, government forms
   - Test on your specific document types

2. **You need specific features**
   - OCR for scanned documents (not tested here)
   - Language-specific extraction (non-English)
   - Embedded image extraction

3. **Performance requirements differ**
   - Real-time extraction (test latency, not just accuracy)
   - Batch processing (test memory, throughput)
   - Edge deployment (test resource constraints)

4. **Quality tolerances differ**
   - Some applications tolerate 70% accuracy
   - Others require 99.9%
   - Match evaluation to requirements

---

## Conclusion

Parser rankings change by document type because:
1. **Documents have different complexity profiles**—legal is easy, invoices are hard
2. **Parsers optimize for different use cases**—no universal best
3. **Generic benchmarks hide domain-specific variation**

For practitioners:
- **Don't trust single-number rankings**—ask "for what document type?"
- **Benchmark on your documents**—generic results don't transfer
- **Plan for variance**—the 49-point legal-to-invoice gap is real
- **Consider multi-parser strategies**—different tools for different jobs

The "best PDF parser" question has no universal answer. The right question is: "What's the best parser for my documents?"

---

*This is part of a series on PDF parser evaluation. See also: [Comprehensive Evaluation of 10 PDF Parsers](#) | [The 50% Structure Gap Problem](#)*
