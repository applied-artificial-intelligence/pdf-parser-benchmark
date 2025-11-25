### **Introduction: The PDF-Bench Initiative**

1\. The Problem:

Our consulting practice consistently faces the challenge of selecting the right PDF parsing tool for client projects. Existing benchmarks are either too academic (focused only on arXiv), too shallow (raw text extraction), or proprietary. There is no public, reproducible benchmark that measures the quality of semantic Markdown (headings, tables, math, lists) from diverse, business-relevant documents.

2\. The Solution:

We will create and open-source PDF-Bench: a benchmark dataset and evaluation library. It will consist of a curated, legally-clean corpus of paired (PDF, Ground-Truth-Markdown) documents and a Python library to evaluate any parser (open-source or commercial) against it.

3\. The Goal (Thought Leadership):

By open-sourcing PDF-Bench, we establish ourselves as a leading, objective authority in the document intelligence space. It will serve as a powerful asset for content marketing, client conversations, and community building, directly demonstrating our expertise.

This document outlines the landscape, corpus design, evaluation metrics, and product roadmap.

---

## **1\. 🗺️ Landscape Review: Existing Benchmarks**

Our primary gap is the lack of a benchmark focused on **semantic Markdown** from **business documents**.

| Benchmark / Dataset | Data Sources | Ground Truth Format | Evaluation Metrics | Pros / Cons / Gaps for Us |
| :---- | :---- | :---- | :---- | :---- |
| **1.1. PDF→Markdown** |  |  |  |  |
| readoc (2024) | arXiv (1.1k), GitHub (500) | Markdown | Tree-Edit Distance (TED), readoc-score (F1-based) | **Pros:** Closest to our goal. Targets Markdown. Uses structural metrics. **Cons:** No business/corporate documents. readoc-score is complex. |
| **1.2. Layout Datasets** |  |  |  |  |
| DocLayNet | Finance, Patents, Legal, etc. (69k docs) | JSON (COCO-style bounding boxes) | mAP (Object Detection) | **Pros:** Excellent diversity in *business doc types*. Human-annotated. **Cons:** **No ground truth text or semantics**, only layout boxes. Cannot be directly used for PDF→Markdown. |
| PubLayNet, DocBank | PubMed, arXiv | XML, LaTeX (source) | mAP, F1 (layout) | **Pros:** Large scale. Paired with source (LaTeX). **Cons:** Layout-focused. Converting LaTeX to *our* canonical Markdown is still work. Academic-only. |
| OmniDocBench (2024) | Diverse (9 types) | JSON (text, layout, hierarchy) | F1, L1 (layout), TEDS (tables) | **Pros:** Very diverse. Good metrics (TEDS). **Cons:** Ground truth is a complex JSON, not Markdown. Not easily reusable as a "gold standard" for our specific task. |
| **1.3. Model-Driven** |  |  |  |  |
| Nougat (Dataset) | arXiv (subset) | LaTeX (source) | BLEU, ROUGE (on text), Edit Distance | **Pros:** Proved the LaTeX → Ground Truth pipeline is viable for academic docs. **Cons:** Academic-only. Text-level metrics are weak (miss structure). |
| Marker (Dataset) | Synthetic (Markdown, LaTeX) | Markdown, LaTeX | Edit Distance | **Pros:** Directly uses Markdown as ground truth. **Cons:** Dataset is not public. Methodology (synthetic generation) is sound, but we need to replicate it. |
| **1.4. Surveys** |  |  |  |  |
| Surveys (e.g., 2024\) | N/A | N/A | Taxonomies (logical, layout, text) | **Pros:** Provide best practices (e.g., use TEDS for tables, AST-based metrics for structure). **Cons:** No concrete, reusable assets. |

Key Takeaway:

No single benchmark meets our needs. We must synthesize a new one.

* **We will borrow the LaTeX → Markdown pipeline** from Nougat/readoc for academic docs.  
* **We will borrow the *document categories*** from DocLayNet for our business track.  
* **We will fill the primary gap:** creating a **business document corpus** with **Markdown ground truth**, which we will primarily achieve through *synthetic generation* and *curated public sources*.

