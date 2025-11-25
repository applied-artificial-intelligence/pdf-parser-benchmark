# **A Strategic Benchmark for PDF-to-Markdown Conversion: Design, Specification, and Implementation PRD**

## **Executive Summary**

This report presents a comprehensive plan for the design, construction, and deployment of an open-source benchmarking suite for PDF-to-semantic-Markdown conversion. The objective is to create a practical, legally sound, and technically rigorous asset for a consulting firm to evaluate document intelligence systems and establish public thought leadership.

The current landscape of document parsing benchmarks is bifurcated. On one side are layout-centric datasets (e.g., DocLayNet) that lack semantic ground truth.1 On the other are academically-focused, end-to-end benchmarks (e.g., \\readoc, OmniDocBench).3 Critically, the most comprehensive benchmark, OmniDocBench, is explicitly restricted to non-commercial, research-only use.5 This creates a prohibitive gap for commercial applications, including internal evaluation for client projects.

This specification details a practical solution. It outlines a "recipes-only" corpus built from two commercially permissive sources: (1) **Harvested academic and government documents** (e.g., arXiv, GOV.UK 3), where paired LaTeX/HTML and PDF content exists under open licenses; and (2) **Synthetically generated enterprise documents**, created using a deterministic DOCX/Pandoc-to-PDF pipeline.8

The report specifies a multi-layered evaluation framework, including metrics for text accuracy (Normalized Edit Distance 6), table structure (TEDS 6), mathematical content (LaTeX string match 3), and, importantly, semantic structure (Markdown AST Tree-Edit Distance).

Finally, this document serves as a Product Requirements Document (PRD) for the open-source evaluation library, pdf-bench. It details the system architecture, a pluggable adapter interface for benchmarking parsers (e.g., Marker, Nougat, AWS Textract, Azure Document Intelligence 10), and a CLI/API specification. This asset is designed not only to improve internal tool-selection processes but also to serve as a high-visibility platform for community engagement and content marketing.

## **1\. Analysis of the Existing Benchmark Landscape**

A review of the existing ecosystem reveals a critical gap for a benchmark that is simultaneously (1) focused on semantic PDF-to-Markdown conversion, (2) representative of diverse business and enterprise documents, and (3) available under a commercially permissive license.

### **1.1 Review of PDF-to-Markdown and Rich Text Benchmarks**

Benchmarks explicitly targeting PDF-to-rich-text conversion are nascent but provide important precedents.

* **\\readoc:** This recent benchmark defines the task of Document Structured Extraction (DSE) as a PDF-to-Markdown conversion.3 Its corpus is divided into two parts. \\readoc-arXiv (1,009 documents) uses a ground truth pipeline of LaTeX $\\rightarrow$ LaTeXML $\\rightarrow$ HTML $\\rightarrow$ Markdown, validating this as a scalable method for academic content. \\readoc-GitHub (1,224 documents) uses a clever "round-trip" method, converting source Markdown READMEs to PDF via Pandoc and evaluating the reconversion.3 While its methodology is sound and its license (Apache 2.0) is permissive, its corpus has significant gaps for enterprise use: the GitHub set *explicitly excludes tables and formulas* 3, and the arXiv set is, by definition, purely academic.  
* **dp-bench:** This benchmark targets PDF-to-HTML/Markdown conversion. However, its ground truth is a JSON file representing 12 layout element types (e.g., Table, Paragraph, Figure) with positional information.14 This positions it as a layout *segmentation* benchmark ("is this bounding box a Table?") rather than a true semantic *content* benchmark ("is this the correct Markdown representation of the table's content and structure?").

### **1.2 Review of Layout and Structure Datasets**

Layout-focused datasets are mature but serve a different purpose, prioritizing visual segmentation over semantic content extraction.

* **DocLayNet:** This is a large-scale, valuable dataset of 80,863 pages, human-annotated with bounding boxes for 11 layout classes.1 Its key strength is its diversity, sourcing from finance, patents, legal, and other non-academic domains.1 However, its COCO-format ground truth only identifies *where* a table is, not what its content, structure, or reading order is.16 It is unsuitable as a primary ground truth for semantic conversion but provides an excellent model for document sourcing and diversity.  
* **PubLayNet and DocBank:** These are large-scale datasets (360k+ samples for PubLayNet 17) but are severely limited in variability, as they are sourced almost exclusively from scientific articles on PubMed and arXiv.2  
* **OmniDocBench:** This is the most functionally relevant existing benchmark. It is distinguished by:  
  * **Document Diversity:** It includes 1,355 pages covering 9 document types, critically including *financial reports, slides, textbooks, magazines*, and *newspapers*—a significant step into business-relevant domains.4  
  * **Semantic Richness:** Its annotations are multi-level, including 15 block-level (e.g., tables) and 4 span-level (e.g., inline formulas) types.5 Crucially, it provides *LaTeX annotations for formulas* and *both LaTeX and HTML annotations for tables*.5  
  * **Evaluation:** It explicitly supports an "end2end" evaluation 6 that can use Markdown as a ground truth ("md2md" 6) and employs a sophisticated metric portfolio (Normalized Edit Distance, TEDS, CDM).6

### **1.3 Analysis of Model-Specific Datasets**

Models targeting PDF-to-Markdown conversion implicitly rely on paired datasets.

* **Nougat:** The official model from Meta AI is trained on a large corpus of scientific documents from arXiv, leveraging the paired PDF and LaTeX source files.11 This confirms that a high-fidelity academic benchmark *must* be sourced from TeX to evaluate complex math and table structures correctly.22  
* **Marker:** This open-source tool underscores the importance of hybrid (model \+ LLM) approaches, particularly for post-processing tasks such as merging tables across pages, handling inline math, and properly formatting tables.4 Any robust benchmark must include cases that test these specific, high-level semantic structuring capabilities.

### **1.4 Synthesis: A Comparative Analysis and Gap Identification**

The analysis of OmniDocBench reveals a critical, project-defining gap. While its *functionality* (diverse types, semantic GT, MD evaluation) is precisely what the market needs, its *license* is fundamentally incompatible with the stated goals. The dataset, hosted on Hugging Face and OpenDataLab, is explicitly restricted: **"The dataset is for research purposes only and not for commercial use"**.5 A related discussion also points to a cc-by-nc-4.0 (NonCommercial) license.24

This non-commercial restriction makes OmniDocBench unusable for the consulting firm's objectives:

1. It cannot be used for internal evaluation on client projects (a commercial activity).  
2. It cannot be used as the basis for a public-facing "thought-leadership" asset, which serves a commercial marketing purpose.

