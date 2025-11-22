# Measurement Transparency & Benchmark Credibility Analysis

**Date**: 2025-11-20
**Purpose**: Document what we measure, how we measure it, what we don't measure, and justify our corpus choices

---

## 1. Current Measurement: What "88% Similarity" Actually Means

### 1.1 The Metric: Normalized Levenshtein Edit Distance

**What we compute**:
- **edit_similarity** = 1.0 - (edit_distance / max(len(ground_truth), len(prediction)))
- Uses **Levenshtein distance**: minimum number of single-character edits (insertions, deletions, substitutions)
- **Normalized** by maximum length of the two strings
- Returns score in [0.0, 1.0] where 1.0 = identical, 0.0 = completely different

**Example**:
```python
ground_truth = "hello world"  # 11 characters
prediction = "helo wrld"       # 9 characters
edit_distance = 2              # missing 'l' and 'o'
similarity = 1.0 - (2 / 11) = 0.818 = 81.8%
```

### 1.2 Text Normalization Applied

Before computing similarity, we normalize BOTH texts to handle superficial differences:

**Default normalizations** (applied to all comparisons):
1. **Unicode NFC normalization**: Canonical character composition
2. **Whitespace normalization**:
   - CRLF/CR → LF
   - Tabs → spaces
   - Multiple spaces → single space
   - Trim leading/trailing whitespace per line
   - Collapse multiple blank lines → single blank line
3. **Quote normalization**: Smart quotes ("") → straight quotes ("")

**Optional normalizations** (NOT currently used):
- Hyphen normalization: en-dash/em-dash → ASCII hyphen
- Ligature normalization: fi/fl → fi/fl

**Why this matters**:
- PDFs may use different Unicode encodings for the same character
- Extractors produce different whitespace (tabs vs spaces, line endings)
- Quote characters vary by extraction method
- **Without normalization**: parsers penalized for superficial differences
- **With normalization**: focuses on actual content differences

### 1.3 What This Metric Measures Well

✅ **Character-level accuracy**: How many characters match after normalization
✅ **Overall content fidelity**: Did the parser get the text right?
✅ **Robustness to whitespace variations**: Normalized before comparison
✅ **Simple to understand**: "88% of characters are correct" is intuitive

### 1.4 What This Metric Does NOT Measure

❌ **Document structure**: Headers, paragraphs, lists, sections
❌ **Table structure**: Rows, columns, cell alignment, merged cells
❌ **Reading order**: Multi-column documents, sidebars, callouts
❌ **Semantic correctness**: "$1,250" → "$1250" is wrong but only -2 characters
❌ **Layout preservation**: Bold, italic, indentation, visual hierarchy
❌ **Element-level precision**: Did it get ALL the headers? ALL the list items?

**Critical example where this fails**:
```markdown
# Ground Truth
## Section 1
Paragraph A

## Section 2
Paragraph B

# Parser Output (WRONG but 95% similar)
Section 1
Paragraph A

Section 2
Paragraph B
```
Parser lost ALL structure (no headers) but text similarity is ~95% because the words are still there!

---

## 2. Advanced Metrics: What We COULD Measure (Already Implemented!)

### 2.1 Available Metrics (Not Currently Used in Benchmarks)

The codebase already implements 6 sophisticated metrics, but they're **not enabled in benchmark configs**:

#### **A. Structure Metrics**

**tree_similarity** (`pdf_bench/metrics/tree_edit_distance.py`):
- Parses markdown to AST (Abstract Syntax Tree)
- Computes tree edit distance on document structure
- **Measures**: Heading hierarchy, list nesting, document organization
- **Returns**: Similarity score [0.0, 1.0] based on structural match

**element_f1** (`pdf_bench/metrics/element_f1.py`):
- Counts document elements by type (headings, paragraphs, lists, tables, code blocks)
- Computes precision, recall, F1 per element type
- **Measures**: Did parser find all the headers? All the tables? All the lists?
- **Returns**: ElementScores(precision, recall, f1) per element type

#### **B. Table Metrics**

**teds** (`pdf_bench/metrics/teds.py`):
- **Tree Edit Distance-based Similarity** for table structure
- Converts markdown/HTML tables to tree representation
- Measures structural correctness: rows, columns, cells, spanning
- **Gold standard** for table evaluation in academic literature
- **Returns**: TEDS score [0.0, 1.0]

