# Task Details Directory

This directory contains individual task specification files for the PDF-Bench implementation.

## Overview

All 85 tasks are defined in the main `state.json` file with:
- Task ID (TASK-XXX)
- Title and description
- Type, phase, status
- Dependencies
- Acceptance criteria
- Estimated hours
- Priority
- Agent recommendations

## Task Organization

**Phase 1: Foundation** (TASK-001 to TASK-010)
- Project setup, core abstractions, baseline parser, basic metrics

**Phase 2: Synthetic Corpus** (TASK-011 to TASK-018)
- Markdown→PDF and DOCX→PDF pipelines, ground truth validation

**Phase 3: Advanced Metrics** (TASK-019 to TASK-028)
- AST-TED, TEDS, Element F1, LaTeX normalization

**Phase 4: Open-Source Adapters** (TASK-029 to TASK-036)
- Marker, Nougat, Unstructured parser adapters

**Phase 5: Runner & Reporting** (TASK-037 to TASK-046)
- Benchmark orchestration, CLI, HTML reports

**Phase 6: GOV.UK Corpus** (TASK-047 to TASK-052)
- HTML scraping, GOV.UK→Markdown conversion

**Phase 7: SEC EDGAR Corpus** (TASK-053 to TASK-058)
- Financial filings, table extraction

**Phase 8: arXiv Corpus** (TASK-059 to TASK-066)
- LaTeX→Markdown pipeline, academic papers

**Phase 9: Commercial Adapters** (TASK-067 to TASK-072)
- AWS Textract, Azure DI, cost tracking

**Phase 10: Documentation** (TASK-073 to TASK-080)
- DATASHEET.md, README, CONTRIBUTING, release checklist

**Phase 11: Launch** (TASK-081 to TASK-085)
- PyPI package, full benchmark, blog post, public release

## Usage

To begin implementation:

1. Review the complete `implementation-plan.md` for context
2. Check `state.json` for current task status
3. Run `/next` to start the first available task (TASK-001)
4. Complete acceptance criteria for each task
5. Track progress using `/workflow:status`

## Next Available Tasks

Initially: **TASK-001** (Initialize Project with uv)

As tasks complete, the `next_available` list in `state.json` will update automatically based on dependency resolution.