This finding establishes a clear and immediate market opportunity. A "spiritual successor" to OmniDocBench is needed—one that adopts its rigorous methodology but is built from the ground up on a corpus of **commercially permissive data sources**.

**Table 1: Landscape Benchmark Comparison**

| Dataset | Source Types | Ground Truth Format | Metrics Used | License | Commercial Reusability | Key Gaps for Enterprise Use |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **DocLayNet** | Diverse (Finance, Legal) 1 | COCO (Bounding Boxes) 2 | mAP | Permissive | **Yes** | **No semantic/content ground truth.** Layout only. |
| **PubLayNet** | Academic (PubMed) 17 | COCO (Bounding Boxes) | mAP | Permissive | **Yes** | No semantic GT. Academic only. |
| **\\readoc** | Academic (arXiv), Code (GitHub) 3 | Markdown 3 | Text-level | Apache 2.0 | **Yes** | **No business/enterprise docs.** GitHub set lacks tables/math.3 |
| **OmniDocBench** | **Diverse (Finance, Slides, Books)** 4 | **Rich JSON (Layout \+ Content), Markdown** 5 | **TEDS, CDM, Edit Distance** 6 | CC-BY-NC 4.0 / **Non-Commercial** 5 | **No** | **License is prohibitive.** This is the primary blocker. |
| **Proposed Benchmark** | **Diverse (Academic, Gov, Finance, Synthetic)** | **Canonical Markdown (w/ HTML tables)** | **TEDS, AST-Edit-Dist, Norm. Edit-Dist** | **Permissive (MIT / CC-BY)** | **Yes (Core Design Goal)** | *(N/A \- Designed to fill gaps)* |

## 

## **2\. A Practical Corpus Design for a Business-Relevant Benchmark**

The primary challenge is to construct a diverse, business-relevant corpus that is both legally permissive and obtainable without manual annotation. This will be achieved by harvesting from sources with paired structured data and by deterministic synthetic generation.

### **2.1 Track 1: Academic and Technical Corpus (v0: \~150 documents)**

This track provides a high-complexity baseline for math, tables, and multi-column layouts, following the precedent of Nougat and \\readoc.3

* **Source:** arXiv (e.g., categories cs.CL, cs.CV, math.AP, econ.EM).  
* **Sampling Strategy:** Documents will be sampled to ensure diversity in layout (single-column, two-column), subject matter, and mathematical complexity (measured by count of LaTeX environments in source).  
* **Ground Truth Pipeline:** A "recipes-only" builder script will:  
  1. Download the paired PDF and LaTeX source (.tar.gz) from arXiv.  
  2. Identify the main .tex file and parse it using **LaTeXML**.25 LaTeXML is chosen over Pandoc 27 for its superior, high-fidelity conversion of complex LaTeX macros and mathematical environments, which is a known limitation of Pandoc.28  
  3. A Python script will parse the intermediary LaTeXML output (HTML/XML) and convert it into the Canonical Markdown specification defined in Section 3\.  
* **License:** arXiv content is distributed under permissive licenses (e.g., CC-BY, arXiv perpetual license), making it suitable for this use.

### **2.2 Track 2: Business and Institutional Corpus (v0: \~250 documents)**

This track is the core strategic asset, providing the business-relevant diversity that existing benchmarks lack.

#### **2.2.1 Sub-Corpus A (Harvested): Government and NGO Reports (v0: \~150 documents)**

This sub-corpus leverages a key finding: government portals mandate open standards and often provide paired HTML/PDF content under permissive licenses.

* **Sources:**  
  1. **GOV.UK:** The UK Government Digital Service (GDS) mandates that content be published as HTML for accessibility, not PDF.29 Many complex reports (annual reports, policy briefs) are available as both a full HTML version and a downloadable PDF.32  
  2. **data.europa.eu (EU Portal):** The Publications Office of the European Union provides similar access to reports and publications in multiple formats.35  
  3. **SEC EDGAR:** The U.S. Securities and Exchange Commission provides financial filings (10-K, 10-Q) as public data.37 The source HTML/XML can be parsed to create ground truth for complex, multi-level financial tables, which are then paired with the official PDF version.38  
* **License:** The GOV.UK content is licensed under the **Open Government Licence v3.0 (OGL v3.0)**.7 The OGL v3.0 is a permissive, "copyleft-compatible" license that explicitly allows users to "copy, publish, distribute," "adapt," and "exploit the Information commercially and non-commercially," requiring only attribution.7 This *directly solves* the licensing barrier posed by OmniDocBench.5  
* **Ground Truth Pipeline:** A Python builder script will scrape the canonical HTML source, use a library like BeautifulSoup to clean and extract the semantic content (stripping headers, footers, nav-bars), and convert it to the Canonical Markdown specification.

#### **2.2.2 Sub-Corpus B (Synthetic): Enterprise Templates (v0: \~100 documents)**

This sub-corpus provides deterministic coverage for specific layouts not found in public-sector reports, such as consulting-style whitepapers, marketing slicks, and complex forms.

* **Ground Truth Pipeline (DOCX-based):**  
  1. A set of master templates (.docx) will be created in Microsoft Word, representing common business layouts (e.g., two-column whitepaper, financial statement, product brief).  
  2. **python-docx-template** 41 will be used to programmatically populate these templates with (e.g., faker) data via Jinja2 syntax. This allows for scalable generation of unique documents from a few templates. python-docx can create complex tables, images, and rich text.43  
  3. The generated .docx files will be deterministically converted to .pdf using a headless **LibreOffice** command.8 The command soffice \--headless \--convert-to pdf:writer\_pdf\_Export... provides a reliable server-side conversion.46  
  4. The ground truth is the structured data (Jinja context) and the source .docx structure, which is mapped to Canonical Markdown.  
* **Ground Truth Pipeline (Markdown-based):**  
  1. As a simpler "round-trip" test 3, a subset of documents will be authored in Markdown.  
  2. **Pandoc** 27 will be used with a professional LaTeX template (such as the Eisvogel template 9) to convert the source Markdown into a high-quality, business-styled PDF.  
  3. The source .md file serves as the perfect ground truth.

### **2.3 Phase 2: Extended Tracks (Roadmap)**

* **Scanned/OCR (v1.0):** The v0 born-digital PDFs will be "degraded" via a deterministic print-and-scan simulation (adding noise, rotation, and blur) to create a paired dataset for OCR-based parsers.  
* **Forms (v1.5):** A synthetic track for transactional documents (invoices, POs) using the pipeline from 2.2.2.  
* **Presentations (v2.0):** Paired .pptx (ground truth) and .pdf files.

