# pdf-bench Migration to ~/applied-ai/

**Date**: 2025-11-22
**Status**: READY TO EXECUTE

## What Just Completed

1. **pdfsmith library** pushed to GitHub: `git@github.com:applied-artificial-intelligence/pdfsmith.git`
   - 11 backend parsers, lazy loading, CLI
   - Ready for PyPI publish when desired

2. **No cleanup needed** in pdf-bench - pdfsmith was created directly in `/home/stefan/applied-ai/pdfsmith/`

## Migration Steps (Manual - Requires Claude Code Restart)

### Step 1: Move the directory
```bash
mv /home/stefan/projects/pdf-bench /home/stefan/applied-ai/pdf-bench
```

### Step 2: Rename Claude projects config
```bash
mv ~/.claude/projects/-home-stefan-projects-pdf-bench \
   ~/.claude/projects/-home-stefan-applied-ai-pdf-bench
```

### Step 3: Restart Claude Code
```bash
cd /home/stefan/applied-ai/pdf-bench
claude
```

## Current pdf-bench State

### Uncommitted Changes (git status)
- Corpus expansion: CUAD (75 docs), OmniDocBench (193 docs)
- New benchmark configs
- Loader fixes
- Many new synthetic test files

### Active Benchmarks
- **CUAD benchmark** started but died after ~10 documents - needs restart
- **OmniDocBench benchmark** ready to run

### Key Files Added This Session
- `corpus/business/cuad/` - 75 legal contracts from CUAD dataset
- `corpus/academic/omnidocbench/` - 193 documents (mostly Chinese)
- `benchmarks/cuad_75docs.yaml`
- `benchmarks/omnidocbench_193docs.yaml`
- `builders/convert_omnidocbench.py`

## After Migration: Next Tasks

1. **Commit pdf-bench changes** - Corpus expansion work
2. **Restart CUAD benchmark** (75 documents with docling)
3. **Run OmniDocBench benchmark** (193 documents)
4. **Build additional corpora**:
   - Financial documents (tax forms, bank statements)
   - Logistics (Bill of Lading)
   - Healthcare (CMS forms)
5. **Test commercial parsers** (Databricks, Landing.AI)
6. **Publish pdfsmith to PyPI**

## Working Directories After Migration

```
~/applied-ai/
├── pdfsmith/           # PDF parsing library (GitHub: applied-artificial-intelligence/pdfsmith)
├── pdf-bench/          # Benchmark suite (moved from ~/projects/)
├── enterprise-agents/  # Main enterprise AI project
└── website/            # Corporate website
```

## User Intent Context

The goal is **content marketing through factual benchmarking**:
- Generate real benchmark data comparing PDF parsers
- Write "how-to" and technical analysis content
- NOT clickbait, but substantive practitioner-focused material
- pdfsmith serves dual purpose: open source contribution + practical tool
