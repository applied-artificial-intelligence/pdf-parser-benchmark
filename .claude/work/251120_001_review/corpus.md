# **Strategic Corpus Design for Enterprise Document Parsing Benchmarks: A Comprehensive Analysis and Specification**

## **1\. The Strategic Imperative for Structural Fidelity in Document Parsing**

The fundamental challenge in the field of Document Understanding (DU) has shifted precipitously in the post-LLM era.
Historically, the objective of Optical Character Recognition (OCR) and document parsing was textual recovery: the
accurate transcription of glyphs into machine-readable strings. However, the rise of Retrieval-Augmented Generation (
RAG) and large-scale knowledge extraction pipelines has fundamentally altered the requirements for document processing
systems. It is no longer sufficient to merely recover the text; the modern enterprise parser must recover the **Document
Object Model (DOM)**—the hierarchical, logical, and semantic structure that transforms a stream of characters into
meaningful information.

Current benchmarks, however, have largely failed to keep pace with this paradigm shift. The legacy metrics of Character
Error Rate (CER) and Word Error Rate (WER) are increasingly irrelevant in a business context where a missing decimal
point in a financial table or a scrambled reading order in a multi-column legal contract can have catastrophic
downstream effects. A parser might achieve a 99.9% OCR accuracy score while completely destroying the semantic
relationship between a section header and its subsequent paragraphs, or flattening a nested list into an incoherent blob
of text.

This report outlines a comprehensive strategy for designing a next-generation benchmarking corpus specifically tailored
for **machine-readable business documents**. The objective is to evaluate parsers not on their ability to see
characters, but on their ability to reconstruct the logical fabric of a document into structured formats like Markdown
or HTML. This requires a corpus strategy that prioritizes **structural ground truth**—canonical representations of
layout, hierarchy, and table topology—over simple text transcription.

The analysis that follows is exhaustive. It dissects the current landscape of available corpora, identifying the
specific strengths and failures of datasets like OmniDocBench, DocLayNet, and FinTabNet in the context of business
documentation. It exposes the critical gaps in representation—specifically regarding Standard Operating Procedures (
SOPs), complex legal cross-references, and human resources documentation. Finally, it proposes a rigorous, technically
detailed specification for a **Synthetic Ground Truth Generation Pipeline**, utilizing headless browser rendering and
semantic HTML templates to create a "Gold Standard" corpus that holds parsers accountable to the reality of enterprise
documentation.

### **1.1 The Shift from Visual Detection to Logical Parsing**

To understand the corpus requirements, one must first understand the architectural shift in the models being evaluated.
Traditional systems treated document understanding as a computer vision object detection task (e.g., finding the
bounding box of a table). Modern systems, such as **Marker**, **Docling**, and multimodal VLMs (e.g., **Qwen2.5-VL**, *
*Llama 3.2-Vision**), attempt to translate the visual document directly into a serialized text format.1

This necessitates a benchmark where the Ground Truth is not a set of coordinates (COCO format), but a **canonical
Markdown or HTML string**. The evaluation metric transforms from Intersection over Union (IoU) to metrics like **Tree
Edit Distance Similarity (TEDS)** and **Markdown-to-Markdown alignment**.4 Consequently, the ideal corpus must possess "
Digital-Born" lineage where the underlying structure is preserved, or "High-Fidelity Annotation" where the structure has
been rigorously reconstructed by human experts.

The distinction between "Visual Layout" and "Logical Structure" is paramount. Visual layout concerns where text appears
on the page (e.g., top-left quadrant). Logical structure concerns what the text *is* (e.g., Title, Section 1.0,
Subsection 1.1). A business benchmark must penalize a parser that correctly identifies the pixels of a title but fails
to tag it as \# Heading 1 in the output Markdown.

---

## **2\. Landscape Analysis of Existing Corpora**

The existing ecosystem of Document Understanding datasets is vast but fragmented. Most datasets are optimized for
academic publications (arXiv papers) or specific sub-tasks (Table Recognition) rather than the holistic parsing of
complex business documents. The following analysis evaluates the most promising candidates against the requirements of a
business-centric Markdown benchmark.

### **2.1 OmniDocBench: The New Standard for Parsing Evaluation**

Among the recently released benchmarks, **OmniDocBench** represents the most sophisticated attempt to align visual
layout with logical parsing, making it a cornerstone candidate for this strategy.6 Unlike its predecessors, which often
focused exclusively on bounding box detection, OmniDocBench was explicitly designed to evaluate "Document Parsing,"
creating a direct alignment with our benchmark's objectives.

#### **2.1.1 Domain and Scale**