### **2.4 Licensing, Distribution, and Governance**

* **License:** The benchmark library code and all synthetic/generated ground truth files will be licensed under **MIT** or **Apache 2.0**.  
* **Distribution:** A "recipes-only" approach is mandatory for legal safety. The repository will *not* redistribute any PDFs. It will contain:  
  1. ground\_truth/: The canonical Markdown ground truth files.  
  2. builders/: Python scripts to download/build the corpus.  
  3. metadata/: YAML files containing source URLs, file hashes, and document tags (see 3.3).  
* **Documentation:** To establish trust and transparency, the benchmark will adhere to the **"Datasheets for Datasets"** framework.49 A DATASHEET.md file will meticulously document:  
  * Motivation, composition, and collection process.50  
  * Full data provenance, including source URLs and the specific license for *each* document (e.g., OGL v3.0 7).  
  * Known limitations and biases (e.g., "English-only," "heavy focus on UK/EU report structures").53

**Table 2: v0 Corpus Design Specification**

| Track | Source | Document Types | Est. v0 Count | Ground Truth Method | License |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Academic** | arXiv 3 | CS/Math/Econ Papers | \~150 | Paired LaTeX source processed via LaTeXML pipeline 25 | arXiv License (e.g., CC-BY) |
| **Business (Harvested)** | GOV.UK 32 | Policy Reports, Whitepapers, Annual Reports | \~100 | Paired HTML source scraped & normalized 30 | Open Government Licence v3.0 7 |
| **Business (Harvested)** | EU Portal 35 | Policy Reports, Technical Briefs | \~50 | Paired HTML/XML source scraped & normalized | EU Permissive License 56 |
| **Business (Harvested)** | SEC EDGAR 57 | 10-K, 10-Q Financial Filings | \~50 | Source HTML/XML parsed for tables 39 | Public Domain |
| **Business (Synthetic)** | DOCX+LibreOffice 8 | Consulting Whitepapers, Marketing Layouts | \~50 | Programmatic generation via python-docx-template 41 | MIT License (generated data) |
| **Business (Synthetic)** | MD+Pandoc 9 | Simple Reports, Articles (Round-trip) 3 | \~50 | Source Markdown (round-trip validation) | MIT License (generated data) |
| **Total** |  |  | **\~450** |  |  |

## 

## **3\. Ground Truth Specification: Canonical Markdown and Normalization**

A benchmark's utility is contingent on a precise, unambiguous ground truth. This section defines the "Consulting Markdown" (CMD) specification, a strict subset of GFM with extensions for complex data.

### **3.1 The "Consulting Markdown" (CMD) Specification**

* **Headings:** \#, \#\#, \#\#\#,... Must be hierarchical and sequential.  
* **Paragraphs:** Standard text blocks separated by a double newline.  
* **Lists:** Ordered/unordered, must capture nesting correctly.  
* **Tables (Key Specification):**  
  * **Simple Tables:** Must be represented using GitHub Flavored Markdown (GFM) table syntax.  
  * **Complex Tables:** GFM syntax *cannot* represent merged cells (e.g., rowspan, colspan) or multi-level headers. Parsers *must* detect this. For any table that cannot be represented by GFM, the parser is expected to output an **embedded HTML \<table\> block** within the Markdown. This is valid Markdown and allows for the evaluation of complex structures. This methodology follows the practice of OmniDocBench, which uses HTML/LaTeX for table ground truth.5  
* **Mathematical Content:**  
  * Inline: Enclosed in single dollar signs, e.g., $E=mc^2$.  
  * Display: Enclosed in double dollar signs, e.g., $$\\sum\_{i=0}^{n}...$$.  
  * This follows the standard set by Nougat and \\readoc.3  
* **Figures and Images:**  
  * Syntax: \!\[caption text\](image\_filename.png).  
  * The caption text must match the semantic caption in the document (e.g., "Figure 1:...").  
