# **A Survey of Benchmarks and Evaluation Frameworks for PDF Document Structure Recovery**

## **Executive Summary**

This report provides a comprehensive analysis of benchmark systems and evaluation frameworks for PDF parsing, with a
specific focus on document structure recovery. The transformation of unstructured or semi-structured PDF documents into
structured, machine-readable data presents a complex, multi-stage challenge. The evaluation of systems designed for this
task is similarly stratified, moving from foundational object detection to complex hierarchical understanding.

This analysis organizes the landscape of evaluation tools into a conceptual "Evaluation Stack," which models the
increasing complexity of parsing tasks. This stack includes: (1) Physical Layout Segmentation (detecting physical
blocks), (2) Logical Role Labeling (assigning semantic labels), (3) Relational and Hierarchical Recovery (identifying
reading order and nested structures), (4) Specialized Content Parsing (analyzing the internal structure of tables and
figures), and (5) Unified End-to-End Parsing (evaluating all preceding tasks simultaneously).

Key benchmark families have emerged to address distinct layers of this stack. For foundational layout segmentation, *
*PubLayNet** 1 and its more diverse, human-annotated successor, **DocLayNet** 3, serve as industry standards, evaluated
using object detection metrics like mean Average Precision (mAP). For logical role labeling, **DocBank** 5 provides a
large-scale, weakly-supervised dataset for pre-training semantic models.

The critical domain of table parsing is dominated by **TableBank** 7 for detection and, most importantly, **PubTabNet**
9 for detailed structure recognition. The adoption of the **Tree-Edit-Distance-based Similarity (TEDS)** metric 10 by
PubTabNet has created a robust standard for evaluating the complex, hierarchical nature of tables. Concurrently,
dedicated benchmarks like **ReadingBank** 12 have emerged to specifically address the challenge of reading order
reconstruction.

More recently, research has pushed into true hierarchical recovery. Benchmarks like **DocParser** 14, **HRDoc** 15, and
**SRFUND** 17 move beyond simple links to model the deep, nested relationships (e.S\_S., sections, subsections, list
items) that define a document's logical architecture. This new frontier has even adopted metrics like TEDS to evaluate
the entire document's tree structure.16 Finally, new comprehensive evaluation suites, exemplified by **OmniDocBench**
19, provide a unified framework to test models on layout, hierarchy, reading order, and table structure simultaneously,
using composite metrics for a holistic assessment.19

No single benchmark is sufficient to evaluate a modern, general-purpose PDF parsing system. This report concludes by
recommending a *suite* of 3–6 benchmarks. A robust evaluation harness should include, at minimum: **DocLayNet** for
domain generalization, **PubTabNet** for table structure, **ReadingBank** for sequential flow, **HRDoc** for multi-page
hierarchy, and **OmniDocBench** for unified end-to-end performance.

## **Part 1: The Evaluation Stack: A Framework for Document Parsing Benchmarks**

The field of document understanding lacks a single, universal evaluation task. Instead, a "stack" of tasks, increasing
in semantic complexity, has evolved. Benchmarks can be categorized by which layer of this stack they primarily address.

### **L1: Physical Layout Segmentation (DLA)**

This is the foundational task of Document Layout Analysis (DLA). It is concerned with identifying the *physical*
boundaries of content blocks on a page, regardless of their semantic meaning.

* **Task:** To place a bounding box around every distinct text column, figure, table, or other physical region.
* **Key Benchmarks:** PubLayNet 2, DocLayNet.4
* **Key Metrics:** Mean Average Precision (mAP) over a range of Intersection over Union (IoU) thresholds (e.S\_S.,
  COCO-style mAP @ IoU \[0.50:0.95\]).4

### **L2: Logical Layout Analysis (Semantic Role Labeling)**

This task moves beyond physical detection to *classification*. It assigns a *semantic* label to each physically detected
block, identifying its role in the document's structure.

* **Task:** To label a detected block as a title, abstract, section\_heading, paragraph, footnote, or page\_header.
* **Key Benchmarks:** DocBank 6, DocLayNet (which blends L1 and L2).4
* **Key Metrics:** Token-level or block-level classification metrics, such as Precision, Recall, and F1-score.20

### **L3: Relational and Hierarchical Structure Recovery**

This is the first layer of true structure recovery. It focuses not on the blocks themselves, but on the *relationships*
between them. This layer has two primary components:

* **Sequential Structure (Reading Order):** Identifying the correct, one-dimensional sequence in which text blocks
  should be read.
    * **Task:** Given all text blocks on a page, sort them into a coherent order, correctly handling multi-column
      layouts.
    * **Key Benchmarks:** ReadingBank.12
    * **Key Metrics:** Sequence metrics like BLEU 13, Average Relative Distance (ARD) 13, or Normalized Edit Distance.19
* **Hierarchical Structure (Logical Grouping):** Identifying the *nested* or *parent-child* relationships between
  logical blocks.
    * **Task:** To link a list\_item block to its parent list block, or to group all paragraph blocks that belong under
      a specific section\_heading.
    * **Key Benchmarks:** DocParser (arXivdocs) 14, HRDoc 15, SRFUND.17
    * **Key Metrics:** F1-score on relational triples 14, or structural metrics like Tree Edit Distance (TEDS).16

### **L4: Specialized Content Parsing (Deep Structure)**

This layer involves recursively parsing the *internal* structure of highly complex, self-contained blocks. This task is
dominated by table structure recognition (TSR) but also applies to formulas and figures.

* **Task:** Given an image of a table, reconstruct its full grid structure, including row and column spans, and extract
  the text from each cell.
* **Key Benchmarks:** PubTabNet 10, TableBank 7, ICDAR competitions.21
* **Key Metrics:** The dominant metric is **TEDS (Tree-Edit-Distance-based Similarity)**, which evaluates both
  structural accuracy and cell content accuracy.10

### **L5: Unified End-to-End Parsing**

A recent development, this layer consists of comprehensive benchmarks designed to evaluate a *single system* on all
L1-L4 tasks simultaneously.

* **Task:** To take a raw document page and produce a full, hierarchical, and structured representation (e.S\_S.,
  Markdown or HTML) that correctly identifies all layouts, logical roles, reading orders, and table structures.
* **Key Benchmarks:** OmniDocBench.19
* **Key Metrics:** Composite scores that aggregate multiple metrics (e.S\_S., OmniDocBench's "Overall" score combining
  Text Edit Distance, Table TEDS, and Formula CDM).19

### **L6: Downstream Task Evaluation (Comprehension)**

While partially out of scope for pure *structure recovery*, this layer evaluates how well a parsed structure facilitates
downstream tasks, such as Key Information Extraction (KIE) or Visual Question Answering (VQA).

* **Task:** To answer a question ("What is the invoice total?") or extract a key-value pair ("Date": "12-Jan-2025").
* **Key Benchmarks:** FUNSD 23 (which bridges L3 and L6), DUE.25
* **Key Metrics:** F1-score for KIE, Accuracy for VQA.25

## **Part 2: Foundational Benchmarks for Page Layout Segmentation (L1/L2)**

These benchmarks are the foundation of the evaluation stack, enabling the pre-training and evaluation of models that
perform the initial, fundamental task of page segmentation.

### **2.1 PubLayNet: The Large-Scale Weakly-Supervised Baseline**

* **Citation:** Zhong, Xu, Jianbin Tang, and Antonio Jimeno Yepes. "PubLayNet: largest dataset ever for document layout
  analysis." *2019 International Conference on Document Analysis and Recognition (ICDAR)*. IEEE, 2019\.2
