# **A Design Blueprint for a Machine-Readable Business Document Benchmark Corpus: Generation, Ground Truth, and Evaluation for RAG Systems**

## **Phase 1: Problem Definition and Landscape Review**

### **1.1 Clarification of Objectives and Rationale**

The primary objective of this project is to design and blueprint an end-to-end, reproducible system for generating and evaluating a benchmark corpus specifically targeting **machine-readable business document parsing**. The corpus will consist of synthetically generated documents originating from source files (e.g., .docx, .pptx) and their programmatically derived, perfect ground-truth representations.

The core problem this benchmark addresses is a critical gap in the existing document intelligence landscape. Current benchmarks are overwhelmingly focused on *image-based* documents, such as scanned papers or forms, and their document content is predominantly *academic* (e.g., from PubMed or arXiv).1 This leaves a vast and commercially significant domain unevaluated: the common, everyday "business document" (e.g., reports, white papers, slide decks, memos). In these documents, the text is typically machine-readable (i.e., "born-digital"), but the *layout* is complex, varied, and non-trivial to parse.

This evaluation must be tailored for downstream Retrieval-Augmented Generation (RAG) and knowledge system use cases.5 For RAG, simple text extraction is insufficient; parsing failures in structure and semantics are catastrophic.7 Poor parsing leads to "garbage in, garbage out" 6, resulting in fragmented, out-of-order, or contextually "polluted" chunks. This, in turn, degrades retrieval accuracy and causes model hallucinations.6

Therefore, this benchmark's evaluation criteria must transcend simple bounding-box detection or text accuracy and focus on:

* **Hierarchical Understanding:** The correct identification of sections, headings (e.g., H1, H2, H3), and their logical nesting.  
* **Reading Order:** The correct sequencing of text blocks, especially in challenging multi-column layouts 8 or on slides with multiple text boxes.  
* **Semantic Block Integrity:** The correct grouping of semantically coherent units. For example, all items in a list should be identified as such, table rows and cells must remain intact, and captions must be correctly associated with their corresponding figures or tables. Failure to do so "breaks" these units during chunking.10  
* **Element-Specific Extraction:** The robust and accurate extraction of complex structures, particularly tables (including merged cells and headers), lists (including nested lists), and footnotes.  
* **Cost-Quality Frontier:** A unique objective is to create a methodology for plotting parser *accuracy* (across the dimensions above) against parser *cost* (for commercial APIs) or *latency* (for local models). This provides a practical, business-oriented Pareto frontier analysis, enabling organizations to select the optimal parser for their specific needs.

### **1.2 Survey of Existing Benchmarks and Datasets**

An analysis of existing benchmarks reveals *why* a new corpus is necessary. The current landscape is dominated by datasets that are unsuitable for our target domain (machine-readable business documents) for three primary reasons: they are (1) image-based, (2) academic-focused, or (3) reliant on imperfect manual annotation.

* **DocLayNet:** This is a large dataset (over 80,000 pages) for layout segmentation, notable for its diversity beyond academic papers, including financial reports, manuals, and patents.3 However, it is fundamentally an *image-based* dataset. Its ground truth consists of COCO-format bounding boxes for 11 layout classes.3 This is a *geometric* ground truth, not a *semantic* or *hierarchical* one. It does not encode reading order, section hierarchy, or table structure. Furthermore, its reliance on a fixed set of manually-applied labels makes comparison difficult; one analysis had to *discard 165 pages* from the dataset because other parsers did not use the same fine-grained labels (e.g., for list items).12  
* **PubLayNet:** This is another large-scale dataset for page layout segmentation. Its critical limitation is its complete lack of diversity; it is sourced *only* from scientific articles in PubMed Central.3 Consequently, the layout variability is low, and it is irrelevant for our business-document focus. It is also image-based.  
* **DocBank:** Similar to PubLayNet, DocBank is a large dataset (500,000 pages) constructed using weak supervision from scientific articles on arXiv.4 It shares the same limitations: it is image-based and academic-only.  
* **PubTabNet & FinTabNet:** These are large datasets designed specifically for *table recognition*, with PubTabNet containing over 568,000 table images.2 Their format is again image-based, with the ground truth provided as an HTML representation of the table.14 While their image-based nature makes them unsuitable for our primary goal, the project's major contribution that *will* be borrowed is its evaluation metric: the **Tree-Edit-Distance-based Similarity (TEDS)**.16 TEDS is the *de facto* standard for evaluating the correctness of extracted table structures 18, and it will be a cornerstone of our evaluation methodology.  
* **OmniDocBench:** This is the most relevant and modern benchmark in the existing landscape.20 It is a *manually annotated* benchmark of approximately 981 to 1,355 PDF pages 21 covering 9 diverse document types, including *financial reports, slides, and textbooks*.5 Its annotations are rich, covering 15 block-level types, and it is one of the few benchmarks to explicitly evaluate *reading order*.5

The primary weakness of OmniDocBench, however, stems directly from its **reliance on manual annotation**.

1. **Scale:** It is small. 981 pages is insufficient to train large models and provides limited test coverage.24  
2. **Cost:** Manual annotation of this complexity is prohibitively expensive, making the benchmark difficult to extend or adapt.  
3. **Incompleteness:** The manual ground truth is imperfect, forcing evaluation compromises. For instance, the OmniDocBench evaluators explicitly *ignore* headers, footers, and captions when assessing reading order because, in their words, these elements are "handled inconsistently by different models" and have "uncertain placements".5

This landscape analysis proves that manual annotation is the single greatest bottleneck to creating a large-scale, high-fidelity, and semantically rich benchmark. It is slow, costly, and inherently error-prone.

The central hypothesis of this project is that **programmatic generation from source authoring files** (.docx, .pptx) is the *only* way to create a large-scale, 100% accurate benchmark with perfect *semantic* ground truth. By parsing the source OpenXML directly, we can *know* a heading's level with certainty from its style tag.25 We can *know* a table's exact merged-cell structure.27 We can *know* the nesting level of every list item.29 This "source-derived" ground truth is infallible in a way that manual annotation can never be, eliminating the compromises (like ignoring captions) that current benchmarks are forced to make.

### **1.3 Survey of Target Parser Ecosystem**

To design an effective normalization layer (Phase 3\) and cost-quality analysis (Phase 5), a survey of the target parser ecosystem is required. The parsers to be benchmarked fall into distinct categories, each with different output formats, capabilities, and pricing models.

The table below provides a representative sample of the parsers this benchmark is designed to evaluate.

**Table 1: Target Parser Ecosystem: Output Formats, RAG-Readiness, and Pricing Analysis**

| Parser | Type | Core Technology | Primary Output Format | RAG-Ready Features (Reading Order, Hierarchy, Tables) | Cost Model | Est. Cost (USD/1k Pages) (Layout \+ Tables) |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **pdfminer.six** | OSS | Rules-based | Text, XML | Low (Infers text flow, no semantic structure) | Free | $0.00 |
| **PDFPlumber** | OSS | Rules-based (Wraps pdfminer) | Python Objects, CSV | Low (Good for simple table extraction, no hierarchy) | Free | $0.00 |
| **Camelot** | OSS | Rules-based (Lattice/Stream) | JSON, CSV, Pandas 30 | Table-only (Specialized for tables) | Free | $0.00 |
| **Marker** | OSS | ML (Transformer-based) | Markdown, JSON 32 | High (Outputs order, headings, tables, formulas) | Free (Compute cost) | $0.00 |
| **MinerU** | OSS | ML (Pipeline) | Markdown, JSON 33 | High (Layout, order, tables, formulas) 33 | Free (Compute cost) | $0.00 |
| **Docling** | OSS | ML (VLM) | Markdown, JSON 35 | High (Layout, order, tables, code) 35 | Free (Compute cost) | $0.00 |
| **LlamaParse** | Commercial (API) | ML (Proprietary) | Markdown, JSON | High (Marketed for RAG, extracts tables/lists) 36 | Per Page (Free Tier) | $0.00 (Free Tier) |
| **AWS Textract** | Commercial (API) | ML (Proprietary) | Proprietary JSON (Block objects) 37 | Very High (Layout, Tables, Forms, Queries) | Per Feature, Per 1k Pages | \~$15.00 (Tables: $15/k. Layout: $4/k, but free with Tables) 38 |
| **Google Doc AI** | Commercial (API) | ML (Proprietary) | Proprietary JSON (Document object) 40 | Very High (Layout Parser, Custom Extractor) | Per Feature, Per 1k Pages | \~$10.00 (Layout Parser: $10/k) 41 |
| **Azure Doc Intel** | Commercial (API) | ML (Proprietary) | Proprietary JSON (v4.0 GA) 42 | Very High (Layout, Tables, Roles) 42 | Per Page (Free Tier) | \~$10.00 (Layout: $10/k) |

Note: Pricing is based on public 2024-2025 data 38 and is subject to change. The "Cost" column is for illustrative purposes to demonstrate the range of pricing models.

This survey reveals two critical facts. First, the output formats are heterogeneous (text, Markdown, multiple proprietary JSON schemas), making a **canonical normalization layer** (Phase 3\) an absolute prerequisite for evaluation.

Second, the granular, per-feature pricing models of commercial APIs are highly informative. For example, AWS Textract charges separately for different levels of analysis: Layout ($4/k pages), Tables ($15/k pages), and Forms ($50/k pages).38 This implies a 1:4:12.5 cost ratio for these features. This directly validates the project's hypothesis that "parsing" is not a monolithic task. These are distinct, difficult, and increasingly expensive problems.

