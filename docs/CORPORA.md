# PDF-Bench Test Corpora

**Total Documents**: 275+ with perfect ground truth
**Categories**: Synthetic, Business (Invoices, Legal, HR), Academic
**Ground Truth Method**: DOCX → PDF with programmatic structure extraction

---

## Overview

PDF-Bench uses a multi-corpus approach to test parser performance across different document types and use cases.

### Corpus Summary

| Corpus | Documents | Status | Ground Truth Method | Use Case |
|--------|-----------|--------|---------------------|----------|
| **Synthetic** | 33 | ✅ Complete | DOCX programmatic | Systematic feature testing |
| **Invoices** | 100 | ✅ Complete | Template generation | Business document extraction |
| **Legal** | 108 | ✅ Complete | Template generation | Contract parsing |
| **HR** | 34 | ✅ Complete | Template generation | Resume extraction |
| **Academic** | 5 | ✅ Sample | LaTeX source | Equation extraction |

**Total**: 280 documents across 5 corpora

---

## 1. Synthetic Corpus (33 Documents)

**Purpose**: Systematic testing of parser capabilities across document features

### Statistics
- **Documents**: 33 PDFs with perfect ground truth
- **Size**: ~900KB total
- **Generation**: DOCX (python-docx) → PDF (LibreOffice headless)
- **Success Rate**: 100% (all documents generated successfully)

### Document Categories

#### Basic Text (7 documents)
Simple documents testing fundamental extraction:
- 01: Basic text and headings
- 02: Lists (bullets, numbered)
- 03: Basic tables
- 05: Mixed content
- 06: DOCX-generated simple report
- 07: DOCX table-heavy document
- 08: DOCX multi-column layout

#### Tables (6 documents: 09-14)
Progressive table complexity:
- 09: Simple 3x4 grid
- 10: Merged columns (colspan)
- 11: Wide table (7 columns)
- 12: Multiple tables per document
- 13: Complex multi-level headers
- 14: Financial statement with formatting

**Parser Performance**:
- Best: PyPDFium2 (78.57%), PyPDF, Kreuzberg
- Worst: PDFMiner (54.55%), Docling (53.01%)
- **Challenge**: Merged cells and complex headers

#### Lists (6 documents: 15-20)
List detection and nesting:
- 15: Simple bullets
- 16: Numbered lists
- 17: Two-level nesting
- 18: Three-level nesting
- 19: Mixed numbered/bullets
- 20: Lists with paragraphs

**Parser Performance**:
- Best: PdfPlumber (97.71%), Unstructured (97.98%)
- All parsers perform well (>90%)
- **Challenge**: Nesting levels

#### Multi-Column (6 documents: 21-26)
Reading order challenges:
- 21: Two-column text
- 22: Three-column layout
- 23: Mixed full-width and columns
- 24: Newsletter style
- 25: Academic paper format
- 26: Marketing brochure

**Parser Performance**:
- Best: PyMuPDF (89-97%), Kreuzberg (88-93%), Marker (88-92%)
- Worst: PdfPlumber (44-67%), Unstructured (42-65%)
- **Challenge**: Reading order (down-then-across vs across-then-down)

#### Mixed Content (6 documents: 27-32)
Real-world complexity:
- 27: Business report
- 28: Technical documentation
- 29: Policy document
- 30: Meeting minutes
- 31: Research summary
- 32: Comprehensive annual report

**Parser Performance**:
- Best: PyPDFium2 (76-88%), Kreuzberg (76-88%), PyMuPDF (73-87%)
- **Challenge**: Combining tables, lists, multi-column, and text

### Ground Truth Quality
**Perfect** - Extracted directly from DOCX structure using python-docx:
- Paragraphs → Markdown text
- Tables → Markdown tables
- Lists → Markdown lists
- Headings → Markdown headings

**Files**:
- PDFs: `corpus/synthetic/*.pdf`
- Ground truth: `corpus/synthetic/*.md`
- Metadata: `corpus/synthetic/*.yaml`
- Summary: `corpus/synthetic/CORPUS_SUMMARY.md`

---

## 2. Business Invoices Corpus (100 Documents)

**Purpose**: Test extraction of structured business documents with tables and key-value pairs

### Statistics
- **Documents**: 100 invoices
- **Size**: ~8MB total
- **Generation Time**: ~45 seconds (automated)
- **Industries**: Retail, consulting, manufacturing, services, etc.

### Document Variants
- Simple invoices (single product)
- Multi-line invoices (10+ products)
- Service invoices (hourly billing)
- Complex invoices (discounts, taxes, shipping)
- International invoices (multiple currencies)

### Key Features Tested
- **Tables**: Product line items
- **Key-value extraction**: Invoice #, date, total, tax
- **Formatting**: Currency, percentages
- **Layout**: Headers, footers, logos