* **Benchmark Description:** PubLayNet was a foundational development, providing a massive-scale dataset for training
  deep learning models. It consists of over 360,000 document images.29 Its scale was achieved not through manual
  annotation but via a "weak supervision" paradigm, automatically generating annotations by matching the PDF format and
  the XML representations of articles from the PubMed Central Open Access Subset (PMCOA).2
* **Tasks and Annotations:** The benchmark defines a core Document Layout Analysis (DLA) task, treated as object
  detection.2 The label taxonomy is simple and physical, containing five classes: text, title, list, table, and
  figure.32 Annotations are provided as both bounding boxes and polygonal segmentations in the standard COCO JSON
  format.2
* **Evaluation Protocol and Metrics:** The standard evaluation protocol is based on object detection metrics. It was
  notably used in Task A of the ICDAR 2021 Competition on Scientific Literature Parsing (SLP).32 The primary metric is
  the COCO standard: mean Average Precision (mAP) calculated over a range of IoU thresholds from 0.50 to 0.95 with a
  step of 0.05 (mAP @ IoU \[0.50:0.95\]).32
* **Relevance and Limitations:** PubLayNet is crucial as a *pre-training* dataset. The pre-trained Faster-RCNN and
  Mask-RCNN models released with the dataset serve as common baselines for transfer learning.2 Its primary weakness,
  however, is its "PubMed Niche"—its severe *domain specificity*. Models trained exclusively on PubLayNet exhibit a
  significant drop in accuracy when applied to documents from other domains, such as business or legal reports.3

### **2.2 DocLayNet: The Human-Annotated, Diverse-Domain Successor**

* **Citation:** Pfitzmann, Birgit, et al. "DocLayNet: A Large Human-Annotated Dataset for Document-Layout Segmentation."
  *Proceedings of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD)*. 2022\.35
* **Benchmark Description:** DocLayNet was created specifically to address the domain-specificity and annotation-quality
  limitations of PubLayNet and DocBank.3 It is a large, *human-annotated* dataset 38 containing 80,863 pages.3 Its key
  strength is its *diversity*, with documents sourced from six distinct domains: financial\_reports,
  scientific\_articles, laws\_and\_regulations, government\_tenders, manuals, and patents.3 This manual annotation, in
  contrast to weak supervision, provides higher-quality, more reliable ground truth. The dataset also includes double-
  and triple-annotated pages to measure inter-annotator agreement, setting a "human baseline" for the task.3
* **Tasks and Annotations:** The task is L1/L2 layout segmentation. DocLayNet provides a more granular 11-class logical
  taxonomy: Caption, Footnote, Formula, List-item, Page-footer, Page-header, Picture, Section-header, Table, Text, and
  Title.4 The annotations are provided as bounding boxes in COCO format. Critically, the dataset also includes the
  source single-page PDFs and the corresponding extracted digital text cells (with coordinates and content), enabling
  the development and evaluation of multi-modal models that fuse visual and textual information.37
* **Evaluation Protocol and Metrics:** DocLayNet was the basis for the ICDAR 2023 Competition on Robust Layout
  Segmentation.4 The evaluation metric is the same as PubLayNet's: mAP @ IoU \[0.50:0.95\].4
* **Relevance and Limitations:** DocLayNet is arguably the current *industry standard* for evaluating general-purpose
  layout segmentation. Its domain diversity and high-quality annotations make it the recommended starting point for
  testing L1/L2 generalization.3 Its primary limitation is that it is still a *single-page, flat* representation. It
  identifies a Section-header and Text blocks, but it does not create the L3 link to show which text blocks *belong* to
  that header.

### **2.3 RoDLA: A Framework for Evaluating Robustness**

* **Citation:** Chen, Jiapeng, et al. "RoDLA: Benchmarking the Robustness of Document Layout Analysis Models." *2024
  IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*. 2024\.40
* **Benchmark Description:** RoDLA is not a new dataset but an *evaluation framework* designed to test model robustness,
  a critical factor for production systems. It introduces a taxonomy of 12 common, real-world perturbations (e.S\_S.,
  spatial transformation, content interference, blur, noise) applied at 3 severity levels.41
* **Tasks and Metrics:** The framework is applied to existing benchmarks, creating perturbed versions (e.S\_S.,
  PubLayNet-P, DocLayNet-P).41 It introduces two new metrics: **Mean Perturbation Effect (mPE)** and **Mean Robustness
  Degradation (mRD)**, which quantify the drop in a model's mAP score when faced with these corruptions.41
* **Relevance:** This framework is essential for moving beyond clean academic benchmarks. A model may achieve a high mAP
  on DocLayNet but fail in a real-world pipeline processing noisy, scanned documents. RoDLA provides the methodology to
  measure and benchmark this critical robustness gap.

## **Part 3: Benchmarks for Logical Structure and Semantic Hierarchy (L2/L3)**

This set of benchmarks moves beyond physical boxes to the core of structure recovery: assigning semantic roles, linking
related entities, and building a hierarchical representation of the document's logic.

### **3.1 DocBank: Large-Scale Semantic Role Labeling**

* **Citation:** Li, Minghao, et al. "DocBank: A Benchmark Dataset for Document Layout Analysis." *Proceedings of the
  28th International Conference on Computational Linguistics (COLING)*. 2020\.5
* **Benchmark Description:** DocBank is a massive L2 benchmark, containing 500,000 document pages (400k train, 50k val,
  50k test).5 It is a "natural extension" 5 of the TableBank dataset 8 and was, like its sibling, constructed using weak
  supervision. It leverages the LaTeX source code from articles on arXiv to automatically generate fine-grained
  annotations.44
* **Tasks and Annotations:** The task is semantic role labeling at the *token* level. Its goal is to enable models to
  integrate both textual and layout information.5 It features a rich 12-class semantic taxonomy: Abstract, Author,
  Caption, Equation, Figure, Footer, List, Paragraph, Reference, Section, Table, and Title.6 Each token is annotated
  with its bounding box, font, color, and semantic label.6
* **Evaluation Protocol and Metrics:** With its large train/val/test splits, DocBank is primarily evaluated using
  standard classification metrics (F1-score, Precision, Recall) at the token or block level.
* **Relevance and Limitations:** DocBank, along with PubLayNet, was a foundational dataset for pre-training the first
  generation of powerful multi-modal layout-aware models, such as LayoutLM.5 Its token-level, semantic-class data is
  ideal for this purpose. However, like other L2 benchmarks, it suffers from the "flat structure" problem: it identifies
  *all* paragraphs and *all* section headings, but provides no relational links to group them.

### **3.2 FUNSD and XFUND: Benchmarking Form Understanding (L3)**

* **Citation (FUNSD):** Jaume, Guillaume, Hazım Kemal Ekenel, and Jean-Philippe Thiran. "FUNSD: A Dataset for Form
  Understanding in Noisy Scanned Documents." *2019 International Conference on Document Analysis and Recognition
  Workshops (ICDARW)*. 2019\.24
* **Citation (XFUND):** Xu, Yiheng, et al. "XFUND: A Benchmark Dataset for Multilingual Visually Rich Form
  Understanding." *Findings of the Association for Computational Linguistics: ACL 2022*.46
* **Benchmark Description:** FUNSD (Form Understanding in Noisy Scanned Documents) is a seminal dataset that emphasizes
  quality over quantity. It consists of only 199 fully annotated, noisy scanned forms (149 train, 50 test).23 Its value
  lies in its meticulous *manual, fine-grained L3 annotations*. XFUND is its direct successor, extending the same task
  and annotation schema to seven languages (Chinese, Japanese, Spanish, French, Italian, German, Portuguese) to enable
  cross-lingual form understanding.47