This pricing structure *mandates* our multi-dimensional evaluation approach. A single, aggregate "accuracy" score would be useless. The benchmark *must* produce separate, fine-grained scores for Layout, Reading Order, Table Structure, and Hierarchy. This is the only way to generate a meaningful cost-quality analysis that allows a user to determine, for example, "Is Parser B's 80% table accuracy worth its 4x cost over Parser A's 50% table accuracy, even if their layout accuracy is identical?"

### **1.4 Landscape and Rationale Summary**

Existing benchmarks are unsuitable for evaluating the parsing of machine-readable business documents for RAG systems. They are overwhelmingly image-focused, academic-focused, and/or rely on small-scale, imperfect manual annotation. This creates a critical, unevaluated gap for the most common types of enterprise documents. The wide variance in parser outputs (from plain text to rich JSON) and the granular, per-feature pricing of commercial APIs further necessitates a new benchmark with three core properties: (1) a large-scale corpus with **perfect, source-derived ground truth**, (2) a **canonical normalization schema** to compare all parsers fairly, and (3) a **multi-dimensional, cost-aware evaluation methodology**.

---

## **Phase 2: Taxonomy of Business Documents and Layout Phenomena**

This phase defines the *content* of the benchmark. It provides the specification for the corpus generation pipeline (Phase 4\) by defining *what* document types will be generated and *what* structural features they must contain.

### **2.1 Document Type Taxonomy**

The corpus will be built from a set of "archetypes," each representing a common business document. Each archetype is a template with a specific content profile and a set of layout characteristics designed to stress-test different parser capabilities.

**Table 2: Taxonomy of Business Document Archetypes and Layout Characteristics**

| Doc Archetype | Source Format | Typical Content | Key Layout Characteristics & Evaluation Focus |
| :---- | :---- | :---- | :---- |
| **1\. Narrative Reports** (e.g., Annual Report, ESG Report, White Paper) | .docx | Mixed (Narrative-heavy) | **Focus: Hierarchy & Complex Objects.** Single and double-column layouts; deep section hierarchy (H1-H4); callout boxes/sidebars; complex tables (with merged cells, multi-line headers); charts with captions; extensive footnotes; headers/footers with page numbers. |
| **2\. Financial/Analytic Reports** (e.g., Quarterly Earnings, KPI Dashboard) | .docx | Numeric-heavy | **Focus: Table Extraction.** Dominated by numerous, dense tables. Tests numeric precision, table boundary detection, and handling of multi-level headers. Simple text, minimal hierarchy (H1/H2). Many charts linked to tables. |
| **3\. Policy/Procedural Docs** (e.g., HR Manual, SOP, Compliance Guide) | .docx | Narrative (Procedural) | **Focus: List Extraction.** Dominated by deeply *nested lists* (e.g., 1.a.i., bullets within bullets). Tests list detection, item integrity, and correct nesting level. Simple hierarchy and simple tables. |
| **4\. Marketing Materials** (e.g., Product Brochure, Case Study, One-Pager) | .docx | Mixed | **Focus: Reading Order.** Highly visual, non-linear layouts. Heavy use of 2- and 3-column sections, text flowing around images, and pull-quotes. This is the primary stress test for all reading order algorithms. |
| **5\. Internal Communications** (e.g., Memo, Status Report, Meeting Notes) | .docx | Narrative | **Focus: Baseline/Sanity Check.** Simple, single-column, linear layouts. Mostly text, simple headings (H1/H2), and basic bullet points. Used to establish a baseline performance. |
| **6\. Presentation Decks** (e.g., Investor Deck, Marketing Deck, Update) | .pptx | Mixed (Bullet-point heavy) | **Focus: Slide Structure & Non-Visual Content.** Tests slide-based parsing. Key features: detection of the slide *Title* 44; reading order of multiple, side-by-side text boxes 45; bulleted lists within text frames 46; and extraction of "hidden" *speaker notes*.47 |

### **2.2 Layout and Structural Phenomena Checklist**

This master checklist defines the universe of features that the corpus generator must randomly sample from and that the evaluation harness must measure.

* **Document-Level**  
  * Metadata: Title, Author(s), Date.  
  * Outline: A correct, hierarchical Table of Contents derived from heading styles.  
* **Page-Level**  
  * Headers: Text and page numbers appearing at the top of the page.  
  * Footers: Text and page numbers appearing at the bottom of the page.5  
  * Footnotes / Endnotes: Correct parsing of the reference marker (e.g., $^1$) in the text and its link to the note content at the bottom of the page or end of the document.  
* **Block-Level (Layout)**  
  * Single-column text (baseline).  
  * Multi-column text (2- and 3-column layouts).  
  * Callout Boxes / Sidebars: Text blocks (e.g., in a styled frame) that are visually separate from the main narrative flow and should be ordered correctly (e.g., at the end of the section).  
