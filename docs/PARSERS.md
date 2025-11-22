# PDF Parser Feature Comparison

## Quick Reference Matrix

| Parser | Accuracy | Speed | Tables | OCR | Multi-Column | Math | Images | License | Language | Deps |
|--------|----------|-------|--------|-----|--------------|------|--------|---------|----------|------|
| **PyPDFium2** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ | ❌ | ✅ | Apache-2.0/BSD | Python/C++ | Minimal |
| **Kreuzberg** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ | ❌ | ✅ | MIT | Rust | Minimal |
| **PyPDF** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ | ❌ | ✅ | BSD | Python | None |
| **PyPDF2** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ | ❌ | ✅ | BSD | Python | None |
| **PyMuPDF** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | ⭐⭐⭐⭐⭐ | ❌ | ✅ | AGPL | Python/C | Minimal |
| **Extractous** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ❌ | ⭐⭐⭐ | ❌ | ✅ | Apache-2.0 | Rust | Minimal |
| **Tika** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | ⭐⭐⭐ | ❌ | ✅ | Apache-2.0 | Java/Python | Java |
| **PyMuPDF4LLM** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ | ❌ | ✅ | AGPL | Python/C | Minimal |
| **PDFMiner** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ❌ | ⭐⭐ | ❌ | ⭐ | MIT | Python | None |
| **Unstructured** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ✅ | ⭐⭐ | ❌ | ✅ | Apache-2.0 | Python | Heavy |
| **PdfPlumber** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐ | ❌ | ✅ | MIT | Python | Minimal |
| **Docling** | ⭐⭐ | ⭐ | ⭐⭐⭐ | ✅ | ⭐⭐⭐ | ❌ | ✅ | MIT | Python | Heavy |
| **Marker** | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | GPL-3.0 | Python | GPU |

**Rating Scale**: ⭐ Poor / ⭐⭐ Fair / ⭐⭐⭐ Good / ⭐⭐⭐⭐ Very Good / ⭐⭐⭐⭐⭐ Excellent

## Detailed Parser Profiles

### 1. PyPDFium2 (Winner - 82.65%)

**Overview**: Python bindings for Google's PDFium engine (used in Chrome)

**Strengths**:
- Highest accuracy in our benchmark (82.65%)
- Fast performance (1-4ms per doc)
- Consistent across all document types
- Well-maintained by Google
- Minimal dependencies

**Weaknesses**:
- No OCR support
- No mathematical equation extraction
- Limited table structure API

**Best For**:
- General-purpose PDF extraction
- Production applications needing reliability
- When accuracy matters most

**Installation**: `uv pip install pypdfium2`

**Example**:
```python
from pypdfium2 import PdfDocument

doc = PdfDocument("file.pdf")
text = ""
for page in doc:
    textpage = page.get_textpage()
    text += textpage.get_text_range()
```

---

### 2. Kreuzberg (Runner-up - 82.55%)

**Overview**: Modern Rust-based PDF parser with OCR support

**Strengths**:
- Nearly tied for first (82.55%)
- Built-in OCR via Tesseract
- Async API support
- Memory-safe (Rust)
- Fast (5-11ms per doc)

**Weaknesses**:
- Relatively new project
- Smaller community
- OCR adds complexity

**Best For**:
- Modern async Python applications
- Projects already using Rust
- When OCR is needed

**Installation**: `uv pip install kreuzberg`

**Example**:
```python
import asyncio
from kreuzberg import extract_file

async def extract():
    result = await extract_file("file.pdf")
    return result.content

text = asyncio.run(extract())
```

---

### 3. PyPDF (79.61%)

**Overview**: Modern, actively maintained PyPDF fork

**Strengths**:
- Active development
- Pure Python (no C deps)
- Good documentation
- Easy to install
- Strong community

**Weaknesses**:
- No OCR
- Table extraction is basic
- Multi-column handling decent but not great

**Best For**:
- Projects wanting pure Python
- When dependencies are a concern
- General text extraction

**Installation**: `uv pip install pypdf`

**Example**:
```python
from pypdf import PdfReader

reader = PdfReader("file.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()
```

---

### 4. PyPDF2 (78.95%)

**Overview**: Legacy PyPDF version, stable but less maintained

**Strengths**:
- Very stable
- Well-tested
- Pure Python
- No dependencies
- Familiar to many developers

