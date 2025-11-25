# Ground Truth Methodology and Metric Limitations

*Last Updated: 2025-11-22*

## Overview

This document explains how ground truth is created for PDF benchmarking and why it fundamentally affects metric reliability. **This is critical knowledge for interpreting benchmark results.**

## The Ground Truth Problem

### What You Measure Is What You Optimize For

PDF-to-Markdown benchmarks evaluate parser output against "ground truth" - a reference markdown representation of what the document *should* look like. However:

1. **Ground truth quality directly determines metric meaningfulness**
2. **Flawed ground truth biases results toward parsers that match the flaws**
3. **A parser producing objectively better structure can score WORSE if it doesn't match the ground truth**

### Real Example: Element F1 Paradox

From our CUAD benchmark analysis comparing the same legal contract:

**Parser A (unstructured)** - Element F1 score: 0.48
```markdown
# Source: COMPANY...
# WHEREAS, ...
# NOW THEREFORE...
[wall of text, 23 lines total]
```

**Parser B (marker)** - Element F1 score: 0.34
```markdown
# EXCLUSIVE LICENSE AGREEMENT
## 1. GRANT AND SCOPE OF LICENSE
### 1.1 Grant of License
Licensor hereby grants...

### 1.2 Goodwill
Licensee expressly recognizes...

- **(a)** use the Licensed Technology
- **(b)** manufacture products
- **(c)** sell products
```

Parser B has **objectively better structure** (proper heading hierarchy, list items, clear sections) but scores 30% LOWER because the ground truth was too simple.

## Ground Truth Sources by Corpus

### CUAD Legal Contracts (75 documents)

