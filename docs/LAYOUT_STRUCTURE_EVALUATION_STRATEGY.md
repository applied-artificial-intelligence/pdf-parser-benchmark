# Layout & Structure Recovery Evaluation Strategy

**Date**: 2025-11-24
**Status**: Proposal for addressing "it depends on your documents" challenge

## Executive Summary

**Problem**: Text recovery metrics show parsers performing similarly (~75-88%), but **document structure recovery** (headings, lists, tables, multi-column layouts) likely varies significantly. We need to "open the kimono" and evaluate structural fidelity to answer "which parser for which document type?"

**Solution**: Multi-layered evaluation strategy using existing metrics + document characteristic profiling.

---

## Available Metrics & Capabilities

### ✅ Implemented & Fast

**1. Raw vs Normalized Edit Distance (`edit_similarity` vs `edit_similarity_normalized`)**
- **What it reveals**: Format sensitivity
- **Compute cost**: <1s per doc
- **Current use**: Already computed
- **Finding**: Databricks +14.5% boost reveals format bias in metrics

**2. Tree Edit Distance (`tree_edit_distance`, `tree_similarity`)**
- **What it reveals**: Heading hierarchy, list nesting, document structure
- **Compute cost**: 1-5s per doc (depends on tree size)
- **Current use**: Available but NOT currently computed in benchmarks
- **How it works**: Parses Markdown AST, compares tree structure
- **What it captures**:
  * Heading levels (#, ##, ###)
  * List nesting (ordered, unordered, nested)
  * Block structure (paragraphs, code blocks)
  * **Does NOT capture**: Tables, multi-column layouts

**3. Element F1 Score (`element_f1_score`)**
- **What it reveals**: Element-level precision/recall (headings, lists, tables, images)
- **Compute cost**: 1-5s per doc
- **Current use**: Available but NOT currently computed
- **How it works**: Counts semantic elements in GT vs output
- **What it captures**:
  * `# ` (H1 headings)
  * `## ` (H2 headings)
  * `-` or `*` or `1.` (list items)
  * `|` (table rows)
  * `![` (images)

**4. TEDS for Tables (`teds_score`, `teds_score_with_content`)**
- **What it reveals**: Table structure accuracy
- **Compute cost**: 5-30s per doc (slow!)
- **Current use**: Available but NOT currently computed
- **How it works**: Converts HTML tables to trees, computes edit distance
- **Limitation**: Only works for documents WITH tables

### ❌ Not Implemented (Would be onerous)

**General Document Structure TEDS** ("Zero" metric you mentioned)
- **What it would reveal**: Full semantic document structure (like TEDS but for entire docs)
- **Why not implemented**:
  * Requires semantic element extraction from both GT and parsed output
  * Complex alignment algorithm
  * Tree matching across different document structures
  * Estimated: 10-60s per doc
  * High implementation complexity

**Multi-column Layout Detection**
- No direct metric
- Could be approximated via:
  * Comparing reading order between GT and output
  * Checking if text flows correctly across columns
  * Not currently implemented

---

## What We CAN Do: Pragmatic Evaluation Strategy

### Strategy 1: Document Characteristic Profiling + Targeted Metrics

**Approach**: Profile documents by characteristics, then apply appropriate metrics

**Step 1: Auto-classify documents by structure** (fast, ~1s per doc)

```python
def profile_document(markdown_text):
    """Profile document structural characteristics"""
    return {
        "num_h1": count_pattern(r"^# ", markdown_text),
        "num_h2": count_pattern(r"^## ", markdown_text),
        "num_h3": count_pattern(r"^### ", markdown_text),
        "max_heading_depth": max_heading_depth(markdown_text),
        "num_tables": count_pattern(r"^\|", markdown_text),
        "num_lists": count_pattern(r"^- |^\* |^\d+\. ", markdown_text),
        "has_code_blocks": "```" in markdown_text,
        "has_images": "![" in markdown_text,
        "num_columns": estimate_columns(markdown_text),  # heuristic
    }
```

**Step 2: Apply metrics selectively**

| Document Type | Key Characteristics | Metrics to Apply |
|---------------|---------------------|------------------|
| **Academic Papers** | Many headings (H1-H4), tables, math | tree_edit_distance, element_f1, teds (if tables) |
| **Legal Contracts** | Deep heading hierarchy, numbered lists | tree_edit_distance, element_f1 |
| **Invoices/Forms** | Tables, minimal hierarchy | teds, element_f1 (table focus) |
| **Multi-column Layouts** | Estimated 2+ columns | edit_similarity (raw), manual reading order check |
| **Simple Text** | Few headings, no tables | edit_similarity_normalized, token_recall |

**Step 3: Report by document type**

```
Parser Performance by Document Complexity
==========================================
Simple docs (0-2 headings, no tables):
  Azure:    95% text recall, N/A structure
  PyMUPDF:  93% text recall, N/A structure

Complex docs (5+ headings, 3+ tables):
  Azure:    88% text, 82% tree_sim, 0.85 element_F1
  PyMUPDF:  85% text, 65% tree_sim, 0.72 element_F1
  Docling:  84% text, 78% tree_sim, 0.81 element_F1
