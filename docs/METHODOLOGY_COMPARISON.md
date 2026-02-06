# LaTeX Ground Truth: arXiv Methodology Redesign

**Date**: 2026-02-01
**Status**: Proof-of-concept validated on 1 paper; 4 papers pending conversion

## Background

The benchmark's arXiv evaluation used ar5iv (LaTeX→HTML) converted to Markdown as ground truth. This introduced HTML artifacts that penalized parsers for NOT producing those artifacts—biasing all scores downward by roughly the same amount.

arXiv papers provide a cleaner path: download the LaTeX source directly and convert via Pandoc. This produces faithful, artifact-free Markdown that enables proper equation evaluation.

## What Was Done

### 1. Ground Truth Conversion (1 of 5 papers)

**Paper converted**: `2302.14852` (Navier-Stokes, single-file LaTeX)

```bash
pandoc corpus/academic/sample/2302.14852.tex -o ground_truth.md --wrap=none
```

The remaining 4 papers (`2302.13971`, `2303.08774`, `2303.17564`, `2303.18223`) have multi-file LaTeX with `\input{}` commands. Pandoc hangs on these because it can't resolve includes from a flat invocation. They need `latexpand` (not currently installed) to flatten the LaTeX first:

```bash
# Not yet done — requires: sudo apt install texlive-extra-utils
latexpand main.tex > combined.tex
pandoc combined.tex -o ground_truth.md --wrap=none
```

### 2. Bug Fix: latex_f1 JSON Serialization

`latex_f1_score()` returns a `LaTeXF1Scores` dataclass, but the metric registry expected functions returning `float`. The benchmark crashed with `Object of type LaTeXF1Scores is not JSON serializable`.

**Fix** in `pdf_bench/runner.py`: Added `_latex_f1_wrapper()` that extracts the `.f1` field:

```python
def _latex_f1_wrapper(ground_truth: str, prediction: str) -> float:
    try:
        scores = latex_f1_score(ground_truth, prediction)
        return scores.f1
    except Exception:
        return float("nan")
```

The metric registry now uses this wrapper instead of the raw function.

### 3. Benchmark Config Updates

**`benchmarks/academic_5docs.yaml`** — Added `latex_f1` and `element_f1` to the metric list (previously only had `edit_similarity`, `chrf++`, `character_error_rate`).

**`benchmarks/academic_pandoc_test.yaml`** — New config for single-paper testing with the Pandoc ground truth. Filters to `arxiv-2302.14852` only.

### 4. Comparative Evaluation

Ran the same paper through all 4 parsers (pypdfium2, pymupdf, marker, docling) with both ground truths.

**Important discovery during testing**: The ground truth path resolution in the loader uses Pattern 1 (same directory as YAML metadata file), which means the active ground truth for `2302.14852` is at `corpus/academic/sample/2302.14852.md`, NOT `corpus/academic/sample/ground_truth/2302.14852.md`. Both locations were updated.

## Results

### ar5iv vs Pandoc Ground Truth (paper 2302.14852)

| Parser | Metric | ar5iv | Pandoc | Change |
|--------|--------|-------|--------|--------|
| pypdfium2 | edit_similarity | 0.210 | 0.457 | **+118%** |
| pymupdf | edit_similarity | 0.208 | 0.455 | **+119%** |
| marker | edit_similarity | 0.300 | 0.643 | **+114%** |
| docling | edit_similarity | 0.187 | 0.409 | **+119%** |
| pypdfium2 | chrf++ | 22.2 | 42.0 | **+89%** |
| pymupdf | chrf++ | 22.2 | 42.1 | **+90%** |
| marker | chrf++ | 31.1 | 65.2 | **+110%** |
| docling | chrf++ | 21.6 | 40.6 | **+88%** |
| marker | latex_f1 | 0.119 | 0.158 | **+32%** |
| others | latex_f1 | 0.0 | 0.0 | — |

### What the ar5iv Artifacts Look Like

These are present in ar5iv-derived Markdown but absent from Pandoc output:

```markdown
# ar5iv artifacts (inflate ground truth, penalize all parsers)
[Roy Burson ]{.ltx_creator .ltx_role_author}          ← CSS class spans
[Theorem 1]{.ltx_tag .ltx_tag_theorem}                ← CSS tag annotations
[[1](#S1.E1 "In 1. The Navier-Stokes...")]{.ltx_ref}  ← verbose internal links
-- ----------------------------------------------------------------- --        ← table formatting junk
```

