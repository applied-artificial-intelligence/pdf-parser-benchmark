# Cleanup Summary - 2025-11-17

## What Was Deleted

### Broken Corpus (All Custom Ground Truth Failed)
- `corpus/synthetic/` - 8 trivial documents
- `corpus/business/sec_edgar/` - 29% similarity (XML artifacts, broken HTML→MD)
- `corpus/business/govuk/` - 2.6% similarity (HTML was download pages, not content)
- `corpus/academic/arxiv/` - Academic papers (not business documents)

### Wrong Approach
- `builders/` - All corpus generation scripts
- All benchmark scripts using edit distance metric (wrong metric)
- False documentation claiming "Phase 10/11" and "124 documents"

### Outdated Infrastructure
- `examples/`, `benchmark_results/`, `docs/`, `scripts/`
- All cache and build artifacts
- TASK-*.md validation files
- Most .claude/transitions/ (kept last 6 directories for context)

## What Was Preserved

### Claude Infrastructure
- `.claude/reference/benchmark_survey.md` - Excellent research on PDF benchmarks
- `.claude/work/2025117_001_parser_evaluation/` - New requirement document
- Recent transitions (2025-11-14 through 2025-11-18)

### Potentially Salvageable Code
- `pdf_bench/utils/cost_tracking.py` - Cost estimation utilities
- `pdf_bench/systems/aws_textract.py` - AWS API integration
- `pdf_bench/systems/azure_document_intelligence.py` - Azure API integration
- `pdf_bench/systems/base_parser.py` - Parser interface concept (needs redesign)

### Core Infrastructure
- `pyproject.toml`, `uv.lock` - Dependency management
- `.gitignore`
- `tests/` structure (will need complete rewrite)
- Git history (all commits preserved)

## Why This Failed

**Root Cause**: HTML→Markdown ground truth generation is fundamentally flawed

**Problems**:
1. HTML and PDF are semantically different formats
2. GOV.UK doesn't publish documents as HTML (they're native PDFs)
3. SEC HTML has too many artifacts to serve as clean ground truth
4. Edit distance metric inappropriate for structured document comparison
5. No validation of ground truth quality before building pipeline

## Lessons Learned

1. **Validate data quality FIRST** - Don't build infrastructure on untested assumptions
2. **Use established benchmarks** - Don't reinvent the wheel
3. **Question approaches** - HTML as ground truth was questionable from the start
4. **Test small** - Should have tested 1-2 documents before generating 124
5. **Use proper metrics** - mAP and TEDS exist for a reason

## Path Forward

Use established benchmarks:
- DocLayNet (81K pages, CDLA-Permissive)
- PubTabNet (568K tables, Public)
- OmniDocBench (CVPR 2025, Apache-2.0)

Build leaderboard + white paper as originally spec'd.