* **Code Blocks:** GFM fenced blocks (\`\`\`python... \`\`\`).  
* **Footnotes/Endnotes:** GFM-style \[^1\] and \[^1\]:... at the document's end.  
* **Artifacts (Exclusions):** The ground truth will *not* contain running headers, footers, or page numbers. These are considered printing artifacts, not semantic content.

### **3.2 Normalization Rules for Evaluation**

To ensure the evaluation is robust and not brittle, a strict normalization pipeline, inspired by OmniDocBench 4, will be applied to both the ground truth and the parser's output *before* any comparison.

* **Text Normalization:**  
  * Unicode normalization (NFC).  
  * Collapse all sequences of whitespace (space, tab, newline) to a single space, except for newlines separating semantic blocks (e.g., paragraphs, list items).  
  * Trim leading/trailing whitespace from all blocks and lines.  
  * Normalize "smart" quotes and dashes: “...” $\\rightarrow$ "...", — $\\rightarrow$ \--.  
* **Table Normalization:**  
  * Before TEDS comparison, all HTML table tags and attributes will be lowercased and whitespace inside tags will be normalized.  
* **Equation Normalization:**  
  * Collapse whitespace within LaTeX expressions (e.g., \\frac {1} {2} becomes \\frac{1}{2}).  
  * Remove redundant grouping (e.g., {{a}} becomes {a}).

### **3.3 Document Metadata Schema (Per-File YAML)**

Each ground truth file (.md) will be accompanied by a YAML file (.yml) with the same name, containing essential metadata for the evaluation library.

YAML

doc\_id: gov\_uk\_env\_plan\_2023  
source\_url: https://www.gov.uk/government/publications/environmental-improvement-plan  
pdf\_url: https://assets.publishing.service.gov.uk/media/64a6d9c1c531eb000c64fffa/environmental-improvement-plan-2023.pdf  
pdf\_hash\_sha256: \<sha256\_hash\_of\_pdf\>  
ground\_truth\_file: gov\_uk\_report\_001.md  
license: Open Government Licence v3.0  
source: GOV.UK

properties:  
  category: "business\_harvested"  
  subcategory: "government\_report"  
  language: "en"  
  layout: "mixed"  
  page\_count: 262

tags: \# For slicing and dicing results  
  \- "has\_complex\_tables"  
  \- "has\_figures"  
  \- "has\_toc"  
  \- "has\_lists"  
  \- "has\_footnotes"

## **4\. Evaluation Design: Metrics, Tasks, and Error Analysis**

The evaluation suite must be multi-dimensional, capturing not just text content but also structural fidelity and semantic accuracy.

### **4.1 Core Evaluation Tasks**

* **Task 1: Full-Document PDF→Markdown:** The primary task. A parser is given a multi-page PDF and must output a single, complete Markdown file adhering to the CMD specification.  
* **Task 2 (Optional): Element-Specific Extraction:** The library will support evaluation focused on specific elements:  
  * **Table Extraction:** Evaluate *only* the table-containing blocks.  
  * **Math Extraction:** Evaluate *only* the LaTeX-containing blocks.  
  * **Layout Segmentation (v2):** A future track could compare bounding boxes for layout elements (Paragraph, Heading, Table) against DocLayNet-style 1 annotations.

### **4.2 A Multi-Layered Metric Portfolio**

The benchmark will produce a hierarchical set of scores, from coarse text-level to fine-grained structural analysis.

**Table 3: Core Metrics Specification**

| Metric | Target | Implementation | Interpretation |
| :---- | :---- | :---- | :---- |
| **Normalized Edit Distance** | Text Content | 1 \- (Levenshtein / max\_len).58 Applied to pure text blocks (tables/math excluded). | "How accurate is the raw text (OCR/extraction)?" |
| **Element F1 Score** | Structure (Coarse) | F1-score (Precision/Recall) on counts of element types (e.t., \#\#, \*, \<table\>). | "Did the parser find all 5 tables, or did it find 7?" |
| **AST Tree-Edit Distance** | Structure (Fine) | zss (Zhang-Shasha) tree-edit distance on the Markdown AST (e.g., from mistune). | "Is the document structure correct? (e.g., nesting, ordering)" |
| **TEDS (Tree-Edit-Distance)** | Table Structure | Python table-recognition-metric 60 on HTML \<table\> blocks. | "How accurate is the *structure* of the extracted tables?" |
| **Equation Match F1** | Math Content | F1-score on normalized LaTeX strings.3 | "How many math expressions were correctly extracted?" |

* ---

  **Text-Level Metrics:**  
  * **Normalized Edit Distance:** This is the standard for text-level comparison, used by OmniDocBench.6 After normalization (3.2), the Levenshtein distance 61 between the "pure text" (all structure/tables/math stripped) of the GT and the prediction is calculated and normalized to an accuracy score: $1 \- (\\text{Levenshtein} / \\text{max\\\_length})$.59  
* **Structure-Level Metrics:**  
  * This is a key differentiator. Text-level metrics can be high even if the document structure is completely wrong (e.g., all paragraphs merged, all headings at the wrong level).  
  * **Element F1 Score:** The system will parse both GT and prediction files and count the occurrences of key structural elements (e.g., H1, H2, ListItem, Table, DisplayMath). This yields a Precision, Recall, and F1 score for each element type, answering: "Did the parser find the correct *number* of tables?"  
  * **Markdown AST Tree-Edit Distance:** This is the most advanced structural metric. The GT and prediction Markdown files are parsed into Abstract Syntax Trees (ASTs). The tree-edit distance (e.g., using the zss library) is calculated between these two trees. This score robustly penalizes *structural* errors like incorrect nesting (a list item placed under the wrong section) or heading level errors.  
* **Table-Level Metrics:**  
  * **TEDS (Tree-Edit-Distance for Table Structure):** This is the industry standard, used by OmniDocBench 6 and available as a Python package.60 It compares the *HTML structure* of the GT and predicted tables, providing a single score that captures both structural and content accuracy.  
* **Equation-Level Metrics:**  
  * **v0: Normalized String Match:** After applying the normalization rules from 3.2, an F1-score based on exact string-matching of LaTeX expressions will be used.  
  * **v1 (Roadmap): Character Difference Metric (CDM):** A superior, image-based metric, also used by OmniDocBench.6 CDM renders both GT and predicted LaTeX to images and performs a visual, character-level comparison.62 This is more robust as it is not sensitive to different *valid* LaTeX representations of the same formula.64

### **4.3 Error Taxonomy and Reporting**

The benchmark will generate a human-readable HTML/Markdown report, not just a JSON file. This report will include:

* **Leaderboard:** A high-level table with an overall weighted score, plus scores per category (Academic, Government, Finance).  
* **Common Failure Modes:** A qualitative taxonomy of common errors (e.g., "Paragraph Merging," "Table Structure Collapse," "Dropped Math," "Heading Level Mis-attribution").  
* **Per-Document Analysis:** Ability to drill down into specific documents to see a diff of the GT and prediction.

## **5\. Library and Repository Design (PRD Core)**

This section defines the product requirements for the open-source library, pdf-bench.

### **5.1 Scope and Non-Goals**

* **In-Scope (v0 MVP):**  
  * Corpus builder scripts ("recipes") for all v0 documents.  
  * Ground truth Markdown \+ YAML metadata files.  
  * Python evaluation library implementing all v0 metrics (Norm. Edit Dist, TEDS, Element-F1, AST-Edit-Dist).  
  * Parser adapters for 3-5 open-source systems (Marker 10, Nougat 11, unstructured 65) and 2-3 commercial APIs (AWS Textract 12, Azure Document Intelligence 13).  
  * CLI for running benchmarks and generating static HTML/Markdown reports.  
  * DATASHEET.md for dataset governance.49  
* **Out-of-Scope (v0):**  
  * Model training.  
  * A GUI or web application (reports are static files).  
  * The Scanned/OCR track (v1.0).  
  * Manual annotation tooling.

### **5.2 User Personas and Use Cases**

* **Persona 1: Internal Consultant (Primary User)**  
  * *Story:* As a document AI specialist, I need to choose a parser for a new client project. I run pdf-bench on our internal test set and the new "business-finance" track to get a data-driven recommendation on whether AWS Textract, Marker, or GPT-4o provides the best cost/performance trade-off for complex tables.  
* **Persona 2: External ML Practitioner (Community User)**  
  * *Story:* As an ML engineer building a RAG pipeline, I need to select a PDF parser. I find the pdf-bench leaderboard, read the launch blog post, and pip install pdf-bench to run it on my own 20-document sample to validate the public results.  
* **Persona 3: Researcher / Model Builder**  
  * *Story:* As a researcher, I have developed a new document VLM. I write a simple MyParser adapter, run it against pdf-bench, and publish my model's superior scores on the "academic-math" and "business-finance" tracks.

### **5.3 System Architecture and Repository Structure**

/pdf-bench  
├── datasets/  
│   └── recipes/          \# YAML/JSON metadata with URLs, hashes  
├── ground\_truth/  
│   ├── academic/  
│   │   └── arxiv\_cs\_cl\_001.md  
│   │   └── arxiv\_cs\_cl\_001.yml  
│   └── business/  
│       └── gov\_uk\_report\_001.md  
│       └── gov\_uk\_report\_001.yml  
├── builders/  
│   ├── download\_corpus.py  \# Fetches PDFs from public URLs  
│   ├── build\_academic.py   \# Runs LaTeXML pipeline  
│   └── build\_synthetic.py  \# Runs DOCX/Pandoc pipelines  
├── pdf\_bench/  
│   ├── \_\_init\_\_.py  
│   ├── systems/            \# Parser adapters  
│   │   ├── base\_parser.py  \# Abstract class: BaseParser  
│   │   ├── marker.py       \# Implements BaseParser  
│   │   └── aws\_textract.py \# Implements BaseParser  
│   ├── metrics/  
│   │   ├── text\_metrics.py \# Normalized Edit Distance  
│   │   ├── table\_metrics.py \# TEDS wrapper  
│   │   └── struct\_metrics.py \# AST-Edit-Distance, F1  
│   ├── core.py             \# Core benchmark running logic  
│   ├── cli.py              \# CLI entry point (using Typer/Click)  
│   └── report.py           \# HTML/Markdown report generator  
├── benchmarks/             \# Benchmark config files (e.g., lists of doc\_ids)  
│   ├── academic\_v0.yml  
│   └── business\_v0.yml  
├── reports/                \# Generated output reports  
│   └── 2025-10-27\_business\_v0\_report.html  
├──.cache/                 \# Cached parser outputs (hashed)  
├── DATASHEET.md            \# The Datasheet for Datasets   
├── pyproject.toml  
└── README.md

### **5.4 The Parser Adapter Interface**

A BaseParser Abstract Base Class will be defined to ensure extensibility.

Python

from abc import ABC, abstractmethod  
from pathlib import Path

class BaseParser(ABC):  
    """Abstract Base Class for all PDF parsers."""  
      
    @property  
    @abstractmethod  
    def name(self) \-\> str:  
        """Return the parser's name and version."""  
        pass  
          
    @abstractmethod  
    def parse(self, pdf\_path: Path, output\_dir: Path) \-\> Path:  
        """  
        Takes an input PDF path, processes it, and saves the  
        resulting Markdown to a file in output\_dir.  
          
        Returns:  
            The Path to the generated Markdown file.  
        """  
        pass

\# Example implementations:  
\# \- marker.py: Implements parse() by shelling out to the \`marker\_pdf\` CLI.  
\# \- aws\_textract.py: Implements parse() by calling the AWS API,   
\#   using the linearization-to-markdown features.\[12, 66\]  
\# \- azure\_doc\_intel.py: Implements parse() by calling the Azure API  
\#   with \`outputContentFormat=markdown\`.\[13, 67\]

### **5.5 CLI and Python API Specification**

* **Python API:**  
  Python  
  from pdf\_bench import Benchmark, run\_benchmark  
  from pdf\_bench.systems import MarkerParser, AWSTextractParser

  \# Load a benchmark config (a list of doc\_ids)  
  bench\_spec \= Benchmark.load("benchmarks/business\_v0.yml")

  \# Define systems to test  
  systems\_to\_test \=

  \# Run the benchmark  
  results \= run\_benchmark(  
      bench\_spec,   
      systems\_to\_test,   
      cache\_dir=".cache"  
  )

  \# Save the final report  
  results.save\_report("reports/my\_report.html")

* **CLI:**  
  Bash  
  \# Download/build the corpus data  
  $ pdfbench build-corpus \--track academic \--track business

  \# List available benchmarks and systems  
  $ pdfbench list benchmarks  
  $ pdfbench list systems

  \# Run a benchmark on specific systems  
  \# Caching will automatically handle re-runs  
  $ pdfbench run \--benchmark business\_v0 \--systems marker,aws,azure

  \# Generate a report from the last run  
  $ pdfbench report \--run\_id \<run\_id\> \--format html

### **5.6 Caching, Cost, and Performance**

* **Caching:** A robust caching mechanism is non-negotiable. All parser outputs will be cached in .cache/. The cache key will be a hash of (parser\_name, parser\_version, pdf\_file\_hash, parser\_params). This prevents re-running expensive commercial APIs 68 and VLM calls.  
* **Cost Management:** Adapters for paid APIs (AWS, Azure) will include cost estimation and a max\_cost parameter to prevent accidental over-runs.  
* **Performance Metrics:** The benchmark runner will (optionally) record latency (seconds/page) and throughput (pages/second), inspired by benchmarks like AdaParse.69 This provides a critical cost-benefit axis for practitioners.

### **5.7 Roadmap**

* **v0 MVP:** Core library, v0 corpus (450 docs), core metrics (TEDS, AST), adapters for 5+ parsers, static HTML reports.  
* **v1.0:** Scanned/OCR track, multi-language track, CDM metric implementation 62 for math.  
* **v2.0:** Forms/transactional track, presentation (.pptx) track, interactive report viewer.

## 

## **6\. Strategic Positioning and Community Engagement**

This benchmark's value is as much in its "thought leadership" as its technical utility. This section outlines the strategy to maximize its impact.

### **6.1 Positioning**

* **Key Message:** "The Practitioner's Benchmark for Real-World Documents."  
* **Core Differentiation:**  
  * **vs. DocLayNet:** "We go beyond *layout* to measure *semantic content*."  
  * **vs. \\readoc:** "We go beyond *academic* papers to cover the *business and financial documents* you actually process."  
  * **vs. OmniDocBench:** This is the key. The positioning is respectful but clear: "While academic benchmarks like OmniDocBench 4 have advanced the science, their non-commercial licenses 5 prevent practitioners from using them. pdf-bench is the first high-quality, diverse benchmark *built for and by* the practitioner community, with a fully permissive license."  
* **Emphasize:** Transparency (open methodology, Datasheets for Datasets 49), Reproducibility (code \+ recipes), and Business Relevance (finance, legal, and government docs).

### **6.2 Content Plan (Content Marketing)**

1. **Launch Blog:** "Introducing pdf-bench: A Commercially Permissive Benchmark for PDF-to-Markdown." (Announces the project, highlights the OmniDocBench license gap 5, and explains our solution).  
2. **Technical Deep Dive:** "The GOV.UK Goldmine: How We Built a 200-Document Business Benchmark Without Annotating a Single Page." (This post establishes expertise. It details the OGL v3.0 7 / GOV.UK 30 harvesting strategy and the DOCX synthetic pipeline 8).  
3. **Vendor Comparison (The "Leaderboard"):** "PDF Parsing Leaderboard (v0.1): Marker vs. AWS Textract vs. GPT-4o on Real-World Business Reports." (This will be the high-traffic, recurring post. It must be framed fairly and with full transparency).  
4. **Metric Deep Dive:** "Why Edit Distance is Not Enough: Using AST Tree-Edit Distance to Evaluate Document Structure." (Explains the technical rigor of our metrics).  
5. **Community Call:** "How to Add Your Parser (or Data) to pdf-bench."

### **6.3 Community and Contributions**

The library must be easy to extend. The systems/ adapter architecture 69 is the primary contribution vector. A clear CONTRIBUTING.md will explain:

1. How to implement the BaseParser interface for a new parser.  
2. How to submit a new document *source*, which must include a URL and proof of a permissive license.  
3. How to propose and add a new metric (e.g., CDM 62).

### **6.4 Guidelines for Responsible Communication**

As a consulting firm, the objective is to be a **neutral, trusted arbiter**, not a partisan. All published results must:

* Be **reproducible**, linking to the exact benchmark version and code.  
* Be **fair**, using the latest stable versions of all parsers.  
* Be **transparent**, disclosing all parameters and costs.  
* **Avoid hype.** The goal is not "Parser X *destroys* Parser Y." The goal is "Parser X shows high TEDS scores on financial tables, while Parser Y excels at LaTeX extraction in academic papers." This nuanced, data-driven analysis *is* the thought leadership.

## **Conclusion**

The proposed pdf-bench suite directly addresses a critical, unmet need in the document intelligence market: a high-quality, semantically-rich, and business-focused benchmark for PDF-to-Markdown conversion that is **commercially permissive**.

By systematically avoiding the licensing pitfalls of existing academic benchmarks 5 and employing a practical, scalable data-sourcing strategy (leveraging GOV.UK's Open Government Licence 7 and synthetic generation 8), this project is immediately feasible.

The PRD in this report outlines a clear v0 MVP that will provide immediate internal value for tool selection and, more importantly, create a durable, high-visibility "thought-leadership" asset. By becoming the *de facto* standard for practitioners evaluating document parsing, the firm can cement its reputation as a transparent, rigorous, and leading expert in the document AI domain.

#### 

#### **Works cited**

1. DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis \- GitHub, accessed November 14, 2025, [https://github.com/DS4SD/DocLayNet](https://github.com/DS4SD/DocLayNet)  
2. DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis, accessed November 14, 2025, [https://www.researchgate.net/publication/361051040\_DocLayNet\_A\_Large\_Human-Annotated\_Dataset\_for\_Document-Layout\_Analysis](https://www.researchgate.net/publication/361051040_DocLayNet_A_Large_Human-Annotated_Dataset_for_Document-Layout_Analysis)  
3. \\readoc: A Unified Benchmark for Realistic Document Structured Extraction \- arXiv, accessed November 14, 2025, [https://arxiv.org/html/2409.05137v1](https://arxiv.org/html/2409.05137v1)  
4. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- CVF Open Access, accessed November 14, 2025, [https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang\_OmniDocBench\_Benchmarking\_Diverse\_PDF\_Document\_Parsing\_with\_Comprehensive\_Annotations\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.pdf)  
5. opendatalab/OmniDocBench · Datasets at Hugging Face, accessed November 14, 2025, [https://huggingface.co/datasets/opendatalab/OmniDocBench](https://huggingface.co/datasets/opendatalab/OmniDocBench)  
6. opendatalab/OmniDocBench: \[CVPR 2025\] A Comprehensive Benchmark for Document Parsing and Evaluation \- GitHub, accessed November 14, 2025, [https://github.com/opendatalab/OmniDocBench](https://github.com/opendatalab/OmniDocBench)  
7. Open Government Licence for public sector information \- The National Archives, accessed November 14, 2025, [https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)  
8. Convert Office files to PDF with LibreOffice and Python | by Tarik Nazorek \- Medium, accessed November 14, 2025, [https://tariknazorek.medium.com/convert-office-files-to-pdf-with-libreoffice-and-python-a70052121c44](https://tariknazorek.medium.com/convert-office-files-to-pdf-with-libreoffice-and-python-a70052121c44)  
9. A pandoc LaTeX template to convert markdown files to PDF or LaTeX. \- GitHub, accessed November 14, 2025, [https://github.com/Wandmalfarbe/pandoc-latex-template](https://github.com/Wandmalfarbe/pandoc-latex-template)  
10. datalab-to/marker: Convert PDF to markdown \+ JSON quickly with high accuracy \- GitHub, accessed November 14, 2025, [https://github.com/datalab-to/marker](https://github.com/datalab-to/marker)  
11. Implementation of Nougat Neural Optical Understanding for Academic Documents \- GitHub, accessed November 14, 2025, [https://github.com/facebookresearch/nougat](https://github.com/facebookresearch/nougat)  
12. Document Linearization to Markdown or HTML with Textractor \- GitHub Pages, accessed November 14, 2025, [https://aws-samples.github.io/amazon-textract-textractor/notebooks/document\_linearization\_to\_markdown\_or\_html.html](https://aws-samples.github.io/amazon-textract-textractor/notebooks/document_linearization_to_markdown_or_html.html)  
13. Document layout analysis \- Document Intelligence \- Azure AI services | Microsoft Learn, accessed November 14, 2025, [https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0)  
14. upstage/dp-bench · Datasets at Hugging Face, accessed November 14, 2025, [https://huggingface.co/datasets/upstage/dp-bench](https://huggingface.co/datasets/upstage/dp-bench)  
15. \[2206.01062\] DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis, accessed November 14, 2025, [https://arxiv.org/abs/2206.01062](https://arxiv.org/abs/2206.01062)  
16. docling-project/DocLayNet · Datasets at Hugging Face, accessed November 14, 2025, [https://huggingface.co/datasets/docling-project/DocLayNet](https://huggingface.co/datasets/docling-project/DocLayNet)  
17. \[1908.07836\] PubLayNet: largest dataset ever for document layout analysis \- ar5iv \- arXiv, accessed November 14, 2025, [https://ar5iv.labs.arxiv.org/html/1908.07836](https://ar5iv.labs.arxiv.org/html/1908.07836)  
18. ibm-aur-nlp/PubLayNet \- GitHub, accessed November 14, 2025, [https://github.com/ibm-aur-nlp/PubLayNet](https://github.com/ibm-aur-nlp/PubLayNet)  
19. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- 2077AI, accessed November 14, 2025, [https://www.2077ai.com/dataset/dataset-omnidocbench](https://www.2077ai.com/dataset/dataset-omnidocbench)  
20. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations | alphaXiv, accessed November 14, 2025, [https://www.alphaxiv.org/overview/2412.07626v1](https://www.alphaxiv.org/overview/2412.07626v1)  
21. Nougat: Neural Optical Understanding for Academic Documents \- arXiv, accessed November 14, 2025, [https://arxiv.org/pdf/2308.13418](https://arxiv.org/pdf/2308.13418)  
22. Nougat, accessed November 14, 2025, [https://facebookresearch.github.io/nougat/](https://facebookresearch.github.io/nougat/)  
23. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- arXiv, accessed November 14, 2025, [https://arxiv.org/html/2412.07626v2](https://arxiv.org/html/2412.07626v2)  
24. opendatalab/OmniDocBench · Add dataset card and link to paper \- Hugging Face, accessed November 14, 2025, [https://huggingface.co/datasets/opendatalab/OmniDocBench/discussions/2](https://huggingface.co/datasets/opendatalab/OmniDocBench/discussions/2)  
25. Pandoc vs LaTeXML for LaTeX conversion \- TeX \- LaTeX Stack Exchange, accessed November 14, 2025, [https://tex.stackexchange.com/questions/698081/pandoc-vs-latexml-for-latex-conversion](https://tex.stackexchange.com/questions/698081/pandoc-vs-latexml-for-latex-conversion)  
26. How to convert LaTeX document with multiple files to markdown using pandoc, accessed November 14, 2025, [https://stackoverflow.com/questions/77247013/how-to-convert-latex-document-with-multiple-files-to-markdown-using-pandoc](https://stackoverflow.com/questions/77247013/how-to-convert-latex-document-with-multiple-files-to-markdown-using-pandoc)  
27. Pandoc User's Guide, accessed November 14, 2025, [https://pandoc.org/MANUAL.html](https://pandoc.org/MANUAL.html)  
28. Using Pandoc to Convert LaTeX to HTML and MathML \- Digital Accessibility | University of South Carolina, accessed November 14, 2025, [https://sc.edu/about/offices\_and\_divisions/digital-accessibility/toolbox/math/pandoc/](https://sc.edu/about/offices_and_divisions/digital-accessibility/toolbox/math/pandoc/)  
29. Publishing government documents \- GOV.UK, accessed November 14, 2025, [https://www.gov.uk/government/publications/open-standards-for-government/viewing-government-documents](https://www.gov.uk/government/publications/open-standards-for-government/viewing-government-documents)  
30. Why GOV.UK content should be published in HTML and not PDF, accessed November 14, 2025, [https://gds.blog.gov.uk/2018/07/16/why-gov-uk-content-should-be-published-in-html-and-not-pdf/](https://gds.blog.gov.uk/2018/07/16/why-gov-uk-content-should-be-published-in-html-and-not-pdf/)  
31. Making a positive change: PDF to HTML \- Accessibility in government \- GOV.UK blogs, accessed November 14, 2025, [https://accessibility.blog.gov.uk/2023/06/12/making-a-positive-change-pdf-to-html/](https://accessibility.blog.gov.uk/2023/06/12/making-a-positive-change-pdf-to-html/)  
32. Government Functional Standard \- GovS 005: Digital (HTML) \- GOV ..., accessed November 14, 2025, [https://www.gov.uk/government/publications/government-functional-standard-govs-005-digital/government-functional-standard-govs-005-digital-html](https://www.gov.uk/government/publications/government-functional-standard-govs-005-digital/government-functional-standard-govs-005-digital-html)  
33. Using HTML publications on GOV.UK – part 1, accessed November 14, 2025, [https://insidegovuk.blog.gov.uk/2015/02/03/using-html-publications-on-gov-uk-part-1/](https://insidegovuk.blog.gov.uk/2015/02/03/using-html-publications-on-gov-uk-part-1/)  
34. Environmental Improvement Plan 2023 \- GOV.UK, accessed November 14, 2025, [https://www.gov.uk/government/publications/environmental-improvement-plan](https://www.gov.uk/government/publications/environmental-improvement-plan)  
35. Documentation of data.europa.eu (DEU) \- GitLab, accessed November 14, 2025, [https://dataeuropa.gitlab.io/data-provider-manual/pdf/documentation\_data-europa-eu\_V1.2.pdf](https://dataeuropa.gitlab.io/data-provider-manual/pdf/documentation_data-europa-eu_V1.2.pdf)  
36. A practical guide to user-friendly data in publications, accessed November 14, 2025, [https://data.europa.eu/apps/data-in-publications-guide/2022-data-in-publications-guide-extended.pdf](https://data.europa.eu/apps/data-in-publications-guide/2022-data-in-publications-guide-extended.pdf)  
37. Accessing EDGAR Data \- SEC.gov, accessed November 14, 2025, [https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)  
38. 2\. QUICK GUIDE TO EDGAR FILING 2.1 EDGAR Filing Process This section is designed for the novice filer to explain the filing proc \- SEC.gov, accessed November 14, 2025, [https://www.sec.gov/files/edgar/filermanual/efmvol2-c2.pdf](https://www.sec.gov/files/edgar/filermanual/efmvol2-c2.pdf)  
39. Download SEC Filings as PDFs, accessed November 14, 2025, [https://sec-api.io/resources/download-sec-filings-as-pdfs](https://sec-api.io/resources/download-sec-filings-as-pdfs)  
40. Open Standards Principles: \- GOV.UK, accessed November 14, 2025, [https://assets.publishing.service.gov.uk/media/5a7f8f0f40f0b62305b87e0b/Open-Standards-Principles-2012.pdf](https://assets.publishing.service.gov.uk/media/5a7f8f0f40f0b62305b87e0b/Open-Standards-Principles-2012.pdf)  
41. Welcome to python-docx-template's documentation\! — python-docx-template 0.20.x documentation, accessed November 14, 2025, [https://docxtpl.readthedocs.io/](https://docxtpl.readthedocs.io/)  
42. elapouya/python-docx-template: Use a docx as a jinja2 template \- GitHub, accessed November 14, 2025, [https://github.com/elapouya/python-docx-template](https://github.com/elapouya/python-docx-template)  
43. Working with Tables \- Python .docx Module \- GeeksforGeeks, accessed November 14, 2025, [https://www.geeksforgeeks.org/python/working-with-tables-python-docx-module/](https://www.geeksforgeeks.org/python/working-with-tables-python-docx-module/)  
44. Python-docx: A Comprehensive Guide to Creating and Manipulating Word Documents in Python | by Manoj Das | Medium, accessed November 14, 2025, [https://medium.com/@HeCanThink/python-docx-a-comprehensive-guide-to-creating-and-manipulating-word-documents-in-python-a765cf4b4cb9](https://medium.com/@HeCanThink/python-docx-a-comprehensive-guide-to-creating-and-manipulating-word-documents-in-python-a765cf4b4cb9)  
45. Converting docx to pdf with pure python (on linux, without libreoffice) \- Stack Overflow, accessed November 14, 2025, [https://stackoverflow.com/questions/50982064/converting-docx-to-pdf-with-pure-python-on-linux-without-libreoffice](https://stackoverflow.com/questions/50982064/converting-docx-to-pdf-with-pure-python-on-linux-without-libreoffice)  
46. Command \`libreoffice \--headless \--convert-to pdf test.docx \--outdir /pdf\` is not working \[closed\] \- Stack Overflow, accessed November 14, 2025, [https://stackoverflow.com/questions/30349542/command-libreoffice-headless-convert-to-pdf-test-docx-outdir-pdf-is-not](https://stackoverflow.com/questions/30349542/command-libreoffice-headless-convert-to-pdf-test-docx-outdir-pdf-is-not)  
47. Converting doc/docx Format to PDF With Help of LibreOffice and LaTeX | Baeldung on Linux, accessed November 14, 2025, [https://www.baeldung.com/linux/latex-doc-docx-pdf-conversion](https://www.baeldung.com/linux/latex-doc-docx-pdf-conversion)  
48. Generating a nice-looking PDF with Pandoc | LornaJane \- Lorna Jane Mitchell, accessed November 14, 2025, [https://lornajane.net/posts/2023/generating-a-nice-looking-pdf-with-pandoc](https://lornajane.net/posts/2023/generating-a-nice-looking-pdf-with-pandoc)  
49. Datasheets for Datasets \- Microsoft, accessed November 14, 2025, [https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/1803.09010.pdf](https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/1803.09010.pdf)  
50. Datasheets for Datasets \- ResearchGate, accessed November 14, 2025, [https://www.researchgate.net/publication/324055506\_Datasheets\_for\_Datasets](https://www.researchgate.net/publication/324055506_Datasheets_for_Datasets)  
51. \[1803.09010\] Datasheets for Datasets \- arXiv, accessed November 14, 2025, [https://arxiv.org/abs/1803.09010](https://arxiv.org/abs/1803.09010)  
52. Datasheets for Datasets \- arXiv, accessed November 14, 2025, [https://arxiv.org/pdf/1803.09010](https://arxiv.org/pdf/1803.09010)  
53. Data Governance in Open Source AI, accessed November 14, 2025, [https://openfuture.eu/wp-content/uploads/2025/01/250123\_OSI-Data-Governance-OSAI.pdf](https://openfuture.eu/wp-content/uploads/2025/01/250123_OSI-Data-Governance-OSAI.pdf)  
54. What data governance should look like in open source AI models | datos.gob.es, accessed November 14, 2025, [https://datos.gob.es/en/blog/what-data-governance-should-look-open-source-ai-models](https://datos.gob.es/en/blog/what-data-governance-should-look-open-source-ai-models)  
55. Five Ways to Document Your Data, accessed November 14, 2025, [https://data.wisc.edu/data-literacy/document/](https://data.wisc.edu/data-literacy/document/)  
56. Open data goldbook for data managers and data holders (2018) \- European Data Portal, accessed November 14, 2025, [https://data.europa.eu/sites/default/files/european\_data\_portal\_-\_open\_data\_goldbook.pdf](https://data.europa.eu/sites/default/files/european_data_portal_-_open_data_goldbook.pdf)  
57. Search Filings \- SEC.gov, accessed November 14, 2025, [https://www.sec.gov/search-filings](https://www.sec.gov/search-filings)  
58. Edit distance \- Wikipedia, accessed November 14, 2025, [https://en.wikipedia.org/wiki/Edit\_distance](https://en.wikipedia.org/wiki/Edit_distance)  
59. Normalizing the edit distance \- Stack Overflow, accessed November 14, 2025, [https://stackoverflow.com/questions/45783385/normalizing-the-edit-distance](https://stackoverflow.com/questions/45783385/normalizing-the-edit-distance)  
60. table-recognition-metric \- PyPI, accessed November 14, 2025, [https://pypi.org/project/table-recognition-metric/](https://pypi.org/project/table-recognition-metric/)  
61. Levenshtein distance \- Wikipedia, accessed November 14, 2025, [https://en.wikipedia.org/wiki/Levenshtein\_distance](https://en.wikipedia.org/wiki/Levenshtein_distance)  
62. Dolphin: Document Image Parsing via Heterogeneous Anchor Prompting \- ACL Anthology, accessed November 14, 2025, [https://aclanthology.org/2025.findings-acl.1130.pdf](https://aclanthology.org/2025.findings-acl.1130.pdf)  
63. CDM: A Reliable Metric for Fair and Accurate Formula Recognition Evaluation \- arXiv, accessed November 14, 2025, [https://arxiv.org/html/2409.03643v1](https://arxiv.org/html/2409.03643v1)  
64. Paper page \- CDM: A Reliable Metric for Fair and Accurate Formula Recognition Evaluation, accessed November 14, 2025, [https://huggingface.co/papers/2409.03643](https://huggingface.co/papers/2409.03643)  
65. How to Parse a PDF, Part 1 \- Unstructured, accessed November 14, 2025, [https://unstructured.io/blog/how-to-parse-a-pdf-part-1](https://unstructured.io/blog/how-to-parse-a-pdf-part-1)  
66. Intelligent document processing with Amazon Textract, Amazon Bedrock, and LangChain, accessed November 14, 2025, [https://aws.amazon.com/blogs/machine-learning/intelligent-document-processing-with-amazon-textract-amazon-bedrock-and-langchain/](https://aws.amazon.com/blogs/machine-learning/intelligent-document-processing-with-amazon-textract-amazon-bedrock-and-langchain/)  
67. Image2Struct: Benchmarking Structure Extraction for Vision-Language Models, accessed November 14, 2025, [https://openreview.net/forum?id=8m6zw8Jur0\&referrer=%5Bthe%20profile%20of%20Percy%20Liang%5D(%2Fprofile%3Fid%3D\~Percy\_Liang1)](https://openreview.net/forum?id=8m6zw8Jur0&referrer=%5Bthe+profile+of+Percy+Liang%5D\(/profile?id%3D~Percy_Liang1\))
