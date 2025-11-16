# Plan Update Summary - Parser Strategy Revision

**Date**: 2025-11-15
**Session**: Following TASK-028 completion (chrF++ metric)

## Changes Made

### ✅ Tasks Added (2)

#### TASK-086: pdfplumber Parser Adapter
- **Phase**: 4 (Parser Integration)
- **Type**: feature
- **Estimated**: 3 hours
- **Priority**: high
- **Dependencies**: TASK-004, TASK-005

**Rationale**:
- Already mentioned in synthetic corpus as comparison target
- Excellent table extraction via visual layout analysis
- Alternative rule-based approach to PyMuPDF
- Free, open-source, no GPU needed
- Different extraction strategy provides valuable baseline

**Acceptance Criteria**:
- pdf_bench/systems/pdfplumber.py created
- Implements BaseParser interface
- Text extraction with character-level positioning
- Table extraction via visual layout analysis
- Cache integration, error handling, integration tests

#### TASK-087: Databricks ai_parse_document Adapter
- **Phase**: 9 (Commercial Integrations)
- **Type**: feature
- **Estimated**: 6 hours
- **Priority**: medium (optional)
- **Dependencies**: TASK-004, TASK-005

**Rationale**:
- User-requested (per blog: https://www.databricks.com/blog/...)
- Represents "platform-integrated" approach (vs standalone APIs)
- Announced late 2024, claims 3-5x cost reduction vs AWS/Azure/Google
- LLM-based document understanding with Unity Catalog storage
- Unique positioning in leaderboard

**Requirements**:
- Databricks workspace (US/EU region)
- Runtime 17.1+
- Mosaic AI Model Serving access
- Files stored as BINARY in Delta tables

**Acceptance Criteria**:
- pdf_bench/systems/databricks.py created
- Implements BaseParser interface
- Databricks SQL integration with ai_parse_document
- Binary file handling, Unity Catalog retrieval
- Parse VARIANT output to Markdown
- Documentation for workspace setup
- Integration tests (mock or requires account)

### ❌ Tasks Cancelled (2)

#### TASK-031: Install and Test Nougat Locally
- **Status**: cancelled
- **Saved**: 2 hours
- **Reason**: Redundant with Marker

#### TASK-032: Implement NougatParser Adapter
- **Status**: cancelled
- **Saved**: 4 hours
- **Reason**: Redundant with Marker

**Cancellation Rationale**:
- Nougat is academic-focused (arXiv papers)
- Heavy dependencies (GPU preferred, slow inference)
- Marker (Meta) provides better ML-based coverage
- Already have table/LaTeX metrics, don't need Nougat-specific features
- Simplifies integration work

### 📦 Dependencies Updated

**pyproject.toml** - Added to `[project.optional-dependencies]`:

```toml
parsers = [
    "pymupdf>=1.23.0",
    "pdfplumber>=0.10.0",      # NEW
    "unstructured>=0.10.0",
]

commercial = [
    "boto3>=1.28.0",
    "azure-ai-formrecognizer>=3.3.0",
    "databricks-sql-connector>=3.0.0",  # NEW
]
```

## Updated Project Stats

### Task Count
- **Original**: 85 tasks
- **Cancelled**: -2 (Nougat tasks)
- **Added**: +2 (pdfplumber, Databricks)
- **New Total**: 87 tasks

### Time Estimates
- **Cancelled**: -6 hours (Nougat)
- **Added**: +9 hours (pdfplumber 3h + Databricks 6h)
- **Net Change**: +3 hours
- **New Total**: ~258 hours

### Completion Status
- **Completed**: 28/87 tasks (32%)
- **Phase 1**: 100% complete (10/10)
- **Phase 2**: 100% complete (8/8)
- **Phase 3**: 100% complete (10/10)
- **Phase 4+**: 0% complete

## Parser Lineup (Finalized)

### Tier 1: Core Leaderboard (6 parsers)

**Open Source**:
1. ✅ **PyMuPDF** - Complete (baseline)
2. ❌ **pdfplumber** - NEW (table specialist, 3h)
3. ❌ **Marker** (Meta) - ML-based (6h)
4. ❌ **Unstructured.io** - Enterprise (6h)

**Commercial Cloud**:
5. ❌ **AWS Textract** - Market leader (4h)
6. ❌ **Azure Document Intelligence** - Microsoft (4h)

**Work for Tier 1**: ~33 hours (parsers + commercial integration)

### Tier 2: Optional Extensions (2 parsers)

7. ❌ **Google Document AI** - Alternative commercial (4h)
8. ❌ **Databricks ai_parse_document** - NEW, Platform-specific (6h)

**Additional work for Tier 2**: +10 hours

### Comparison

**Before**:
- 7 parsers planned (PyMuPDF, Marker, Nougat, Unstructured, AWS, Azure, Google)
- Nougat redundant with Marker

**After**:
- 8 parsers (6 core + 2 optional)
- Better coverage: 2 rule-based, 2 ML open-source, 3 commercial cloud, 1 platform
- More diverse approaches
- pdfplumber adds table extraction strength
- Databricks adds platform-integrated approach

## Updated Timeline to Credible Leaderboard

### Milestone: Core Leaderboard (6 parsers)

**Components**:
- ✅ Phase 1-3: Foundation + Metrics (COMPLETE)
- Phase 4: Open-source parsers (15h)
  * Marker: 6h
  * Unstructured: 6h
  * pdfplumber: 3h
- Phase 5: Benchmark runner (23h)
- Phase 9: Commercial APIs (14h)
  * AWS Textract: 4h
  * Azure DI: 4h
  * Cost tracking + tests + docs: 6h
- Phase 6+8: Real corpus (28h)
  * GOV.UK: 14h (~25 docs)
  * arXiv: 14h (~40 docs)

**Total Work**: ~80 hours
**Timeline**: 2 weeks full-time, 4 weeks half-time
**Credibility**: 8/10 - Publishable

### Optional: Extended Coverage (+2 parsers)

**Additional Work**: +10 hours
- Google DocAI: 4h
- Databricks: 6h

**Total with extensions**: ~90 hours
**Credibility**: 9/10 - Industry-leading

## Recommendations

### Immediate Next Steps (in order):

1. **Continue with Phase 4**: Open-source parser integration
   - Start with **pdfplumber** (quick win, 3h)
   - Then Marker (6h)
   - Then Unstructured (6h)

2. **Build Phase 5**: Benchmark runner system (23h)
   - Critical: Can't run benchmarks without this
   - Parallel work opportunity while parsers integrate

3. **Corpus Building**: Phase 6+8 (28h)
   - GOV.UK first (business documents)
   - Then arXiv (academic papers)
   - Can skip SEC EDGAR initially

4. **Commercial APIs**: Phase 9 (14-24h)
   - AWS + Azure (core)
   - Google + Databricks (optional)

### Tier Assignment Decision

**Recommendation**: Keep as planned
- **Tier 1 (Required)**: 6 parsers (PyMuPDF, pdfplumber, Marker, Unstructured, AWS, Azure)
- **Tier 2 (Optional)**: 2 parsers (Google, Databricks)

**Rationale**:
- Tier 1 provides comprehensive, balanced coverage
- Tier 2 adds completeness but not critical
- Databricks requires platform access (not all users will have)
- Google is third major cloud option (nice-to-have)

## Implementation Strategy

### Parallel Execution Opportunities

1. **Parsers** (Phase 4): Can run integrations in parallel
   - pdfplumber + Marker + Unstructured
   - Use `/workflow:next --parallel 3`

2. **Corpus** (Phase 6+8): Can build in parallel
   - GOV.UK + arXiv simultaneously
   - Different teams/scripts

3. **Runner + Parsers**: Can develop concurrently
   - Build runner while parser integration happens

**With aggressive parallelization**: 2-3 weeks full-time possible

### Quality Gates

Before marking leaderboard as "credible":
- [ ] At least 6 parsers integrated (Tier 1)
- [ ] At least 60+ real documents (GOV.UK + arXiv)
- [ ] All metrics implemented and tested
- [ ] Full benchmark runner + CLI
- [ ] HTML reports generating correctly
- [ ] Manual review of sample results

## Git Changes

**Commit**: addedd2 "feat: Add pdfplumber and Databricks parsers to plan"

**Files Modified**:
- `.claude/work/current/001_pdf_bench_exploration/state.json`
  - Added TASK-086, TASK-087
  - Cancelled TASK-031, TASK-032
  - Updated project metadata

- `pyproject.toml`
  - Added pdfplumber to parsers dependencies
  - Added databricks-sql-connector to commercial dependencies

**Files Created**:
- `.claude/work/current/001_pdf_bench_exploration/UPDATED-PARSER-PLAN.md`
- `.claude/work/current/001_pdf_bench_exploration/PLAN-UPDATE-SUMMARY.md` (this file)

## Next Session Planning

**User preference**: "Build it right" - not in a rush

**Recommended focus**: Phase 4 (Open-source parsers)
- Quick win: pdfplumber integration (3h)
- Can demonstrate progress with minimal time
- Sets up for more complex integrations (Marker, Unstructured)

**Command to continue**:
```bash
/workflow:next --task TASK-086
# Or for parallel execution:
/workflow:next --parallel 3  # Run pdfplumber, Marker setup, Unstructured setup
```

---

**Summary**: Plan updated to include 8 parsers (6 core + 2 optional) with better coverage of parsing approaches. Net +3 hours added to timeline. Removed redundant Nougat tasks. Ready to proceed with Phase 4.