**cell_content_f1** (`pdf_bench/metrics/cell_content_f1.py`):
- Compares table cell contents (precision/recall/F1)
- **Measures**: Did parser get the table data correct?
- **Returns**: CellF1Scores(precision, recall, f1, accuracy)

#### **C. Text Metrics**

**chrf++** (`pdf_bench/metrics/text_metrics.py`):
- Character n-gram F-score with word n-grams
- More sophisticated than simple edit distance
- **Measures**: Character-level + word-level similarity
- **Used in**: Machine translation evaluation
- **Returns**: Score [0.0, 100.0]

**character_error_rate** (CER) (`pdf_bench/metrics/edit_distance.py`):
- edit_distance / len(ground_truth)
- Standard metric for OCR evaluation
- **Returns**: Error rate (can exceed 1.0)

#### **D. Math Metrics**

**latex_f1** (`pdf_bench/metrics/latex_matching.py`):
- Extracts LaTeX expressions from markdown
- Computes precision/recall/F1 on equation matching
- **Measures**: Did parser correctly extract equations?
- **Returns**: LaTeXF1Scores(precision, recall, f1, accuracy)

### 2.2 Why Aren't We Using These?

**Historical reason**: Benchmark configs deleted during cleanup specified only `edit_similarity`

**Old benchmark config** (benchmarks/mvp_all.yaml, deleted):
```yaml
metric_config:
  metrics:
    - edit_distance
    - edit_similarity
    - character_error_rate
    - chrf++
    - tree_edit_distance
    - tree_similarity
    - element_f1
    - teds
    - teds_with_content
    - cell_content_f1
    - latex_f1
```

**Current issue**: All advanced metrics implemented but NOT configured in any active benchmark!

### 2.3 Enabling Multi-Dimensional Evaluation

**What we should do**:
1. Create new benchmark config with all metrics
2. Run comprehensive evaluation
3. Report per-metric scores in results
4. Create radar charts showing parser strengths/weaknesses

**Example output**:
```
Marker+Ollama Results (33 synthetic docs):
- edit_similarity:      88.17%  ✅ Best overall
- tree_similarity:      84.3%   ✅ Good structure
- element_f1:           0.89    ✅ Found most elements
- teds (tables):        0.76    ⚠️  Tables struggle
- chrf++:               86.2    ✅ Good character/word
- latex_f1:             0.00    ❌ No equations in corpus
```

---

## 3. External Benchmarks: Why We're Not Using Them (Yet)

### 3.1 Available Benchmarks (NOT OCR-only!)

Your concern: "I'm surprised that the external benchmarks all require OCR"

**Clarification**: They DON'T require OCR - they're PDF parsing benchmarks, but with different annotation formats that need conversion.

| Benchmark | Domain | Size | Ground Truth Format | Integration Effort |
|-----------|--------|------|--------------------|--------------------|
| **OmniDocBench** | Diverse business | 1.3k pages | JSON (block + span + HTML) | **Low** - JSON → Markdown conversion |
| **DocLayNet** | Finance, legal | 80k pages | COCO bounding boxes | **High** - Need linearization heuristic |
| **FinTabNet** | Financial tables | 112k tables | PDF + HTML tables | **Medium** - Table-only, not full docs |
| **Kleister NDA** | Legal contracts | 3.2k pages | PDF + entities | **Medium** - HTML origin, need conversion |
| **DocILE** | Invoices | 6.7k docs | JSON (KILE/LIR) | **Low** - JSON → Markdown |
| **VRDU** | Forms | 2k docs | JSON entities | **Medium** - Key-value extraction |

### 3.2 Why We Can't Use Them Immediately

**Not OCR issue - it's ground truth format mismatch**:

1. **OmniDocBench**: Provides JSON annotations, NOT ready-to-use Markdown
   - Have: `{"type": "paragraph", "bbox": [x1, y1, x2, y2], "text": "..."}`
   - Need: Markdown file with headers, lists, tables
   - **Conversion required**: Write JSON → Markdown converter
   - **Status**: Attempted, couldn't parse annotation format