The dataset comprises 1,355 PDF pages.3 While this volume is significantly lower than massive pre-training datasets like
DocLayNet, the diversity within OmniDocBench is meticulously curated to stress-test parsing logic. It covers nine
distinct document types, including **financial reports**, **research reports**, **textbooks**, and **newspapers**.3 This
diversity is critical. A parser trained solely on single-column academic papers often fails catastrophically when
presented with the multi-column, mixed-media layouts of a corporate annual report or a newspaper-style newsletter.

#### **2.1.2 Annotation Richness and Ground Truth**

The ground truth quality in OmniDocBench is exceptional and serves as a model for our proposed benchmark standards.

* **Hierarchical Granularity:** It provides localization for 15 block-level categories (including paragraphs, headings,
  and tables) and, crucially, 4 span-level categories (text lines, inline formulas).3 This distinction allows for the
  evaluation of fine-grained text recovery.
* **Dual Table Annotation:** Perhaps its most valuable feature for business benchmarking is that tables are annotated
  with **both LaTeX and HTML representations**.3 Business documents are defined by their tabular density. A parser's
  ability to recover the *topology* of a table (row spans, column spans, headers) is best evaluated against an HTML
  ground truth. The availability of this data allows us to use TEDS metrics to strictly evaluate table structure
  recovery.
* **Reading Order:** The dataset includes explicit annotations for the reading order of document components.6 This
  addresses the "Linearization Problem" in RAG—determining the correct sequence of text tokens when visual layout is
  non-linear (e.g., sidebars, callouts, multi-column flows).

#### **2.1.3 Business Relevance Assessment**

Rating: High.  
The inclusion of "financial reports" and "research reports" directly maps to high-value enterprise use cases. The
dataset's explicit design for "markdown-to-markdown" evaluation 3 means the engineering effort to adapt it is minimal.
The JSON schema, which links visual blocks to semantic attributes (like "caption" or "footer"), can be deterministically
compiled into a canonical Markdown Ground Truth.3

### **2.2 DocLayNet: The Foundation of Layout Analysis**

**DocLayNet**, developed by IBM, is arguably the most important large-scale dataset for document layout analysis (DLA)
currently available.8 It serves as a critical counterweight to the academic bias of datasets like PubLayNet (which is
sourced purely from PubMed).

#### **2.2.1 Domain and Scale**

DocLayNet is massive, containing 80,863 manually annotated pages.8 Its primary differentiator is its source diversity.
It explicitly categorizes documents into six classes:

1. **Financial Reports** (Annual reports, SEC filings)
2. **Manuals** (User guides, technical specifications)
3. **Laws & Regulations** (Government gazettes, legal codes)
4. **Scientific Papers** (arXiv, etc.)
5. **Patents**
6. **Government Tenders**

This composition is nearly ideal for a business benchmark. The "Manuals" and "Laws" categories are particularly rare in
other datasets and represent the unstructured "dark data" that enterprises struggle to process—internal SOPs, compliance
guidelines, and technical documentation.10

#### **2.2.2 Ground Truth Structure and Limitations**

DocLayNet provides page-by-page layout segmentation using bounding boxes in COCO format for 11 distinct class labels (
Caption, Footnote, Formula, List-item, Page-footer, Page-header, Picture, Section-header, Table, Text, Title).8

* **The Parsing Gap:** While DocLayNet identifies *where* a paragraph is, it does not inherently provide the *logical
  connectivity* between them. The ground truth is a set of isolated boxes. To use this for a Markdown generation
  benchmark, one must perform an "Engineering Linearization" step: writing a heuristic to sort these boxes (usually
  top-down, left-right) and concatenate their text content into a single Markdown stream.