**Source**: [CUAD (Contract Understanding Atticus Dataset)](https://www.atticusprojectai.org/cuad) - A dataset for legal contract review created by The Atticus Project.

**Paper**: ["CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review"](https://arxiv.org/abs/2103.06268) (NeurIPS 2021)
- **Authors**: Dan Hendrycks, Collin Burns, Anya Chen, Spencer Ball
- **Organization**: The Atticus Project, Inc.
- **Dataset**: 510 commercial legal contracts with 13,000+ expert annotations for 41 clause types
- **GitHub**: [TheAtticusProject/cuad](https://github.com/TheAtticusProject/cuad)
- **HuggingFace**: [theatticusproject/cuad-qa](https://huggingface.co/datasets/theatticusproject/cuad-qa)

**Important Note**: CUAD was designed for **clause extraction** (Q&A task), not document structure recovery. The text was extracted to support NLP contract review, where clause content matters more than visual formatting.

**Critical Issue Discovered**: The CUAD source text is **structurally flattened** at the dataset level:
- Average ~1,458 characters per line (entire pages merged into single lines)
- Section markers like 1.1, 1.2, 1.3 concatenated without line breaks
- Structure cannot be recovered without re-extracting from original PDFs

```
Example: A 65,651 character document has only 45 non-empty lines.
Each "line" contains multiple merged paragraphs and section definitions.
```

**Original Ground Truth Method** (`builders/build_cuad_corpus.py::txt_to_markdown()`):
- All-caps lines → H2 headings
- Lines starting with numbers (1., 2.) → H3 headings
- Everything else → plain paragraphs

**Problems**:
- Source text already flattened (line breaks lost during original extraction)
- No ARTICLE hierarchy (H1)
- No list item detection for (a), (b), (i), (ii) patterns
- No recognition of legal preamble (WHEREAS, RECITALS)
- Page markers included as content

**Improved Method** (`builders/improved_txt_to_markdown.py::txt_to_markdown_v2()`):
- ARTICLE → H1, Section → H2, 1.1 subsections → H3
- (a), (b), (c) → list items; (i), (ii), (iii) → nested list items
- Legal keywords recognized (RECITALS, WHEREAS, NOW THEREFORE)
- Page markers and CONFIDENTIAL notices removed
- **BUT**: Cannot improve structure when source is already flattened

**Implication for Metrics**: Element F1 is **not meaningful** for CUAD corpus because:
1. Ground truth lacks proper structure (flattened at source)
2. Parsers producing better structure score WORSE
3. Parsers producing wall-of-text score HIGHER (match flattened ground truth)

### OmniDocBench (193 documents)

**Source**: Academic benchmark dataset with human-annotated ground truth.

**Method**: Converted from OmniDocBench's MD format.

**Quality**: Generally higher quality as ground truth was created by human annotators specifically for evaluation.

### Synthetic Corpus (32 documents)

**Source**: Generated programmatically using document templates.

**Method**: Ground truth is the source markdown before PDF rendering.

**Quality**: Perfect by construction - we know exactly what structure was intended.

## Metrics and Their Ground Truth Sensitivity

### High Sensitivity (Ground Truth Quality Critical)

| Metric | What It Measures | Ground Truth Impact |
|--------|------------------|---------------------|
| **Element F1** | Match of element types (heading, list, paragraph) | Completely dependent on ground truth element detection |
| **Tree Similarity** | AST structural match | Sensitive to heading levels, nesting depth |

### Medium Sensitivity

| Metric | What It Measures | Ground Truth Impact |
|--------|------------------|---------------------|
| **ChrF++** | Character n-gram overlap | Somewhat robust - measures text content |
| **Edit Similarity** | Character-level edit distance | Primarily text-focused |

### Low Sensitivity

| Metric | What It Measures | Ground Truth Impact |
|--------|------------------|---------------------|
| **TEDS** | Table Edit Distance Similarity | Only for tables - N/A when no tables |
| **CER** | Character Error Rate | Pure text accuracy |

## What Element F1 Actually Measures

The `element_f1.py` metric:

1. Parses markdown into AST nodes
2. Extracts element types: `heading`, `list`, `paragraph`, `code_block`, `table`
3. Counts occurrences of each type
4. Computes precision/recall/F1 between predicted and ground truth counts

**What It Ignores**:
- Heading levels (H1, H2, H3 all count as "heading")
- Element positions within document
- Content correctness
- Nesting structure
- List item hierarchy

**Example**: These two documents have Element F1 = 1.0 against each other:

```markdown
# Main Title                    | ### Subsection
## Section                      | # Main
### Subsection                  | ## Section
```

Both have 3 headings → perfect match, despite completely wrong hierarchy.

## Tree Similarity Limitations

`tree_edit_distance.py` DOES capture heading levels via AST, but:

1. **O(n^4) complexity** - Zhang-Shasha algorithm
2. Legal contracts can have 3,000-10,000+ AST nodes
3. A single document comparison can take minutes
4. Excluded from CUAD benchmarks for practical reasons

## Recommendations

### For Benchmark Consumers

1. **Check ground truth quality before trusting Element F1** - Low scores may indicate parser produces BETTER structure than ground truth
2. **Use edit_similarity for text extraction quality** - Less sensitive to structural annotation issues
3. **Use average rank across multiple metrics** - No single metric tells the whole story
4. **Manually inspect top parsers** - Quantitative metrics are starting points, not conclusions

### For Benchmark Developers

1. **Document ground truth creation method** - Be explicit about heuristics used
2. **Provide multiple ground truth versions** - Simple text vs. full structure
3. **Include qualitative examples** - Show actual parser outputs alongside scores
4. **Consider human evaluation** - For structural quality, human judgment may be necessary

### Metric Selection by Use Case

| Use Case | Recommended Metrics |
|----------|---------------------|
| **Text extraction accuracy** | edit_similarity, CER, ChrF++ |
| **RAG/Search preprocessing** | edit_similarity (content matters most) |
| **Document structure recovery** | tree_similarity (if feasible), manual review |
| **Table extraction** | TEDS |
| **Overall comparison** | See corpus-specific guidance below |

### Corpus-Specific Metric Guidance

| Corpus | Trust Element F1? | Primary Metric | Notes |
|--------|-------------------|----------------|-------|
| **Synthetic** | YES | Element F1 | Ground truth is perfect by construction |
| **CUAD** | NO | edit_similarity | Source text is flattened; structure metrics inverted |
| **OmniDocBench** | YES | Element F1, TEDS | Human-annotated ground truth |

**For CUAD benchmark rankings:**
- Use **edit_similarity only** for ranking
- Report Element F1 but note it penalizes good structure
- Consider re-extracting ground truth from PDFs in future

## Regenerating Ground Truth

To regenerate CUAD ground truth with improved structure detection:

```bash
# Test the improved converter
uv run python builders/improved_txt_to_markdown.py

# To regenerate full corpus (requires original CUAD .txt files):
# Modify build_cuad_corpus.py to use txt_to_markdown_v2()
# Then rebuild the corpus
```

## Key Takeaway

**Ground truth quality is the ceiling for structural metrics.** No parser can score higher than the ground truth allows, even if it produces objectively better output. Always:

1. Understand how ground truth was created
2. Know what each metric actually measures
3. Validate quantitative results with qualitative inspection
4. Report methodology alongside scores

---

## Appendix: Legal Contract Structure Patterns

Common patterns the improved converter recognizes:

```
ARTICLE I → H1
ARTICLE II → H1

RECITALS → H1
WHEREAS → H1 (preamble marker)
NOW, THEREFORE → H1 (transition to operative clauses)

1. DEFINITIONS → H2 (numbered major section)
2. GRANT OF RIGHTS → H2

1.1 "Term" means... → H3 (subsection)
1.2 "Agreement" means... → H3

(a) first item → list item
(b) second item → list item

(i) sub-item → nested list item
(ii) sub-item → nested list item

IN WITNESS WHEREOF → H1 (signature block marker)
```

These patterns are derived from analyzing actual SEC filing exhibits and standard legal contract formatting conventions.
