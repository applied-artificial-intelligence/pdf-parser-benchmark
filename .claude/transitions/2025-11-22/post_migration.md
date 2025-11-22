# Handoff: 2025-11-22 Post-Migration to ~/applied-ai/

## What Just Happened

1. **pdfsmith library** pushed to GitHub: `git@github.com:applied-artificial-intelligence/pdfsmith.git`
   - 11 open-source backend parsers
   - Ready for PyPI publish when desired

2. **pdf-bench cleaned up** and moved from `~/projects/pdf-bench` to `~/applied-ai/pdf-bench`
   - Removed: `.venv/` (8.6G), `.cache/` (19M), `archive/` (67M), `__pycache__/`, `.idea/`, `.kreuzberg/`, `omnidocbench_pilot/`
   - Kept: All core code, corpus, results, tests, docs

3. **Claude projects config** renamed from `-home-stefan-projects-pdf-bench` to `-home-stefan-applied-ai-pdf-bench`

## Immediate Next Steps

1. **Recreate venv**:
   ```bash
   cd /home/stefan/applied-ai/pdf-bench
   uv sync
   ```

2. **Add commercial parsers to pdfsmith** (tomorrow):
   - AWS Textract (full implementation exists in pdf-bench)
   - Azure Document Intelligence (full implementation exists)
   - Google Document AI (full implementation exists)
   - Databricks and Landing AI still need real implementations

3. **Publish pdfsmith to PyPI** (when ready):
   ```bash
   cd /home/stefan/applied-ai/pdfsmith
   uv build
   uv publish
   ```

## pdf-bench Current State

### Uncommitted Changes
Run `git status` - there are many uncommitted changes from corpus expansion:
- CUAD corpus (75 legal contracts)
- OmniDocBench corpus (193 documents)
- New benchmark configs
- Loader fixes

### Benchmark Results (kept in results/)
- `full_corpus_353docs.json` - Main benchmark results
- `comprehensive_278docs_all_parsers.json` - Multi-parser comparison
- Various other benchmark runs

### Corpus Structure
```
corpus/
├── academic/
│   ├── omnidocbench/     # 193 docs (mostly Chinese)
│   └── sample/
├── business/
│   ├── cuad/             # 75 legal contracts
│   ├── hr/
│   ├── invoices/
│   └── legal/
└── synthetic/            # Generated test docs
```

## Working Directories (all in ~/applied-ai/)

```
~/applied-ai/
├── pdfsmith/           # PDF parsing library (pushed to GitHub)
├── pdf-bench/          # Benchmark suite (THIS repo, just moved)
├── enterprise-agents/  # Main enterprise AI project
└── website/            # Corporate website
```

## User Intent Context

**Goal**: Content marketing through factual benchmarking data
- Generate real benchmark data comparing PDF parsers
- Write "how-to" and technical analysis content
- NOT clickbait - substantive practitioner-focused material
- pdfsmith serves dual purpose: open source contribution + practical tool for enterprise-agents

**What Claude provides**: Factual information (benchmark results, technical analysis)
**What user's agents do**: Write the actual content

## Pending Benchmark Tasks

1. Restart CUAD benchmark (75 documents) - started but died after ~10 docs
2. Run OmniDocBench benchmark (193 documents)
3. Build additional corpora:
   - Financial documents (tax forms, bank statements)
   - Logistics (Bill of Lading)
   - Healthcare (CMS forms)
4. Test commercial parsers (Databricks, Landing.AI need real implementations)

## Files to Commit (when ready)

The repo has significant uncommitted work. Consider committing:
- Corpus expansion (CUAD, OmniDocBench)
- Benchmark configs
- Loader fixes
- Results should stay gitignored (already are)
