# **PDF-to-Markdown Parsing: Evaluation**

## **1\. Introduction: The Structural Crisis in Unstructured Document Processing**

The transformation of unstructured documents—specifically the Portable Document Format (PDF)—into structured, semantic
representations like Markdown or HTML has evolved from a peripheral administrative task into a central bottleneck for
the deployment of enterprise Artificial Intelligence. As organizations rapidly adopt Retrieval-Augmented Generation (
RAG) architectures and Large Language Models (LLMs), the fidelity of the "context" fed into these systems determines the
upper bound of their intelligence. A parser that correctly identifies characters via Optical Character Recognition (OCR)
but fails to reconstruct the reading order of a multi-column financial report renders that document semantically
incoherent to an LLM. Consequently, the evaluation of PDF parsers has shifted from simple text accuracy measurements to
complex, multi-dimensional assessments of *logical structure recovery*.

This report establishes a definitive, state-of-the-art scoring framework for comparing PDF parsers against a canonical
Markdown ground truth. Unlike traditional OCR benchmarks that focus on character error rates, this framework emphasizes
**layout-aware evaluation**, business document complexity (tables, forms, nested lists), and the preservation of
semantic hierarchy. We synthesize methodologies from recent academic breakthroughs—including OmniDocBench, DocLayNet,
and the TEDS metric family—to propose a rigorous standard for the late 2025 landscape. The objective is to move beyond "
bag-of-words" similarity and measure whether a parser truly "understands" the document's visual language.

The urgency of this framework stems from the "PDF Trap": the format was designed for visual fixity, not logical
structure. A PDF file contains instructions on where to place ink on a page (e.g., "draw text at coordinates x,y"), but
it rarely contains explicit information about whether that text is a header, a footnote, or a cell in a table.
Reconstructing this lost structure is an inverse problem of high complexity. Business documents exacerbate this with
dense information layouts, such as annual reports where a single page may contain a three-column article, a spanning
data table, and a floating figure caption. A parser's failure to accurately segment these regions—a concept known as
layout segmentation—catastrophically degrades downstream tasks. For instance, if a parser merges a sidebar into the main
text body, it introduces hallucinatory adjacency, causing an RAG system to infer relationships between facts that are
actually distinct.1

This report is structured to guide technical decision-makers through the taxonomy of evaluation dimensions, the specific
mathematical definitions of advanced metrics, and the practical implementation of a scoring pipeline. We define a
composite "DocParse-Score" that balances strict deterministic evaluation (layout geometry and graph topology) with
semantic flexibility, ensuring that parsers are penalized for functional errors (like breaking a table) but not for
trivial stylistic choices.

## **2\. Taxonomy of Evaluation Dimensions**

To rigorously evaluate a parser, we must deconstruct the parsing task into its constituent challenges. A "good" parse is
not a monolith; it is the successful execution of several distinct sub-tasks: text recognition, layout analysis, table
extraction, and logical serialization. We define a taxonomy of six primary dimensions that must be independently
measured to diagnose parser performance accurately.

### **2.1. Text Content Accuracy**

At the foundational level, a parser must accurately transcribe the document's alphanumeric content. While modern OCR
engines have achieved high accuracy on clean documents, business documents often present challenges such as varying
fonts, embedded watermarks, and complex encoding (e.g., ligatures).

* **Per-span Text Correctness:** This dimension evaluates the fidelity of text extraction at the finest
  granularity—lines or small text runs. It detects character-level hallucinations, misspellings, and encoding failures.
  For example, extracting financial figures requires absolute precision; mistaking a "3" for an "8" in a balance sheet
  is a critical failure, whereas a typo in a prose paragraph may be recoverable.
* **Per-block Text Correctness:** Business documents are organized into logical blocks (paragraphs, headers). Evaluating
  text at the block level assesses the parser's ability to group related sentences together without merging unrelated
  content (under-segmentation) or fracturing single thoughts (over-segmentation). This distinction is vital because LLMs
  process text in chunks; a fractured sentence broken across two chunks may lose its semantic meaning.4

### **2.2. Layout Segmentation and Block Classification**

This dimension evaluates the parser's "computer vision" capabilities—its ability to perceive the document as a set of
distinct functional regions rather than a continuous stream of pixels.