* **Text Integrity:** Fortunately, the dataset includes the underlying JSON text cells for digital-born documents.11
  This means we have perfect text ground truth, even if the high-level semantic hierarchy (e.g., "Is this Section-header
  a specific H2 or H3?") is flattened to a generic label.

#### **2.2.3 Business Relevance Assessment**

Rating: Very High.  
The sheer scale of DocLayNet allows for statistically significant evaluation of layout robustness. The "Financial
Reports" and "Manuals" subsets are non-negotiable inclusions for any credible business benchmark. The primary trade-off
is the engineering effort required to construct a "Canonical Markdown" from the COCO boxes, which introduces a potential
bias based on the linearization algorithm chosen.

### **2.3 FinTabNet: The Tabular Structure Standard**

Business documents differ from general prose primarily in their reliance on structured data presentation. **FinTabNet**
12 is the definitive corpus for evaluating the extraction of complex financial tables.

#### **2.3.1 Domain and Ground Truth**

Sourced from the annual reports of S\&P 500 companies, FinTabNet focuses exclusively on the most difficult regions of
business documents: the financial statements.

* **Annotation Format:** It provides the PDF page and a paired **HTML representation** of the table structure.12 This is
  a critical distinction. Simple Markdown table syntax (pipes and dashes) cannot represent the complex features of
  financial tables, such as nested column headers, multi-row spanning cells, and indentation-based hierarchy (e.g., "
  Total Assets" being indented under "Assets").
* **Structural Fidelity:** The HTML ground truth captures this topology explicitly (\<td colspan="3"\>).

#### **2.3.2 Strategic Utility**

We should not view FinTabNet as a full-document parsing task, but rather as a specialized sub-module of the benchmark. A
robust business parser must be able to identify a table region and switch modes to generate a high-fidelity HTML or
complex Markdown representation for that specific block. FinTabNet allows us to isolate and evaluate this specific
capability—"Needle-in-a-haystack" parsing—where the parser must handle the transition from narrative text to dense
tabular data and back again.13

### **2.4 The Kleister Ecosystem (NDA & Charity): Long-Context Legal Parsing**

Most benchmarks operate at the page level. **Kleister NDA** and **Kleister Charity** 14 were designed to address the
challenge of **Long Document Understanding**.

#### **2.4.1 Domain and Features**

* **Kleister NDA:** \~540 Non-Disclosure Agreements, totaling 3,229 pages.15
* **Kleister Charity:** \~2,788 Annual Financial Reports, totaling 61,643 pages.
* **Origin:** Crucially, many of these documents are **born-digital**, derived from HTML sources (EDGAR filings)
  converted to PDF.16 This lineage implies that a high-quality structural ground truth exists (or can be reconstructed
  from the original HTML).

#### **2.4.2 Relevance to Business Parsing**

Rating: High.  
NDAs represent the archetype of "unstructured" business text. They lack the clear visual signposts of a magazine or
textbook (e.g., large images, colorful sidebars). Instead, they rely on logical structure—numbered lists, nested
clauses (1.1, 1.1(a), 1.1(a)(i)), and precise cross-references.  
A parser's failure mode here is often "structure collapse," where the hierarchy of the legal clauses is lost, and the
text is flattened into a single paragraph. Evaluating parsers on Kleister NDA tests their ability to maintain the
integrity of nested lists over multiple pages—a capability essential for legal RAG applications where the scope of a
clause is determined by its indentation level.

### **2.5 DocILE: Transactional Document Intelligence**

**DocILE** 18 targets **Transactional Documents**—invoices, purchase orders, and receipts.

#### **2.5.1 Domain and Annotations**

The dataset contains 6,700 annotated business documents and a massive synthetic component.20 The annotations focus on *
*Key Information Localization and Extraction (KILE)** and **Line Item Recognition (LIR)**.

* **Relevance:** Medium-High. While "parsing to Markdown" is less standard for invoices (which are usually parsed to
  JSON), the ability to represent an invoice as a structured Markdown document (e.g., a header section followed by a
  line-item table and a footer of totals) is a valid test of a generic parser's flexibility.
* **Synthetic Utility:** DocILE's use of synthetic data to augment the real corpus 21 validates the synthetic strategy
  proposed later in this report.

### **2.6 VRDU: Visually Rich Document Understanding**

**VRDU** 22 bridges the gap between rigid templates and unstructured text.

#### **2.6.1 Domain**

It focuses on **Registration Forms** and **Ad-buy Forms**.24

* **Key Feature:** "Template Variance." The dataset includes the same semantic document type (e.g., an ad-buy form)
  rendered in many different layouts. This tests a parser's ability to generalize: can it recognize that a "Total
  Amount" field is semantically the same whether it appears in the top-right or bottom-left?
* **Relevance:** Medium. Forms are often best handled by specialized extractors, but a general-purpose PDF-to-Markdown
  parser should minimally be able to transcribe the form fields as a Key-Value list or a definition list. VRDU provides
  the ground truth to test this "Form-to-Text" serialization.

### **2.7 Comparative Summary Matrix**

The following table summarizes the key attributes of the selected corpora, highlighting their suitability for a
Markdown-centric benchmark.

| Corpus Name      | Domain / Archetype               | Business Relevance  | Scale         | Ground Truth Format           | Suitability for Markdown Benchmark                                 |
|:-----------------|:---------------------------------|:--------------------|:--------------|:------------------------------|:-------------------------------------------------------------------|
| **OmniDocBench** | Diverse (Finance, Reports, News) | **High**            | \~1.3k pages  | JSON (Block \+ Span \+ HTML)  | **Ideal**: JSON hierarchy maps directly to Markdown elements.      |
| **DocLayNet**    | Finance, Manuals, Laws           | **Very High**       | \~80k pages   | JSON (COCO Bboxes)            | **Strong**: Requires "Linearization" of boxes to create MD stream. |
| **FinTabNet**    | Financial Tables                 | **High (Specific)** | \~112k tables | PDF \+ HTML Table Structure   | **Specific**: Critical for evaluating table structure (TEDS).      |
| **Kleister NDA** | Legal Contracts                  | **High**            | \~3.2k pages  | PDF \+ Entities (HTML origin) | **Strong**: Tests nested list/clause recovery in long docs.        |
| **DocILE**       | Invoices / Orders                | **Medium**          | \~6.7k docs   | JSON (KILE/LIR)               | **Moderate**: Better for JSON extraction than Markdown parsing.    |
| **VRDU**         | Forms                            | **Medium**          | \~2k docs     | JSON (Entities)               | **Moderate**: Tests Key-Value pair serialization.                  |

---

## **3\. The "Business Reality" Gap Analysis**

Despite the richness of the corpora detailed above, a forensic analysis reveals significant gaps when compared to the
full spectrum of enterprise documentation. Real-world business data lakes are not composed solely of annual reports and
invoices. They are filled with operational documentation, HR records, and complex compliance materials that possess
unique structural characteristics underrepresented in current datasets.

### **3.1 The "SOP" Gap (Standard Operating Procedures)**

**Standard Operating Procedures (SOPs)** are the lifeblood of operational businesses (manufacturing, logistics,
healthcare).

* **Structural Signature:** SOPs are characterized by **deeply nested ordered lists** (e.g., 1., 1.1., 1.1.1., a., i.).
  They frequently contain "Admonitions"—warnings, cautions, or notes—that visually interrupt the text flow (often in
  colored boxes) but must be logically integrated into the instructions.25
* **The Deficit:** While DocLayNet has a "Manuals" category, it classifies content broadly as text or list-item. It
  rarely validates the *correctness of the nesting level*. A parser that flattens a four-level list into a single-level
  list might score well on OCR metrics but fails the business use case (where "step 1.1.a" is distinct from "step 1.2").
* **Requirement:** A corpus that specifically penalizes nesting errors and failure to capture admonition blocks (e.g.,
  mapping them to Markdown blockquotes \>).

### **3.2 The "HR" Gap (Resumes and CVs)**

**Resumes** represent a topological nightmare for parsers.

* **Structural Signature:** They typically utilize dense, multi-column layouts where the reading order is strictly
  vertical within columns, often uncorrelated with the column next to it. They contain "Skill Clouds"—clusters of
  keywords separated by pipes, bullets, or simply whitespace.27
* **The Deficit:** Existing resume datasets often focus on entity extraction (Named Entity Recognition) rather than
  layout parsing.29 They care about extracting "Python" as a skill, but not about reconstructing the visual layout into
  a coherent Markdown representation that preserves the "Experience" vs. "Education" columns.
* **Requirement:** A dataset of resumes with ground truth that defines the *reading order* of disconnected text blocks,
  challenging the parser's spatial clustering algorithms.31

### **3.3 The "Visual-Text Interleaving" Gap**

Marketing collateral (White Papers, Product Brochures) and complex Government Reports often feature text wrapping around
irregular images, or sidebars that contain semantically distinct content (e.g., a "Case Study" box embedded in a main
article).

* **The Deficit:** Most parsers attempt to linearize this by simply reading left-to-right, top-to-bottom. This results
  in the sidebar text being spliced into the middle of a sentence in the main column.
* **Requirement:** A corpus where the ground truth explicitly separates "Main Flow" from "Supplementary Flow" (
  Sidebars), forcing the parser to distinguish between the two.

### **3.4 The "Complex Cross-Reference" Gap**

Legal and Technical documents rely heavily on internal linking (e.g., "See Table 4 on page 12").

* **The Deficit:** Current benchmarks do not evaluate whether a parser preserves these links. In a Markdown output,
  these should ideally be rendered as internal links ((\#table-4)).
* **Requirement:** Ground truth that validates the presence and accuracy of internal anchor links.

---

## **4\. Design Specification for a Realistic Synthetic Corpus**

To address the gaps identified in Section 3—specifically the need for deep nesting, complex multi-column layouts, and
verified reading order—we cannot rely solely on scraping real PDFs, as establishing the "Logical Ground Truth" for such
complex layouts is prohibitively expensive. Instead, we define a **Synthetic Ground Truth Generation Pipeline**.

The core philosophy of this pipeline is **"Forward Generation"**: We generate the *logical source* first (
HTML/Markdown), render it to PDF, and then use the original source as the infallible ground truth. This guarantees 100%
alignment between the visual PDF and the target structure.

### **4.1 Generation Pipeline Architecture**

We propose a pipeline utilizing **Headless Browsers (Puppeteer/Playwright)** and **CSS Paged Media** standards. This
approach mimics modern digital-born business document generation (often done via web-based engines) and allows for
pixel-perfect extraction of ground truth from the DOM.32

#### **Step 1: Semantic Source Generation (The "Gold Master")**

We utilize Large Language Models (LLMs) or procedural generation scripts to create realistic *content* stored in a
strict **JSON Schema**. This schema represents the "Platonic Ideal" of the document.

* **Schema Structure:**  
  JSON  
  {  
  "document\_id": "sop\_001",  
  "type": "SOP",  
  "structure":}  
  \]}  
  \]}  
  \]  
  }