* **Block-Level (Hierarchy & Semantics)**  
  * Headings: Levels 1-4, with and without section numbering (e.g., "1. Introduction" vs. "1.1.3 Key Findings").  
  * Paragraphs: Standard narrative text blocks.  
  * Lists (Bulleted): Simple (single-level) and nested (up to 3 levels).  
  * Lists (Numbered): Simple and nested (e.g., 1., 1.1., 1.1.1.).  
  * Checklists (e.g., using Word's "checkbox" bullet style).  
* **Table Phenomena**  
  * Simple Tables: Basic grid with a single, unambiguous header row.  
  * Complex Headers (Column): Multi-row headers, where one header spans multiple columns below it.  
  * Complex Headers (Row): "Stub" columns where a header in the first column spans multiple rows.  
  * Merged Cells: Cells with rowspan or colspan greater than 1, occurring in both header and body.27  
  * Content-Type: Tables containing only text, tables containing only numbers, and mixed-content tables.  
* **Figure Phenomena**  
  * Images / Charts: Placeholders for graphical elements.  
  * Captions: Single-line and multi-line captions appearing *below* the figure.  
  * Text-to-Figure Reference: In-text references (e.g., "As shown in Figure 3..."). The benchmark will evaluate if the caption is correctly extracted and if its proximity to the reference is preserved.  
* **Slide-Deck Phenomena (from .pptx)**  
  * Slide Title: Correct identification of the main slide title.44  
  * Multi-shape Reading Order: Correct ordering of text from non-overlapping text boxes (e.g., two columns of bullets).45  
  * Bulleted Lists: Standard bulleted content within a text frame.46  
  * Speaker Notes: Text that is part of the document but not visually rendered on the slide.48

---

## **Phase 3: Ground-Truth Representation and Normalization Target**

This phase defines the canonical data structure—the "perfect" ground truth—that serves as the target for both the corpus generation pipeline and the parser normalization adapters. This schema is the single most critical component of the benchmark.

### **3.1 Choice of Canonical Format**

* **Proposal:** A single, hierarchical **JSON schema** for each document.  
* **Justification:**  
  * **Expressiveness:** A tree-like structure (document \-\> sections \-\> blocks) is ideally suited to represent the hierarchical nature of documents.50 It can naturally encode section nesting (in the metadata object), list nesting, and table structure (rows, cells) (in the blocks array).  
  * **Ease of Mapping (Source → Ground Truth):** This JSON structure maps cleanly from the OpenXML trees of .docx 52 and .pptx 46 files. Document-level properties become metadata, and the ordered list of w:p (paragraph) and w:tbl (table) elements becomes the blocks array.  
  * **Ease of Mapping (Parser → Ground Truth):** This format is a "lingua franca." All target parsers already output some form of structured data that can be mapped to this schema. Commercial APIs provide proprietary JSON 37, and ML-based tools like Marker provide Markdown 32 or JSON 33, all of which are trivially convertible to our canonical JSON.  
  * **Evaluation:** A JSON ground truth is 100% machine-readable, easy to parse, and allows for precise, programmatic comparison. For example, the structure.html field for tables can be extracted and compared directly using the TEDS metric.14

### **3.2 Schema Design**

The proposed schema is block-based. The root contains document-level metadata (including the section hierarchy for Hierarchy\_TED evaluation) and a single, flat list of blocks. This blocks array represents the *global reading order*, and hierarchical relationships (like lists) are defined within each block's structure field.

JSON

{  
  "document\_id": "report\_001",  
  "document\_type": "Narrative Report",   
  "source\_file": "report\_001.docx",  
  "pdf\_file": "report\_001.pdf",  
  "metadata": {  
    "title": "Annual ESG Report 2025",  
    "authors":,  
    "date": "2025-10-27",  
    "section\_outline": \[   
      {  
        "title": "1. Introduction",   
        "level": 1,   
        "block\_id": "uuid-block-005",  
        "children": \[  
          {  
            "title": "1.1 Our Mission",   
            "level": 2,   
            "block\_id": "uuid-block-008",  
            "children":  
          }  
        \]  
      },  
      {  
        "title": "2. Governance",   
        "level": 1,  
        "block\_id": "uuid-block-020",  
        "children":  
      }  
    \]  
  },  
  "blocks": \[  
    {  
      "block\_id": "uuid-block-001",  
      "block\_type": "header",   
      "reading\_order\_index": 0,  
      "page\_numbers": ,  
      "text": "Annual ESG Report 2025 \- Page 1"  
    },  
    {  
      "block\_id": "uuid-block-005",  
      "block\_type": "heading",  
      "reading\_order\_index": 1,  
      "page\_numbers": ,  
      "text": "1. Introduction",  
      "structure": {  
        "level": 1,  
        "numbering": "1."  
      }  
    },  
    {  
      "block\_id": "uuid-block-006",  
      "block\_type": "paragraph",  
      "reading\_order\_index": 2,  
      "page\_numbers": ,  
      "text": "This report outlines our initiatives for fiscal year 2025."  
    },  
    {  
      "block\_id": "uuid-block-007",  
      "block\_type": "list\_item",  
      "reading\_order\_index": 3,  
      "page\_numbers": ,  
      "text": "Our first goal is sustainability.",  
      "structure": {  
        "list\_id": "uuid-list-001",   
        "level": 0,   
        "ordered": false,  
        "item\_index": 0   
      }  
    },  
    {  
      "block\_id": "uuid-block-008",  
      "block\_type": "list\_item",  
      "reading\_order\_index": 4,  
      "page\_numbers": ,  
      "text": "A nested goal.",  
      "structure": {  
        "list\_id": "uuid-list-001",  
        "level": 1,   
        "ordered": false,  
        "item\_index": 0   
      }  
    },  
    {  
      "block\_id": "uuid-block-010",  
      "block\_type": "table",  
      "reading\_order\_index": 5,  
      "page\_numbers": ,  
      "structure": {  
          
        "html": "\<table\>\<thead\>\<tr\>\<th rowspan='2'\>Region\</th\>\<th colspan='2'\>Sales (2025)\</th\>\</tr\>\<tr\>\<th\>Q1\</th\>\<th\>Q2\</th\>\</tr\>\</thead\>\<tbody\>\<tr\>\<td\>North America\</td\>\<td\>$1.2M\</td\>\<td\>$1.4M\</td\>\</tr\>\</tbody\>\</table\>",  
          
        "grid":,  
          \[  
            {"cell\_id": "cell-1-1", "text": "Q1", "is\_header": true, "row\_span": 1, "col\_span": 1},  
            {"cell\_id": "cell-1-2", "text": "Q2", "is\_header": true, "row\_span": 1, "col\_span": 1}  
          \],  
          \[  
            {"cell\_id": "cell-2-0", "text": "North America", "is\_header": false, "row\_span": 1, "col\_span": 1},  
            {"cell\_id": "cell-2-1", "text": "$1.2M", "is\_header": false, "row\_span": 1, "col\_span": 1},  
            {"cell\_id": "cell-2-2", "text": "$1.4M", "is\_header": false, "row\_span": 1, "col\_span": 1}  
          \]  
      }  
    },  
    {  
      "block\_id": "uuid-block-011",  
      "block\_type": "caption",  
      "reading\_order\_index": 6,  
      "page\_numbers": ,  
      "text": "Table 1: Regional Sales",  
      "structure": {  
        "captions\_block\_id": "uuid-block-010"   
      }  
    },  
    {  
      "block\_id": "uuid-block-012",  
      "block\_type": "speaker\_note",   
      "reading\_order\_index": \-1,   
      "page\_numbers": ,   
      "text": "Remember to emphasize the growth in NA."  
    }  
  \]  
}

### **3.3 Source → Ground Truth Pipeline**

This section details the precise, programmatic methods for converting the source .docx and .pptx files into the canonical JSON ground truth. This is the core engineering of the benchmark.

* **From Word (.docx) using python-docx and lxml:**  
  * **Reading Order:** A naive iteration of document.paragraphs followed by document.tables is incorrect. The *logical* reading order is the order of elements in the word/document.xml file.52 This will be achieved by implementing a function similar to the iter\_block\_items utility 53, which iterates over the direct children of the document body (CT\_P for paragraphs and CT\_Tbl for tables) in their defined XML order.  
  * **Headings:** For each Paragraph object, its style will be inspected. If paragraph.style.name.startswith('Heading') (e.g., 'Heading 1', 'Heading 2') 25, it will be classified as a block\_type: "heading". The integer level will be extracted and stored, and this information will be used to build the metadata.section\_outline tree.  
  * **Lists:** The python-docx library has poor high-level support for *reading* list properties. Therefore, it is necessary to drop into the underlying lxml representation of the paragraph (paragraph.\_element). The presence of a w:pPr/w:numPr (numbering properties) child tag indicates a list item.29 The w:ilvl (indent level) and w:numId (list ID) tags within this element will be parsed to determine the structure.level and structure.list\_id, respectively.  
  * **Tables:** For each Table object, the pipeline will iterate through its rows and cells to build the structure.grid. To handle merged cells, a simple iteration of row.cells is insufficient, as python-docx will return the same "merged" cell multiple times.27 The correct approach is to iterate the "unique" cells by inspecting the underlying \_tc (table cell) element for its properties.28 The presence of a vMerge="continue" attribute indicates a vertically spanned cell. The presence of a gridSpan attribute indicates a horizontally spanned cell. This allows for the 100% accurate population of the row\_span and col\_span fields in the ground-truth grid.  
  * Multi-Column Layouts (The Hybrid Ground-Truth Pipeline):  
    A critical challenge is the discrepancy between semantic order and visual order. In the .docx XML, a two-column layout is just a single, continuous flow of text. However, in the rendered PDF, the reading order flows down the first column, then to the top of the second. For RAG, the visual order is what matters.  
    A novel, hybrid ground-truth pipeline will be used to solve this:  
    1. **Pass 1 (Semantics):** The docx\_to\_canonical.py parser (described above) will run *first*, extracting all semantic information (block type, text, hierarchy, list levels, table structure) and the *logical* XML order.  
    2. **Pass 2 (PDF Conversion):** The .docx file is converted to .pdf using the headless LibreOffice converter (Phase 4).  
    3. **Pass 3 (Visuals):** A *simple, trusted* spatial parser (e.g., PyMuPDF) will be run on the *newly generated PDF*. This pass is *not* used to determine block *type* (which is unreliable), but *only* to extract text blocks with their (page\_number, y\_coordinate, x\_coordinate) and to detect column boundaries (e.g., using PyMuPDF's column\_boxes feature 9).  
    4. Pass 4 (Merge): The semantic blocks from Pass 1 are aligned (via text match) with the visual blocks from Pass 3\. The page\_numbers and sorted visual coordinates from Pass 3 are then used to populate the final reading\_order\_index in the ground-truth JSON.  
       This hybrid approach provides the best of both worlds: the perfect, infallible semantic data from the source file, and the correct visual reading order from the rendered PDF.  
* **From PowerPoint (.pptx) using python-pptx:**  
  * **Reading Order:** Unlike .docx, the .pptx XML does *not* store shapes in a logical reading order; it stores them in z-order (stacking order).45 The standard heuristic to approximate visual reading order is to iterate all shapes on a slide and *sort them by their (shape.top, shape.left) coordinates*.45 This sorted list will define the reading\_order\_index.  
  * **Structure:** The slide.title shape, if it exists, will be explicitly tagged as block\_type: "heading" with level: 1\.44 All other text-bearing shapes (shape.has\_text\_frame 46) will be parsed as paragraph or list\_item blocks.  
  * **Speaker Notes:** A key feature for testing "hidden" context extraction. The pipeline will access the notes slide via slide.notes\_slide.notes\_text\_frame.text 47 and store this content as a block\_type: "speaker\_note" with reading\_order\_index: \-1.

---

## **Phase 4: Corpus Generation Strategy (Word/PowerPoint → PDF)**

This phase details the automated "factory" for producing the corpus of .docx, .pptx, .pdf, and ground-truth .json files.

### **4.1 Tools and Stack**

* **Document Authoring:** python-docx 25 and python-pptx 57 will be used to programmatically create the source Office documents from the templates defined in Phase 2\.  
* **Content Generation:** Synthetic "business-style" text will be generated using libraries like faker. Numeric data for tables and charts will be generated using numpy.  
* **PDF Conversion (The Critical Step):**  
  * **Tool:** LibreOffice (or soffice) running in headless mode.  
  * **Justification:** This is the *only* solution that is high-fidelity, free, cross-platform (Linux, macOS, Windows), and fully automatable for *both* .docx and .pptx conversion.58 Alternatives that use MS Office automation (e.g., win32com, docx2pdf) are Windows-only, require licensed Office installs 61, and are not suitable for a reproducible, containerized benchmark. Other commercial APIs (e.g., Apryse, ConvertAPI) 63 introduce external dependencies and costs.  
  * **Implementation:** The conversion process will be containerized using **Docker** for maximum reproducibility. A Dockerfile will be created based on a minimal Linux image (e.g., Alpine or Debian) that installs the specific required libreoffice packages (e.g., libreoffice-writer, libreoffice-impress, and necessary font packages).65  
  * The conversion will be invoked from a Python script using subprocess.run 67:  
    soffice \--headless "-env:UserInstallation=file:///tmp/LibreOffice\_Conversion\_Profile" \--convert-to pdf \--outdir /output\_directory /input\_directory/document.docx  
  * **Risk Mitigation:**  
    1. LibreOffice conversion fidelity can vary by version, especially with complex .pptx tables.68 The Dockerfile will pin a *specific version* (e.g., LibreOffice 24.2.5 60) to ensure all generated PDFs are identical.  
    2. Headless LibreOffice instances can conflict, causing hangs.69 The "-env:UserInstallation=file:///...\_Profile" flag is *mandatory* to ensure each conversion uses a separate, temporary profile, enabling safe, parallel execution.

### **4.2 Document Templates and Parameterization**

The corpus generator will be built around a system of Generator classes, one for each Doc Archetype in Table 2 (e.g., NarrativeReportGenerator, PptxDeckGenerator).

* **Template Logic:** A template will be a Python function (e.g., generate\_esg\_report(params)) that uses the python-docx API to build the document. For example, it will call document.add\_heading(level=1), programmatically create a table and set merged cells, or apply a "2 column" style to a section.  
* **Parameterization:** To ensure diversity and coverage, each generator will accept a params dictionary to randomize the document's structure. This prevents parsers from "overfitting" to a single template.  
  * num\_sections: Random integer (e.g., 2 to 5\)  
  * heading\_depth: Random integer (e.g., 2 to 4\)  
  * use\_multi\_column: Boolean (True/False)  
  * num\_tables: Random integer (e.g., 1 to 5\)  
  * table\_complexity: String ('simple' or 'complex' \-\> with merged cells)  
  * num\_lists: Random integer (e.g., 2 to 6\)  
  * list\_nesting\_depth: Random integer (e.g., 1 to 3\)  
  * include\_footnotes: Boolean  
  * include\_charts: Boolean

### **4.3 Content Generation**

* **Text:** Synthetic "business lorem ipsum" will be used. This will not be standard "lorem ipsum" but rather text generated from a domain-specific vocabulary (e.g., "fiscal year," "quarterly results," "ESG initiatives," "stakeholder engagement," "product overview") to be more realistic.  
* **Tables:** numpy.random will be used to generate arrays of numeric data. These will be programmatically formatted as currency ($), percentages (%), or simple integers. Headers will be pulled from the same synthetic business vocabulary.  
* **Charts:** Both python-docx and python-pptx support adding charts. While the graphic rendering itself is not the focus, the *presence* of the chart, its *caption*, and any in-text *references* ("See Chart 5") are critical elements to be included and evaluated. All text in charts will be machine-readable.

### **4.4 Corpus Scale and Coverage**

* **Target Scale:** **300-500 documents**.  
  * *Reasoning:* This scale is a strategic balance. It is large enough to (a) be statistically significant, (b) provide thousands of pages for processing, and (c) ensure ample test cases for all layout phenomena (e.g., hundreds of complex tables, hundreds of nested lists). It is also small enough to (d) be computationally feasible to run all local parsers against and (e) fit within the free tiers or reasonable testing budgets of commercial APIs (e.g., Azure's 500 free pages/month 70). This page count is comparable to OmniDocBench 23 but is generated at zero-cost with perfect ground truth.  
* **Coverage Tracking:** A manifest.json file will be generated for the entire corpus. Each document entry will include a list of "tags" corresponding to the phenomena it contains (from the checklist in 2.2).  
  * {"document\_id": "report\_001", "tags": \["multi\_column", "merged\_cell\_table", "nested\_list\_3", "footnotes"\]}  
  * This manifest serves two purposes:  
    1. **Validation:** It allows us to verify that the generator is successfully covering all target phenomena.  
    2. **Fine-Grained Evaluation:** It allows users to run evaluations on *subsets* of the corpus (e.g., "Test all parsers *only* on documents tagged with multi\_column" or "Calculate table accuracy *only* on merged\_cell\_table documents").

---

## **Phase 5: Evaluation Design and Metrics**

This phase defines the evaluation harness, the normalization adapter layer, and the specific, multi-dimensional metrics for scoring parser performance and cost.

### **5.1 What Parsers Must Output / How We Normalize**

A direct comparison of heterogeneous parser outputs (e.g., Marker's Markdown 32 vs. AWS's JSON 37) is impossible. An adapter and normalization layer is required to map *all* parser outputs to our canonical JSON schema (Section 3.2).

* **Invocation:** A central run\_parser.py script will manage the execution of each parser against a PDF. This script will be responsible for:  
  1. Calling the parser's API or command-line interface.  
  2. Capturing its raw output (e.g., .json or .md files).  
  3. Recording the wall-clock latency (for local parsers).  
  4. Calculating the monetary\_cost based on API pricing tiers (for commercial parsers).  
* **Normalization:** For *each* parser, a dedicated adapter script (e.g., normalize\_aws\_to\_canonical.py) will be implemented. This script will read the parser's raw output and transform it into a *valid* instance of our schema.json.  
  * **Example (AWS Textract):** The adapter will iterate through the list of Block objects.37 BlockType='TABLE' will be mapped to our table block structure. BlockType='LAYOUT\_HEADING' will become a heading block. BlockType='LINE' blocks will be grouped into paragraph blocks based on proximity.  
  * **Example (Marker):** The adapter will parse the output Markdown.32 \#\# Header becomes block\_type: "heading", level: 2\. Markdown tables (| A | B |...) will be parsed into our table.structure.grid.  
  * **Handling Missing Features (Lossy Mapping):** This is a critical aspect of the evaluation. If a parser does not support a feature, its normalized output will be missing that data. For example, pdfminer.six does not explicitly identify headings or tables 71; its normalized JSON will *only* contain paragraph blocks. When this is compared to the ground truth, it will receive a 0% accuracy score for Hierarchy and Tables, *as it should*. This "evaluates by omission" and is a core design principle.  
  * **Text Normalization:** Before any text comparison, all text strings (from both ground truth and predicted output) will be passed through a simple normalization function: text.lower().strip(), remove all punctuation, and normalize internal whitespace to a single space. This ensures the evaluation focuses on structure, not trivial differences like a misplaced comma.

### **5.2 Core Metrics**

The evaluation will not produce a single score. It will produce a *vector* of scores, one for each dimension of parsing, enabling fine-grained analysis.

* **1\. Block-Level Structure and Reading Order**  
  * **Alignment:** The list of *predicted* blocks (from the normalized parser output) will be aligned with the list of *ground-truth* blocks (from the GT blocks array) using a sequence-matching algorithm based on their normalized text content.  
  * **Reading Order Accuracy:** From the alignment, we derive two sequences of block IDs: the ground-truth order (e.g., ) and the predicted order (e.g., ).  
  * **Metric:** **Kendall's Tau (Rank Correlation)**.72 This is a standard metric for measuring the similarity between two ranked lists.74 It counts the number of "swapped" pairs (e.g., (B, C) is an inversion). The result will be a score from \-1.0 (perfectly inverted) to 1.0 (perfectly correct).  
* **2\. Section Hierarchy and Headings**  
  * **Data:** The metadata.section\_outline *tree* from the predicted JSON will be compared directly to the metadata.section\_outline tree from the ground-truth JSON.  
  * **Metric:** **Tree Edit Distance (TED)**.50 This algorithm computes the minimum "cost" (number of inserts, deletes, and re-labels) to transform the predicted tree into the ground-truth tree. This will be normalized to a similarity score (e.g., Normalized\_TED \= 1 \- (TED / max(len(tree1), len(tree2)))).  
* **3\. Lists and Bullets**  
  * **Metric:** **List Item F1 Score**.  
    * *Precision:* What percentage of blocks that the parser *predicted* as list\_item were *actual* list\_item blocks in the ground truth?  
    * *Recall:* What percentage of the *ground-truth* list\_item blocks did the parser correctly identify?  
  * **Metric:** **List Nesting Accuracy**. For all list items that were *correctly* matched (true positives), what percentage had the correct structure.level?  
* **4\. Tables**  
  * **Metric 1 (Structure): TEDS (Tree-Edit-Distance-based Similarity)**. This is the standard for table structure.17 We will compare the structure.html string from the predicted JSON to the ground-truth structure.html.14 We will use the "structure\_only" mode of the TEDS metric 77 to isolate layout recovery from text extraction errors (which should be minimal in machine-readable PDFs anyway).  
  * **Metric 2 (Content):** Cell-level F1 Score. For the predicted table that best aligns with the ground truth, we will compute a simple F1 score based on the normalized text content of each cell in the structure.grid.  
* **5\. RAG-Specific Metric (Novel Contribution): "Chunk Purity"**  
  * *Rationale:* Existing metrics do not adequately capture the fragmentation and pollution problem that is central to RAG success.10 A parser might "find" all the text (100% text accuracy) but split a single table row into three separate chunks ("fragmentation") or merge a paragraph with a nearby footnote ("pollution").  
  * *Definition:*  
    1. Let GT\_Blocks be the set of $N$ ground-truth semantic blocks (e.g., 100 paragraphs, 20 list items, 5 tables).  
    2. Let P\_Blocks be the set of $M$ blocks output by the parser.  
    3. **Fragmentation Score:** For each block gt\_b in GT\_Blocks, find all blocks in P\_Blocks that contain text from it. If one gt\_b is split across three p\_b blocks, its fragmentation score is low. The overall score is the average.  
    4. **Pollution Score:** For each block p\_b in P\_Blocks, find all blocks in GT\_Blocks that its text overlaps with. If one p\_b contains text from a paragraph *and* a footnote, its pollution score is low. The overall score is the average.  
    5. **Chunk Purity Score (CPS) \= $F1(Fragmentation\\\_Score, Pollution\\\_Score)$**. This score directly measures the parser's ability to produce semantically coherent chunks, which is arguably the most important feature for a RAG ingestion pipeline.

### **5.3 Aggregated Scores and Use-Case Focus**

While the per-dimension scores are primary, a high-level aggregated score is useful for quick comparison. A weighted **"RAG-Readiness Score"** will be provided:

Score \= (0.4 \* Chunk\_Purity) \+ (0.3 \* Reading\_Order\_Tau) \+ (0.2 \* Table\_TEDS) \+ (0.1 \* Hierarchy\_TED)

*Reasoning:* For RAG, having clean, well-ordered chunks (Purity, Order) is more critical for retrieval than having a perfect section tree (Hierarchy). Tables are also highly critical as they contain dense factual data.

### **5.4 Cost and Performance Metrics**

The final component of the evaluation is to integrate cost and performance.

* **Monetary Cost:** For commercial APIs, the run\_parser.py script will log the exact cost of each API call. This will be aggregated to a Cost\_per\_1000\_pages metric.38 This will be broken down by feature (e.g., Cost\_Layout\_Only vs. Cost\_Layout\_and\_Tables).  
* **Latency:** For local, open-source models, latency\_per\_page (in seconds) will be recorded. To ensure a fair comparison, this will be benchmarked on a standardized cloud VM (e.g., a gcp-n2-standard-4 or specific AWS EC2 instance) with and without GPU, where applicable.  
* **Visualization:** The final benchmark report will feature **Pareto Frontier plots**.  
  * **Plot 1 (Commercial):** X-axis: Cost ($/1k pages), Y-axis: RAG-Readiness Score.  
  * **Plot 2 (Local):** X-axis: Latency (sec/page), Y-axis: RAG-Readiness Score.

These plots are the ultimate deliverable for a business user, allowing them to instantly identify which parsers are on the "efficient frontier" (offering the best possible accuracy for a given cost/latency) and which are "dominated" (i.e., they are both slower/more expensive *and* less accurate than another option).

---

## **Phase 6: Implementation Plan and Coding-Assistant Backlog**

This phase translates the preceding design into a practical, actionable engineering plan, including repository structure, task backlog, and reproducibility guidelines.

### **6.1 High-Level Phases & Repository Structure**

The project will be organized into a single repository with a logical directory structure that separates concerns: corpus generation, ground-truth generation, parser adapters, and evaluation.

**Proposed Repository Structure:**

/benchmark-corpus-generator/  
|  
|-- /corpus\_generator/       \# Phase 2: Python scripts to generate docs  
| |-- generate\_docx.py  
| |-- generate\_pptx.py  
| |-- /templates/  
| | |-- report\_template.py  
| | |-- deck\_template.py  
| | |-- policy\_template.py  
| |-- /content/  
| |-- business\_text.py \# Synthetic text generator  
| |-- numeric\_data.py  \# Synthetic table data  
|  
|-- /gt\_generator/           \# Phase 3: Python scripts for GT  
| |-- docx\_to\_canonical.py  
| |-- pptx\_to\_canonical.py  
| |-- hybrid\_gt\_merger.py  \# Implements the PymuPDF merge (Insight 3.3)  
| |-- schema.json          \# The canonical schema definition  
|  
|-- /corpus/                 \# Phase 4: The generated dataset  
| |-- /docx/               \# Source.docx files  
| |-- /pptx/               \# Source.pptx files  
| |-- /pdf/                \# Generated.pdf files  
| |-- /ground\_truth/       \# Generated canonical.json files  
| |-- manifest.json        \# Maps doc\_id to phenomena tags (4.4)  
|  
|-- /parser\_adapters/        \# Phase 5: Normalization scripts  
| |-- run\_parser.py        \# Main invocation script  
| |-- /adapters/  
| | |-- run\_marker.py  
| | |-- normalize\_marker.py  
| | |-- run\_aws\_textract.py  
| | |-- normalize\_aws.py  
| | |-- run\_google\_docai.py  
| | |-- normalize\_google.py  
| | |--...  
|  
|-- /evaluation\_harness/     \# Phase 5: Metrics implementation  
| |-- evaluate.py          \# Main evaluation script  
| |-- /metrics/  
| | |-- alignment.py     \# Block alignment logic  
| | |-- reading\_order.py \# Kendall's Tau   
| | |-- hierarchy.py     \# Tree Edit Distance   
| | |-- tables.py        \# TEDS   
| | |-- lists.py         \# List F1 and Nesting Accuracy  
| | |-- chunking.py      \# Chunk Purity (Novel Metric)  
|  
|-- /scripts/  
| |-- 01\_generate\_corpus.sh  \# (Runs Phase 2, 3, 4\)  
| |-- 02\_run\_all\_parsers.sh  \# (Runs Phase 5.1)  
| |-- 03\_run\_evaluation.sh   \# (Runs Phase 5.2-5.4)  
|  
|-- /reports/                \# Final output: plots, leaderboards  
| |-- results\_summary.json  
| |-- cost\_quality\_frontier.png  
| |-- Results\_Analysis.ipynb  
|  
|-- Dockerfile               \# For LibreOffice PDF conversion   
|-- pyproject.toml           \# Python dependencies  
|-- README.md

### **6.2 Detailed Task Backlog (Prioritized)**

This backlog is prioritized into milestones, with tasks designed to be assigned to a coding assistant or engineering team.

Milestone 1: Schema & Ground-Truth Pipeline (Phase 3\)  
This milestone builds the "ruler" we will use to measure everything.

* **Task 1.1 (Schema):** Define, validate, and save the final schema.json for the canonical ground-truth representation, as detailed in Section 3.2.  
* **Task 1.2 (GT: Docx):** Implement the gt\_generator/docx\_to\_canonical.py module.  
  * **Sub-task 1.2.1:** Implement the iter\_block\_items function to iterate paragraphs and tables in their correct logical document order, based on the OpenXML structure.53  
  * **Sub-task 1.2.2:** Implement heading detection by reading paragraph.style.name. It must correctly parse levels from styles like 'Heading 1', 'Heading 2', etc..25 This must also build the metadata.section\_outline tree.  
  * **Sub-task 1.2.3:** Implement list detection by using lxml to inspect the paragraph.\_element for w:pPr/w:numPr tags and their w:ilvl and w:numId children to determine nesting level and list grouping.29  
  * **Sub-task 1.2.4:** Implement table parsing. This function *must* iterate "unique" cells by inspecting the \_tc element for vMerge and gridSpan properties to correctly populate row\_span and col\_span.27 It must also generate the structure.html string for TEDS evaluation.14  
* **Task 1.3 (GT: Pptx):** Implement the gt\_generator/pptx\_to\_canonical.py module.  
  * **Sub-task 1.3.1:** Implement a function to get the correct reading order for a slide by sorting all shape.has\_text\_frame shapes by their (shape.top, shape.left) properties.45  
  * **Sub-task 1.3.2:** Implement logic to identify the slide.title shape and tag it as a heading block.44  
  * **Sub-task 1.3.3:** Implement logic to extract speaker notes using slide.notes\_slide.notes\_text\_frame.text and tag them as speaker\_note blocks.48

Milestone 2: Corpus Generation (Phase 4\)  
This milestone builds the "factory" and the corpus itself.

* **Task 2.1 (PDF Converter):** Create the Dockerfile that installs a pinned version of LibreOffice and all required dependencies (fonts, etc.).65 Write a Python wrapper convert\_office\_to\_pdf.py that uses subprocess.run to call soffice \--headless with the correct flags, including \-env:UserInstallation.67  
* **Task 2.2 (GT: Hybrid):** Implement gt\_generator/hybrid\_gt\_merger.py.  
  * **Sub-task 2.2.1:** This script will orchestrate the hybrid GT pipeline. It will call the semantic parser (Task 1.2) to get the semantic JSON.  
  * **Sub-task 2.2.2:** It will then use PyMuPDF to open the corresponding PDF, extract text blocks with coordinates, and determine column breaks.9  
  * **Sub-task 2.2.3:** It will implement the alignment logic (text-matching) to merge the two, updating the semantic JSON with the *correct* visual reading\_order\_index and page\_numbers.  
* **Task 2.3 (Generator: Templates):** Implement the template generators in corpus\_generator/templates/.  
  * **Sub-task 2.3.1:** Implement report\_template.py using python-docx to programmatically create documents with parameterized features (multi-column sections, tables with merged cells, nested lists, footnotes).  
  * **Sub-task 2.3.2:** Implement deck\_template.py using python-pptx to create slides with titles, side-by-side text boxes, and speaker notes.  
* **Task 2.4 (Generator: Main):** Implement corpus\_generator/generate\_docx.py and generate\_pptx.py to call the templates with randomized parameters (from 4.2).  
* **Task 2.5 (Script: Generate):** Implement scripts/01\_generate\_corpus.sh. This script will:  
  1. Call the generators (Task 2.4) to create $N$ .docx and .pptx files.  
  2. Call the PDF converter (Task 2.1) to create the .pdf files.  
  3. Call the GT pipeline (Task 2.2) to create the final ground-truth .json files.  
  4. Generate the manifest.json file.

Milestone 3: Parser Integration & Evaluation (Phase 5\)  
This milestone builds the "testing harness" and runs the benchmark.

* **Task 3.1 (Adapters: OSS):** Implement the first set of adapters.  
  * **Sub-task 3.1.1:** Implement run\_marker.py and normalize\_marker.py. The normalizer must parse Marker's Markdown 32 into the schema.json format.  
  * **Sub-task 3.1.2:** Implement run\_pdfminer.py and normalize\_pdfminer.py. This will be a "lossy" adapter, likely only producing paragraph blocks.71  
* **Task 3.2 (Adapters: Commercial):** Implement the first commercial adapter.  
  * **Sub-task 3.2.1:** Implement run\_aws\_textract.py. It must call analyze\_document with FeatureTypes= 37 and securely log API costs.  
  * **Sub-task 3.2.2:** Implement normalize\_aws.py to map the AWS Block object JSON 37 to our canonical schema.json.  
* **Task 3.3 (Metrics: Libs):** Implement all metric functions in evaluation\_harness/metrics/.  
  * **Sub-task 3.3.1:** reading\_order.py: Implement Kendall's Tau correlation.74  
  * **Sub-task 3.3.2:** hierarchy.py: Implement normalized Tree Edit Distance, likely using a library like zss.75  
  * **Sub-task 3.3.3:** tables.py: Implement TEDS by wrapping the official pubtabnet library and feeding it the structure.html strings.17  
  * **Sub-task 3.3.4:** chunking.py: Implement the novel "Chunk Purity" (Fragmentation & Pollution) F1 score as defined in 5.2.  
* **Task 3.4 (Eval Harness):** Implement the main evaluation\_harness/evaluate.py script. This script will:  
  1. Take a ground\_truth.json and a predicted.json as input.  
  2. Perform the text-based block alignment.  
  3. Call all metric functions (Task 3.3) on the aligned blocks.  
  4. Output a scores.json file with the full vector of scores (Tau, TED, TEDS, Purity, etc.).  
* **Task 3.5 (Reporting):** Implement scripts/03\_run\_evaluation.sh to aggregate all scores.json files. Create the reports/Results\_Analysis.ipynb notebook to load this aggregated data, merge it with cost/latency data, and generate the final Cost vs. Quality Pareto frontier plots.

### **6.3 Reproducibility and Packaging**

* **Environment:** Reproducibility is paramount. The environment will be managed by two files:  
  1. pyproject.toml: Manages all Python dependencies (e.g., python-docx, python-pptx, pymupdf, numpy, zss, boto3, google-cloud-aiplatform).  
  2. Dockerfile: Manages the LibreOffice system dependency, ensuring identical PDF conversion across all systems.65  
* **Publication:** The final benchmark will be published as a "reproducibility pack" on a platform like Hugging Face and GitHub.  
  1. **The Corpus:** The generated /pdf/ and /ground\_truth/ folders, along with the manifest.json.  
  2. **The Code:** The full GitHub repository containing all generation, normalization, and evaluation scripts.  
  3. **The Report:** A paper.pdf (this document) that formally describes the benchmark's design, taxonomy, schema, and metrics, justifying all design choices.  
  4. **Instructions:** A README.md that provides clear instructions on how to (a) re-run the corpus generation, (b) add a new parser adapter, and (c) re-run the full evaluation.

---

## **Phase 7: "Prompt Pack" for Coding Assistant**

This section provides a sample of concrete, actionable prompts that can be provided to a coding assistant to begin executing the backlog from Phase 6\.

* Prompt 1 (Ref: Task 1.2.4):  
  "Implement a Python function parse\_table(table: docx.table.Table) \-\> dict for the docx\_to\_canonical.py module. This function must parse a python-docx Table object and return a dictionary matching the table.structure part of our schema.json. It is critical that this function correctly identifies row\_span and col\_span for merged cells. You cannot simply iterate row.cells, as this misrepresents merged cells.27 You must inspect the underlying \_tc (table cell) elements and their vMerge (for vertical merges) and gridSpan (for horizontal merges) XML attributes.28 The function must also generate a structure.html string representation of the table for later TEDS evaluation.14"  
* Prompt 2 (Ref: Task 1.3.1):  
  "Implement a Python function get\_slide\_reading\_order(slide: pptx.slide.Slide) \-\> list for the pptx\_to\_canonical.py module. The default slide.shapes list is in z-order (stacking order), which is incorrect for reading order.45 Your function must iterate all shapes on the slide, filter for only those that have a text frame (shape.has\_text\_frame 46), and return a new list of these text-bearing shapes sorted by their vertical, then horizontal, position. The sort key should be (shape.top, shape.left).45 This sorted list will define the reading order."  
* Prompt 3 (Ref: Task 2.1):  
  "Create a Dockerfile that installs all dependencies for headless LibreOffice PDF conversion on an Alpine Linux base.65 This must include libreoffice-writer (for.docx) and libreoffice-impress (for.pptx), as well as all necessary font packages (e.g., ttf-freefont).66 Then, write a Python function convert\_to\_pdf(input\_path: str, output\_dir: str) that calls the soffice binary using subprocess.run.67 The command must include the \--headless, \--convert-to pdf, and \--outdir flags. Most importantly, it must include the "-env:UserInstallation=file:///tmp/lo\_profile" flag to prevent instance collisions and hangs.69"  
* Prompt 4 (Ref: Task 3.2.2):  
  "Write the normalization adapter normalize\_aws.py. This module must contain a function normalize\_aws\_to\_canonical(aws\_json: dict) \-\> dict that transforms the JSON output from an AWS Textract AnalyzeDocument call into our schema.json format. The function will need to iterate the list of Block objects 37 and map AWS BlockType values (e.g., LAYOUT\_HEADING, TABLE, LINE) to our canonical block\_type values (heading, table, paragraph). For TABLE blocks, it must parse the cell structure. For LINE blocks, it must implement logic to group contiguous lines into coherent paragraph blocks."  
* Prompt 5 (Ref: Task 3.3.4):  
  "Implement the 'Chunk Purity' metric in evaluation\_harness/metrics/chunking.py, as defined in our design (Section 5.2). The primary function calculate\_chunk\_purity(gt\_blocks: list, predicted\_blocks: list) \-\> dict must first align the two lists of blocks based on their normalized text content. Then, it must:  
  1. Calculate a 'Fragmentation' score: For each gt\_block, determine how many predicted\_blocks its text is split into.  
  2. Calculate a 'Pollution' score: For each predicted\_block, determine how many gt\_blocks it incorrectly merges text from.  
  3. Return a dictionary with {'fragmentation\_score':..., 'pollution\_score':..., 'chunk\_purity\_f1':...}. This metric is intended to directly measure a parser's suitability for RAG chunking.10"

#### **Works cited**

1. A Hybrid Approach for Document Layout Analysis in Document images \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2404.17888v2](https://arxiv.org/html/2404.17888v2)  
2. ibm-aur-nlp/PubTabNet \- GitHub, accessed November 18, 2025, [https://github.com/ibm-aur-nlp/PubTabNet](https://github.com/ibm-aur-nlp/PubTabNet)  
3. DocLayNet: A Large Human-Annotated Dataset for Document-Layout Segmentation, accessed November 18, 2025, [https://research.ibm.com/publications/doclaynet-a-large-human-annotated-dataset-for-document-layout-segmentation](https://research.ibm.com/publications/doclaynet-a-large-human-annotated-dataset-for-document-layout-segmentation)  
4. DocBank: A Benchmark Dataset for Document Layout Analysis \- GitHub, accessed November 18, 2025, [https://github.com/doc-analysis/DocBank](https://github.com/doc-analysis/DocBank)  
5. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- CVF Open Access, accessed November 18, 2025, [https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang\_OmniDocBench\_Benchmarking\_Diverse\_PDF\_Document\_Parsing\_with\_Comprehensive\_Annotations\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.pdf)  
6. The RAG Engineer's Guide to Document Parsing (with some head to head comparisons) : r/LLMDevs \- Reddit, accessed November 18, 2025, [https://www.reddit.com/r/LLMDevs/comments/1ef1abg/the\_rag\_engineers\_guide\_to\_document\_parsing\_with/](https://www.reddit.com/r/LLMDevs/comments/1ef1abg/the_rag_engineers_guide_to_document_parsing_with/)  
7. Best PDF Parser for RAG Apps: A Comprehensive Guide \- Nanonets, accessed November 18, 2025, [https://nanonets.com/blog/best-pdf-parser-for-rag-apps-a-comprehensive-guide/](https://nanonets.com/blog/best-pdf-parser-for-rag-apps-a-comprehensive-guide/)  
8. Multi-column layout extraction fails \- text flows incorrectly across columns despite table structure recognition enabled · Issue \#2067 · docling-project/docling \- GitHub, accessed November 18, 2025, [https://github.com/docling-project/docling/issues/2067](https://github.com/docling-project/docling/issues/2067)  
9. Extract Text From a Multi-Column Document Using PyMuPDF in Python | Artifex, accessed November 18, 2025, [https://artifex.com/blog/extract-text-from-a-multi-column-document-using-pymupdf-inpython](https://artifex.com/blog/extract-text-from-a-multi-column-document-using-pymupdf-inpython)  
10. Evaluating Chunking Strategies for Retrieval \- Chroma Research, accessed November 18, 2025, [https://research.trychroma.com/evaluating-chunking](https://research.trychroma.com/evaluating-chunking)  
11. Document Layout Analysis with Graph-based Methods \- Prometeia, accessed November 18, 2025, [https://prometeia.com/en/about-us/insights/article/document-layout-analysis-with-graphbased-methods-15929781](https://prometeia.com/en/about-us/insights/article/document-layout-analysis-with-graphbased-methods-15929781)  
12. Benchmarking PDF segmentation and parsing models \- Aryn, accessed November 18, 2025, [https://www.aryn.ai/post/benchmarking-pdf-segmentation-and-parsing-models](https://www.aryn.ai/post/benchmarking-pdf-segmentation-and-parsing-models)  
13. DocBank: A Benchmark Dataset for Document Layout Analysis \- Microsoft Research, accessed November 18, 2025, [https://www.microsoft.com/en-us/research/publication/docbank-a-benchmark-dataset-for-document-layout-analysis/](https://www.microsoft.com/en-us/research/publication/docbank-a-benchmark-dataset-for-document-layout-analysis/)  
14. SPRINT: Script-agnostic Structure Recognition in Tables \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2503.11932v1](https://arxiv.org/html/2503.11932v1)  
15. (PDF) Image-based table recognition: data, model, and evaluation \- ResearchGate, accessed November 18, 2025, [https://www.researchgate.net/publication/337531286\_Image-based\_table\_recognition\_data\_model\_and\_evaluation](https://www.researchgate.net/publication/337531286_Image-based_table_recognition_data_model_and_evaluation)  
16. Turn Complex Documents into Usable Data with VLM, NVIDIA NeMo Retriever Parse, accessed November 18, 2025, [https://developer.nvidia.com/blog/turn-complex-documents-into-usable-data-with-vlm-nvidia-nemo-retriever-parse/](https://developer.nvidia.com/blog/turn-complex-documents-into-usable-data-with-vlm-nvidia-nemo-retriever-parse/)  
17. \[PDF\] Image-based table recognition: data, model, and evaluation | Semantic Scholar, accessed November 18, 2025, [https://www.semanticscholar.org/paper/Image-based-table-recognition%3A-data%2C-model%2C-and-Zhong-Shafieibavani/99b2a05177c17dd86627863608ac45dc4cfe0446](https://www.semanticscholar.org/paper/Image-based-table-recognition%3A-data%2C-model%2C-and-Zhong-Shafieibavani/99b2a05177c17dd86627863608ac45dc4cfe0446)  
18. \[1911.10683\] Image-based table recognition: data, model, and evaluation \- arXiv, accessed November 18, 2025, [https://arxiv.org/abs/1911.10683](https://arxiv.org/abs/1911.10683)  
19. Image-based table recognition: data, model, and evaluation, accessed November 18, 2025, [https://www.ecva.net/papers/eccv\_2020/papers\_ECCV/papers/123660562.pdf](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123660562.pdf)  
20. opendatalab/OmniDocBench · Datasets at Hugging Face, accessed November 18, 2025, [https://huggingface.co/datasets/opendatalab/OmniDocBench](https://huggingface.co/datasets/opendatalab/OmniDocBench)  
21. opendatalab/OmniDocBench: \[CVPR 2025\] A Comprehensive Benchmark for Document Parsing and Evaluation \- GitHub, accessed November 18, 2025, [https://github.com/opendatalab/OmniDocBench](https://github.com/opendatalab/OmniDocBench)  
22. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2412.07626v1](https://arxiv.org/html/2412.07626v1)  
23. A Novel Paradigm for Model Evaluation: The Innovative Multi-source Document Parsing Evaluation Framework OmniDocBench \- 2077AI, accessed November 18, 2025, [https://www.2077ai.com/blog/OmniDocBench](https://www.2077ai.com/blog/OmniDocBench)  
24. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- ResearchGate, accessed November 18, 2025, [https://www.researchgate.net/publication/394650843\_OmniDocBench\_Benchmarking\_Diverse\_PDF\_Document\_Parsing\_with\_Comprehensive\_Annotations](https://www.researchgate.net/publication/394650843_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations)  
25. Working with Styles — python-docx 1.2.0 documentation, accessed November 18, 2025, [https://python-docx.readthedocs.io/en/latest/user/styles-using.html](https://python-docx.readthedocs.io/en/latest/user/styles-using.html)  
26. python \- Extracting headings' text from word doc \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/40388763/extracting-headings-text-from-word-doc](https://stackoverflow.com/questions/40388763/extracting-headings-text-from-word-doc)  
27. Python docx row.cells return a "merged" cell multiple times \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/48090922/python-docx-row-cells-return-a-merged-cell-multiple-times](https://stackoverflow.com/questions/48090922/python-docx-row-cells-return-a-merged-cell-multiple-times)  
28. How to detect merged cells? · Issue \#1312 · python-openxml/python-docx \- GitHub, accessed November 18, 2025, [https://github.com/python-openxml/python-docx/issues/1312](https://github.com/python-openxml/python-docx/issues/1312)  
29. python-docx detect enumerated list \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/51765750/python-docx-detect-enumerated-list](https://stackoverflow.com/questions/51765750/python-docx-detect-enumerated-list)  
30. Python Libraries to Extract Tables From PDF: A Comparison \- Unstract, accessed November 18, 2025, [https://unstract.com/blog/extract-tables-from-pdf-python/](https://unstract.com/blog/extract-tables-from-pdf-python/)  
31. Quickstart — Camelot 1.0.9 documentation \- Read the Docs, accessed November 18, 2025, [https://camelot-py.readthedocs.io/en/master/user/quickstart.html](https://camelot-py.readthedocs.io/en/master/user/quickstart.html)  
32. datalab-to/marker: Convert PDF to markdown \+ JSON quickly with high accuracy \- GitHub, accessed November 18, 2025, [https://github.com/datalab-to/marker](https://github.com/datalab-to/marker)  
33. Output File Format \- MinerU, accessed November 18, 2025, [https://opendatalab.github.io/MinerU/reference/output\_files/](https://opendatalab.github.io/MinerU/reference/output_files/)  
34. Pdf text extraction process : r/Rag \- Reddit, accessed November 18, 2025, [https://www.reddit.com/r/Rag/comments/1k7upmm/pdf\_text\_extraction\_process/](https://www.reddit.com/r/Rag/comments/1k7upmm/pdf_text_extraction_process/)  
35. docling-project/docling: Get your documents ready for gen AI \- GitHub, accessed November 18, 2025, [https://github.com/docling-project/docling](https://github.com/docling-project/docling)  
36. Best PDF Parser for RAG? : r/LangChain \- Reddit, accessed November 18, 2025, [https://www.reddit.com/r/LangChain/comments/1dzj5qx/best\_pdf\_parser\_for\_rag/](https://www.reddit.com/r/LangChain/comments/1dzj5qx/best_pdf_parser_for_rag/)  
37. Tables \- Amazon Textract \- AWS Documentation, accessed November 18, 2025, [https://docs.aws.amazon.com/textract/latest/dg/how-it-works-tables.html](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-tables.html)  
38. Textract Pricing Page \- Amazon AWS, accessed November 18, 2025, [https://aws.amazon.com/textract/pricing/](https://aws.amazon.com/textract/pricing/)  
39. A detailed breakdown of the Amazon Textract pricing \- Cloudtech, accessed November 18, 2025, [https://www.cloudtech.com/resources/aws-textract-pricing-usage-insights](https://www.cloudtech.com/resources/aws-textract-pricing-usage-insights)  
40. Sample processor output | Document AI \- Google Cloud Documentation, accessed November 18, 2025, [https://docs.cloud.google.com/document-ai/docs/output](https://docs.cloud.google.com/document-ai/docs/output)  
41. Document AI pricing \- Google Cloud, accessed November 18, 2025, [https://cloud.google.com/document-ai/pricing](https://cloud.google.com/document-ai/pricing)  
42. Document layout analysis \- Document Intelligence \- Azure AI services | Microsoft Learn, accessed November 18, 2025, [https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout?view=doc-intel-4.0.0)  
43. Document Models \- List Models \- REST API (Azure Azure AI Services) | Microsoft Learn, accessed November 18, 2025, [https://learn.microsoft.com/en-us/rest/api/aiservices/document-models/list-models?view=rest-aiservices-v4.0%20(2024-11-30)](https://learn.microsoft.com/en-us/rest/api/aiservices/document-models/list-models?view=rest-aiservices-v4.0+\(2024-11-30\))  
44. python-pptx Extract text from slide titles \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/43366360/python-pptx-extract-text-from-slide-titles](https://stackoverflow.com/questions/43366360/python-pptx-extract-text-from-slide-titles)  
45. How to extract text from powerpoint text boxes, in their order within the presentation using python-pptx. \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/51999656/how-to-extract-text-from-powerpoint-text-boxes-in-their-order-within-the-presen](https://stackoverflow.com/questions/51999656/how-to-extract-text-from-powerpoint-text-boxes-in-their-order-within-the-presen)  
46. Working with text — python-pptx 1.0.0 documentation \- Read the Docs, accessed November 18, 2025, [https://python-pptx.readthedocs.io/en/latest/user/text.html](https://python-pptx.readthedocs.io/en/latest/user/text.html)  
47. Extract speaker notes from PowerPoint to text \- Dries Buytaert, accessed November 18, 2025, [https://dri.es/extract-speaker-notes-from-powerpoint-to-text](https://dri.es/extract-speaker-notes-from-powerpoint-to-text)  
48. python \- Extract presenter notes from PPTx file (powerpoint) \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/63659972/extract-presenter-notes-from-pptx-file-powerpoint](https://stackoverflow.com/questions/63659972/extract-presenter-notes-from-pptx-file-powerpoint)  
49. Working with Tables — python-docx 1.2.0 documentation, accessed November 18, 2025, [https://python-docx.readthedocs.io/en/latest/user/tables.html](https://python-docx.readthedocs.io/en/latest/user/tables.html)  
50. A clique-based method for the edit distance between unordered trees and its application to analysis of glycan structures \- PMC \- PubMed Central, accessed November 18, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3044267/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3044267/)  
51. DocParser: Hierarchical Document Structure Parsing from Renderings \- AAAI Publications, accessed November 18, 2025, [https://ojs.aaai.org/index.php/AAAI/article/view/16558/16365](https://ojs.aaai.org/index.php/AAAI/article/view/16558/16365)  
52. Reading and writing Microsoft Word docx files with Python | Virantha Namal Ekanayake, accessed November 18, 2025, [https://virantha.com/2013/08/16/reading-and-writing-microsoft-word-docx-files-with-python/](https://virantha.com/2013/08/16/reading-and-writing-microsoft-word-docx-files-with-python/)  
53. how to read paragraphs AND tables? · Issue \#276 · python-openxml/python-docx \- GitHub, accessed November 18, 2025, [https://github.com/python-openxml/python-docx/issues/276](https://github.com/python-openxml/python-docx/issues/276)  
54. python-docx: iterate through paragraphs, tables and images while keeping order, accessed November 18, 2025, [https://stackoverflow.com/questions/52838399/python-docx-iterate-through-paragraphs-tables-and-images-while-keeping-order](https://stackoverflow.com/questions/52838399/python-docx-iterate-through-paragraphs-tables-and-images-while-keeping-order)  
55. Working with Notes Slides — python-pptx 1.0.0 documentation, accessed November 18, 2025, [https://python-pptx.readthedocs.io/en/latest/user/notes.html](https://python-pptx.readthedocs.io/en/latest/user/notes.html)  
56. Working with Titles and Heading \- Python docx Module \- GeeksforGeeks, accessed November 18, 2025, [https://www.geeksforgeeks.org/python/working-with-titles-and-heading-python-docx-module/](https://www.geeksforgeeks.org/python/working-with-titles-and-heading-python-docx-module/)  
57. Getting Started — python-pptx 1.0.0 documentation, accessed November 18, 2025, [https://python-pptx.readthedocs.io/en/latest/user/quickstart.html](https://python-pptx.readthedocs.io/en/latest/user/quickstart.html)  
58. Headless document conversion and printing using LibreOffice or Microsoft Office \- GitHub, accessed November 18, 2025, [https://github.com/scivision/office-headless](https://github.com/scivision/office-headless)  
59. Convert Office files to PDF with LibreOffice and Python | by Tarik Nazorek \- Medium, accessed November 18, 2025, [https://tariknazorek.medium.com/convert-office-files-to-pdf-with-libreoffice-and-python-a70052121c44](https://tariknazorek.medium.com/convert-office-files-to-pdf-with-libreoffice-and-python-a70052121c44)  
60. Converting doc/docx Format to PDF With Help of LibreOffice and LaTeX | Baeldung on Linux, accessed November 18, 2025, [https://www.baeldung.com/linux/latex-doc-docx-pdf-conversion](https://www.baeldung.com/linux/latex-doc-docx-pdf-conversion)  
61. Convert .doc files to pdf using python COM interface to Microsoft Word \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/6011115/convert-doc-files-to-pdf-using-python-com-interface-to-microsoft-word](https://stackoverflow.com/questions/6011115/convert-doc-files-to-pdf-using-python-com-interface-to-microsoft-word)  
62. How to Convert DOC, DOCX, PPT, and PPTX Files to PDF in Windows and Linux Using Python | by Aalam Info Solutions LLP | Medium, accessed November 18, 2025, [https://medium.com/@aalam-info-solutions-llp/how-to-convert-doc-docx-ppt-and-pptx-files-to-pdf-in-windows-and-linux-using-python-300b78e55a49](https://medium.com/@aalam-info-solutions-llp/how-to-convert-doc-docx-ppt-and-pptx-files-to-pdf-in-windows-and-linux-using-python-300b78e55a49)  
63. Convert Office DOCX, XLSX and PPTX to PDF without installing Office using Python \- Apryse, accessed November 18, 2025, [https://apryse.com/blog/ms-office-sdk/office-doc-to-pdf-conversion-in-browser-using-python-without-installing-office](https://apryse.com/blog/ms-office-sdk/office-doc-to-pdf-conversion-in-browser-using-python-without-installing-office)  
64. DOCX to PDF Conversion Python SDK \- Fast and Accurate \- ConvertAPI, accessed November 18, 2025, [https://www.convertapi.com/docx-to-pdf/python](https://www.convertapi.com/docx-to-pdf/python)  
65. Convert DOCX to PDF for Free: A Docker \+ LibreOffice Implementation Guide | by Aaryan Jha | Oct, 2025 | Medium, accessed November 18, 2025, [https://medium.com/@jha.aaryan/convert-docx-to-pdf-for-free-a-docker-libreoffice-implementation-guide-cca493831391](https://medium.com/@jha.aaryan/convert-docx-to-pdf-for-free-a-docker-libreoffice-implementation-guide-cca493831391)  
66. Debian: Minimum LibreOffice Packages to Convert docx Files to pdf in Headless Mode, accessed November 18, 2025, [https://unix.stackexchange.com/questions/700814/debian-minimum-libreoffice-packages-to-convert-docx-files-to-pdf-in-headless-mo](https://unix.stackexchange.com/questions/700814/debian-minimum-libreoffice-packages-to-convert-docx-files-to-pdf-in-headless-mo)  
67. From 12 Seconds to 1: Building a Lightning-Fast DOCX to PDF Converter with Flask and Docker \- Omri Beladev, accessed November 18, 2025, [https://omribeladev.medium.com/from-12-seconds-to-1-building-a-lightning-fast-docx-to-pdf-converter-with-flask-and-docker-8f9efb6edbb8](https://omribeladev.medium.com/from-12-seconds-to-1-building-a-lightning-fast-docx-to-pdf-converter-with-flask-and-docker-8f9efb6edbb8)  
68. PPTX to PDF conversion issue \- English \- Ask LibreOffice, accessed November 18, 2025, [https://ask.libreoffice.org/t/pptx-to-pdf-conversion-issue/33511](https://ask.libreoffice.org/t/pptx-to-pdf-conversion-issue/33511)  
69. Command \`libreoffice \--headless \--convert-to pdf test.docx \--outdir /pdf\` is not working \[closed\] \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/30349542/command-libreoffice-headless-convert-to-pdf-test-docx-outdir-pdf-is-not](https://stackoverflow.com/questions/30349542/command-libreoffice-headless-convert-to-pdf-test-docx-outdir-pdf-is-not)  
70. Use Document Intelligence client library or REST API \- Azure AI services | Microsoft Learn, accessed November 18, 2025, [https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/use-sdk-rest-api?view=doc-intel-4.0.0](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/use-sdk-rest-api?view=doc-intel-4.0.0)  
71. Pdf to Json export using pdfminer.six python \- Stack Overflow, accessed November 18, 2025, [https://stackoverflow.com/questions/70966246/pdf-to-json-export-using-pdfminer-six-python](https://stackoverflow.com/questions/70966246/pdf-to-json-export-using-pdfminer-six-python)  
72. Automatic Evaluation of Information Ordering: Kendall's Tau \- ACL Anthology, accessed November 18, 2025, [https://aclanthology.org/J06-4002.pdf](https://aclanthology.org/J06-4002.pdf)  
73. Automatic Evaluation of Information Ordering: Kendall's Tau \- ResearchGate, accessed November 18, 2025, [https://www.researchgate.net/publication/220355191\_Automatic\_Evaluation\_of\_Information\_Ordering\_Kendall's\_Tau](https://www.researchgate.net/publication/220355191_Automatic_Evaluation_of_Information_Ordering_Kendall's_Tau)  
74. \\readoc: A Unified Benchmark for Realistic Document Structured Extraction \- arXiv, accessed November 18, 2025, [https://arxiv.org/html/2409.05137v1](https://arxiv.org/html/2409.05137v1)  
75. Computing Text Similarity using Tree Edit Distance \- CIC IPN, accessed November 18, 2025, [https://www.cic.ipn.mx/\~sidorov/sngrams\_ted\_2015.pdf](https://www.cic.ipn.mx/~sidorov/sngrams_ted_2015.pdf)  
76. Evaluating Structural Similarity in XML Documents \- Database Research Group, accessed November 18, 2025, [http://dbgroup.eecs.umich.edu/timber/files/similarity.pdf](http://dbgroup.eecs.umich.edu/timber/files/similarity.pdf)  
77. Could you provide the corresponding "structure\_only" TEDS in the paper? · Issue \#22 · ibm-aur-nlp/PubTabNet \- GitHub, accessed November 18, 2025, [https://github.com/ibm-aur-nlp/PubTabNet/issues/22](https://github.com/ibm-aur-nlp/PubTabNet/issues/22)  
78. A complete guide to RAG evaluation: metrics, testing and best practices \- Evidently AI, accessed November 18, 2025, [https://www.evidentlyai.com/llm-guide/rag-evaluation](https://www.evidentlyai.com/llm-guide/rag-evaluation)