* **Tasks and Annotations:** FUNSD defines two core tasks: (1) **Semantic Entity Labeling** (L2) and (2) **Entity
  Linking** (L3).24 Entities (groups of words) are first labeled with one of four semantic categories: header, question,
  answer, or other.23 Then, the key L3 task is to predict the *links* (\[id\_from, id\_to\]) that connect related
  entities, such as linking a question (e.S\_S., "Name:") to its corresponding answer (e.S\_S., "John Doe").23
* **Evaluation Protocol and Metrics:** The evaluation is similarly split. The L2 labeling task is measured with an
  F1-score. The L3 linking task is measured using Precision, Recall, and F1-score on the predicted links.24
* **Relevance:** FUNSD was one of the first benchmarks to move beyond simple layout to evaluate *semantic
  relationships*. It is a classic dataset for Key Information Extraction (KIE) and logical relation prediction. Its
  primary limitation is that its relationship model is flat (simple key-value links).

### **3.3 The Hierarchical Frontier: DocParser, HRDoc, and SRFUND (L3+)**

This emerging class of benchmarks directly addresses the "flat structure" limitation of previous datasets. They are
designed to model the full, *nested, hierarchical* (parent-child) structure of a document.

#### **3.3.1 DocParser (arXivdocs)**

* **Citation:** Rausch, Johannes, et al. "DocParser: Hierarchical Document Structure Parsing from Renderings." *The
  Thirty-Fifth AAAI Conference on Artificial Intelligence (AAAI-21)*. 2021\.14
* **Benchmark (arXivdocs):** A dataset of 127,472 scientific articles from arXiv, labeled via a weak supervision
  mechanism.14
* **Tasks and Annotations:** This benchmark was pioneering in explicitly defining *hierarchical* document structure
  parsing as a single task. Its label taxonomy is extremely granular, with 23 categories including not just HEADING and
  TABLE, but also TABLE ROW, TABLE CELL, ITEMIZE, and ITEM.14 Most importantly, it defines three relation types: parent
  of, followed by, and null. This relational model simultaneously captures both *hierarchy* (parent of) and *reading
  order* (followed by).14
* **Metrics:** Evaluation is two-fold: mAP (using IoU) for detecting the entities, and an F1-score for correctly
  classifying the *relational triples* (e.S\_S., \<$E\_{subj}$, $E\_{obj}$, $parent of$\>).14
* **Relevance:** DocParser provided a critical conceptual framework and dataset for parsing *deeply-nested* structures,
  including tables, as a unified hierarchical problem.

#### **3.3.2 HRDoc**

* **Citation:** Ma, Jiefeng, et al. "HRDoc: Dataset and Baseline Method toward Hierarchical Reconstruction of Document
  Structures." *The Thirty-Seventh AAAI Conference on Artificial Intelligence (AAAI-23)*. 2023\.16
* **Benchmark (HRDoc):** A dataset of 2,500 *multi-page* documents (from ACL and arXiv) with nearly 2 million annotated
  semantic units.15
* **Tasks and Annotations:** HRDoc's unique contribution is its focus on the *multi-page* challenge. Most benchmarks are
  single-page, but HRDoc correctly identifies that document structure is continuous across page breaks; it shows that
  models restricted to a single page perform significantly worse.16 Its 14-class taxonomy includes Section, First-Line,
  and Para-Line.16 Its three relation types are Connect (e.S\_S., lines within a paragraph), Contain (e.S\_S., section
  to subsection), and Equality (e.S\_S., two sibling subsections).16
* **Metrics:** For its overall "hierarchical document reconstruction" task, HRDoc adopted the **Tree Edit Distance (
  TEDS)** metric.16 This methodological leap—using a metric from table parsing to evaluate the *entire document's tree
  structure*—is a powerful and effective way to measure hierarchical accuracy.
* **Relevance:** HRDoc is one of the only benchmarks available to evaluate a system's ability to maintain structural and
  hierarchical coherence *across page breaks*, filling a major gap in the evaluation landscape.

#### **3.3.3 SRFUND**

* **Citation:** Ma, Jiefeng, et al. "SRFUND: A Multi-Granularity Hierarchical Structure Reconstruction Benchmark in Form
  Understanding." *Advances in Neural Information Processing Systems (NeurIPS)*. 2024\.17
* **Benchmark (SRFUND):** A dataset of 1,592 forms in 8 languages, built as a meticulous *refinement* and *extension* of
  FUNSD and XFUND.17
* **Tasks and Annotations:** This benchmark was created explicitly because FUNSD and XFUND were too shallow, being "
  limited to local and entity-level annotations" and overlooking the "hierarchically structured representation of
  documents".17 SRFUND adds this missing deep hierarchy by defining five multi-granularity tasks: (1) word-to-line
  merging, (2) line-to-entity merging, (3) entity classification, (4) **item table localization** (annotating tables
  *within* forms), and (5) **entity-based full-document hierarchical structure recovery**.18
* **Relevance:** SRFUND is the state-of-the-art benchmark for evaluating hierarchical *form* understanding. It combines
  the semantic linking task of FUNSD with the deep hierarchical modeling of HRDoc, making it a comprehensive and
  challenging test for modern parsers.

##   

## **Part 4: The Critical Challenge: Table Detection and Structure Recognition (L4)**

Table parsing is a complex sub-field of document understanding with its own specialized benchmarks and metrics. This L4
task is twofold: first, *detecting* the table's location (L1), and second, *recognizing its structure* (L4).

### **4.1 TableBank: Large-Scale Table Detection**

* **Citation:** Li, Minghao, et al. "TableBank: Table benchmark for image-based table detection and recognition."
  *Proceedings of the 12th Language Resources and Evaluation Conference (LREC)*. 2020\.52
* **Benchmark Description:** The sibling dataset to DocBank, TableBank is a large-scale benchmark containing 417,000
  high-quality labeled tables.7 It was also built using weak supervision, extracting tables from Word and LaTeX
  documents on the internet.7
* **Tasks and Annotations:** The dataset supports two tasks. Its primary use is **Table Detection**, for which it
  provides bounding boxes for the table regions. It also supports **Table Structure Recognition (TSR)** on a subset of
  15,000 tables, with the ground truth being the HTML/LaTeX tag sequence.7
* **Evaluation Protocol and Metrics:** For detection, standard Precision, Recall, and F1-score based on bounding box
  overlap are used.7 For structure recognition, the paper uses a 4-gram BLEU score to compare the generated tag sequence
  to the ground truth.7 This reliance on BLEU is a key difference from its successor, PubTabNet.
* **Relevance:** TableBank is the largest and most-used benchmark for the *table detection* task.

### **4.2 PubTabNet: The Standard for Table Structure Recognition (TSR)**

* **Citation:** Zhong, Xu, Elaheh ShafieiBavani, and Antonio Jimeno Yepes. "Image-based table recognition: data, model,
  and evaluation." *European Conference on Computer Vision (ECCV)*. 2020\.9
* **Benchmark Description:** PubTabNet is the industry-standard benchmark for the *structure recognition* task. It
  consists of over 568,000 table images extracted from scientific publications in PubMed Central (PMCOA).9
* **Tasks and Annotations:** The task is full image-based Table Recognition. The goal is to convert a table *image* into
  its complete *structured HTML representation*.9 This single task combines structure recognition (rows, columns,
  rowspan, colspan) and cell content recognition (the text within each cell).10 An updated version, PubTabNet 2.0, also
  added the bounding box coordinates for all non-empty cells, enabling more granular, localization-aware models.9