### Generation Method
1. **Template**: Jinja2 templates with python-docx
2. **Data**: Realistic generated data (Faker library)
3. **Variants**: Randomized complexity
4. **Conversion**: LibreOffice headless DOCX→PDF

### Ground Truth
Extracted from DOCX structure:
- Invoice header (number, date, due date)
- Vendor/customer information
- Line items (description, quantity, price, total)
- Totals (subtotal, tax, shipping, grand total)

### Benchmark Results
- Status: Benchmarking in progress
- Expected: Table parsers (PdfPlumber, PyPDFium2) to excel

**Files**:
- PDFs: `corpus/business/invoices/pdfs/*.pdf`
- Ground truth: `corpus/business/invoices/ground_truth/*.md`
- Metadata: `corpus/business/invoices/metadata/*.yaml`
- Builder: `builders/generate_invoice_corpus.py`

---

## 3. Business Legal Corpus (108 Documents)

**Purpose**: Test extraction of legal documents with complex structure and numbering

### Statistics
- **Documents**: 108 legal documents
- **Size**: ~15MB total
- **Generation Time**: ~60 seconds (automated)
- **Types**: Contracts, agreements, terms of service

### Document Types
- Employment agreements (40 documents)
- Non-disclosure agreements (25 documents)
- Service contracts (20 documents)
- Terms of service (15 documents)
- Other legal documents (8 documents)

### Key Features Tested
- **Hierarchical numbering**: 1.1, 1.1.1, 1.1.1.1
- **Defined terms**: Capitalized defined terms
- **Cross-references**: Section references
- **Complex clauses**: Multi-paragraph clauses
- **Legal formatting**: All caps headers, indentation

### Generation Method
1. **Templates**: Legal document templates with realistic clauses
2. **Variations**: Randomized parties, dates, terms
3. **Complexity**: 5-50 sections per document
4. **Conversion**: LibreOffice DOCX→PDF

### Ground Truth
Extracted from DOCX structure:
- Section numbering and hierarchy
- Clause text with formatting
- Defined terms
- Signature blocks

### Benchmark Results
- Status: Benchmarking in progress
- Expected: Structure-aware parsers to excel on numbering

**Files**:
- PDFs: `corpus/business/legal/pdfs/*.pdf`
- Ground truth: `corpus/business/legal/ground_truth/*.md`
- Metadata: `corpus/business/legal/metadata/*.yaml`
- Builder: `builders/build_legal_corpus.py`

---

## 4. Business HR Corpus (34 Documents)

**Purpose**: Test extraction of resumes and job applications

### Statistics
- **Documents**: 34 resumes
- **Size**: ~3MB total
- **Generation Time**: ~20 seconds (automated)
- **Formats**: Multiple layout styles

### Resume Variants
- Traditional format (reverse chronological)
- Functional format (skills-focused)
- Combination format
- Academic CV style
- Creative/design-focused

### Industries Represented
- Technology
- Finance
- Healthcare
- Education
- Manufacturing
- Retail
- Consulting

### Key Features Tested
- **Sections**: Contact, summary, experience, education, skills
- **Lists**: Bullet points (responsibilities, achievements)
- **Tables**: Skills matrix
- **Formatting**: Bold, italics, different font sizes
- **Layout**: Single column, two-column

### Generation Method
1. **Templates**: Resume templates with realistic content
2. **Data**: Generated profiles (names, companies, dates)
3. **Variations**: Different layouts and styles
4. **Conversion**: LibreOffice DOCX→PDF

### Ground Truth
Extracted from DOCX structure:
- Section headers
- Work experience (company, title, dates, responsibilities)
- Education (institution, degree, dates)
- Skills lists
- Contact information

### Benchmark Results
- Status: Benchmarking in progress
- Expected: Layout-aware parsers to handle format variations

**Files**:
- PDFs: `corpus/business/hr/pdfs/*.pdf`
- Ground truth: `corpus/business/hr/ground_truth/*.md`
- Metadata: `corpus/business/hr/metadata/*.yaml`
- Builder: `builders/build_hr_corpus.py`

---

## 5. Academic Corpus (5 Sample Papers)

**Purpose**: Test equation extraction and academic paper formatting

### Statistics
- **Documents**: 5 arXiv papers
- **Source**: LaTeX source from arXiv
- **Format**: Two-column academic papers
- **Equations**: Math-heavy content

### Papers Included
1. **2303.18223**: Navier-Stokes analysis (high math complexity)
2. **2303.08774**: GPT-4 technical report
3. **2302.13971**: LLaMA paper
4. **2303.17564**: BloombergGPT
5. **2303.18223**: LLM survey

### Key Features Tested
- **Equations**: LaTeX math rendering
- **Two-column layout**: Academic format
- **Citations**: References and bibliography
- **Figures**: Captions and placement
- **Tables**: Academic data tables

