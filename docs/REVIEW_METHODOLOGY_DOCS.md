# Review: METHODOLOGY_COMPARISON.md & GROUND_TRUTH_METHODOLOGY.md

**Reviewer**: Claude Code
**Date**: 2026-02-06
**Status**: Changes requested before publication

---

## Critical Issues (Must Fix)

### 1. Wrong Paper Title in YAML Metadata

**File**: `corpus/academic/sample/2302.14852.yaml`

METHODOLOGY_COMPARISON.md correctly identifies `2302.14852` as a Navier-Stokes paper, but the YAML metadata the benchmark actually uses says:

```yaml
doc_id: arxiv-2302.14852
title: "Toolformer: Language Models Can Teach Themselves to Use Tools"
```

Toolformer is arXiv 2302.04761, not 2302.14852. This is a data integrity bug. Add to immediate follow-up list.

### 2. File State Table References Non-Existent Files

**File**: `docs/METHODOLOGY_COMPARISON.md`, lines 97-109

The "Current State of Files" table lists files that don't exist:

| Documented File | Status |
|-----------------|--------|
| `corpus/academic/sample/2302.14852_pandoc.md` | NOT FOUND |
| `corpus/academic/sample/ground_truth/2302.14852.md` | NOT FOUND |
| `corpus/academic/ground_truth/2302.14852.md` | NOT FOUND |
| `results/pandoc_correct.json` | NOT FOUND |
| `results/ar5iv_correct.json` | NOT FOUND |

The table describes intended state rather than actual state. Anyone trying to reproduce the work will be confused.

### 3. Referenced Builder Script Doesn't Exist

**File**: `docs/GROUND_TRUTH_METHODOLOGY.md`, lines 85 and 236-240

References `builders/improved_txt_to_markdown.py::txt_to_markdown_v2()` and includes:

```bash
uv run python builders/improved_txt_to_markdown.py
```

This file is not in the repository. The "Regenerating Ground Truth" section will fail.

---

## Important Issues (Should Fix)

### 4. Contradictory Element F1 Guidance for arXiv Pandoc

**GROUND_TRUTH_METHODOLOGY.md line 224** says:
> arXiv (Pandoc) | **YES** | Trust Element F1

**METHODOLOGY_COMPARISON.md line 95** says:
> Element F1 shows mixed results. Some parsers improved (+29%), others dropped slightly (-5% to -9%)

Follow-up item 8 acknowledges Pandoc-specific markup remains (fenced divs, heading IDs, cross-reference attributes) -- these create the same problem as ar5iv artifacts.

**Fix**: Change "YES" to "CAUTION" in the corpus guidance table until Pandoc markup normalization is complete.

### 5. HuggingFace URL Typo

**File**: `docs/GROUND_TRUTH_METHODOLOGY.md`, line 59

```markdown
[theatticusproject/cuad-qa](https://huggingface.co/datasets/theatricusproject/cuad-qa)
```

Display text has "theatticusproject" (correct, double 't') but URL has "theatricusproject" (missing a 't'). Will 404.

**Fix**: `https://huggingface.co/datasets/theatticusproject/cuad-qa`

### 6. File Table Row Contradicts Itself

**File**: `docs/METHODOLOGY_COMPARISON.md`, line 103

```
| corpus/academic/sample/2302.14852_pandoc.md | Copy of Pandoc version | In ground_truth/ subdir |
```

The path is NOT in `ground_truth/` subdir -- it's in `corpus/academic/sample/`. The Notes column contradicts the File column.

### 7. Shell Script Will Silently Fail

**File**: `docs/METHODOLOGY_COMPARISON.md`, lines 117-124

The conversion loop hardcodes `main.tex`:

```bash
for paper in 2302.13971 2303.08774 2303.17564 2303.18223; do
    latexpand /tmp/$paper/main.tex > /tmp/${paper}_flat.tex
```

But the note immediately after says `2302.13971` uses `acl2023.tex`, not `main.tex`. The script needs a conditional or the note should say "modify the command for 2302.13971".

---

## Suggestions (Consider)

### 8. O(n^4) Complexity Claim

**File**: `docs/GROUND_TRUTH_METHODOLOGY.md`, line 186

Zhang-Shasha is O(n^4) worst case but typically much better. Consider: "O(n^2 * m^2) worst case" or add "in degenerate cases".

### 9. Content Overlap Will Diverge

The arXiv section in GROUND_TRUTH_METHODOLOGY.md (lines 97-115) duplicates METHODOLOGY_COMPARISON.md. Since it already links with "See docs/METHODOLOGY_COMPARISON.md for full details", consider keeping only the summary in the reference doc.

### 10. Clarify Document Counts

"arXiv Academic Papers (5 documents)" -- but the corpus directory has 11 papers. The benchmark config uses 5. Consider: "arXiv Academic Papers (5 documents in primary benchmark; 11 in corpus)".

### 11. Cross-Reference Loader Path Resolution

The "important discovery" about ground truth path resolution (METHODOLOGY_COMPARISON.md:57) is valuable but buried. Cross-reference in GROUND_TRUTH_METHODOLOGY.md under a "Technical Notes" section.

---

## What's Good

- The "Element F1 Paradox" example effectively demonstrates why naive metric interpretation is dangerous
- Percentage improvements in results table are mathematically verified
- Tiered recommendation structure serves multiple audiences well
- Code changes (`_latex_f1_wrapper`, metric registry, config updates) verified against source

---

## Verification Notes

| Claim | Verified |
|-------|----------|
| `_latex_f1_wrapper` exists in runner.py | YES |
| Metric registry uses wrapper | YES |
| Element F1 ignores heading levels | YES |
| Tree similarity captures heading levels | YES |
| academic_5docs.yaml has latex_f1, element_f1 | YES |
| 88-119% improvement range | YES (calculated from table) |
| `builders/improved_txt_to_markdown.py` exists | NO |
| File state table accuracy | PARTIAL (multiple files missing) |