* **Diversity:** The generator must vary the content length, terminology, and structural depth based on the target
  vertical (e.g., Legal vs. HR).34

#### **Step 2: Template Rendering (HTML/CSS)**

The JSON content is injected into high-fidelity HTML5 templates. Crucially, we use **Semantic HTML** tags (\<article\>,
\<section\>, \<h1\>-\<h6\>, \<table\>, \<aside\>) to embed the logical structure directly into the code.

* **CSS Paged Media:** We utilize CSS @page rules to define distinct print layouts (A4 vs. Letter), margins, and page
  breaks (break-inside: avoid for tables). This ensures the PDF looks like a professional document, not just a printed
  web page.36
* **DOM Instrumentation:** Every HTML element is tagged with a unique data-id attribute corresponding to the JSON
  source.

#### **Step 3: The "Tagged PDF" Rendering Engine**

We employ two distinct rendering engines to ensure diversity in the PDF internal structure:

1. **WeasyPrint:** A Python-based engine that strictly adheres to CSS Paged Media standards.38 It produces clean,
   well-structured PDFs that are "friendly" but rigorously standard-compliant.
2. **Puppeteer (Headless Chrome):** The industry standard for web-to-PDF.32 It represents how most modern SaaS tools
   generate reports. Puppeteer allows us to execute JavaScript to measure the exact bounding box of every element
   *after* layout but *before* PDF printing.39