2. **DocLayNet**: Provides bounding boxes only
   - Have: COCO-format bounding boxes for 11 element types
   - Need: Linear markdown with correct reading order
   - **Conversion required**: Complex linearization algorithm (top-down, left-right, column-aware)
   - **Challenge**: Reading order ambiguous from boxes alone

3. **FinTabNet**: Table-only benchmark
   - Provides HTML ground truth for tables
   - **Use case**: Evaluate table extraction only, not full documents
   - **Integration**: Could extract table-heavy pages from our business docs and use TEDS metric

4. **Kleister NDA**: Entity-based annotations
   - Provides entities (dates, parties, amounts) NOT full markdown
   - **Use case**: Information extraction, not parsing
   - **Note**: Documents are born-digital (HTML → PDF), so HTML source exists

### 3.3 Why OmniDocBench Failed (Specifically)

From handoff document: "We were unable to really get the annotations. We failed at a bunch of basic things. We were unable to understand how the annotations work and how we could actually utilize this."

**What happened**:
1. Downloaded OmniDocBench dataset
2. Tried to parse JSON annotations
3. Format was undocumented or unclear
4. Couldn't map JSON structure to usable Markdown ground truth
5. **Gave up** and archived it

**What we should have done**:
- Read OmniDocBench paper/documentation
- Examine annotation examples
- Write JSON → Markdown converter
- Validate on 1-2 examples before scaling

### 3.4 The "Why Roll Your Own" Defense

**Anticipated criticism**: "Why generate synthetic corpus when established benchmarks exist?"

**Answer**: We're not avoiding external benchmarks - we're **complementing** them

**Justification**:

1. **Immediate availability**: External benchmarks need conversion (weeks of work)
2. **Perfect ground truth**: We KNOW synthetic corpus is correct (Markdown → PDF → Markdown)
3. **Controlled testing**: Each doc tests specific features (tables, lists, columns)
4. **Business relevance**: Generated invoices/legal/HR docs match real use cases
5. **Rapid iteration**: Can generate 100 docs in 60 seconds to fill gaps

**Two-track approach**:
- **Track 1** (done): Synthetic + generated business corpus for immediate results
- **Track 2** (future): Integrate OmniDocBench/DocLayNet for academic credibility

**Validation strategy**:
1. Show sample PDFs + ground truth (visual inspection)
2. Document generation process (reproducible)
3. Expand corpus to 500+ docs (statistical significance)
4. Add external benchmarks (when converted) as Phase 3

---

## 4. Synthetic Corpus Quality Assessment

### 4.1 Realism Check

**Invoices** (100 documents):
- ✅ Real company names (Faker library)
- ✅ Realistic addresses, phone numbers
- ✅ Proper invoice structure (header, line items, totals)
- ✅ Tax calculations (8.2% Texas sales tax)
- ✅ Multiple templates (enterprise, simple, detailed)
- ✅ Varied line item counts (5-15 items)
- ❓ Numbers too large ($20M invoices) - may need adjustment

**Legal Documents** (108 documents):
- ✅ Proper nested numbering (1.0.1, 5.2.1, etc.)
- ✅ Legal language (WHEREAS, NOW THEREFORE, IN WITNESS WHEREOF)
- ✅ Standard clauses (IP, indemnification, governing law)
- ✅ Multiple document types (NDA, consulting, employment)
- ✅ Signature blocks
- ✅ Real company/person names

**HR Documents** (34 documents):
- ✅ Performance reviews with rating scales
- ✅ Job descriptions with requirements
- ✅ Offer letters with comp packages
- ✅ Realistic job titles and skills

**Synthetic Tests** (33 documents):
- ✅ Hand-crafted for feature coverage
- ✅ Labeled structures (TABLE-01, LIST-03)
- ✅ Diagnostic capability (know exact failure points)
- ⚠️ Not realistic - designed for testing, not production similarity

### 4.2 Validation: Visual Inspection Needed

**Action item**: Show sample PDFs to users to confirm they "look real"

**Files to share**:
- `corpus/business/invoices/pdfs/invoice_001.pdf`
- `corpus/business/legal/pdfs/legal_cons_007.pdf`
- `corpus/business/hr/pdfs/hr_perf_001.pdf`