**Weaknesses**:
- Less active maintenance
- Fewer features than PyPDF
- Community moved to PyPDF

**Best For**:
- Legacy projects
- When stability > features
- Pure Python requirement

**Installation**: `uv pip install PyPDF2`

---

### 5. PyMuPDF (78.26%)

**Overview**: Python bindings for MuPDF C library

**Strengths**:
- **Fastest parser** (0-3ms per doc)
- Excellent multi-column support
- Mature, stable
- Rich feature set
- Memory efficient

**Weaknesses**:
- AGPL license (restrictive)
- No OCR
- C dependency

**Best For**:
- Speed-critical applications
- High-volume processing
- When AGPL is acceptable

**Installation**: `uv pip install pymupdf`

**Example**:
```python
import fitz  # pymupdf

doc = fitz.open("file.pdf")
text = ""
for page in doc:
    text += page.get_text()
```

---

### 6. Extractous (75.95%)

**Overview**: Rust-based parser supporting 50+ file formats

**Strengths**:
- Supports 50+ formats (PDF, DOCX, XLSX, etc.)
- Rust performance
- Single library for all formats
- Active development

**Weaknesses**:
- Slower than specialized parsers (100-160ms)
- Generalist vs specialist tradeoff
- Larger dependency footprint

**Best For**:
- Multi-format document processing
- When you need one library for everything
- ETL pipelines with varied inputs

**Installation**: `uv pip install extractous`

---

### 7. Apache Tika (72.94%)

**Overview**: Apache's content analysis framework

**Strengths**:
- Battle-tested
- Multi-format support
- OCR via Tesseract
- Rich metadata extraction
- Enterprise-ready

**Weaknesses**:
- Requires Java runtime
- Slower than native parsers
- Large dependency

**Best For**:
- Enterprise environments
- When you already use Java
- Metadata extraction important

**Installation**: `uv pip install tika`

---

### 8. PyMuPDF4LLM (69.86%)

**Overview**: PyMuPDF variant optimized for LLM consumption

**Strengths**:
- Markdown output optimized for LLMs
- Fast (based on PyMuPDF)
- Good for RAG pipelines
- Preserves structure for AI

**Weaknesses**:
- Lower accuracy than base PyMuPDF
- AGPL license
- Optimization tradeoffs

**Best For**:
- RAG (Retrieval Augmented Generation)
- LLM training data preparation
- AI/ML pipelines

**Installation**: `uv pip install pymupdf4llm`

---

### 9. PDFMiner (68.55%)

**Overview**: Pure Python PDF parser focusing on internals

**Strengths**:
- Pure Python
- Deep PDF structure access
- No dependencies
- Educational value
- Layout analysis tools

**Weaknesses**:
- Lower accuracy
- Slower than C-based parsers
- Less intuitive API
- Less maintained

**Best For**:
- Learning PDF internals
- When you need layout coordinates
- Pure Python requirement

**Installation**: `uv pip install pdfminer.six`

---

### 10. Unstructured (65.45%)

**Overview**: ETL-focused library for unstructured data

**Strengths**:
- Multi-format support
- ETL pipeline integration
- Chunking strategies
- Fast (0-1ms)
- Good for data pipelines

**Weaknesses**:
- Lower accuracy than specialists
- Heavy dependencies
- Complex configuration

**Best For**:
- Data engineering pipelines
- Multi-format ETL
- When you need chunking/partitioning

**Installation**: `uv pip install unstructured`

---

### 11. PdfPlumber (63.60%)

**Overview**: Table extraction specialist built on pdfminer.six

**Strengths**:
- **Excellent table extraction API**
- Visual debugging tools
- Fast (0-228ms)
- Pure Python
- Great for data extraction

**Weaknesses**:
- Struggles with multi-column layouts
- Lower overall accuracy
- Complex documents harder

**Best For**:
- **Table-heavy documents**
- Financial reports
- Data extraction from forms

**Installation**: `uv pip install pdfplumber`

**Example**:
```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        text = page.extract_text()
```

---

### 12. Docling (51.65%)

**Overview**: IBM's structure-preserving document converter

**Strengths**:
- Preserves document structure
- OCR support
- GPU acceleration
- Multi-format output
- Active IBM development

**Weaknesses**:
- **Struggled with synthetic PDFs** (51.65%)
- Slowest parser (1-2s per doc)
- Heavy dependencies
- Complex setup