---

## **2\. 🗂️ Corpus Design: A Phased Approach**

Our corpus will be built using a **"recipes-only"** approach for legal cleanliness. Our repository will contain scripts and metadata (URLs and hashes) for downloading public PDFs, along with our canonical ground-truth Markdown. We will only commit synthetic documents (source \+ PDF) that we create.

### **MVP Corpus (v0.1) \- Total: \~150 Documents**

| Category | Sub-Category | Count | Source | Ground Truth Generation |
| :---- | :---- | :---- | :---- | :---- |
| **Academic** | CS / Math | 30 | **arXiv** | pandoc or latexml on .tex source. |
|  | Biomedical | 20 | **PubMed Central** | Scrape/parse paired HTML/XML. |
| **Business** | Financial | 20 | **SEC EDGAR** | Paired 10-K (PDF \+ ixbrl HTML). |
|  | Government | 30 | **EU Publications** | Paired (PDF \+ HTML) reports. |
|  | **Synthetic** | 50 | Our team | Word/GDocs/Markdown templates → PDF. |

### **Extended Corpus (v1.0) \- Total: \~400 Documents**

* **Academic (100 docs):** Broader arXiv subjects (Physics, Econ) with more tables and complex math.  
* **Business (300 docs):**  
  * **Financial:** More 10-Ks, shareholder reports.  
  * **Government:** More EU, World Bank, and national government reports.  
  * **Consulting/Marketing:** (Synthetic) 50+ templates mimicking McKinsey/BCG/Vendor whitepapers (2-column, sidebars, charts).  
  * **Legal:** (Synthetic/Found) 20+ templates/examples of contracts (heavy on nested lists, footnotes).  
  * **Slide Decks:** 20+ examples (PowerPoint source → PDF, .pptx text as ground truth).

### **Optional Extension Track (v2.0)**

* **Scanned/OCR:** A small set (\~50) of scanned documents (from our synthetic set) to test OCR-inclusive pipelines.  
* **Forms/Invoices:** A synthetic set from templates for a "key-value" extraction sub-task.  
* **Multi-lingual:** Re-running synthetic templates in 3-5 other languages.

---

## **3\. 📝 Ground Truth Specification**

Our ground truth must be simple, precise, and parseable.

Baseline: GitHub Flavored Markdown (GFM).

### **3.1. Markdown Schema**

* **Headings:** \#\# Section (ATX-style). Levels must match semantic hierarchy.  
* **Lists:** Standard \*, 1\., and nested/mixed.  
* **Paragraphs:** Standard. Parsers will be penalized for merging distinct paragraphs or splitting one.  
* **Tables (Critical):**  
  * **Simple Tables:** Must be GFM syntax: | A | B | \\n |---|---| \\n | 1 | 2 |.  
  * **Complex Tables (Merged Cells):** GFM does not support this. **Decision:** We will embed complex tables as **inline HTML** (\<table\>...\</table\>) within the Markdown. This is valid Markdown and the only robust way to represent structure.  
* **Math (Critical):**  
  * **Inline:** $E \= mc^2$ (Pandoc/LaTeX-style).  
  * **Display:** $$\\sum\_{i=0}^{n} ...$$  
