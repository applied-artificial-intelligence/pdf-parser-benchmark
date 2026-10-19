# PDF-Bench: Comprehensive PDF Parser Benchmark

**17 Parsers | 353+ Documents | 7 Domains | Open Source + Commercial + Frontier LLMs**

---

## NEW: Frontier LLM Parsers (November 2025)

We benchmarked frontier LLMs (GPT-5.1, Gemini 3 Pro, Claude Sonnet 4.5) against traditional parsers:

| Category | Parser | Edit Similarity | Cost/Page |
|----------|--------|-----------------|-----------|
| **Premium LLM** | GPT-5.1 | **92%** | ~$0.05 |
| **Premium LLM** | Gemini 3 Pro | 87% | ~$0.03 |
| **Premium LLM** | Claude Sonnet 4.5 | 80% | ~$0.04 |
| **Budget LLM** | LlamaParse | 78% | $0.003 |
| **Budget LLM** | Gemini 2.0 Flash | 77% | ~$0.001 |
| **Open Source** | pypdfium2 | 78% | Free |
| **Commercial** | Azure Doc Intel | 88% | ~$0.0015 |

### Key Insight: The 14-Point Premium Gap

GPT-5.1 achieves **92% edit similarity**—14 points higher than the best open-source parser (78%). But at $0.05/page, it's 50x more expensive than LlamaParse which matches open-source quality at $0.003/page.

**Recommendation**: Use **LlamaParse** for most use cases (best quality/cost ratio). Reserve premium LLMs for high-value, low-volume documents.

See [docs/LEADERBOARDS.md](docs/LEADERBOARDS.md) for full LLM comparison.

---

## Key Findings

### The 49-Point Gap: Domain Matters More Than Parser Choice

Our benchmark reveals that **parser rankings change dramatically by document type**:

| Domain | Best Parser | Score | Worst Parser | Score |
|--------|-------------|-------|--------------|-------|
| Legal Contracts | pypdfium2/pypdf | **98.8%** | pdfminer | 98.5% |
| Invoices | kreuzberg | **49.9%** | unstructured | 21.7% |
| HR/Resumes | unstructured | **87.8%** | pymupdf4llm | 85.2% |

**The same parser (pypdfium2) scores 98.8% on legal documents but 49.9% on invoices**—a 49-point gap.

### The Invoice Problem

**Invoices remain challenging**, with most parsers achieving 70-80% accuracy on our test set. Complex table layouts and varied formatting continue to pose difficulties across all parsers.

### The Structure Gap

Parsers achieve **74% text accuracy** but only **35% structure preservation**—a 50% gap. The correlation between these metrics is just 0.174.

---

## Overall Rankings (353 Documents)

| Rank | Parser | Edit Similarity | chrF++ | Reliability | Best For |
|------|--------|-----------------|--------|-------------|----------|
| 1 | **pypdfium2** | 78.3% | 90.5 | 100% | Legal, general text |
| 2 | **pypdf** | 78.3% | 90.4 | 100% | Legal, general text |
| 3 | extractous | 77.5% | 90.4 | 100% | HR documents |
| 4 | pymupdf | 77.3% | 90.5 | 100% | Fast extraction |
| 5 | kreuzberg | 74.9% | 87.5 | 100% | Consistency, invoices |
| 6 | pymupdf4llm | 74.7% | 86.1 | 100% | LLM pipelines |
| 7 | docling | 71.3% | 87.5 | 97.4% | Structure preservation |
| 8 | pdfplumber | 70.4% | 91.6 | 100% | **Table extraction** |
| 9 | pdfminer | 68.2% | 89.1 | 100% | Text positioning |
| 10 | unstructured | 66.5% | 87.4 | 100% | HR documents |

### Table Extraction (TEDS Score)

| Parser | TEDS | Note |
|--------|------|------|
| **pdfplumber** | 93.4% | Best for tables |
| pymupdf4llm | 84.8% | Markdown tables |
| docling | 84.5% | Structure-aware |

---

## Quick Recommendations

### Legal/Contract Intelligence
**Use**: pypdfium2 or pymupdf
- 98.8% accuracy on contracts
- 100% reliability, fast
- Simple parsers suffice

### Invoice Processing
**Use**: Custom solution required
- No parser exceeds 50%
- Consider: LayoutLM, Donut, commercial APIs
- Generic PDF parsers are insufficient

### RAG/LLM Applications
**Use**: docling or pymupdf4llm
- Best structure preservation (60%+)
- Trade-off: docling has 2.6% failure rate

### Table-Heavy Documents
**Use**: pdfplumber
- 93.4% table structure accuracy
- Purpose-built for tables

---

## Installation