* **Detection and Classification:** The parser must identify the geometric boundaries (bounding boxes) of semantic
  elements and assign them correct labels. The critical categories for business contexts include:
    * **Titles and Headings:** These are the skeleton of the document. Correct identification is essential for
      generating Markdown hierarchy (\#, \#\#, etc.), which RAG systems use for chunking and indexing.
    * **Paragraphs:** The primary containers of prose.
    * **Tables:** Tables are distinct from prose and require specialized structural handling. A parser that treats a
      table as a series of short paragraphs destroys the row-column relationships.
    * **Lists:** Ordered and unordered lists carry significant semantic weight in legal and technical documents. The
      parser must distinguish between a list bullet and a random punctuation mark.
    * **Figures and Captions:** Identifying images and, crucially, their associated descriptive text.
    * **Artifacts:** Headers, footers, and page numbers. A sophisticated parser should identify these but optionally
      exclude them from the final Markdown to preserve the narrative flow across page boundaries.5

### **2.3. Reading Order and Linearization**

One of the most challenging aspects of PDF parsing is "linearization"—converting the 2D layout into a 1D sequence of
characters. In multi-column layouts, sidebars, and complex forms, the linear sequence of text in the PDF's internal
storage often does not match the logical reading order.

* **Sequence Reconstruction:** This dimension measures whether the parser serializes the text blocks in the logically
  correct order. Failure here results in "text salad," where a sentence jumping across columns is interrupted by
  unrelated content from a sidebar or footer. This destroys the context window for LLMs, as the model loses the thread
  of the argument. Metrics here must penalize global reordering (e.g., reading column 2 before column 1\) more heavily
  than local reordering (e.g., swapping two items in an unordered list).3

### **2.4. Table Recognition and Structure**

Tables are high-density information structures common in financial statements and scientific reports. Evaluating them
requires a three-layered approach, as a table can be partially correct in deceptive ways.

* **Detection:** Simply finding where the table is located on the page.
* **Structure Reconstruction:** Correctly identifying the grid topology—rows, columns, and, crucially, row/column
  spans (merged cells). A missing column span can shift all subsequent data, invalidating the entire table.
* **Cell Content:** Ensuring the text within each cell is correct and assigned to the right coordinates. A parser might
  correctly identify a 3x3 grid but place the header text in the data row, which is a semantic failure.1

### **2.5. Hierarchical and Logical Structure**

Markdown is inherently hierarchical. This dimension assesses how well the parser infers the logical tree of the document
from visual cues (font size, indentation, bolding).

* **Nesting and Levels:** Correctly identifying that a sub-section belongs to a parent section (e.g., converting a
  bolded line to \#\#\# vs \#\#). This structure allows downstream applications to understand the scope of a topic.
* **List Handling:** distinguishing between flat lists and nested lists. In legal contracts, the difference between "
  1.a" and "2" determines the scope of a clause.10

### **2.6. Cross-Element Relations and Semantic Linking**

High-quality business parsers must go beyond identifying isolated blocks; they must identify the relationships between
them.

* **Linkage:** Associating captions with their respective figures or tables. A caption "Figure 1: Q3 Revenue" placed
  below a chart must be semantically linked to that chart, not treated as a dangling paragraph.
* **Footnotes:** Linking footnote markers in the text body (e.g., \`\`) to the footnote text at the bottom of the page.
* **Key-Value Pairs:** In forms (e.g., invoices), associating a label ("Total:") with its value ("$500"). This is often
  treated as a separate task (Key Information Extraction) but is increasingly integrated into general parsing.11

| Evaluation Dimension    | Data Input (Parser)       | Ground Truth Data         | Criticality for RAG       |
|:------------------------|:--------------------------|:--------------------------|:--------------------------|
| **Text Accuracy**       | UTF-8 String              | UTF-8 String              | High (Search/Retrieval)   |
| **Layout Segmentation** | Bounding Boxes (JSON)     | Bounding Boxes (JSON)     | High (Context Separation) |
| **Reading Order**       | Sequence ID / Linear Text | Ordered List of Block IDs | Critical (Coherence)      |
| **Table Fidelity**      | HTML/Markdown Table       | HTML/Markdown Table       | Critical (Data Integrity) |
| **Hierarchy**           | Markdown AST / Headers    | Markdown AST              | Medium (Indexing)         |
| **Semantic Linking**    | Key-Value JSON / Links    | Relation Graph            | High (Fact Association)   |

## **3\. Survey of Existing Metrics and Protocols**

Having defined *what* to measure, we now examine *how* to measure it. The field of Document Layout Analysis (DLA) and
parsing has evolved significantly, moving from simple OCR accuracy to holistic structural evaluation. This section
surveys the metrics currently deployed in leading benchmarks like OmniDocBench, DocLayNet, and PubTabNet, and adapts
them for our proposed framework.

### **3.1. Layout Segmentation Metrics**

The detection of document elements (paragraphs, tables, images) is functionally an object detection task. Therefore, the
primary metrics are derived from computer vision standards, specifically those used in the COCO and VOC competitions.

#### **3.1.1. Intersection over Union (IoU) and mAP**

The fundamental unit of measurement for layout accuracy is Intersection over Union (IoU). For a predicted bounding
box $B\_p$ and a ground truth box $B\_{gt}$, IoU is defined as:

$$IoU \= \\frac{Area(B\_p \\cap B\_{gt})}{Area(B\_p \\cup B\_{gt})}$$

Benchmarks like DocLayNet use Mean Average Precision (mAP) at various IoU thresholds (typically 0.50 to 0.95). This
metric aggregates precision across different classes (e.g., Header, Paragraph, Table) and strictness levels. A parser
achieves a high mAP if it consistently draws boxes that tightly wrap the correct content.13

* **Strengths:** Standardized, widely understood, and effective for measuring localization.
* **Weaknesses:** It is "text-agnostic." A box that is slightly too small might clip the first letter of every line,
  rendering the text useless, yet still have a high IoU (e.g., 0.90). Conversely, a box that is slightly too large (
  including whitespace) has a lower IoU but captures all text perfectly. Thus, mAP is necessary but insufficient for
  parsing evaluation.4

#### **3.1.2. Document Layout Error Rate (DLER)**

To address the limitations of mAP, recent research has introduced the **Document Layout Error Rate (DLER)**. This metric
is specifically designed to penalize segmentation errors that affect downstream text recognition and understanding: *
*over-segmentation** and **under-segmentation**.

* **Under-segmentation ($S\_{under}$):** Occurs when a parser merges two distinct ground truth regions (e.g., two
  paragraphs) into a single block. This is generally less damaging, as the text remains sequential, but it loses
  structural granularity.
* **Over-segmentation ($S\_{over}$):** Occurs when a parser splits a single ground truth region into multiple blocks.
  This is considered a severe error because the reading order algorithm might subsequently scatter these fragments,
  destroying the sentence structure.
* Calculation: DLER aggregates these errors, often weighting over-segmentation ($w\_{over}$) more heavily than
  under-segmentation ($w\_{under}$) to reflect their impact on utility.

  $$DLER \= \\frac{w\_{over} \\cdot S\_{over} \+ w\_{under} \\cdot S\_{under} \+ w\_{miss} \\cdot S\_{miss}}{N\_{total\\\_gt}}$$

  This metric provides a "granular assessment of segmentation quality," particularly at region boundaries, and is
  superior for evaluating pipelines intended for scholarly editions or high-fidelity archives.4

### **3.2. Reading Order Metrics**

Evaluating reading order is complex because there is often no single "correct" order for disjoint elements (e.g., a
sidebar vs. the main text). However, the local order within a flow is strict.

#### **3.2.1. Normalized Edit Distance (NED) on Text Sequence**

The simplest approach, used by benchmarks like **OmniDocBench** and **ReadingBank**, is to concatenate all text blocks
in the predicted order into a single string and compare it to the ground truth string using Levenshtein distance.

* **Metric:** The Normalized Edit Distance (NED) is calculated
  as $1 \- \\frac{EditDistance(S\_{pred}, S\_{gt})}{\\max(|S\_{pred}|, |S\_{gt}|)}$.
* **Analysis:** This metric provides a holistic view of "text salad." If a parser reads column 1 then column 2 (
  correct), the NED is low. If it reads line 1 of col 1, then line 1 of col 2 (incorrect), the NED is massive. However,
  it is computationally expensive for very long documents and can be overly sensitive to minor OCR errors that are
  actually layout-neutral.5

#### **3.2.2. Average Relative Distance (ARD) and Pairwise Ordering**

To mitigate the "all-or-nothing" nature of string edit distance, the **Average Relative Distance (ARD)** and **Pairwise
Ordering Accuracy** metrics focus on the relative positions of blocks.

* **Pairwise Ordering:** This metric identifies all unique pairs of text blocks $(A, B)$ in the ground truth where $A$
  comes before $B$. It then checks if this relationship holds in the predicted output.
* Formula:

  $$Accuracy \= \\frac{\\sum\_{i\<j} \\mathbb{I}(pos(b\_i) \< pos(b\_j))}{N(N-1)/2}$$
* **Significance:** This approach is robust. If a parser correctly orders a 10-page document but moves the very last
  paragraph to the first page, sequence-based edit distance might indicate a catastrophic failure (0% match) because the
  strings are offset. Pairwise accuracy would only penalize the pairs involving that one displaced paragraph, resulting
  in a score (e.g., 98%) that accurately reflects the parser's general competence. This is critical for "legal review"
  scenarios where finding specific clauses is more important than perfect global flow.16

### **3.3. Table Evaluation Metrics**

Tables represent the most significant challenge in PDF parsing due to their diverse visual styles (bordered, borderless,
colored backgrounds).

#### **3.3.1. TEDS (Tree-Edit-Distance-based Similarity)**

The industry standard, introduced with the **PubTabNet** dataset, is **TEDS**. This metric acknowledges that a table is
a tree structure (Table $\\rightarrow$ Rows $\\rightarrow$ Cells $\\rightarrow$ Content).

* **Methodology:** It converts both the predicted and ground truth tables into HTML-like tree structures. It then
  calculates the tree edit distance—the minimum number of node insertions, deletions, and renames required to transform
  one tree into the other.
* Formula:

  $$TEDS(T\_a, T\_b) \= 1 \- \\frac{EditDist(T\_a, T\_b)}{\\max(|T\_a|, |T\_b|)}$$
* **Variants:** TEDS often includes a threshold for cell content similarity (e.g., using BLEU or LevDist for cell text).
  If the structural distance is zero (perfect grid) but the text is wrong, TEDS penalizes the score based on the text
  error. This holistic scoring makes it the gold standard for tabular data.9

#### **3.3.2. Markdown TEDS**

Recent research in financial document processing has adapted TEDS specifically for **Markdown** outputs. Since Markdown
tables are simpler than HTML (often lacking support for complex row/column spans or nested headers), **Markdown TEDS**
focuses on the fidelity of the serialized Markdown table.

* **Algorithm:** It parses the Markdown into a simplified tree (Header Row vs. Body Rows). Crucially, it includes
  preprocessing steps like "flattening" multi-level headers (concatenating stacked headers into a single line) to align
  with Markdown's flat table limitations. This ensures that parsers are not unfairly penalized for Markdown's inherent
  format limitations when converting complex PDF tables.8

### **3.4. Structure-Aware Document Similarity**

Moving beyond individual components, we must evaluate the document as a whole hierarchy.

#### **3.4.1. Tree Edit Distance on Markdown AST**

A Markdown document is effectively an Abstract Syntax Tree (AST). By using parsers like markdown-it or commonmark, we
can generate this tree (Root $\\rightarrow$ Section $\\rightarrow$ Subsection $\\rightarrow$ Paragraph).

* **Metric:** Calculating the Tree Edit Distance (TED) between the Predicted AST and the Ground Truth AST evaluates
  structural hallucinations. For example, if a parser mistakenly converts a "List" into a "Table," the AST distance will
  be high, capturing a structural failure that simple text overlap metrics might miss. This metric is particularly
  sensitive to hierarchy errors, such as flattening nested sections.22

### **3.5. LLM-Based Semantic Evaluation ("LLM-as-a-Judge")**

While deterministic metrics are reproducible, they often lack nuance. An LLM-as-a-judge approach uses a powerful model (
like GPT-4o) to evaluate the *perceptual* quality of the parse.

* **Methodology:** The LLM is provided with the Ground Truth and the Predicted Markdown (or the original PDF image and
  the prediction) and asked to score the alignment on a Likert scale (1-5) based on specific criteria: Layout
  Correctness, Text Fidelity, and Table Readability.
* **Constraint:** To ensure reliability, this method uses "pairwise comparison" (asking the LLM which of two parses is
  better) or "criteria-based grading" (asking the LLM to verify specific facts). Research indicates that LLM judges
  correlate strongly with human evaluation for layout correctness and are far cheaper than manual review.25

## **4\. Analysis of Major Benchmarks**

Understanding the datasets used to train and test current models is crucial for interpreting metric values.

### **4.1. OmniDocBench**

**OmniDocBench** represents the current state-of-the-art for comprehensive document parsing evaluation.

* **Scale:** 1,355 PDF pages covering 9 types (academic, financial, notes, etc.).
* **Annotations:** Highly detailed, including 15 block-level categories (titles, paragraphs, captions) and 4 span-level
  categories (inline formulas).
* **Unique Feature:** It specifically annotates **Reading Order**, allowing for the rigorous sequence evaluations
  described above. It employs an "Adjacency Search Match" algorithm to robustly align ground truth paragraphs with
  predicted paragraphs, mitigating the impact of minor segmentation differences.1

### **4.2. DocLayNet**

**DocLayNet** focuses heavily on the visual layout segmentation aspect.

* **Scale:** 80k+ pages.
* **Focus:** Human-annotated bounding boxes for 11 classes.
* **Metrics:** Primary metric is mAP @ IoU 0.50:0.95.
* **Relevance:** This is the benchmark for checking if a parser can "see" the document structure correctly. A parser
  that scores low on DocLayNet will likely fail to group text correctly for Markdown conversion.13

### **4.3. PubTabNet**

**PubTabNet** is the definitive dataset for table recognition.

* **Focus:** 568k images of tables matched with HTML representations.
* **Metrics:** It introduced TEDS.
* **Relevance:** Any parser claiming table extraction capabilities must be benchmarked against PubTabNet or a similar
  TEDS-based standard. It enforces the requirement that tables are structured data, not just text.9

## **5\. Proposed Evaluation Framework: The "DocParse-Score"**

Based on the taxonomy and survey above, we propose a unified scoring framework designed for business-critical PDF
parsing. This framework, the **DocParse-Score**, is a composite metric that penalizes functional failures while allowing
for harmless stylistic variations.

### **5.1. Alignment and Normalization Strategy**

Evaluation is impossible without accurate alignment. We recommend a rigorous pre-processing pipeline:

1. **Canonicalization:** Both the Ground Truth (GT) and Prediction (Pred) Markdown are normalized. This involves:
    * Standardizing list bullets (e.g., converting \* to \-).
    * Collapsing multiple newlines to a single newline (unless meaningful for layout).
    * Removing "ignored" artifacts like page numbers or running headers.5
2. **Anchor-Based Alignment:** Instead of simple line-by-line matching, we align the document based on "anchors"—unique,
   high-confidence text strings (like Section Headers or Table Titles). The content between anchors is then compared.

### **5.2. Composite Metric Suite**

The **DocParse-Score** is calculated as a weighted average of four components, tailored to typical RAG requirements:

#### **Component A: Structural Fidelity (30%)**

* **Metric:** **Tree Edit Distance (TED)** on the Markdown AST.
* **Rationale:** This measures the correctness of the document hierarchy. Did the parser identify the sections, lists,
  and code blocks correctly? Structural errors (e.g., flattening a nested list) are heavily penalized as they destroy
  the semantic relationships needed for intelligent chunking.
* **Implementation:** Python libraries like apted or zss are used to compute the edit distance between the ASTs
  generated by markdown-it-py.

#### **Component B: Table Integrity (25%)**

* **Metric:** **Markdown TEDS**.
* **Rationale:** Tables are high-value, information-dense regions. A parser must recover the grid structure.
* **Implementation:** Tables are extracted and converted to a canonical HTML intermediate representation. The TEDS
  metric is calculated, with a penalty weight of 1.0 for structural errors (missing row) and 0.5 for cell content
  errors. Missing tables receive a score of 0\.

#### **Component C: Text Accuracy (25%)**

* **Metric:** **Hybrid Text Score (1 \- CER) & BLEU**.
* **Rationale:** We need to ensure the text is readable (CER) and that the words are present (BLEU).
* **Implementation:** Character Error Rate (CER) checks for OCR hallucinations. BLEU (or chrF) checks for n-gram
  overlap, ensuring that even if the text is slightly reordered within a block, the content is preserved.

#### **Component D: Reading Order & Coherence (20%)**

* **Metric:** **Pairwise Ordering Accuracy**.
* **Rationale:** This ensures that the linear stream of text fed to the LLM makes logical sense.
* **Implementation:** All text blocks are indexed. We compute the percentage of concordant pairs ($Prediction\_{order}$
  matches $GT\_{order}$) across the document. This is robust against minor, irrelevant reorderings but strictly
  penalizes cross-column mixing.

### **5.3. Aggregation: The Pareto-Front Leaderboard**

A single score obscures trade-offs. We recommend reporting a **Pareto-Front** visualization:

* **Axis X:** **Speed** (Pages per Second).
* **Axis Y:** **DocParse-Score**.
* **Axis Z (Color):** **Table Score**.

This allows users to choose a parser based on their specific bottleneck. A financial analyst might choose a slower
parser with a high "Table Score" (Axis Z), while a search engine indexer might prioritize "Speed" (Axis X) with
acceptable Text Accuracy.

## **6\. Implementation of LLM-as-a-Judge**

To complement the deterministic metrics, we incorporate an **LLM-as-a-Judge** protocol. This serves as a semantic "
sanity check" to catch errors that metrics might miss (e.g., a table that is structurally perfect but contains gibberish
text due to encoding errors).

### **6.1. Prompt Engineering**

We utilize a specific prompt template designed to elicit nuanced feedback 27:

"You are an expert document auditor. Compare the Ground Truth Markdown (A) with the Predicted Markdown (B). Rate the
Prediction on a scale of 1-5 for the following dimensions:

1. **Layout Correctness:** Does the hierarchy (headers, lists) match?
2. **Table Fidelity:** Are all rows/columns preserved and aligned?
3. **Text Integrity:** Is the text accurate and free of artifacts?
4. Reading Order: Does the text flow logically?  
   Provide a brief rationale for any score below 5."

### **6.2. Scoring Protocol**

To reduce variance, we employ **Batch Evaluation**:

1. Sample 50 representative pages from the test set (covering diverse layouts).
2. Run the LLM Judge on these 50 pages.
3. Average the Likert scores.
4. **Correlation Check:** If the LLM score diverges significantly from the DocParse-Score (e.g., High Metric / Low LLM),
   it indicates "Metric Hacking" (the parser is optimizing for the metric but producing poor output). If Low Metric /
   High LLM, it suggests the Ground Truth might be flawed or the metric is too strict.26

## **7\. Algorithmic and Technical Implementation Details**

This section provides the specific technical details required to build the evaluation pipeline.

### **7.1. Tree Edit Distance for Markdown**

To implement Component A, we treat the Markdown document as a tree.

* **Library:** markdown-it-py generates a token stream. We convert this stream into a nested dictionary (JSON)
  representing the DOM.
* **Distance Algorithm:** The **APTED (All Path Tree Edit Distance)** algorithm is the current state-of-the-art for
  exact tree edit distance. It is computationally efficient enough for document-level trees.
    * *Cost Model:* Node Rename cost \= 1, Insert/Delete cost \= 1\.
    * *Normalization:* The raw distance is divided by the number of nodes in the larger tree to produce a normalized
      similarity score.22

### **7.2. Adjacency Search Match for Reading Order**

To implement the robust alignment required for Component D, we adopt the **Adjacency Search Match** algorithm from
OmniDocBench.

* **Step 1:** Calculate the normalized edit distance between every Predicted Block and every Ground Truth Block.
* **Step 2:** Create a similarity matrix.
* **Step 3:** Use a greedy matching strategy or the Hungarian algorithm to pair blocks based on highest similarity.
* **Step 4:** If a GT block matches multiple Pred blocks (over-segmentation), merge the Pred blocks and recalculate.
  This dynamic merging ensures that the reading order evaluation is not penalized by simple segmentation differences.5

### **7.3. Flattening Multi-Level Headers**

For Component B (Markdown TEDS), handling complex tables in Markdown is a specific challenge.

* **Problem:** Markdown tables do not support rowspan or colspan.
* **Solution:** The evaluation pipeline "flattens" the Ground Truth HTML tables before comparison.
    * *Algorithm:* Concatenate the text of all cells in a vertical span into the top cell. Concatenate horizontal spans
      into the left-most cell.
    * *Result:* This reduces the complex table to a simple grid, which matches the representational capacity of
      Markdown. We then compare the Predicted Markdown table (parsed to a grid) against this Flattened Ground Truth grid
      using the TEDS metric.8

## **8\. Strategic Implications and Conclusion**

The evaluation of PDF parsers has matured from a niche OCR task to a foundational pillar of the Generative AI stack. The
framework presented here—the **DocParse-Score**—reflects the complexity of this new reality. By integrating layout-aware
metrics like DLER, structure-aware metrics like TEDS, and semantic validation via LLM-as-a-judge, we provide a roadmap
for identifying parsers that do not just "read" documents, but "comprehend" their structure.

For business stakeholders, the implications are clear: **do not rely on simple text accuracy.** A parser with 99% text
accuracy but poor reading order (low Pairwise Accuracy) will poison your RAG vector database with incoherent chunks. A
parser that fails TEDS on financial tables will hallucinate numbers in your analytical reports. By adopting this
multi-dimensional leaderboard approach, organizations can select parsing technologies that provide the robust structural
data foundation required for reliable, high-performance AI applications.

The future of parsing lies in **Vision-Language Models (VLMs)** that perform end-to-end parsing (pixels to Markdown)
without explicit bounding box detection. As these models mature in late 2025, this evaluation framework—agnostic to the
internal mechanism but strict on the structural output—will remain the definitive standard for assessing their utility.

## **9\. References to Methodologies**

* **OmniDocBench & Adjacency Match:** 1
* **DocLayNet & mAP:** 13
* **DLER (Layout Error Rate):** 4
* **TEDS & Table Analysis:** 8
* **Reading Order & Pairwise Accuracy:** 3
* **LLM-as-a-judge Protocols:** 25
* **Tree Edit Distance:** 22

#### **Works cited**

1. opendatalab/OmniDocBench: \[CVPR 2025\] A Comprehensive Benchmark for Document Parsing and Evaluation \- GitHub,
   accessed November 20,
   2025, [https://github.com/opendatalab/OmniDocBench](https://github.com/opendatalab/OmniDocBench)
2. \[2412.07626\] OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- arXiv,
   accessed November 20, 2025, [https://arxiv.org/abs/2412.07626](https://arxiv.org/abs/2412.07626)
3. Modeling Layout Reading Order as Ordering Relations for Visually-rich Document Understanding \- ACL Anthology,
   accessed November 20,
   2025, [https://aclanthology.org/2024.emnlp-main.540.pdf](https://aclanthology.org/2024.emnlp-main.540.pdf)
4. Evaluation Metrics For Document Layout Analysis | PDF | Image Segmentation \- Scribd, accessed November 20,
   2025, [https://www.scribd.com/document/857963829/Evaluation-Metrics-for-Document-Layout-Analysis](https://www.scribd.com/document/857963829/Evaluation-Metrics-for-Document-Layout-Analysis)
5. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- arXiv, accessed November
   20, 2025, [https://arxiv.org/html/2412.07626v1](https://arxiv.org/html/2412.07626v1)
6. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- arXiv, accessed November
   20, 2025, [https://arxiv.org/html/2412.07626v2](https://arxiv.org/html/2412.07626v2)
7. \[2108.11591\] LayoutReader: Pre-training of Text and Layout for Reading Order Detection \- ar5iv, accessed November
   20, 2025, [https://ar5iv.labs.arxiv.org/html/2108.11591](https://ar5iv.labs.arxiv.org/html/2108.11591)
8. \[2508.05669\] Fine-Tuning Vision-Language Models for Markdown Conversion of Financial Tables in Malaysian Audited
   Financial Reports \- arXiv, accessed November 20,
   2025, [https://arxiv.org/abs/2508.05669](https://arxiv.org/abs/2508.05669)
9. Image-Based Table Recognition: Data, Model, and Evaluation | Request PDF, accessed November 20,
   2025, [https://www.researchgate.net/publication/346843544\_Image-Based\_Table\_Recognition\_Data\_Model\_and\_Evaluation](https://www.researchgate.net/publication/346843544_Image-Based_Table_Recognition_Data_Model_and_Evaluation)
10. Benchmarking the Most Reliable Document Parsing API \- Tensorlake, accessed November 20,
    2025, [https://www.tensorlake.ai/blog/benchmarks](https://www.tensorlake.ai/blog/benchmarks)
11. Benchmarking Extraction of Structured Data from Templatized Documents \- UC Berkeley EECS, accessed November 20,
    2025, [https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-77.pdf](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-77.pdf)
12. Graph-based Document Structure Analysis \- arXiv, accessed November 20,
    2025, [https://arxiv.org/html/2502.02501v1](https://arxiv.org/html/2502.02501v1)
13. Task and Resources \- ICDAR 2023 DocLayNet competition, accessed November 20,
    2025, [https://ds4sd.github.io/icdar23-doclaynet/task/](https://ds4sd.github.io/icdar23-doclaynet/task/)
14. \[2206.01062\] DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis, accessed November 20,
    2025, [https://arxiv.org/abs/2206.01062](https://arxiv.org/abs/2206.01062)
15. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- CVF Open Access, accessed
    November 20,
    2025, [https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang\_OmniDocBench\_Benchmarking\_Diverse\_PDF\_Document\_Parsing\_with\_Comprehensive\_Annotations\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.pdf)
16. ACCSAMS: Automatic Conversion of Exam Documents to Accessible Learning Material for Blind and Visually Impaired \-
    arXiv, accessed November 20, 2025, [https://arxiv.org/html/2405.19124v1](https://arxiv.org/html/2405.19124v1)
17. SCORE: A Semantic Evaluation Framework for Generative Document Parsing \- arXiv, accessed November 20,
    2025, [https://arxiv.org/html/2509.19345v1](https://arxiv.org/html/2509.19345v1)
18. On the utility of enhancing BERT syntactic bias with Token Reordering Pretraining \- ACL Anthology, accessed
    November 20, 2025, [https://aclanthology.org/2023.conll-1.12.pdf](https://aclanthology.org/2023.conll-1.12.pdf)
19. README.md · upstage/dp-bench at ab4b07b149a974f94dce50857edfcc693dd86d66 \- Hugging Face, accessed November 20,
    2025, [https://huggingface.co/datasets/upstage/dp-bench/blob/ab4b07b149a974f94dce50857edfcc693dd86d66/README.md](https://huggingface.co/datasets/upstage/dp-bench/blob/ab4b07b149a974f94dce50857edfcc693dd86d66/README.md)
20. Fine-Tuning Vision-Language Models for Markdown Conversion of Financial Tables in Malaysian Audited Financial
    Reports \- ChatPaper, accessed November 20,
    2025, [https://chatpaper.com/paper/178866](https://chatpaper.com/paper/178866)
21. Fine-Tuning Vision-Language Models for Markdown Conversion of Financial Tables in Malaysian Audited Financial
    Reports \- arXiv, accessed November 20, 2025, [https://arxiv.org/pdf/2508.05669](https://arxiv.org/pdf/2508.05669)
22. actapia/dnted: Python library for computing a normalized tree edit distance metric \- GitHub, accessed November 20,
    2025, [https://github.com/actapia/dnted](https://github.com/actapia/dnted)
23. MDEval: Evaluating and Enhancing Markdown Awareness in Large Language Models, accessed November 20,
    2025, [https://arxiv.org/html/2501.15000v1](https://arxiv.org/html/2501.15000v1)
24. \[Literature Review\] Revisiting Code Similarity Evaluation with Abstract Syntax Tree Edit Distance \- Moonlight,
    accessed November 20,
    2025, [https://www.themoonlight.io/en/review/revisiting-code-similarity-evaluation-with-abstract-syntax-tree-edit-distance](https://www.themoonlight.io/en/review/revisiting-code-similarity-evaluation-with-abstract-syntax-tree-edit-distance)
25. LLM-as-a-judge: a complete guide to using LLMs for evaluations \- Evidently AI, accessed November 20,
    2025, [https://www.evidentlyai.com/llm-guide/llm-as-a-judge](https://www.evidentlyai.com/llm-guide/llm-as-a-judge)
26. ReLook: Vision-Grounded RL with a Multimodal LLM Critic for Agentic Web Coding \- arXiv, accessed November 20,
    2025, [https://arxiv.org/pdf/2510.11498?](https://arxiv.org/pdf/2510.11498)
27. METASPATIAL: REINFORCING 3D SPATIAL REASON- ING IN VLMS FOR THE METAVERSE \- OpenReview, accessed November 20,
    2025, [https://openreview.net/pdf/19a3edc5189283d1bbf9666e6642712221aea9db.pdf](https://openreview.net/pdf/19a3edc5189283d1bbf9666e6642712221aea9db.pdf)
28. SciDoc2Diagrammer-MAF: Towards Generation of Scientific Diagrams from Documents guided by Multi-Aspect Feedback
    Refinement \- ACL Anthology, accessed November 20,
    2025, [https://aclanthology.org/2024.findings-emnlp.780.pdf](https://aclanthology.org/2024.findings-emnlp.780.pdf)
29. DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis \- GitHub, accessed November 20,
    2025, [https://github.com/DS4SD/DocLayNet](https://github.com/DS4SD/DocLayNet)