**Best For**:
- When structure preservation is critical
- IBM ecosystem integration
- Research applications

**Note**: Low score may be due to synthetic PDF compatibility issues, not parser quality

**Installation**: `uv pip install docling`

---

### 13. Marker (TBD - Expected ~74%)

**Overview**: GPU-accelerated ML-based parser

**Strengths**:
- **Excellent mathematical equation support**
- GPU acceleration
- Best multi-column handling
- High quality output
- OCR built-in

**Weaknesses**:
- **Very slow** (5-7s per page)
- Requires GPU for speed
- Heavy dependencies
- GPL license

**Best For**:
- Academic papers with equations
- When quality > speed
- GPU available

**Installation**: `uv pip install marker-pdf`

**Note**: Requires GPU for reasonable performance. CPU fallback is very slow.

---

## Feature Deep Dive

### Table Extraction

**Best**: PdfPlumber (specialized API)
**Good**: PyPDFium2, Kreuzberg, Marker
**Fair**: Most others
**Poor**: Multi-column aware parsers sometimes break tables

### Multi-Column Layouts

**Best**: PyMuPDF, Marker, Kreuzberg
**Good**: PyPDFium2, PyPDF, PyPDF2
**Fair**: Extractous, Tika
**Poor**: PdfPlumber, Unstructured, PDFMiner

### Mathematical Equations

**Best**: Marker (only one with good math support)
**None**: All others don't extract equations well

### OCR Support

**Built-in**: Marker, Kreuzberg, Docling, Unstructured, Tika
**None**: PyPDFium2, PyPDF, PyPDF2, PyMuPDF, Extractous, PdfPlumber, PDFMiner, PyMuPDF4LLM

### Speed

**Fastest** (0-5ms): PyMuPDF, PdfPlumber, Unstructured
**Fast** (5-15ms): PyPDFium2, Kreuzberg, PyPDF, PyPDF2, Tika, PDFMiner, PyMuPDF4LLM
**Slow** (100ms+): Extractous
**Very Slow** (1s+): Docling, Marker

### License Considerations

**Permissive** (MIT, BSD, Apache):
- PyPDFium2 (Apache-2.0/BSD)
- Kreuzberg (MIT)
- PyPDF (BSD)
- PyPDF2 (BSD)
- Extractous (Apache-2.0)
- Tika (Apache-2.0)
- PdfPlumber (MIT)
- PDFMiner (MIT)
- Docling (MIT)
- Unstructured (Apache-2.0)

**Copyleft** (AGPL, GPL):
- PyMuPDF (AGPL) - requires source release if modified
- PyMuPDF4LLM (AGPL)
- Marker (GPL-3.0)

---

## Use Case Recommendations

### Academic Paper Extraction
1. **Marker** - Best for equations and complex layouts
2. **PyPDFium2** - Good general accuracy
3. **Kreuzberg** - Fast with good quality

### Financial Reports (Tables)
1. **PdfPlumber** - Table extraction specialist
2. **PyPDFium2** - Good balance
3. **Kreuzberg** - Fast and accurate

### High-Volume Production
1. **PyMuPDF** - Fastest, very good quality
2. **PyPDFium2** - Best accuracy, fast enough
3. **Kreuzberg** - Good balance

### Multi-Format ETL Pipelines
1. **Extractous** - 50+ formats, Rust-based
2. **Tika** - Enterprise standard
3. **Unstructured** - Data pipeline focus

### RAG / LLM Applications
1. **PyMuPDF4LLM** - LLM-optimized
2. **Marker** - Excellent structure preservation
3. **PyPDFium2** - Most accurate

### Simple Text Extraction
1. **PyPDF** - Pure Python, easy
2. **PyPDF2** - Stable, proven
3. **PyPDFium2** - Most accurate

### OCR Required
1. **Marker** - Best quality
2. **Kreuzberg** - Fast with OCR
3. **Docling** - Structure-aware
4. **Tika** - Battle-tested

---

## Benchmark Notes

- **Test corpus**: 31 synthetic PDFs with perfect ground truth
- **Metric**: Text similarity (case-insensitive)
- **Hardware**: Linux, Python 3.13, RTX 3090 GPU
- **Date**: 2025-11-18

---

**Last Updated**: 2025-11-18
**Benchmark Version**: 1.0
**Total Parsers**: 13