These artifacts account for 62% of the ar5iv file size (70KB ar5iv vs 26KB Pandoc). No parser produces them, so every parser is penalized for their absence.

### Key Conclusions

1. **Parser rankings are unchanged.** Marker still leads on all metrics. The ar5iv penalty affects all parsers roughly equally.
2. **Absolute scores are now meaningful.** 0.64 edit_similarity is a realistic measure of Marker's quality; 0.30 was not.
3. **LaTeX F1 works.** With clean `$...$` delimiters in the ground truth, the metric correctly identifies that only Marker extracts equations. Other parsers score 0.0 because they don't produce LaTeX markup.
4. **Element F1 shows mixed results.** Some parsers improved (+29%), others dropped slightly (-5% to -9%) because ar5iv's CSS artifacts were being counted as structural elements.

## Current State of Files

| File | State | Notes |
|------|-------|-------|
| `corpus/academic/sample/2302.14852.md` | **Pandoc ground truth** | Active — loader uses this (Pattern 1 resolution) |
| `corpus/academic/sample/2302.14852_ar5iv.md` | Archived ar5iv version | For comparison |
| `corpus/academic/sample/ground_truth/2302.14852.md` | **Pandoc ground truth** | Backup copy |
| `corpus/academic/sample/ground_truth/2302.14852_pandoc.md` | Pandoc version | Explicit naming |
| `corpus/academic/sample/ground_truth/2302.14852_ar5iv.md` | Archived ar5iv version | For comparison |
| `corpus/academic/ground_truth/2302.14852.md` | **Pandoc ground truth** | Top-level corpus copy |
| `corpus/academic/ground_truth/2302.14852_ar5iv.md` | Archived ar5iv version | For comparison |
| `results/pandoc_correct.json` | Benchmark results | Pandoc ground truth, 1 paper, 4 parsers |
| `results/ar5iv_correct.json` | Benchmark results | ar5iv ground truth, 1 paper, 4 parsers |

## Follow-Up Work

### Immediate (complete the proof-of-concept)

1. **Install `latexpand`**: `sudo apt install texlive-extra-utils`
2. **Convert remaining 4 papers**:
   ```bash
   # Note: main .tex file varies by paper. Check each archive first.
   # 2302.13971 uses acl2023.tex; others use main.tex
   for paper in 2303.08774 2303.17564 2303.18223; do
     mkdir -p /tmp/$paper
     tar xzf corpus/academic/sample/${paper}.tar.gz -C /tmp/$paper/
     latexpand /tmp/$paper/main.tex > /tmp/${paper}_flat.tex
     pandoc /tmp/${paper}_flat.tex -o corpus/academic/sample/${paper}.md --wrap=none
   done

   # Handle 2302.13971 separately (uses acl2023.tex)
   mkdir -p /tmp/2302.13971
   tar xzf corpus/academic/sample/2302.13971.tar.gz -C /tmp/2302.13971/
   latexpand /tmp/2302.13971/acl2023.tex > /tmp/2302.13971_flat.tex
   pandoc /tmp/2302.13971_flat.tex -o corpus/academic/sample/2302.13971.md --wrap=none
   ```
3. **Re-run full 5-paper benchmark** with `benchmarks/academic_5docs.yaml`
4. **Validate Pandoc output** for each paper: spot-check equations, tables, section hierarchy

### Medium-term (methodology improvement)

5. **Add `teds` metric** to academic config if papers contain tables
6. **Report detailed LaTeX F1 breakdown** (precision/recall/tp/fp/fn) — the wrapper currently only returns F1; consider storing the full `LaTeXF1Scores` dataclass in a sidecar file
7. **Compare Pandoc output to parser output** qualitatively for each paper (not just metrics)
8. **Consider normalizing Pandoc-specific markup** before comparison:
   - `{reference-type="eqref" reference="Eq1"}` attributes on cross-references
   - `::: {#Thm1 .theorem}` fenced div notation
   - `{#S1}` heading ID attributes

### Longer-term (corpus expansion)

9. **Expand to 10-20 arXiv papers** across domains (CS, physics, economics, biology)
10. **Select papers by complexity**: math-heavy vs prose-heavy vs table-heavy
11. **Create separate "academic-pandoc" corpus** with its own metadata directory
12. **Update content briefing** if rankings change with more papers (currently in `~/applied-ai/content-marketing/content/briefings/pdf-parsing/draft.md`)