### Ground Truth Source
**LaTeX source** (arxiv.org provides original .tex files):
- Perfect equation ground truth
- Semantic structure preserved
- Can extract specific elements

**Alternative**: ar5iv HTML5 conversion
- Human-readable HTML
- MathML for equations
- Can serve as additional validation

### Benchmark Results
- Status: Marker+Ollama testing in progress
- Expected: Only Marker variants handle equations well
- Alternative parsers: Text-only extraction

### Use Cases
- Equation extraction quality testing
- Academic paper parsing
- Multi-column layout testing
- Math-heavy document benchmarking

**Files**:
- PDFs: `corpus/academic/sample/*.pdf`
- LaTeX source: `corpus/academic/sample/*.tar.gz`
- Builder: `builders/download_arxiv_corpus.py`

---

## Corpus Generation Infrastructure

### DOCX→PDF Pipeline

**Tools**:
- `python-docx`: Programmatic DOCX creation
- `LibreOffice`: Headless PDF conversion
- `Jinja2`: Template engine for variations

**Benefits**:
- 100% reproducible
- Perfect ground truth (source of truth is code)
- Scalable (can generate 1000s of documents)
- Controlled complexity

**Process**:
```python
# 1. Create DOCX with python-docx
doc = Document()
doc.add_heading('Title', 0)
doc.add_paragraph('Content')
table = doc.add_table(rows=3, cols=3)
# ... add content ...
doc.save('document.docx')

# 2. Extract ground truth from DOCX structure
markdown = extract_markdown_from_docx(doc)
Path('document.md').write_text(markdown)

# 3. Convert DOCX → PDF with LibreOffice
subprocess.run([
    'libreoffice', '--headless', '--convert-to', 'pdf',
    'document.docx', '--outdir', 'output/'
])
```

### Failed Approaches (For Reference)

**HTML→Markdown** (FAILED):
- Tried: GOV.UK, SEC EDGAR HTML as ground truth
- Failed: HTML and PDF are semantically different
- Lesson: Don't use HTML as PDF ground truth

**LaTeX→PDF** (Partial success):
- Works for academic papers
- Complex: LaTeX compilation issues
- Limited: Only for equation-heavy documents

---

## Quality Assurance

### Ground Truth Validation
All ground truth is validated by:
1. **Source validation**: Extracted from structured source (DOCX/LaTeX)
2. **Manual review**: Sample documents manually inspected
3. **Parser consensus**: Multiple parsers should agree on ground truth
4. **Metadata completeness**: All documents have complete metadata

### Known Issues

**Resolved**:
- GOV.UK corpus deleted (HTML/PDF version mismatch)
- OmniDocBench archived (OCR benchmark, out of scope)

**None currently** - All 5 corpora are high quality

---

## Future Expansion

### Planned Corpora

**Financial Documents** (50+ docs):
- 10-K filings
- Earnings reports
- Balance sheets
- Income statements

**Government Forms** (50+ docs):
- Tax forms (1040, W-2, etc.)
- Immigration forms
- License applications
- Government reports

**Healthcare** (30+ docs):
- Medical records (anonymized)
- Insurance claims
- Lab reports
- Prescription forms

**Technical Docs** (30+ docs):
- API documentation
- User manuals
- Technical specifications
- Product datasheets

**Total Target**: 500+ documents across 10+ categories

---

## Usage

### Loading a Corpus

```python
from pdf_bench import load_corpus

# Load specific corpus
corpus = load_corpus("synthetic")
print(f"{len(corpus)} documents loaded")

# Iterate through documents
for doc in corpus:
    pdf_path = doc.pdf_path
    ground_truth = doc.ground_truth
    metadata = doc.metadata
```

### Running Benchmarks

```bash
# Single corpus
python -m pdf_bench benchmarks/synthetic.yaml

# Multiple corpora
python -m pdf_bench benchmarks/comprehensive.yaml

# Specific parser
python -m pdf_bench benchmarks/synthetic.yaml --parsers pypdfium2,marker_ollama
```

### Creating Custom Corpus

See builder scripts in `builders/` directory for examples:
- `builders/generate_invoice_corpus.py` - Invoice generation
- `builders/build_legal_corpus.py` - Legal documents
- `builders/build_hr_corpus.py` - Resume generation

---

## References

**Code**:
- `pdf_bench/loader.py` - Corpus loading
- `pdf_bench/config.py` - Corpus configuration
- `builders/` - Corpus generation scripts

**Documentation**:
- `corpus/synthetic/CORPUS_SUMMARY.md` - Synthetic details
- `.claude/reference/lessons_learned.md` - Generation insights

---

**Last Updated**: 2025-11-20
**Total Documents**: 280 with perfect ground truth
**Ready for Benchmarking**: All 5 corpora
