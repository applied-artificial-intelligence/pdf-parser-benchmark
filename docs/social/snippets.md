# Social Media Snippets: PDF Parser Benchmark

## LinkedIn Posts (5)

### Post 1: The Big Finding
**Hook**: Tested 10 PDF parsers on 273 business documents. The results surprised me.

The same parser (pypdfium2) scores 98.8% on legal contracts but drops to 49.9% on invoices.

That's a 49-point gap—within the same tool.

Key insight: Parser rankings aren't stable across document types. The "best" parser depends entirely on what you're extracting.

For contract intelligence? Use pypdfium2 or pymupdf (98.8% accuracy, free).
For invoices? No open-source parser exceeds 50%. Custom solutions required.

Full benchmark: [link]

#PDFParsing #DocumentAI #MLOps #DataEngineering

---

### Post 2: The Invoice Problem
**Hook**: We benchmarked 10 PDF parsers. Here's the uncomfortable finding:

No parser exceeds 50% accuracy on invoices.

Legal contracts: 98.8% (solved)
Resumes: 87.8% (good)
Invoices: 49.9% (all parsers struggle)

Why? Invoices combine every extraction challenge:
- Complex tables with merged cells
- Variable formats across vendors
- Mixed content (logos, barcodes, text)
- Dense information in small spaces

For invoice processing, generic PDF parsers are insufficient. Consider: LayoutLM, specialized invoice models, or commercial APIs.

#InvoiceProcessing #DocumentAI #PDFExtraction

---

### Post 3: The Structure Gap
**Hook**: PDF parsers achieve 74% text accuracy. Structure preservation? Only 35%.

We measured the correlation between text accuracy and structure preservation across 2,730 extraction runs.

Result: 0.174 correlation.

Translation: Optimizing for text extraction doesn't improve structure quality. These are separate problems.

For RAG systems that need document hierarchy, text accuracy benchmarks are misleading. You need structure-aware evaluation.

Top structure preservation:
- docling: 61.2%
- pymupdf4llm: 60.8%

Top text accuracy:
- pypdfium2: 78.3%
- pypdf: 78.3%

Different parsers, different strengths.

#RAG #DocumentUnderstanding #LLM #AIEngineering

---

### Post 4: Table Extraction
**Hook**: For table-heavy documents, the leaderboard changes completely.

Overall ranking:
1. pypdfium2 (78.3%)
2. pypdf (78.3%)
...
8. pdfplumber (70.4%)

Table extraction (TEDS score):
1. pdfplumber (93.4%)
2. pymupdf4llm (84.8%)
3. docling (84.5%)

pdfplumber ranks 8th overall but dominates table extraction.

Lesson: Single-metric comparisons hide specialized capabilities. Evaluate parsers on the metrics that matter for your use case.

#DataExtraction #DocumentProcessing #Tables

---

### Post 5: Parser Selection Framework
**Hook**: "Which PDF parser should I use?" Here's a data-driven answer.

After 2,730 benchmark runs, the decision tree is clear:

Legal/Contract Intelligence
-> pypdfium2 or pymupdf (98.8%, free, fast)

Invoice Processing
-> Custom solution (LayoutLM, commercial API)

RAG/LLM Applications
-> docling (61% structure preservation)

Table Extraction
-> pdfplumber (93.4% TEDS score)

General Text
-> pypdfium2 (78.3%, 100% reliability)

The "best" parser is context-dependent. Benchmark on your actual documents before deciding.

Full methodology: [link]

#MLEngineering #DocumentAI #TechDecisions

---

## Twitter/X Thread Ideas (10)

### Thread 1: The 49-Point Gap
1/ We tested 10 PDF parsers on 273 business documents. The biggest surprise?

Parser rankings aren't stable.

A thread on why your benchmark results might not transfer to production.

2/ pypdfium2 scores 98.8% on legal contracts.

The same parser scores 49.9% on invoices.

That's a 49-point gap—within the same tool, same parameters.

3/ Why? Document complexity profiles differ.

Legal docs: Dense text, consistent formatting, few tables.
Invoices: Sparse text, complex tables, variable layouts.

4/ The invoice problem is industry-wide. No open-source parser exceeds 50%.

This isn't a parser selection problem—it's a fundamental limitation.

5/ Recommendation: Don't trust single-number rankings.

Always ask: "Best for what document type?"

Then benchmark on YOUR documents.

---

### Thread 2: Structure vs Text
1/ PDF parsers have a hidden problem.

Text accuracy: 74%
Structure preservation: 35%

That's a 50% gap that affects every RAG system.

2/ We measured the correlation between text accuracy and structure preservation.

Result: 0.174

Almost no relationship.

3/ Translation: Parsers optimized for text don't preserve structure.

If your RAG system needs headings, sections, hierarchy—text benchmarks won't help.

4/ Top structure preservation:
- docling: 61.2%
- pymupdf4llm: 60.8%

Top text accuracy:
- pypdfium2: 78.3%
- pypdf: 78.3%

Different tools for different jobs.

---

### Thread 3: Quick Parser Guide
1/ PDF parser selection in 60 seconds:

Legal contracts -> pypdfium2 (98.8%)
Tables -> pdfplumber (93.4% TEDS)
RAG/structure -> docling (61% tree similarity)
Invoices -> None work well (<50%)

2/ Why these recommendations?

2,730 benchmark runs across 273 documents and 4 business domains.

The data is clear: context matters more than generic rankings.

---

## Key Stats for Sharing

**Overall**:
- 2,730 benchmark runs
- 10 parsers tested
- 273 documents
- 99.7% success rate

**Rankings**:
- Best overall: pypdfium2 (78.3%)
- Best tables: pdfplumber (93.4% TEDS)
- Best structure: docling (61.2%)
- Most consistent: kreuzberg (16.7% variance)

**Domain Performance**:
- Legal: 98.8% (solved)
- HR: 87.8% (good)
- Synthetic: 87.5% (good)
- Invoices: 49.9% (all struggle)

**Key Gaps**:
- Legal-to-invoice gap: 49 points
- Text-to-structure gap: ~50%
- Correlation text↔structure: 0.174

---

## Image Captions

### Parser Ranking Chart
"PDF parser rankings by edit similarity across 273 business documents. pypdfium2 leads at 78.3%, but rankings change by document type."

### Domain Heatmap
"Performance varies dramatically by domain. Legal contracts are 'solved' (98.8%), while invoices challenge all parsers (<50%)."

### TEDS Comparison
"For table extraction, pdfplumber dominates (93.4% TEDS) despite ranking 8th in overall text accuracy."

### Metric Correlation
"The 0.174 correlation between text accuracy and structure preservation reveals why single-metric benchmarks mislead."