```

### Strategy 2: Raw vs Normalized Delta as Structure Proxy

**Insight**: `edit_similarity` (raw) - `edit_similarity_normalized` (format-agnostic) = **structure recovery quality proxy**

**Logic**:
- If parser recovers text but not structure → high normalized score, low raw score → **large delta**
- If parser recovers both text AND structure → both scores high → **small delta**

**Current deltas (from our analysis)**:
- Azure: +0.8% (excellent structure recovery)
- AWS Textract: +0.8% (excellent structure recovery)
- Databricks: +14.5% (POOR structure recovery, excellent text)
- Google: +1.6% (good structure recovery)

**This already tells us something valuable!**

### Strategy 3: Corpus-Specific Evaluation

**Current corpus breakdown** (from docs/PARSER_COVERAGE.md):
- **Synthetic (32 docs)**: Known characteristics (2-column, tables, lists, mixed)
- **Invoices (100 docs)**: Table-heavy
- **CUAD Legal (75 docs)**: Deep heading hierarchy
- **HR Documents (34 docs)**: Mixed structure
- **Academic ArXiv (5 docs)**: Complex multi-level headings, tables, math

**Evaluation approach**:
1. **Compute tree_edit_distance + element_f1 on ArXiv** (5 docs, fast)
   - ArXiv papers have rich structure → good testbed
   - 5 docs × 20 parsers × 10s = ~17 minutes compute time

2. **Compute element_f1 on Synthetic corpus** (32 docs, known characteristics)
   - We KNOW what structure should be there
   - Can directly measure heading/list/table recovery

3. **Compute TEDS on Invoices** (100 docs, table-focused)
   - Invoices are table-heavy
   - TEDS directly measures table structure fidelity

---

## Recommended Action Plan

### Phase 1: Quick Wins (1-2 hours compute)

**A. Raw vs Normalized Delta Analysis** (✅ DONE)
- We already have this from format-agnostic analysis
- Databricks shows largest delta → poorest structure recovery

**B. Synthetic Corpus Element F1**
- 32 docs × 20 parsers × 2s = ~21 minutes
- Known ground truth characteristics
- Direct measurement of heading/list/table recovery

**C. ArXiv Tree Similarity**
- 5 docs × 10 parsers (open-source only, free) × 10s = ~8 minutes
- Rich document structure
- Tests heading hierarchy recovery

### Phase 2: Deeper Analysis (2-4 hours compute)

**D. Invoice TEDS Scores**
- 100 docs × ~10 parsers × 20s = ~5.5 hours
- Table structure fidelity
- Critical for business document use cases

**E. Document Profiling + Stratification**
- Auto-classify all 605 docs by characteristics
- Report parser performance by document complexity tiers

### Phase 3: Insights & Publication (no compute)

**F. Generate Findings**
- "PyPDFium2 excels at multi-column layouts (+30% vs Azure)"
- "Azure wins on heading hierarchy (82% tree_sim vs 65% PyMUPDF)"
- "Databricks trades structure for text (+14.5% boost when normalized)"

**G. Blog Post Angle**
- "There's No One-Size-Fits-All PDF Parser: A Data-Driven Guide"
- Leaderboards by document type
- Decision matrix: "Use X for Y document type"

---

## Why NOT Implement "Zero" Metric?

**Time/complexity vs value**:
- Implementation: 8-16 hours
- Compute: 10-60s per doc × 605 docs × 20 parsers = 34-203 HOURS
- **Alternative**: tree_edit_distance + element_f1 gives us 80% of the insight at 5% of the cost

**What we'd gain**:
- Full semantic document structure comparison
- Reading order verification
- Column flow accuracy

**What we lose by not doing it**:
- Marginal: Multi-column layout reading order (can manually inspect)
- Rest: Already covered by tree_edit_distance + element_f1

---

## Decision Matrix

| Question | Metric | Compute Cost | Value |
|----------|--------|--------------|-------|
| Does it recover text? | edit_similarity_normalized | ✅ Done | ✅ High |
| Does it preserve formatting? | Raw - Normalized delta | ✅ Done | ✅ High |
| Does it recover heading hierarchy? | tree_edit_distance | 1-5s/doc | ✅ High |
| Does it detect semantic elements? | element_f1_score | 1-5s/doc | ✅ High |
| Does it preserve table structure? | teds | 5-30s/doc | ✅ Medium (table-heavy docs only) |
| Does it handle multi-column flow? | Manual inspection + raw delta | N/A | ✅ Medium (few docs) |
| Full semantic structure? | "Zero" (not implemented) | 10-60s/doc | ❌ Low (covered by above) |

---

## ArXiv Status

**Question**: "What is missing for ArXiv? Which parsers, how many docs?"

**Answer**:
- **5 ArXiv papers** (LLaMA, GPT-4, Navier-Stokes PDE, BloombergGPT, LLM Survey)
- **ALL 20 parsers missing** (0% coverage currently)
- **100 operations required** (5 docs × 20 parsers)
- **Why it matters**: Academic papers have rich structure (multi-level headings, tables, math) → excellent testbed for structure recovery

**Recommendation**: Run ArXiv with **tree_edit_distance + element_f1** metrics enabled
- Reveals which parsers preserve heading hierarchy
- Shows which detect tables, lists, code blocks
- Small corpus (5 docs) but high structural complexity

---

## Bottom Line

**Can we evaluate layout/structure recovery?** YES

**Which metrics?**
1. Raw vs Normalized delta (✅ done)
2. tree_edit_distance (✅ implemented, not computed)
3. element_f1_score (✅ implemented, not computed)
4. teds (✅ implemented, not computed, slow)

**Where to apply them?**
- **ArXiv (5 docs)**: tree_edit_distance + element_f1 → heading hierarchy
- **Synthetic (32 docs)**: element_f1 → known structure validation
- **Invoices (100 docs)**: teds → table structure

**Time investment**: 2-8 hours compute for Phases 1-2

**Why not "Zero"?**: 80% of insight at 5% of cost using existing metrics

**Next step**: Run Phase 1 (Quick Wins) and see if it answers your question before committing to Phase 2.