* **Evaluation Protocol and Metrics:** PubTabNet's most significant contribution, besides the dataset, is the **TEDS (
  Tree-Edit-Distance-based Similarity)** metric.9 Previous metrics like BLEU were insufficient. TEDS addresses this by
  modeling both the predicted HTML and the ground-truth HTML as *trees*. It then computes the edit distance between
  them.10 This brilliantly allows a single metric to *simultaneously* penalize structural errors (e.S\_S., a missed
  colspan) and cell content errors (using string-edit-distance for node substitution).10 A variant, TEDS-struc,
  evaluates *only* the structure, ignoring cell content, for more detailed analysis.11
* **Relevance:** PubTabNet, combined with the TEDS metric, is the *undisputed standard* for evaluating L4 table
  structure recognition. Any modern system claiming table parsing capabilities must report its TEDS score on this
  benchmark.

### **4.3 ICDAR Competitions: Driving SOTA in Table Parsing**

The International Conference on Document Analysis and Recognition (ICDAR) competitions have been instrumental in
standardizing and advancing the SOTA on these benchmarks.

* **ICDAR 2019 (cTDaR):** The Competition on Table Detection and Recognition was a comprehensive evaluation.22
    * **Track A:** Table Detection on diverse documents (modern and archival).22
    * **Track B:** Table Recognition, split into two sub-tracks: B.1 (TSR-only, given the table bounding box) and B.2 (
      end-to-end detection and TSR).22 This multi-track design provides a comprehensive evaluation framework.
* **ICDAR 2021 (SLP):** The Competition on Scientific Literature Parsing.34
    * **Task A (Layout):** Used PubLayNet, evaluated with mAP.32
    * **Task B (Table Recognition):** Used **PubTabNet**, evaluated with **TEDS**.9 This competition officially
      canonized PubTabNet and TEDS as the SOTA evaluation standard for table parsing in scientific literature.61

### **4.4 Other Notable Table Datasets**

* **Marmot:** An older but still relevant dataset of \~2,000 pages, notable for its inclusion of both Chinese and
  English documents.62
* **PubTables-1M:** A massive dataset of 1 million tables, introduced to address annotation quality issues like "
  oversegmentation in markup annotations" found in other large, weakly-supervised datasets, thereby providing more
  reliable ground truth.65

##   

## **Part 5: Evaluating Reading Order and Unified Systems (L3/L5)**

This section covers the final layers of the stack: (1) the specific L3 challenge of reconstructing sequential flow and (

2) the L5 challenge of evaluating all tasks in a single, unified framework.

### **5.1 ReadingBank: The Dedicated Benchmark for Reading Order (L3)**

* **Citation:** Wang, Zilong, et al. "LayoutReader: Pre-training of Text and Layout for Reading Order Detection."
  *Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP)*. 2021\.12
* **Benchmark Description:** ReadingBank is a large-scale benchmark created specifically for the task of reading order
  detection. It contains 500,000 document pages (400k train, 50k val, 50k test).13 Like its siblings DocBank and
  TableBank, it was constructed using weak supervision. It leverages the *inherent reading order* embedded in the XML
  metadata of Microsoft WORD (DocX) files found on the internet.13
* **Tasks and Annotations:** The task is purely **Reading Order Detection**. Given a document image's text blocks, the
  goal is to sort them into the correct, human-readable sequence.13 This directly addresses the failure of simple "
  top-to-bottom, left-to-right" heuristics, which fail on multi-column or complex layouts.13 Annotations consist of the
  ground-truth sequence of words and their corresponding bounding boxes.13
* **Evaluation Protocol and Metrics:** As this is a *sequencing* problem, it borrows metrics from NLP tasks like machine
  translation. The primary metrics are **Average Page-level BLEU** (measuring n-gram overlap between predicted and
  ground-truth sequences) and **ARD (Average Relative Distance)**.13
* **Relevance:** ReadingBank is the primary, large-scale benchmark for training and evaluating reading order models.
  This L3 task is a critical prerequisite for any downstream NLP, as feeding text in the wrong order can render it
  meaningless.

### **5.2 OmniDocBench: A Modern, Comprehensive Benchmark for Unified Parsing (L5)**

* **Citation:** Ouyang, Linke, et al. "OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive
  Annotations." *2025 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*. 2025\.19
* **Benchmark Description:** OmniDocBench is a new, state-of-the-art L5 benchmark designed to address the fragmented
  nature of previous evaluations. It is a diverse, human-annotated dataset of 1,355 PDF pages 19 covering 9 document
  types (academic papers, textbooks, financial reports, newspapers, handwritten notes), 4 layout types, and 3
  languages.19
* **Tasks and Annotations:** OmniDocBench was created to evaluate *end-to-end* models (like modern Vision-Language
  Models) on *all* major parsing tasks simultaneously within a single framework.68 Its annotation schema is consequently
  the richest available, covering:
    * **Tasks:** End-to-end evaluation, Layout Detection, Table Recognition, Formula Recognition, Text OCR, and *
      *Reading Order**.19
    * **Block-level (15 types):** Over 20,000 annotations for text paragraphs, headings, tables, etc..19
    * **Span-level (4 types):** Over 80,000 annotations for text lines, inline formulas, subscripts, etc..19
    * **Tables:** Ground truth provided in both **LaTeX and HTML** formats.19
    * **Reading Order:** Full annotations for component-level reading order.71
    * **Attributes:** Page, text, and table attributes are also annotated.71
* **Evaluation Protocol and Metrics:** The benchmark provides a unified evaluation suite that combines metrics for each
  task into a single "Overall" score.
    * **Layout:** COCODet metrics (mAP, mAR).19
    * **Tables:** **TEDS**.72
    * **Formulas:** **CDM** (a formula-specific metric).19
    * **Text & Reading Order:** **Normalized Edit Distance**.19
    * **Overall Score:** A composite metric defined
      as $Overall \= \\frac{((1 \- Text Edit Distance) \\times 100\) \+ Table TEDS \+ Formula CDM}{3}$.19
* **Relevance:** OmniDocBench is arguably the *most relevant* and comprehensive benchmark for evaluating a modern,
  general-purpose PDF parsing system. It is diverse, human-annotated, and provides a ready-to-use evaluation suite that
  covers all critical tasks: structure, tables, and reading order, all evaluated with appropriate, state-of-the-art
  metrics.

##   

## **Part 6: Synthesis, Comparison, and Gap Analysis**

The individual benchmarks, when viewed together, reveal a clear evolution in the field and highlight several persistent
gaps in evaluation.

### **6.1 Comparative Overview of Key Document Benchmarks**

The following table provides a high-level comparison of the most critical benchmarks analyzed in this report,
categorized by their position in the Evaluation Stack.

