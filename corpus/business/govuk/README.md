# GOV.UK Publications Corpus

**Version:** 1.0
**Created:** 2025-11-16
**License:** [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

## Overview

This corpus contains 26 UK government publications downloaded from GOV.UK and related government websites. It includes a diverse range of document types including annual reports, white papers, statistical releases, and policy documents from various government departments and agencies.

The corpus is designed for PDF parsing and extraction benchmarking, providing both PDF files and high-quality Markdown ground truth derived from official HTML sources.

## Corpus Statistics

- **Total Documents:** 26
- **Documents with PDF:** 18
- **HTML-only Documents:** 8
- **Total Pages:** 2,251
- **Total Size:** ~77 MB
  - PDF Files: ~70.6 MB
  - Markdown Ground Truth: ~1.9 MB
- **Complexity Distribution:**
  - Simple: 4 documents
  - Medium: 14 documents
  - Complex: 8 documents

## Directory Structure

```
govuk/
├── corpus_metadata.yaml       # Overall corpus metadata
├── download_metadata.json     # Download tracking metadata
├── README.md                  # This file
├── html/                      # Cleaned HTML sources (26 files)
│   ├── govuk_001.html
│   └── ...
├── ground_truth/              # Markdown ground truth (26 files)
│   ├── govuk_001.md
│   └── ...
├── pdfs/                      # PDF files (22 files)
│   ├── govuk_001.pdf
│   └── ...
└── metadata/                  # Individual document metadata (26 files)
    ├── govuk_001.yaml
    └── ...
```

## Document Coverage

### Topics Covered

Agriculture, annual reports, border control, business, civil liberties, courts, crime, dairy, defence, development, disease surveillance, economy, education, employment, energy, epidemiology, finance, GDP, governance, health, housing, immigration, infrastructure, justice, labour market, planning, policing, policy, prisons, public health, public opinion, public transport, regulation, research, schools, security, society, statistics, taxation, training, transport, veterinary, welfare

### Publishers

- Animal and Plant Health Agency
- Cabinet Office
- Companies House
- Department for Education
- Department for Energy Security and Net Zero
- Department for Environment, Food & Rural Affairs
- Department for Transport
- Department for Work and Pensions
- HM Revenue & Customs
- HM Treasury
- Home Office
- Ministry of Defence
- Ministry of Housing, Communities & Local Government
- Ministry of Justice
- NHS England
- Office for National Statistics
- Office of the Chief Medical Officer

## Data Quality

### Ground Truth Generation

Markdown ground truth files were generated from official HTML versions published by the UK government. The conversion process:

1. **HTML Download:** Clean HTML content extracted from GOV.UK pages using BeautifulSoup
2. **Content Extraction:** Navigation, headers, footers removed; main content preserved
3. **Markdown Conversion:** HTML converted to Markdown using markdownify with custom rules
4. **Quality Assurance:** All conversions validated for completeness and correctness

### Validation

All corpus files have been validated for:
- ✅ File existence (HTML, Markdown, PDF where expected, metadata)
- ✅ File integrity (SHA256 hashes for all PDFs)
- ✅ Metadata completeness (all required fields present)
- ✅ License information (OGL v3.0 for all documents)
- ✅ Non-empty content (minimum size checks)

Validation result: **100% PASSED** (0 errors, 0 warnings)

## Sample Documents

### Annual Reports (Complex)
- **govuk_001**: NHS England Annual Report 2024-25 (202 pages, 2.3 MB)
- **govuk_003**: HMRC Annual Report 2024-25 (338 pages, 10.4 MB)
- **govuk_027**: Health Trends and Variation 2025 (186 pages, 20.1 MB)

### Policy Documents (Medium)
- **govuk_007**: Get Britain Working White Paper (87 pages, 1.1 MB)
- **govuk_008**: Immigration System White Paper (80 pages, 2.4 MB)

### Statistical Releases (Simple to Medium)
- **govuk_009**: Crime Outcomes 2024-25 (45 pages, HTML-only)
- **govuk_019**: Employment in the UK Nov 2025 (34 pages, 2.4 MB)
- **govuk_020**: GDP Quarterly Accounts Q4 2024 (28 pages, 1.8 MB)

## Metadata Schema

Each document has an individual metadata file (`metadata/govuk_XXX.yaml`) containing:

```yaml
id: govuk_001
title: "Document Title"
source_url: "https://www.gov.uk/..."
publisher: "Publisher Name"
publication_date: "YYYY-MM-DD"
license: "Open Government Licence v3.0"
license_url: "https://..."
download_date: "2025-11-16"
topics: [topic1, topic2, ...]
complexity: simple|medium|complex
pdf_url: "https://..."           # if PDF available
sha256_pdf: "hash..."            # if PDF available
file_size_pdf: 1234567           # bytes
page_count: 42
has_pdf: true|false
file_size_html: 12345
file_size_markdown: 1234
```

## Usage

### For Benchmarking PDF Parsers

1. **Input:** PDF files from `pdfs/` directory
2. **Expected Output:** Markdown text matching `ground_truth/*.md`
3. **Metadata:** Use `metadata/*.yaml` for document properties

### Loading the Corpus

```python
import yaml
from pathlib import Path

# Load corpus metadata
corpus_dir = Path("corpus/business/govuk")
with open(corpus_dir / "corpus_metadata.yaml") as f:
    corpus = yaml.safe_load(f)

# Iterate through documents
for doc_id in corpus["documents"]:
    # Load document metadata
    with open(corpus_dir / "metadata" / f"{doc_id}.yaml") as f:
        doc = yaml.safe_load(f)

    # Access files
    pdf_path = corpus_dir / "pdfs" / f"{doc_id}.pdf"
    markdown_path = corpus_dir / "ground_truth" / f"{doc_id}.md"

    if doc["has_pdf"] and pdf_path.exists():
        print(f"{doc_id}: {doc['title']} ({doc['page_count']} pages)")
```

## Known Limitations

1. **HTML-Only Documents:** 8 documents do not have official PDFs (marked with `has_pdf: false`)
2. **404 Errors:** 4 documents from the original target list had URLs that were no longer accessible
3. **Page Counts:** Some documents may have page counts from metadata rather than actual PDF analysis
4. **Non-PDF Formats:** 1 document (govuk_011) has data in ZIP format rather than PDF

## License and Attribution

This corpus is distributed under the **Open Government Licence v3.0**.

You are free to:
- Copy, publish, distribute and transmit the information
- Adapt the information
- Exploit the information commercially and non-commercially

Subject to the conditions:
- You must acknowledge the source of the information
- You must not use the information in a way that suggests official status or government endorsement

**License:** https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/

**Source:** UK Government (https://www.gov.uk/)

## Building the Corpus

To rebuild or update this corpus:

```bash
# 1. Download HTML content
python builders/download_govuk_corpus.py --skip-existing

# 2. Convert HTML to Markdown
python builders/convert_govuk_corpus.py \
  --input-dir corpus/business/govuk/html \
  --output-dir corpus/business/govuk/ground_truth

# 3. Download PDFs
python builders/download_govuk_pdf_corpus.py --skip-existing

# 4. Generate metadata
python builders/create_govuk_metadata.py

# 5. Validate corpus
python builders/validate_govuk_corpus.py
```

## Citation

If you use this corpus in academic work, please cite:

```
GOV.UK Publications Corpus v1.0 (2025)
UK Government Publications via GOV.UK
Licensed under Open Government Licence v3.0
https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
```

## Version History

- **v1.0** (2025-11-16): Initial release
  - 26 documents from diverse government departments
  - 18 PDFs with ground truth Markdown
  - 8 HTML-only documents with Markdown ground truth
  - Full metadata and validation

## Contact & Issues

For issues related to this corpus or the PDF-Bench project, please refer to the main project repository.

For issues with source documents or URLs, contact the respective UK government departments or visit https://www.gov.uk/.