* **Figures:** \!\[Figure 1: Caption text.\](images/figure1.png). The path must be canonical.  
* **Code Blocks:** GFM fenced blocks with language hints (e.g., \`\`\`python).  
* **Footnotes:** GFM-style: \[^1\] and \[^1\]: Note text.  
* **Headers/Footers/Page Numbers:** These must be **omitted** from the ground truth. They are layout artifacts, not semantic content.

### **3.2. Normalization Rules (for Evaluation)**

To ensure fair comparison, all output (ground truth and prediction) is normalized before metric calculation:

1. **Whitespace:** Collapse all horizontal whitespace, trim newlines from start/end of lines.  
2. **Math:** Regex-based normalization (e.g., remove \\left, \\right, extra spaces around operators).  
3. **Tables:** Parse GFM/HTML tables into a canonical 2D-array-of-strings representation.  
4. **AST:** Parse both Markdown files into an Abstract Syntax Tree (AST) using markdown-it-py or similar.

### **3.3. Metadata Schema (per-document meta.yaml)**

YAML

doc\_id: "biz-fin-sec-001"  
pdf\_url: "\[https://www.sec.gov/\](https://www.sec.gov/)..."  
pdf\_hash: "sha256:..."  
source\_url: "https..." \# (e.g., to HTML version)  
license: "US-Gov-Public-Domain"

category: "business"  
sub\_category: "financial-report"  
layout\_class: "multi-column"  
page\_count: 52  
language: "en"

tags:  
  \- "complex-tables"  
  \- "footnotes"  
  \- "has-figures"

---

## **4\. 📐 Evaluation Design**

We will provide a dashboard of metrics, not one "magic number."

### **4.1. Core Tasks**

1. **Full Document Parsing:** (PDF File) → (Markdown String). This is the primary task.  
2. **Sub-Task: Table Extraction:** Extract all \<table\> or GFM table blocks and run table-specific metrics.  
3. **Sub-Task: Math Extraction:** Extract all $..$ and $$..$$ blocks and run math-specific metrics.

### **4.2. Core Metrics**

| Level | Metric | Implementation | Purpose |
| :---- | :---- | :---- | :---- |
| **Text** | **Normalized Edit Distance** | Levenshtein on normalized, text-only content. | Measures raw content accuracy (ignoring structure). |
|  | **chrF++** | sacrebleu | Robust, token-free text similarity. |
| **Structure** | **AST Tree-Edit Distance (TED)** | apted on markdown-it-py ASTs. | **Our core metric.** Measures structural fidelity (e.g., did a heading become bold text?). |
|  | **Node F1 Score** | F1 on node types (e.g., heading\_l2, list\_item). | "How many headings did you find, at the right level?" |
| **Table** | **TEDS** (Tree-Edit-Distance) | table-structure-metric | SOTA for table *structure* (merged cells, etc.). |
|  | **Cell Content F1** | F1 on cell text. | "Did you get the *numbers* in the table right?" |
| **Math** | **Exact Match (Normalized)** | String equality on normalized LaTeX. | "How many equations are perfect?" |
|  | **BLEU Score** | sacrebleu on LaTeX token sequences. | "How semantically similar are the garbled equations?" |
| **Speed** | **Time per Page (s)** | time.perf\_counter() | Practicality/throughput metric. |
| **Cost** | **Cost per 1k Pages ($)** | (Configurable) | **Crucial for business decisions** (e.g., Textract vs. Marker). |

### **4.3. Systems Under Test (Abstraction)**

We will use an AbstractParser base class. Adapters will be in systems/.

Python

class AbstractParser:  
    """Base class for all PDF parsers."""  
    def \_\_init\_\_(self, name: str, config: dict):  
        self.name \= name  
        self.config \= config \# API keys, model paths, etc.

    def parse(self, pdf\_path: str, doc\_id: str) \-\> str:  
        """Takes a PDF path, returns a Markdown string."""  
        raise NotImplementedError

**v0 Adapters:**

* **Open Source:** MarkerParser, NougatParser, UnstructuredParser, PyMuPDFParser (as a baseline).  
* **Commercial:** GoogleDocAIParser, AWSTextractParser, AzureFormRecognizerParser. (Requires user to provide API keys via env vars).

### **4.4. Reporting**

The CLI will generate:

1. **results.json:** Raw, per-doc, per-system, per-metric scores.  
2. **report.html / report.md:** A human-readable report with:  
   * **Main Leaderboard:** Overall weighted score (e.g., 0.4*AST-TED \+ 0.3*TEDS \+ ...).  
   * **Breakdown by Category:** (Academic vs. Business-Financial vs. Business-Synthetic).  
   * **Breakdown by Metric:** (Structure vs. Table vs. Math vs. Speed).  
   * **Common Failure Modes:** Top 5 errors (e.g., "Merged Paragraphs," "Dropped Tables").

---

## **5\. 📦 Library & Repository Design (PRD)**

Product Name: PDF-Bench

Mission: An open, reproducible, and business-relevant benchmark for PDF-to-Semantic-Markdown conversion.

### **5.1. Scope**

* **IN (v0.1):**  
  * MVP Corpus (v0.1) recipes and ground truth.  
  * Evaluation library (pdfbench).  
  * CLI for running benchmarks and generating reports.  
  * Adapters for 3-4 OS parsers and 2-3 Commercial APIs.  
  * Dataset Card and CONTRIBUTING.md.  
* **OUT (v0.1):**  
  * A web-based UI / leaderboard (v1.0+).  
  * Model training.  
  * Annotation tooling.  
  * Full OCR/scanned document track (v2.0).

### **5.2. User Personas**

1. **Alice (Internal Consultant):**  
   * **Need:** Quickly determine the best (cost/quality) parser for a new client's financial reports.  
   * **Action:** pdfbench run \--subset biz-financial \--systems marker,textract,goog-dai \--cost-estimate  
   * **Result:** Gets a report showing Textract has the best TEDS score, but Marker is 90% as good for 0 cost.  
2. **Bob (External Practitioner):**  
   * **Need:** Choose a PDF parser for his RAG pipeline.  
   * **Action:** Reads our blog post ("We benchmarked 5 PDF parsers..."), clones PDF-Bench, runs pdfbench run \--systems all \--subset all.  
   * **Result:** Trusts our firm's recommendation because it's backed by a tool he can run himself.  
3. **Carol (Researcher):**  
   * **Need:** Evaluate her new parsing model against SOTA.  
   * **Action:** Writes MyParser(AbstractParser), adds it to the config.  
   * **Result:** Runs pdfbench report and gets metrics to publish in her paper.

### **5.3. Architecture & Repository Structure**

/pdfbench-suite/  
├── pdfbench/              \# The core Python library  
│   ├── \_\_init\_\_.py  
│   ├── main.py            \# CLI entrypoint (typer/click)  
│   ├── core.py            \# BenchmarkRunner, AbstractParser  
│   ├── systems/           \# Adapters: marker\_parser.py, textract\_parser.py  
│   ├── metrics/           \# Metric implementations: ast\_ted.py, teds.py  
│   └── report.py          \# Report generation  
│  
├── corpus/                \# Corpus definition files  
│   ├── academic/  
│   │   ├── arxiv\_cs\_12345.yaml  
│   │   └── pubmed\_54321.yaml  
│   ├── business/  
│   │   └── sec\_report\_001.yaml  
│   └── synthetic/  
│       ├── template\_01.md  
│       └── template\_01.pdf  
│  
├── ground\_truth/          \# The canonical ground truth files  
│   ├── academic/  
│   │   ├── arxiv\_cs\_12345.md  
│   │   └── pubmed\_54321.md  
│   └── business/  
│       └── sec\_report\_001.md  
│  
├── benchmarks/            \# Example benchmark configurations  
│   ├── mvp\_all.yaml  
│   ├── business\_only.yaml  
│   └── quick\_test.yaml  
│  
├── builders/              \# Scripts to build/re-build corpus  
│   ├── download\_corpus.py  
│   ├── build\_synthetic.py  
│   └── build\_gt\_from\_latex.py  
│  
├── reports/               \# (Git-ignored) Generated output  
│   └── report-2025-11-14.html  
│  
├── pyproject.toml  
├── README.md  
├── LICENSE  
└── CONTRIBUTING.md

### **5.4. APIs & CLI**

**Python API:**

Python

from pdfbench import BenchmarkRunner, load\_config  
config \= load\_config("benchmarks/business\_only.yaml")  
runner \= BenchmarkRunner(config)  
results \= runner.run()  
runner.save\_report(results, "reports/my\_report.html")

**CLI:**

Bash

\# List available datasets and systems  
$ pdfbench list datasets  
$ pdfbench list systems

\# Run a benchmark defined in a config file  
$ pdfbench run \--config benchmarks/mvp\_all.yaml \--output reports/mvp\_run

\# Run a quick, ad-hoc benchmark  
$ pdfbench run \--subset academic \--systems marker,nougat \--limit 10

\# Just generate a report from existing results  
$ pdfbench report \--results reports/mvp\_run.json \--format html

### **5.5. Performance & Cost**

* The library will aggressively cache parser outputs in a .cache/ directory.  
* API adapters (Textract, etc.) will have rate-limiting and retry logic.  
* The BenchmarkRunner will support parallel execution (\--workers 4).  
* Cost estimation will be based on user-provided pricing (e.g., $1.50 / 1000 pages) and page counts.

### **5.6. Governance**

* **Library:** Apache 2.0 license.  
* **Dataset (Our Synthetic):** CC-BY-SA 4.0 license.  
* **Dataset (Found):** "Recipes-only." The corpus/\*.yaml files will link to the original sources and state their licenses. We do not redistribute any PDFs we don't own.  
* **Documentation:** We will maintain a "Datasheet for Datasets" (DATASET\_CARD.md) explaining motivation, composition, and risks.  
* **Versioning:** pdfbench library will use SemVer. The corpus will be versioned (e.g., v0.1, v1.0).

---

## **6\. 📢 Marketing & Community Strategy**

This is a thought-leadership play. The goal is to become the trusted, go-to resource.

### **6.1. Positioning**

* **Against Academic Benchmarks (readoc):** "PDF-Bench is the benchmark for *practitioners*. While academic sets test A, PDF-Bench tests B, C, and D, which are critical for business (e.g., multi-column financial tables, not just LaTeX math)."  
* **Against Vendor Blogs ("Top 5..."):** "Stop relying on marketing. PDF-Bench provides the code, the data, and the metrics so you can **reproduce the results yourself.** We're the *objective* standard."  
* **Key Messages:** **Transparent. Reproducible. Business-Relevant.**

### **6.2. Content Plan (Initial 60 Days)**

1. **Launch Blog Post:** "Introducing PDF-Bench: A Practical, Open-Source Benchmark for PDF-to-Markdown."  
   * **Angle:** Announce the problem, our solution, and the v0.1 release. Show a simple leaderboard for the MVP corpus. Call for community feedback.  
2. **Technical Deep Dive \#1:** "The Hardest Part of Benchmarking: Building Ground Truth for Business PDFs."  
   * **Angle:** Detail our synthetic pipeline, our use of SEC/EU data, and our HTML-in-Markdown table strategy. This *shows the work* and builds trust.  
3. **Technical Deep Dive \#2:** "Why 'Text Accuracy' is the Wrong Metric: Evaluating Document Structure with ASTs and TEDS."  
   * **Angle:** Explain our metrics (AST-TED, TEDS). This positions us as experts who think deeper than the competition.  
4. **Results Post:** "The PDF-Bench v0.1 Leaderboard: Marker vs. Nougat vs. Google vs. AWS on Business Reports."  
   * **Angle:** A neutral, data-driven comparison. We *fairly* show the pros/cons of each, including cost and speed. (This will be a high-traffic, inbound-link-generating post).

### **6.3. Community & Contributions**

The CONTRIBUTING.md will provide clear instructions:

* **How to Add a New Parser:** Provide a MyParser.py adapter and a systems.yaml entry.  
* **How to Add a New Document:** Submit a new corpus/my\_doc.yaml (with URL/license) and ground\_truth/my\_doc.md.  
* **How to Suggest a Metric:** Open an issue with a link to the implementation.

By making it easy to contribute, PDF-Bench grows with the community, continuously reinforcing our position as the maintainer of a vital industry tool.