**Questions to answer**:
1. Do these look like documents from your company?
2. Would you expect a parser to handle these?
3. What's missing? (logos, signatures, complex formatting?)

### 4.3 Coverage Expansion (Low-Hanging Fruit)

To increase credibility, we can cheaply generate:

**Broader coverage** (from strategic document):
- SOPs (500 docs): Deep nested lists (1.1.1.1.a.i)
- Resumes (300 docs): Multi-column, mixed formatting
- Meeting minutes (200 docs): Mixed lists, tables, action items
- Technical specs (200 docs): Code blocks, diagrams, equations

**Cost**: ~10 minutes per document type × 4 types = 40 minutes of dev work
**Benefit**: 1,200 additional documents, broader feature coverage
**Risk**: Lower quality than hand-crafted synthetic tests

---

## 5. Measurement Gaps & Recommendations

### 5.1 Critical Gaps in Current Approach

| Aspect | Currently Measured? | Impact | Fix |
|--------|-------------------|--------|-----|
| **Overall text accuracy** | ✅ Yes (edit_similarity) | High | None needed |
| **Document structure** | ❌ No (tree_similarity available but unused) | **Critical** | Enable metric |
| **Table structure** | ❌ No (TEDS available but unused) | **Critical** | Enable metric |
| **Element detection** | ❌ No (element_f1 available but unused) | High | Enable metric |
| **Reading order** | ❌ No | **Critical** | Need new metric |
| **Semantic correctness** | ❌ No | Medium | Future work |
| **Layout preservation** | ❌ No | Low | Not priority |

### 5.2 Immediate Actions (This Week)

**Priority 1: Enable Advanced Metrics**
```bash
# Create comprehensive benchmark config
cat > benchmarks/comprehensive.yaml <<EOF
metric_config:
  metrics:
    - edit_similarity     # Overall accuracy
    - tree_similarity     # Structure preservation
    - element_f1          # Element detection
    - teds                # Table structure
    - chrf++              # Character/word n-grams
    - latex_f1            # Equation extraction
EOF
```

**Priority 2: Run Multi-Metric Evaluation**
```bash
python -m pdf_bench benchmarks/comprehensive.yaml \
  --parsers marker_ollama,pypdfium2,google_document_ai
```

**Priority 3: Document Results Properly**
- Create per-metric leaderboards
- Radar charts showing parser trade-offs
- Document what each metric measures
- Explain why scores differ

### 5.3 Short-Term Actions (Next 2 Weeks)

**Priority 4: Validate Synthetic Corpus**
- Extract 10-15 sample PDFs
- Share with colleagues/users for visual inspection
- Document feedback
- Adjust generation if needed (e.g., invoice amounts, legal language)

**Priority 5: Expand Corpus Coverage**
- Generate SOP corpus (500 docs, deep nesting)
- Generate resume corpus (300 docs, multi-column)
- Document generation process
- Run benchmarks on expanded corpus

**Priority 6: Document Measurement Choices**
- Write "Measurement Methodology" doc
- Explain why edit_similarity + tree_similarity + TEDS
- Compare to academic benchmarks (cite papers)
- Justify synthetic corpus approach

### 5.4 Medium-Term Actions (1-2 Months)

**Priority 7: Integrate External Benchmark**
- Choose one: OmniDocBench (best fit for Markdown evaluation)
- Study annotation format carefully
- Write JSON → Markdown converter
- Validate on 5-10 examples before scaling
- Run all parsers on converted corpus
- Compare results to synthetic corpus

**Priority 8: Reading Order Metric**
- Implement column-aware reading order evaluation
- Annotate multi-column docs with correct token sequence
- Compute sequence alignment score
- Critical for academic papers, newsletters

**Priority 9: Semantic Correctness**
- Number extraction accuracy (tables, financial data)
- Date extraction accuracy
- Entity preservation (names, places)
- Measure downstream task impact (RAG quality, search)

---

## 6. Response to Specific Concerns

### 6.1 "How is 87% similarity actually computed?"

**Answer**: Normalized Levenshtein edit distance on text content after normalization
- Measures character-level accuracy
- Simple and interpretable
- But: doesn't measure structure, tables, reading order
- **Fix**: Enable tree_similarity, element_f1, TEDS metrics