| Benchmark Name   | Year / Venue   | Document Domain                 | Scale (Pages)      | Annotation Method             | Key Tasks Supported (L1-L4)                              | Key Metric(s)                       | License                |
|:-----------------|:---------------|:--------------------------------|:-------------------|:------------------------------|:---------------------------------------------------------|:------------------------------------|:-----------------------|
| **PubLayNet**    | 2019 / ICDAR   | Scientific (PubMed)             | \~360,000          | Weak Supervision (XML)        | Layout (L1), Table Detect                                | mAP @ IoU                           | CDLA-Permissive-1.0 2  |
| **DocLayNet**    | 2022 / KDD     | Diverse (Business, Legal, etc.) | \~81,000           | Human Annotated               | Layout (L1), Logic (L2), Table Detect                    | mAP @ IoU                           | CDLA-Permissive-1.0 37 |
| **DocBank**      | 2020 / COLING  | Scientific (arXiv)              | \~500,000          | Weak Supervision (LaTeX)      | Logic (L2), Table Detect                                 | F1-score (implied)                  | Apache-2.0 5           |
| **FUNSD**        | 2019 / ICDARW  | Scanned Forms                   | 199                | Human Annotated               | Logic (L2), Relations (L3 KIE)                           | F1-score                            | Public 45              |
| **SRFUND**       | 2024 / NeurIPS | Forms (Multilingual)            | 1,592              | Human Annotated (Refined)     | Logic (L2), Hierarchy (L3), Table Detect                 | F1, Hierarchy Metrics               | Public 18              |
| **HRDoc**        | 2023 / AAAI    | Scientific (Multi-page)         | \~2,500 docs       | Rule-based \+ Human           | Logic (L2), **Hierarchy (L3)**, **Reading Order**        | **TEDS** (for hierarchy)            | CC BY-NC-SA 4.0 16     |
| **TableBank**    | 2020 / LREC    | Diverse (Web)                   | \~417,000 (tables) | Weak Supervision (Word/LaTeX) | Table Detect, Table TSR (shallow)                        | F1 (detect), BLEU (TSR)             | Public 54              |
| **PubTabNet**    | 2020 / ECCV    | Scientific (PubMed)             | \~568,000 (tables) | Weak Supervision (XML)        | **Table TSR (L4)**, Cell Detect                          | **TEDS**                            | Public 9               |
| **ReadingBank**  | 2021 / EMNLP   | Diverse (Web, Word)             | \~500,000          | Weak Supervision (Word XML)   | **Reading Order (L3)**                                   | BLEU, ARD                           | Apache-2.0 13          |
| **OmniDocBench** | 2025 / CVPR    | Diverse (9 types)               | 1,355              | Human Annotated               | **Unified (L1-L4)**, Hierarchy, Reading Order, Table TSR | **Composite (TEDS, EditDist, CDM)** | Apache-2.0 19          |

### **6.2 Narrative Comparison: Trends and Inter-relationships**

The evolution of these benchmarks reveals several clear trends.

1. **From Weak Supervision to Human Annotation:** A distinct lineage, largely from major research labs, focused on
   *scale* via weak supervision (PubLayNet 2, DocBank 44, TableBank 8, ReadingBank 12). This was essential for
   *pre-training* the first large multi-modal models. This was followed by a shift to smaller, *human-annotated*, and
   *diverse-domain* datasets (DocLayNet 3, OmniDocBench 19) designed for robust *evaluation* and *fine-tuning*.
2. **From Flat Labels to Deep Hierarchy:** A parallel academic track has focused on *structural complexity*. This
   lineage runs from FUNSD's simple key-value links 24, through the deep, nested, and relational models of DocParser 14
   and HRDoc 16, and culminates in the rich, multi-granularity hierarchy of SRFUND.18
3. **The Rise of Competitions:** Shared tasks, particularly at ICDAR, have acted as catalysts to standardize evaluation.
   The 2019 cTDaR 22 provided a comprehensive framework for table parsing, and the 2021 SLP 32 cemented PubTabNet and
   the TEDS metric as the definitive standard for TSR.
4. **Convergence to Unified Evaluation:** OmniDocBench 19 represents the logical convergence of these trends. It is
   human-annotated, diverse-domain, and explicitly evaluates hierarchy, tables (with TEDS), and reading order (with Edit
   Distance) within a single, unified framework designed for modern end-to-end models.

### **6.3 Gaps and Limitations in the Current Landscape**

Despite this progress, significant gaps remain in the evaluation landscape.

* **The Multi-Page Chasm:** This is the most significant limitation. The vast majority of benchmarks (PubLayNet,
  DocLayNet, DocBank, PubTabNet, OmniDocBench) are *single-page* evaluations. They cannot test a system's ability to
  link a footnote on page 5 to its reference on page 4, or to continue a logical section across a page break. **HRDoc**
  16 is the *only* major benchmark explicitly designed to address this critical *multi-page* document-level hierarchy,
  making it an essential, if specialized, tool.
* **Born-Digital vs. Scanned:** Many benchmarks are image-based, and their metrics (like mAP @ IoU) are pixel-based.
  However, modern PDF parsers should leverage *born-digital* information (embedded text, fonts, precise coordinates).74
  While datasets like DocLayNet 37 provide the source PDFs, the primary evaluation metrics do not always reward the
  optimal use of this digital-native information.
* **Under-represented Domains:** While DocLayNet and OmniDocBench have vastly improved domain diversity, complex *legal*
  documents (e.S\_S., contracts with nested clauses and marginalia) and highly complex *financial* reports (e.S\_S.,
  with borderless, multi-page, and deeply nested tables) remain under-represented in major academic benchmarks.
* **The "Good Enough" Problem:** As highlighted in industry analysis, a gap exists between academic SOTA and production
  viability. Academic benchmarks drive improvements on metrics like TEDS, but for real-world applications, a 1% TEDS
  improvement may be negligible, while system cost, latency, and API reliability are paramount.75 Current benchmarks do
  not capture these operational characteristics.
* **Annotation Quality and Ambiguity:** Weakly-supervised datasets (PubLayNet, DocBank, PubTabNet) are known to contain
  annotation noise. The PubTables-1M dataset was created specifically to address the "oversegmentation" errors found in
  earlier markup-derived ground truth.65 Even in human-annotated datasets, logical structure can be ambiguous, a fact
  DocLayNet 3 addresses by reporting inter-annotator agreement as a "human" error bar.

## **Part 7: Recommendations and Future Outlook**

### **7.1 Recommended Shortlist for a Modern PDF Parser**

No single benchmark is sufficient. A robust evaluation harness for a modern system targeting general-purpose structure
and table parsing requires a *suite* of benchmarks to cover all layers of the stack and test for generalization.

1. **For General Layout and Domain Generalization (L1/L2):**
    * **Benchmark:** **DocLayNet** 3
    * **Justification:** This is the SOTA for L1/L2 evaluation. Its primary strength is its *domain diversity* (finance,
      legal, manuals, etc.) 3, which rigorously tests a model's ability to generalize beyond the scientific-article
      niche. Its high-quality human annotations are a significant advantage over PubLayNet.
    * **Caveat:** It is a single-page, flat-structure benchmark. It evaluates *detection* (mAP), not *hierarchy*.
2. **For Table Structure Recognition (L4):**
    * **Benchmark:** **PubTabNet** 10
    * **Justification:** This is the non-negotiable, industry-standard benchmark for L4 table structure recognition. The
      **TEDS** metric 10 is the key, as it accurately and simultaneously evaluates both hierarchical structure (spans)
      and cell content.
    * **Caveat:** Its domain is specific to scientific tables, which may differ structurally from those in financial or
      business reports.
3. **For Reading Order and Sequential Flow (L3):**
    * **Benchmark:** **ReadingBank** 12
    * **Justification:** This is the only large-scale benchmark dedicated to the L3 task of reading order. It tests a
      system's ability to correctly serialize a 2D page using appropriate sequence metrics (BLEU, ARD) 13, a critical
      step for downstream NLP.
    * **Caveat:** The ground truth is weakly-supervised (from Word XML) 13 and may contain noise or non-human-like
      orderings in complex cases.