#### **Step 4: Ground Truth Extraction (The "Magic" Step)**

Because we control the rendering pipeline, we do not need to OCR the output.

* **Visual Ground Truth:** During the Puppeteer rendering process, we query the DOM to extract the exact (x, y, width,
  height) of every data-id element on every page.32
* **Logical Ground Truth:** We map these bounding boxes back to the original JSON content.
* **Result:** A dataset where we know *exactly* that the pixel region \`\` corresponds to "Section 1.1" and *must* be
  parsed as \#\# Section 1.1.

### **4.2 Vertical-Specific Corpus Specifications**

The synthetic corpus will be divided into specific "Archetypes" designed to target the gaps identified in Section 3\.

#### **A. The "Operations" Corpus (SOPs & Manuals)**

* **Target Volume:** 500 Documents.
* **Structural Focus:** **Deep Nesting.**
* **Specification:**
    * 30% of documents must contain lists nested at least 4 levels deep (1., 1.1., 1.1.1., a.).
    * 20% must utilize "Admonition" blocks (visual boxes for Warnings/Notes) using \<aside\> tags. The Ground Truth
      markdown for these should be standardized as blockquotes (e.g., \> \*\*Warning\*\*).
    * **Rationale:** This stresses the parser's indentation logic and its ability to recognize that a "Warning" box is
      structurally distinct from the surrounding text.25

#### **B. The "Human Resources" Corpus (Resumes)**

* **Target Volume:** 300 Documents.
* **Structural Focus:** **Multi-Column Discontinuity.**
* **Specification:**
    * Layouts must use CSS Grid to position "Skills" sidebars alongside "Experience" timelines.
    * Content generation must ensure that reading logically across the page (left-to-right) produces nonsense, forcing
      the parser to respect column boundaries.
    * **Rationale:** This tests the "Reading Order" recovery algorithms, specifically the ability to segment the page
      into vertical zones before serializing text.27

#### **C. The "Legal" Corpus (Contracts)**

* **Target Volume:** 200 Long-Form Documents (10+ pages each).
* **Structural Focus:** **Continuity & References.**
* **Specification:**
    * Documents must span multiple pages with sentences breaking across pages.
    * High density of "Defined Terms" (e.g., "The 'Company'...") and internal cross-references ("See Section 4.1").
    * **Rationale:** Evaluates the parser's ability to stitch text across page boundaries without inserting phantom line
      breaks, and (potentially) to identify hyperlinks.5

#### **D. The "Financial" Corpus (Statements)**

* **Target Volume:** 500 Documents.
* **Structural Focus:** **Implicit Tables.**
* **Specification:**
    * Use HTML \<table\> tags with border: none. This creates a visual grid of numbers without distinct lines.
    * **Rationale:** Many parsers rely on visual lines to detect tables. This corpus tests whether they can detect
      tables based on *alignment* and *spatial regularity* alone.12

---

## **5\. Benchmark Shortlist and Final Recommendation**

Based on the analysis of existing datasets and the specification for synthetic augmentation, we propose the following
composition for the **Enterprise Business Document Parsing Benchmark**. This shortlist balances the fidelity of
real-world data with the structural precision of synthetic data.

### **Tier 1: The "Real-World" Core (60% of Corpus)**

This tier provides the visual noise, font variety, and unpredictability of real documents.

1. **OmniDocBench (Parsing Subset):** \~500 pages.
    * *Selection:* Categories "Financial Report," "Research Report," "Textbook."
    * *Role:* The primary test for layout-to-markdown conversion, utilizing its high-quality block/span annotations.6
2. **DocLayNet (Business Subset):** \~1,000 pages.
    * *Selection:* Categories "Manuals" and "Financial Reports."
    * *Role:* Stress-testing layout segmentation on a large scale. Requires a heuristic "linearization" script to
      convert COCO boxes to Markdown ground truth.8
3. **Kleister NDA (Parsing Subset):** \~100 documents.
    * *Role:* Evaluating nested list recovery and reading order in long, dense legal text. The "born-digital" HTML
      source should be used to regenerate a clean Markdown ground truth.14
4. **FinTabNet (Table Subset):** \~200 complex tables.
    * *Role:* A dedicated "Table Structure" module. Parsers are evaluated on their ability to output HTML tables that
      match the TEDS score of the ground truth.12

### **Tier 2: The "Synthetic" Extension (40% of Corpus)**

This tier targets the specific structural gaps where real-world ground truth is failing.  
5\. Synthetic SOP Corpus: \~500 documents.  
\* Role: The definition standard for Nested List parsing.  
6\. Synthetic Resume Corpus: \~300 documents.  
\* Role: The definition standard for Multi-Column Reading Order.  
7\. Synthetic "Implicit Table" Corpus: \~200 documents.  
\* Role: Testing table detection in the absence of gridlines.

---

## **6\. Implementation Roadmap and Evaluation Metrics**

### **6.1 The Canonicalization Challenge**

A critical risk in this benchmark is the ambiguity of Markdown itself. Is a title \# Title or Title\\n=====? Is a bold
word \*\*word\*\* or \_\_word\_\_?

* **Standardization Protocol:** All Ground Truth files (both from OmniDocBench and Synthetic pipelines) must be passed
  through a strict **Markdown Linter/Formatter** (e.g., mdformat or prettier).
* **Parser Normalization:** The output of any parser being evaluated must also be normalized using the same tool before
  comparison. This ensures we are evaluating content recovery, not stylistic formatting choices.4

### **6.2 Metrics of Success**

Traditional LEV (Levenshtein Distance) is insufficient for this benchmark because it treats structure (newlines, hash
marks) the same as content. We recommend a multi-dimensional scoring system:

1. **TEDS (Tree Edit Distance Similarity):** For table evaluation. It measures the structural similarity of the
   HTML/Markdown tree, penalizing a missed row/column split far more than a typo in a cell.5
2. **Markdown-Structural-Score (MSS):** A custom metric (inspired by the Marker benchmark 2) that parses both the Ground
   Truth and the Prediction into an Abstract Syntax Tree (AST). It then compares the trees:
    * Do the number of H1/H2/H3 nodes match?
    * Do the number of List Item nodes match?
    * Is the nesting depth identical?
3. **Reading Order Penalty:** A specific penalty applied if text blocks appear in the output but in the wrong sequence (
   e.g., reading across a resume's columns).7

### **6.3 Conclusion**

The proposed strategy moves beyond the era of simple OCR benchmarking. By combining the verified, diverse layouts of *
*OmniDocBench** and **DocLayNet** with a rigorously engineered **Synthetic SOP/Resume** corpus, we can create a
benchmark that truly reflects the needs of the modern enterprise. This benchmark will not just measure how well a
machine can read; it will measure how well a machine can *understand* and *reconstruct* the complex, structured reality
of business documentation.

####  

#### **Works cited**

1. From PDFs to AI-ready structured data: a deep dive \- Explosion AI, accessed November 20,
   2025, [https://explosion.ai/blog/pdfs-nlp-structured-data](https://explosion.ai/blog/pdfs-nlp-structured-data)
2. datalab-to/marker: Convert PDF to markdown \+ JSON quickly with high accuracy \- GitHub, accessed November 20,
   2025, [https://github.com/datalab-to/marker](https://github.com/datalab-to/marker)
3. opendatalab/OmniDocBench: \[CVPR 2025\] A Comprehensive Benchmark for Document Parsing and Evaluation \- GitHub,
   accessed November 20,
   2025, [https://github.com/opendatalab/OmniDocBench](https://github.com/opendatalab/OmniDocBench)
4. \\readoc: A Unified Benchmark for Realistic Document Structured Extraction \- arXiv, accessed November 20,
   2025, [https://arxiv.org/html/2409.05137v1](https://arxiv.org/html/2409.05137v1)
5. Benchmarking the Most Reliable Document Parsing API | by Sarah Guthals, PhD | Tensorlake AI | Nov, 2025 | Medium,
   accessed November 20,
   2025, [https://medium.com/tensorlake-ai/benchmarking-the-most-reliable-document-parsing-api-b8065686daff](https://medium.com/tensorlake-ai/benchmarking-the-most-reliable-document-parsing-api-b8065686daff)
6. opendatalab/OmniDocBench · Datasets at Hugging Face, accessed November 20,
   2025, [https://huggingface.co/datasets/opendatalab/OmniDocBench](https://huggingface.co/datasets/opendatalab/OmniDocBench)
7. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- arXiv, accessed November
   20, 2025, [https://arxiv.org/html/2412.07626v1](https://arxiv.org/html/2412.07626v1)
8. Dataset Card for DocLayNet small \- ModelScope, accessed November 20,
   2025, [https://modelscope.cn/datasets/swift/DocLayNet-small](https://modelscope.cn/datasets/swift/DocLayNet-small)
9. DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis \- GitHub, accessed November 20,
   2025, [https://github.com/DS4SD/DocLayNet](https://github.com/DS4SD/DocLayNet)
10. Task and Resources \- ICDAR 2023 DocLayNet competition, accessed November 20,
    2025, [https://ds4sd.github.io/icdar23-doclaynet/task/](https://ds4sd.github.io/icdar23-doclaynet/task/)
11. docling-project/DocLayNet · Datasets at Hugging Face, accessed November 20,
    2025, [https://huggingface.co/datasets/docling-project/DocLayNet](https://huggingface.co/datasets/docling-project/DocLayNet)
12. README.md · ds4sd/FinTabNet\_OTSL at main \- Hugging Face, accessed November 20,
    2025, [https://huggingface.co/datasets/ds4sd/FinTabNet\_OTSL/blob/main/README.md](https://huggingface.co/datasets/ds4sd/FinTabNet_OTSL/blob/main/README.md)
13. \[2303.00716\] Aligning benchmark datasets for table structure recognition \- arXiv, accessed November 20,
    2025, [https://arxiv.org/abs/2303.00716](https://arxiv.org/abs/2303.00716)
14. RealKIE: Five Novel Datasets for Enterprise Key Information Extraction \- arXiv, accessed November 20,
    2025, [https://arxiv.org/html/2403.20101v2](https://arxiv.org/html/2403.20101v2)
15. Kleister: Key Information Extraction Datasets Involving Long Documents with Complex Layouts | Request PDF \-
    ResearchGate, accessed November 20,
    2025, [https://www.researchgate.net/publication/354356071\_Kleister\_Key\_Information\_Extraction\_Datasets\_Involving\_Long\_Documents\_with\_Complex\_Layouts](https://www.researchgate.net/publication/354356071_Kleister_Key_Information_Extraction_Datasets_Involving_Long_Documents_with_Complex_Layouts)
16. applicaai/kleister-nda \- GitHub, accessed November 20,
    2025, [https://github.com/applicaai/kleister-nda](https://github.com/applicaai/kleister-nda)
17. arXiv:2105.05796v1 \[cs.CL\] 12 May 2021, accessed November 20,
    2025, [https://arxiv.org/pdf/2105.05796](https://arxiv.org/pdf/2105.05796)
18. DocILE: Document Information Localization and Extraction, accessed November 20,
    2025, [https://docile.rossum.ai/](https://docile.rossum.ai/)
19. \[2302.05658\] DocILE Benchmark for Document Information Localization and Extraction, accessed November 20,
    2025, [https://arxiv.org/abs/2302.05658](https://arxiv.org/abs/2302.05658)
20. DocILE 2023 Teaser: Document Information Localization and Extraction \- arXiv, accessed November 20,
    2025, [https://arxiv.org/abs/2301.12394](https://arxiv.org/abs/2301.12394)
21. Extended Overview of DocILE 2023: Document Information Localization and Extraction \- CEUR-WS.org, accessed November
    20, 2025, [https://ceur-ws.org/Vol-3497/paper-049.pdf](https://ceur-ws.org/Vol-3497/paper-049.pdf)
22. We identify the desiderata for a comprehensive benchmark and propose Visually Rich Document Understanding (VRDU).
    VRDU contains two datasets that represent several challenges: rich schema including diverse data types, complex
    templates, and diversity of layouts within a single document type. \- GitHub, accessed November 20,
    2025, [https://github.com/google-research-datasets/vrdu](https://github.com/google-research-datasets/vrdu)
23. \[2211.15421\] VRDU: A Benchmark for Visually-rich Document Understanding \- arXiv, accessed November 20,
    2025, [https://arxiv.org/abs/2211.15421](https://arxiv.org/abs/2211.15421)
24. BoundingDocs: a Unified Dataset for Document Question Answering with Spatial Annotations \- arXiv, accessed November
    20, 2025, [https://arxiv.org/html/2501.03403v1](https://arxiv.org/html/2501.03403v1)
25. Resources: Standard Operating Procedures (SOPs) | NIST, accessed November 20,
    2025, [https://www.nist.gov/pml/owm/laboratory-metrology/documentary-standards-and-resources/sops](https://www.nist.gov/pml/owm/laboratory-metrology/documentary-standards-and-resources/sops)
26. Standard Operating Procedures Data Management August 2022 Rev. 0 \- Alaska Department of Environmental Conservation,
    accessed November 20,
    2025, [https://dec.alaska.gov/media/iltlhx2h/data-management-sop-aug-2022\_accessible.pdf](https://dec.alaska.gov/media/iltlhx2h/data-management-sop-aug-2022_accessible.pdf)
27. Layout Analysis for Robust Resume Parsing \- IEEE Xplore, accessed November 20,
    2025, [https://ieeexplore.ieee.org/document/10455907/](https://ieeexplore.ieee.org/document/10455907/)
28. Layout-Aware Parsing Meets Efficient LLMs: A Unified, Scalable Framework for Resume Information Extraction and
    Evaluation \- arXiv, accessed November 20,
    2025, [https://arxiv.org/html/2510.09722v1](https://arxiv.org/html/2510.09722v1)
29. datasetmaster/resumes · Datasets at Hugging Face, accessed November 20,
    2025, [https://huggingface.co/datasets/datasetmaster/resumes](https://huggingface.co/datasets/datasetmaster/resumes)
30. Public CV dataset for classification by professional categories \- Innovatiana, accessed November 20,
    2025, [https://www.innovatiana.com/en/datasets/resume-dataset](https://www.innovatiana.com/en/datasets/resume-dataset)
31. Data Annotation Strategy for Resume Parser (Images with Grouped Bounding Boxes)?, accessed November 20,
    2025, [https://support.prodi.gy/t/data-annotation-strategy-for-resume-parser-images-with-grouped-bounding-boxes/3006](https://support.prodi.gy/t/data-annotation-strategy-for-resume-parser-images-with-grouped-bounding-boxes/3006)
32. Puppeteer HTML to PDF Generation with Node.js \- RisingStack Engineering, accessed November 20,
    2025, [https://blog.risingstack.com/pdf-from-html-node-js-puppeteer/](https://blog.risingstack.com/pdf-from-html-node-js-puppeteer/)
33. Page.pdf() method \- Puppeteer, accessed November 20,
    2025, [https://pptr.dev/api/puppeteer.page.pdf](https://pptr.dev/api/puppeteer.page.pdf)
34. Scaling Text-Rich Image Understanding via Code-Guided Synthetic Multimodal Data Generation \- Yue Yang, accessed
    November 20, 2025, [https://yueyang1996.github.io/cosyn/](https://yueyang1996.github.io/cosyn/)
35. Synthetic Q\&A and Document Generation for LLM workflows \- YData, accessed November 20,
    2025, [https://ydata.ai/resources/synthetic-qa-documents.html](https://ydata.ai/resources/synthetic-qa-documents.html)
36. Generate PDF with WeasyPrint having common header/footer and pagination, accessed November 20,
    2025, [https://stackoverflow.com/questions/39941967/generate-pdf-with-weasyprint-having-common-header-footer-and-pagination](https://stackoverflow.com/questions/39941967/generate-pdf-with-weasyprint-having-common-header-footer-and-pagination)
37. Weasyprint and CSS: header, footer, pagebreak and positioning \- Stack Overflow, accessed November 20,
    2025, [https://stackoverflow.com/questions/64060477/weasyprint-and-css-header-footer-pagebreak-and-positioning](https://stackoverflow.com/questions/64060477/weasyprint-and-css-header-footer-pagebreak-and-positioning)
38. WeasyPrint, accessed November 20, 2025, [https://weasyprint.org/](https://weasyprint.org/)
39. Element: getBoundingClientRect() method \- Web APIs | MDN, accessed November 20,
    2025, [https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect)
40. Puppeteer \- Render PDF with unique page sizes per page? \- Stack Overflow, accessed November 20,
    2025, [https://stackoverflow.com/questions/77025487/puppeteer-render-pdf-with-unique-page-sizes-per-page](https://stackoverflow.com/questions/77025487/puppeteer-render-pdf-with-unique-page-sizes-per-page)
41. Guidance for Preparing Standard Operating Procedures (SOPs) EPA QA/G-6, accessed November 20,
    2025, [https://www.epa.gov/sites/production/files/2015-06/documents/g6-final.pdf](https://www.epa.gov/sites/production/files/2015-06/documents/g6-final.pdf)
42. Resume OCR: How to Use YOLOv5 for Automated Resume Parsing \- Roboflow Blog, accessed November 20,
    2025, [https://blog.roboflow.com/resume-parsing-computer-vision/](https://blog.roboflow.com/resume-parsing-computer-vision/)