### 6.2 "How do we evaluate specifics like layout, headings, tables, lists?"

**Answer**: We DON'T currently, but we CAN
- Layout/headings: tree_similarity (implemented, unused)
- Tables: TEDS (implemented, unused)
- Lists: element_f1 (implemented, unused)
- **Fix**: Enable metrics in benchmark config, re-run

### 6.3 "How well does it do with the order of text in two-column format?"

**Answer**: We DON'T measure this explicitly
- edit_similarity penalizes wrong order, but not specifically
- Reading order errors look like character mismatches
- **Fix**: Need dedicated reading order metric (not implemented)
- **Workaround**: Manually inspect multi-column docs for catastrophic failures

### 6.4 "Why are you generating your own corpus when established benchmarks exist?"

**Answer**: Time-to-value + perfect ground truth + business relevance
- External benchmarks need weeks of conversion work
- Synthetic corpus has perfect ground truth (we generated it)
- Generated business docs match real use cases (invoices, legal, HR)
- **Not avoiding** external benchmarks - adding them in Phase 3

### 6.5 "How do we justify rolling our own when everybody recommends using the status quo?"

**Three-pronged defense**:

1. **Complementary, not replacement**
   - "We use synthetic corpus for rapid iteration and perfect ground truth"
   - "We're adding OmniDocBench in Phase 3 for academic validation"
   - "Both approaches have value - controlled testing + real-world diversity"

2. **Perfect ground truth advantage**
   - "Synthetic corpus: Markdown → PDF → Markdown (we KNOW it's correct)"
   - "External benchmarks: Manual annotation (human error possible)"
   - "Generated corpus: Reproducible, scalable, no annotation cost"

3. **Business relevance**
   - "Our generated invoices/legal/HR match real business use cases"
   - "External benchmarks may not cover our specific document types"
   - "Can generate 100 docs in 60 seconds to fill any gap"

**Combined strategy**:
- **Now**: 280 docs (synthetic + generated business corpus)
- **Phase 2**: Expand to 1,000+ docs (add SOPs, resumes, meeting minutes)
- **Phase 3**: Add OmniDocBench (1.3k pages) for academic credibility
- **Phase 4**: Add DocLayNet/FinTabNet for specialized evaluation

---

## 7. Credibility Checklist

To address critics who say "this isn't rigorous":

### 7.1 Transparency
- ✅ Document exact metric computation (this document)
- ✅ Explain normalization applied
- ✅ Acknowledge what we don't measure
- ✅ Show sample ground truth files
- ✅ Document generation process

### 7.2 Multi-Dimensional Evaluation
- ❌ Enable advanced metrics (tree_similarity, TEDS, element_f1)
- ❌ Report per-metric scores
- ❌ Create radar charts showing trade-offs
- ❌ Document metric selection justification

### 7.3 Corpus Quality
- ✅ Generated realistic business documents
- ❌ Visual validation with sample PDFs
- ❌ Expand coverage (SOPs, resumes, etc.)
- ❌ Document generation methodology

### 7.4 External Validation
- ❌ Integrate at least one external benchmark (OmniDocBench)
- ❌ Compare results to published baselines
- ❌ Cite academic papers on metrics (TEDS, chrF++)

### 7.5 Statistical Rigor
- ✅ 280 documents (reasonable sample size)
- ❌ Report confidence intervals
- ❌ Per-corpus type results (invoices vs legal vs HR)
- ❌ Statistical significance testing

---

## 8. Recommended Next Steps

**Immediate (today)**:
1. Create comprehensive benchmark config with all metrics
2. Run on marker_ollama, pypdfium2, google_document_ai
3. Analyze per-metric results

**This week**:
4. Extract sample PDFs for visual validation
5. Document measurement methodology
6. Write "Why Synthetic Corpus" defense

**Next 2 weeks**:
7. Expand corpus (SOPs, resumes)
8. Generate per-metric leaderboards
9. Create radar charts

**1-2 months**:
10. Integrate OmniDocBench
11. Implement reading order metric
12. Write comprehensive results paper

---

**Bottom line**: We have excellent infrastructure (6 advanced metrics implemented!) but aren't using it. Enabling multi-dimensional evaluation + documenting methodology + integrating one external benchmark will address all credibility concerns.