4. **For True Hierarchical and Multi-Page Structure (L3+):**
    * **Benchmark:** **HRDoc** 16
    * **Justification:** This benchmark is essential for testing the *most advanced* L3 structure recovery. It fills the
      largest gap in the landscape: *multi-page* document understanding.16 Its use of TEDS to evaluate the *entire
      document's hierarchy* is methodologically sound and powerful.16
    * **Caveat:** It is smaller-scale and domain-specific (scientific papers).
5. **For Unified End-to-End Evaluation (L5):**
    * **Benchmark:** **OmniDocBench** 19
    * **Justification:** As the most modern benchmark (CVPR 2025), this is the best *single* evaluation for an
      end-to-end system. It is diverse-domain, human-annotated, and *simultaneously* evaluates layout, tables (with
      TEDS), formulas, reading order (with EditDist), and hierarchy. Its composite "Overall" score is a powerful tool
      for ranking models on all-around performance.19
    * **Caveat:** As it is new, it is less established. Its scale (1.3k pages) makes it a *test* set, not a *training*
      set.
6. **Optional: For Form-Specific Hierarchy (L3+):**
    * **Benchmark:** **SRFUND** 18
    * **Justification:** If the target system *specifically* processes forms, SRFUND is the new SOTA. It supersedes
      FUNSD by adding the deep hierarchical annotations 18 that are missing from older key-value-based form benchmarks.

### **7.2 Concluding Analysis: The Future of Document Structure Evaluation**

The evolution of these benchmarks demonstrates a clear trajectory. The field is moving decisively away from flat,
single-page, single-domain evaluations and toward a more holistic understanding of document structure. The future of
document parsing evaluation is defined by four key trends:

1. **Hierarchical:** Evaluating parent-of and child-of relations, not just flat labels.
2. **Multi-page:** Understanding the document as a *single, coherent unit*, not a stack of independent pages.
3. **Unified:** Testing end-to-end models that parse layout, text, tables, and order in one shot.
4. **Robust:** Testing against noise, scanning, and domain shifts, not just on clean, in-domain data.

The single most important methodological trend is the adoption of structured-prediction metrics like **TEDS**.
Originally designed for tables 72, its application to full document hierarchy 16 signals a mature approach to a problem
that is, at its core, about tree-matching. Any future system must be prepared to be evaluated not just on *what* it
finds, but on *how* it correctly assembles those findings into a coherent, hierarchical whole.

#### **Works cited**