```bash
# Clone and install
git clone https://github.com/strickvl/pdf-bench.git
cd pdf-bench

# Using uv (recommended)
uv sync

# Or pip
pip install -e .

# Install pdfsmith (required for most parsers)
pip install pdfsmith

# Optional: Install specific parser groups
pip install pdfsmith[light]       # pypdf, pdfplumber, pymupdf
pip install pdfsmith[recommended] # + docling, marker
pip install pdfsmith[frontier]    # + Anthropic, OpenAI, Gemini LLMs
pip install pdfsmith[commercial]  # + AWS, Azure, Google, LlamaParse
```

**Note**: pdf-bench uses [pdfsmith](https://github.com/strickvl/pdfsmith) as its parsing backend. Native parsers (tika, marker_ollama, landing_ai) are implemented directly.

## Quick Start

```bash
# Run benchmark on full corpus
pdfbench run benchmarks/full_corpus_353docs.yaml --output results/output.json

# Single parser test
pdfbench run benchmarks/synthetic.yaml --parsers pypdfium2

# Generate visualizations
python scripts/generate_visualizations.py
```

---

## Test Corpus (353 Documents)

| Domain | Documents | Characteristics |
|--------|-----------|-----------------|
| Legal (Synthetic) | 108 | Contracts, NDAs, licensing |
| CUAD (Real Contracts) | 75 | Actual legal agreements |
| Invoices | 100 | Complex tables, varied formats |
| HR/Resumes | 34 | Multiple layouts and styles |
| Academic Papers | 5 | arXiv papers with LaTeX |
| Synthetic | 31 | Tables, lists, columns |

All documents have manually verified ground truth from source HTML/DOCX/LaTeX conversions.

**Full corpus available**: 798 documents including 445 OmniDocBench academic papers (English subset)

---

## Metrics

| Metric | Measures | Primary Use |
|--------|----------|-------------|
| **Edit Similarity** | Character-level text accuracy | Overall ranking |
| **chrF++** | N-gram similarity | Robust comparison |
| **CER** | Character error rate | Error analysis |
| **Tree Similarity** | Structure preservation | RAG applications |
| **TEDS** | Table structure accuracy | Table extraction |

---

## Documentation

- **[docs/RESULTS.md](docs/RESULTS.md)** - Full benchmark results
- **[docs/PARSERS.md](docs/PARSERS.md)** - Parser comparison
- **[docs/CORPORA.md](docs/CORPORA.md)** - Corpus documentation
- **[docs/blog/](docs/blog/)** - In-depth analysis articles

### Blog Posts

1. **[Comprehensive Evaluation of 10 PDF Parsers](docs/blog/01_comprehensive_evaluation.md)** - Full benchmark analysis
2. **[The 50% Structure Gap](docs/blog/03_structure_gap.md)** - Why text accuracy doesn't predict structure quality
3. **[Why Rankings Change by Document Type](docs/blog/04_domain_variation.md)** - Domain-specific parser selection

---

## Project Structure

```
pdf-bench/
├── pdf_bench/          # Core library
│   ├── systems/        # Parser adapters (pdfsmith + native)
│   ├── metrics/        # Evaluation metrics
│   └── utils/          # Utilities
├── corpus/             # Test documents (353+)
│   ├── synthetic/      # Systematic tests
│   └── business/       # Invoices, legal, HR
├── benchmarks/         # Benchmark configs
├── results/            # Benchmark outputs
├── scripts/            # Analysis scripts
└── docs/               # Documentation
```

### Architecture

pdf-bench uses **pdfsmith** as its unified parsing backend. Most parsers are accessed through `PdfsmithAdapter`, which bridges pdfsmith's API (`parse() -> str`) to pdf-bench's API (`parse() -> Path`).

Native parsers not in pdfsmith: `tika`, `marker_ollama`, `landing_ai`

---

## Parsers Tested (17 Total)

**Frontier LLMs**: GPT-5.1, Gemini 3 Pro, Claude Sonnet 4.5, GPT-4o-mini, Gemini 2.0 Flash, Claude 3.5 Haiku

**Commercial APIs**: LlamaParse, Azure Document Intelligence, AWS Textract, Google Document AI

**Open Source - Text**: pypdfium2, pypdf, pymupdf, pdfminer, extractous, kreuzberg

**Open Source - Structure**: pymupdf4llm, docling, unstructured, marker

**Open Source - Tables**: pdfplumber

---

## Contributing

Contributions welcome:
- Additional parser implementations
- New test corpora
- Metric improvements
- Documentation

---

## License

MIT License. Individual parsers have their own licenses.

---

## Citation

```bibtex
@software{pdfbench2025,
  title = {PDF-Bench: Comprehensive PDF Parser Benchmark},
  author = {PDF-Bench Contributors},
  year = {2025},
  url = {https://github.com/strickvl/pdf-bench}
}
```

---

**Last Updated**: 2025-12-02 | **Version**: 3.0 (pdfsmith integration) | **Parsers**: 17 | **Documents**: 353+