1. \[1908.07836\] PubLayNet: largest dataset ever for document layout analysis \- arXiv, accessed November 17,
   2025, [https://arxiv.org/abs/1908.07836](https://arxiv.org/abs/1908.07836)
2. ibm-aur-nlp/PubLayNet \- GitHub, accessed November 17,
   2025, [https://github.com/ibm-aur-nlp/PubLayNet](https://github.com/ibm-aur-nlp/PubLayNet)
3. \[2206.01062\] DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis, accessed November 17,
   2025, [https://arxiv.org/abs/2206.01062](https://arxiv.org/abs/2206.01062)
4. ICDAR 2023 Competition on Robust Layout Segmentation in ..., accessed November 17,
   2025, [https://arxiv.org/abs/2305.14962](https://arxiv.org/abs/2305.14962)
5. liminghao1630/DocBank · Datasets at Hugging Face, accessed November 17,
   2025, [https://huggingface.co/datasets/liminghao1630/DocBank](https://huggingface.co/datasets/liminghao1630/DocBank)
6. DocBank Dataset, accessed November 17,
   2025, [https://doc-analysis.github.io/docbank-page/](https://doc-analysis.github.io/docbank-page/)
7. TableBank: A Benchmark Dataset for Table Detection and Recognition \- GitHub, accessed November 17,
   2025, [https://github.com/doc-analysis/TableBank](https://github.com/doc-analysis/TableBank)
8. TableBank Dataset, accessed November 17,
   2025, [https://doc-analysis.github.io/tablebank-page/](https://doc-analysis.github.io/tablebank-page/)
9. ibm-aur-nlp/PubTabNet \- GitHub, accessed November 17,
   2025, [https://github.com/ibm-aur-nlp/PubTabNet](https://github.com/ibm-aur-nlp/PubTabNet)
10. Image-based table recognition: data, model, and evaluation \- arXiv, accessed November 17,
    2025, [https://arxiv.org/abs/1911.10683](https://arxiv.org/abs/1911.10683)
11. Rethinking Image-Based Table Recognition Using Weakly Supervised Methods \- SciTePress, accessed November 17,
    2025, [https://www.scitepress.org/Papers/2023/116826/116826.pdf](https://www.scitepress.org/Papers/2023/116826/116826.pdf)
12. ReadingBank: A Benchmark Dataset for Reading Order Detection \- GitHub, accessed November 17,
    2025, [https://github.com/doc-analysis/ReadingBank](https://github.com/doc-analysis/ReadingBank)
13. LayoutReader: Pre-training of Text and Layout for Reading Order ..., accessed November 17,
    2025, [https://arxiv.org/abs/2108.11591](https://arxiv.org/abs/2108.11591)
14. DocParser: Hierarchical Document Structure ... \- AAAI Publications, accessed November 17,
    2025, [https://ojs.aaai.org/index.php/AAAI/article/view/16558/16365](https://ojs.aaai.org/index.php/AAAI/article/view/16558/16365)
15. A Tree Construction based Approach for Hierarchical Document Structure Analysis \- arXiv, accessed November 17,
    2025, [https://arxiv.org/html/2401.11874v2](https://arxiv.org/html/2401.11874v2)
16. HRDoc: Dataset and Baseline Method toward ... \- AAAI Publications, accessed November 17,
    2025, [https://ojs.aaai.org/index.php/AAAI/article/view/25277/25049](https://ojs.aaai.org/index.php/AAAI/article/view/25277/25049)
17. \[2406.08757\] SRFUND: A Multi-Granularity Hierarchical Structure Reconstruction Benchmark in Form Understanding \-
    arXiv, accessed November 17, 2025, [https://arxiv.org/abs/2406.08757](https://arxiv.org/abs/2406.08757)
18. SRFUND: A Multi-Granularity Hierarchical Structure Reconstruction Benchmark in Form Understanding \- NIPS papers,
    accessed November 17,
    2025, [http://papers.nips.cc/paper\_files/paper/2024/file/cbeaff878d6446ed06c3e0ffa53477f2-Paper-Datasets\_and\_Benchmarks\_Track.pdf](http://papers.nips.cc/paper_files/paper/2024/file/cbeaff878d6446ed06c3e0ffa53477f2-Paper-Datasets_and_Benchmarks_Track.pdf)
19. opendatalab/OmniDocBench: \[CVPR 2025\] A ... \- GitHub, accessed November 17,
    2025, [https://github.com/opendatalab/OmniDocBench](https://github.com/opendatalab/OmniDocBench)
20. Evaluate performance | Document AI, accessed November 17,
    2025, [https://docs.cloud.google.com/document-ai/docs/evaluate](https://docs.cloud.google.com/document-ai/docs/evaluate)
21. ICDAR 2021 Competition on Scientific Table Image Recognition to LaTeX \- CodaLab, accessed November 17,
    2025, [https://competitions.codalab.org/competitions/26979](https://competitions.codalab.org/competitions/26979)
22. cndplab-founder/ICDAR2019\_cTDaR: The ICDAR 2019 cTDaR is to evaluate the performance of methods for table
    detection (TRACK A) and table recognition (TRACK B). For the first track, document images containing one or several
    tables are provided. For TRACK B two subtracks exist: the first subtrack (B.1 \- GitHub, accessed November 17,
    2025, [https://github.com/cndplab-founder/ICDAR2019\_cTDaR](https://github.com/cndplab-founder/ICDAR2019_cTDaR)
23. crcresearch/FUNSD: FUNSD Datasets \- GitHub, accessed November 17,
    2025, [https://github.com/crcresearch/FUNSD](https://github.com/crcresearch/FUNSD)
24. FUNSD: A Dataset for Form Understanding in Noisy Scanned ..., accessed November 17,
    2025, [https://arxiv.org/abs/1905.13538](https://arxiv.org/abs/1905.13538)
25. DUE: End-to-End Document Understanding Benchmark, accessed November 17,
    2025, [https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/069059b7ef840f0c74a814ec9237b6ec-Paper-round2.pdf](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/069059b7ef840f0c74a814ec9237b6ec-Paper-round2.pdf)
26. Document Understanding Evaluation Benchmark, accessed November 17,
    2025, [https://duebenchmark.com/](https://duebenchmark.com/)
27. DUE: End-to-End Document Understanding Benchmark \- OpenReview, accessed November 17,
    2025, [https://openreview.net/forum?id=rNs2FvJGDK](https://openreview.net/forum?id=rNs2FvJGDK)
28. PubLayNet: Largest Dataset Ever for Document Layout Analysis \- IEEE Computer Society, accessed November 17,
    2025, [https://www.computer.org/csdl/proceedings-article/icdar/2019/301400b015/1h81wfs4MoM](https://www.computer.org/csdl/proceedings-article/icdar/2019/301400b015/1h81wfs4MoM)
29. Publaynet: Largest Dataset Ever For Document Layout Analysis | PDF \- Scribd, accessed November 17,
    2025, [https://www.scribd.com/document/846884706/1908-07836v1](https://www.scribd.com/document/846884706/1908-07836v1)
30. \[1908.07836\] PubLayNet: largest dataset ever for document layout analysis \- ar5iv \- arXiv, accessed November 17,
    2025, [https://ar5iv.labs.arxiv.org/html/1908.07836](https://ar5iv.labs.arxiv.org/html/1908.07836)
31. PubLayNet: Largest dataset ever for document layout analysis \- IBM Research, accessed November 17,
    2025, [https://research.ibm.com/publications/publaynet-largest-dataset-ever-for-document-layout-analysis](https://research.ibm.com/publications/publaynet-largest-dataset-ever-for-document-layout-analysis)
32. Scientific Literature Parsing | ICDAR 2021, accessed November 17,
    2025, [https://iapr.org/archives/icdar2021/index.html%3Fp=29444.html](https://iapr.org/archives/icdar2021/index.html%3Fp=29444.html)
33. Document layout recognition dataset: PubLayNet \- Kaggle, accessed November 17,
    2025, [https://www.kaggle.com/datasets/devashishprasad/documnet-layout-recognition-dataset-publaynet-t0](https://www.kaggle.com/datasets/devashishprasad/documnet-layout-recognition-dataset-publaynet-t0)
34. ICDAR 2021 Competition on Scientific Literature Parsing \- ResearchGate, accessed November 17,
    2025, [https://www.researchgate.net/publication/353065549\_ICDAR\_2021\_Competition\_on\_Scientific\_Literature\_Parsing](https://www.researchgate.net/publication/353065549_ICDAR_2021_Competition_on_Scientific_Literature_Parsing)
35. DocLayNet: A Large Human-Annotated Dataset for Document-Layout Segmentation, accessed November 17,
    2025, [https://research.ibm.com/publications/doclaynet-a-large-human-annotated-dataset-for-document-layout-segmentation](https://research.ibm.com/publications/doclaynet-a-large-human-annotated-dataset-for-document-layout-segmentation)
36. \[2206.01062\] DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis, accessed November 17,
    2025, [https://ar5iv.labs.arxiv.org/html/2206.01062](https://ar5iv.labs.arxiv.org/html/2206.01062)
37. docling-project/DocLayNet · Datasets at Hugging Face, accessed November 17,
    2025, [https://huggingface.co/datasets/docling-project/DocLayNet](https://huggingface.co/datasets/docling-project/DocLayNet)
38. DocLayNet: A Large Human-Annotated Dataset for Document-Layout Segmentation, accessed November 17,
    2025, [https://www.semanticscholar.org/paper/DocLayNet%3A-A-Large-Human-Annotated-Dataset-for-Pfitzmann-Auer/454eebf9a5dc1fd9b1673bc60f5ea69521547b1a](https://www.semanticscholar.org/paper/DocLayNet%3A-A-Large-Human-Annotated-Dataset-for-Pfitzmann-Auer/454eebf9a5dc1fd9b1673bc60f5ea69521547b1a)
39. docling-project/icdar2023-doclaynet · Datasets at Hugging Face, accessed November 17,
    2025, [https://huggingface.co/datasets/docling-project/icdar2023-doclaynet](https://huggingface.co/datasets/docling-project/icdar2023-doclaynet)
40. RoDLA: Benchmarking the Robustness of Document Layout Analysis Models \- arXiv, accessed November 17,
    2025, [https://arxiv.org/abs/2403.14442](https://arxiv.org/abs/2403.14442)
41. RoDLA: Benchmarking the Robustness of Document Layout Analysis Models \- CVF Open Access, accessed November 17,
    2025, [https://openaccess.thecvf.com/content/CVPR2024/papers/Chen\_RoDLA\_Benchmarking\_the\_Robustness\_of\_Document\_Layout\_Analysis\_Models\_CVPR\_2024\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2024/papers/Chen_RoDLA_Benchmarking_the_Robustness_of_Document_Layout_Analysis_Models_CVPR_2024_paper.pdf)
42. DocBank: A Benchmark Dataset for Document Layout Analysis \- ACL Anthology, accessed November 17,
    2025, [https://aclanthology.org/2020.coling-main.82/](https://aclanthology.org/2020.coling-main.82/)
43. \[2006.01038\] DocBank: A Benchmark Dataset for Document Layout Analysis \- arXiv, accessed November 17,
    2025, [https://arxiv.org/abs/2006.01038](https://arxiv.org/abs/2006.01038)
44. DocBank: A Benchmark Dataset for Document Layout Analysis \- Microsoft Research, accessed November 17,
    2025, [https://www.microsoft.com/en-us/research/publication/docbank-a-benchmark-dataset-for-document-layout-analysis/?locale=ko-kr](https://www.microsoft.com/en-us/research/publication/docbank-a-benchmark-dataset-for-document-layout-analysis/?locale=ko-kr)
45. FUNSD: A Dataset for Form Understanding in Noisy Scanned Documents \- IEEE Xplore, accessed November 17,
    2025, [https://ieeexplore.ieee.org/document/8892998/](https://ieeexplore.ieee.org/document/8892998/)
46. XFUND: A Benchmark Dataset for Multilingual Visually Rich Form Understanding \- ACL Anthology, accessed November 17,
    2025, [https://aclanthology.org/2022.findings-acl.253/](https://aclanthology.org/2022.findings-acl.253/)
47. doc-analysis/XFUND: XFUND: A Multilingual Form Understanding Benchmark \- GitHub, accessed November 17,
    2025, [https://github.com/doc-analysis/XFUND](https://github.com/doc-analysis/XFUND)
48. XFUND: A Benchmark Dataset for Multilingual Visually Rich Form Understanding \- Microsoft, accessed November 17,
    2025, [https://www.microsoft.com/en-us/research/publication/xfund-a-benchmark-dataset-for-multilingual-visually-rich-form-understanding/](https://www.microsoft.com/en-us/research/publication/xfund-a-benchmark-dataset-for-multilingual-visually-rich-form-understanding/)
49. \[1911.01702\] DocParser: Hierarchical Structure Parsing of Document Renderings \- arXiv, accessed November 17,
    2025, [https://arxiv.org/abs/1911.01702](https://arxiv.org/abs/1911.01702)
50. SRFUND: A Multi-Granularity Hierarchical Structure Reconstruction Benchmark in Form Understanding, accessed November
    17,
    2025, [https://neurips.cc/media/neurips-2024/Slides/97841.pdf](https://neurips.cc/media/neurips-2024/Slides/97841.pdf)
51. SRFUND: A Multi-Granularity Hierarchical Structure Reconstruction Benchmark in Form Understanding | OpenReview,
    accessed November 17, 2025, [https://openreview.net/forum?id=66XJOENOrL](https://openreview.net/forum?id=66XJOENOrL)
52. TableBank: Table Benchmark for Image-based Table Detection and Recognition \- ACL Anthology, accessed November 17,
    2025, [https://aclanthology.org/2020.lrec-1.236.pdf](https://aclanthology.org/2020.lrec-1.236.pdf)
53. \[1903.01949\] TableBank: A Benchmark Dataset for Table Detection and Recognition \- arXiv, accessed November 17,
    2025, [https://arxiv.org/abs/1903.01949](https://arxiv.org/abs/1903.01949)
54. TableBank: Table Benchmark for Image-based Table Detection and ..., accessed November 17,
    2025, [https://aclanthology.org/2020.lrec-1.236/](https://aclanthology.org/2020.lrec-1.236/)
55. ICDAR 2019 Competition on Table Detection and Recognition (cTDaR) \- IEEE Xplore, accessed November 17,
    2025, [http://ieeexplore.ieee.org/document/8978120/](http://ieeexplore.ieee.org/document/8978120/)
56. ICDAR 2019 Competition on Table Detection and Recognition (cTDaR) \- Semantic Scholar, accessed November 17,
    2025, [https://www.semanticscholar.org/paper/ICDAR-2019-Competition-on-Table-Detection-and-Gao-Huang/9a2e147403c6e24fe9e782e85fb472f12891dc7d](https://www.semanticscholar.org/paper/ICDAR-2019-Competition-on-Table-Detection-and-Gao-Huang/9a2e147403c6e24fe9e782e85fb472f12891dc7d)
57. ICDAR 2019 cTDaR | Home, accessed November 17,
    2025, [https://cndplab-founder.github.io/cTDaR2019/](https://cndplab-founder.github.io/cTDaR2019/)
58. ICDAR 2019 Competition on Table Detection and Recognition (cTDaR) \- Zenodo, accessed November 17,
    2025, [https://zenodo.org/records/3239032](https://zenodo.org/records/3239032)
59. ICDAR 2021 Scientific Literature Parsing Competition \- Oracle Labs, accessed November 17,
    2025, [https://labs.oracle.com/pls/apex/f?p=94065:10:4399063482375:7649](https://labs.oracle.com/pls/apex/f?p=94065:10:4399063482375:7649)
60. ICDAR 2021 Competition on Scientific Literature Parsing \- GitHub, accessed November 17,
    2025, [https://raw.githubusercontent.com/ibm-aur-nlp/PubLayNet/master/ICDAR\_SLR\_competition/ICDAR\_2021\_Scientific\_Literature\_Parsing.pdf](https://raw.githubusercontent.com/ibm-aur-nlp/PubLayNet/master/ICDAR_SLR_competition/ICDAR_2021_Scientific_Literature_Parsing.pdf)
61. \[2106.14616\] ICDAR 2021 Competition on Scientific Literature Parsing \- arXiv, accessed November 17,
    2025, [https://arxiv.org/abs/2106.14616](https://arxiv.org/abs/2106.14616)
62. Marmot Dataset, accessed November 17,
    2025, [https://www.icst.pku.edu.cn/szwdclyjs/sjzy/index.htm](https://www.icst.pku.edu.cn/szwdclyjs/sjzy/index.htm)
63. Dataset for table recognition, accessed November 17,
    2025, [https://www.icst.pku.edu.cn/cpdp/sjzy/](https://www.icst.pku.edu.cn/cpdp/sjzy/)
64. TableNet: Deep Learning model for end-to-end Table detection and Tabular data extraction from Scanned Document
    Images \[Part-1\] \- Arun Sagar, accessed November 17,
    2025, [https://asagar60.medium.com/tablenet-deep-learning-model-for-end-to-end-table-detection-and-tabular-data-extraction-from-b1547799fe29](https://asagar60.medium.com/tablenet-deep-learning-model-for-end-to-end-table-detection-and-tabular-data-extraction-from-b1547799fe29)
65. PubTables-1M: Towards Comprehensive Table Extraction From Unstructured Documents \- CVF Open Access, accessed
    November 17,
    2025, [https://openaccess.thecvf.com/content/CVPR2022/papers/Smock\_PubTables-1M\_Towards\_Comprehensive\_Table\_Extraction\_From\_Unstructured\_Documents\_CVPR\_2022\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2022/papers/Smock_PubTables-1M_Towards_Comprehensive_Table_Extraction_From_Unstructured_Documents_CVPR_2022_paper.pdf)
66. opendatalab/OmniDocBench \- Workflow runs \- GitHub, accessed November 17,
    2025, [https://github.com/opendatalab/OmniDocBench/actions](https://github.com/opendatalab/OmniDocBench/actions)
67. CVPR Poster OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations, accessed
    November 17,
    2025, [https://cvpr.thecvf.com/virtual/2025/poster/34400](https://cvpr.thecvf.com/virtual/2025/poster/34400)
68. \[2412.07626\] OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- arXiv,
    accessed November 17, 2025, [https://arxiv.org/abs/2412.07626](https://arxiv.org/abs/2412.07626)
69. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- ResearchGate, accessed
    November 17,
    2025, [https://www.researchgate.net/publication/394650843\_OmniDocBench\_Benchmarking\_Diverse\_PDF\_Document\_Parsing\_with\_Comprehensive\_Annotations](https://www.researchgate.net/publication/394650843_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations)
70. OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations \- arXiv, accessed November
    17, 2025, [https://arxiv.org/html/2412.07626v1](https://arxiv.org/html/2412.07626v1)
71. opendatalab/OmniDocBench · Datasets at Hugging Face, accessed November 17,
    2025, [https://huggingface.co/datasets/opendatalab/OmniDocBench](https://huggingface.co/datasets/opendatalab/OmniDocBench)
72. Benchmarking the Most Reliable Document Parsing API \- Tensorlake, accessed November 17,
    2025, [https://www.tensorlake.ai/blog/benchmarks](https://www.tensorlake.ai/blog/benchmarks)
73. Advanced Layout Analysis Models for Docling \- arXiv, accessed November 17,
    2025, [https://arxiv.org/html/2509.11720v1](https://arxiv.org/html/2509.11720v1)
74. Logical Structure Recovery in Scholarly Articles with Rich Document Features \- Stanford NLP Group, accessed
    November 17,
    2025, [https://nlp.stanford.edu/\~lmthang/data/papers/ijdls-SectLabel.pdf](https://nlp.stanford.edu/~lmthang/data/papers/ijdls-SectLabel.pdf)
75. Benchmarking Document Parsing (and What Actually Matters) \- Unstructured, accessed November 17,
    2025, [https://unstructured.io/blog/benchmarking-document-parsing-and-what-actually-matters](https://unstructured.io/blog/benchmarking-document-parsing-and-what-actually-matters)