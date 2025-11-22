# Content Marketing Work Unit: Quick Reference

**Status**: Ready to Execute
**Work Unit ID**: 251120_003_content_marketing
**Timeline**: 8 weeks (2-week MVP possible)
**Effort**: 60 hours

---

## What We're Building

A comprehensive content marketing campaign to showcase document intelligence expertise:

1. 278-document benchmark (10 parsers × 6 metrics)
2. Domain-specific analysis (4 domains: synthetic, legal, invoices, HR)
3. 6-7 high-quality blog posts (3,000+ words each)
4. GitHub polish + visualizations
5. Community engagement + lead capture

**Goal**: 5-10 qualified consulting inquiries via thought leadership

---

## File Structure

```
.claude/work/251120_003_content_marketing/
├── README.md                    # This file
├── state.json                   # Machine-readable task list (15 tasks)
└── implementation-plan.md       # Human-readable detailed plan
```

---

## Quick Start

To begin execution:

```bash
# Review the plan
cat .claude/work/251120_003_content_marketing/implementation-plan.md

# Start first task (278-doc benchmark)
/next
```

---

## Task Summary (15 Tasks)

### Phase 1: Benchmark Evaluation (Week 1, 14h)
- **TASK-001**: Run 278-doc benchmark (8h runtime, CRITICAL) ⚠️
- **TASK-002**: Domain-specific analysis (3h)
- **TASK-003**: OmniDocBench comparison (3h)

### Phase 2: Content - Tier 1 (Week 1-2, 10h)
- **TASK-004**: Blog #1 - Comprehensive 10-parser comparison (4h)
- **TASK-005**: Blog #2 - Docling vs Marker (VLM vs traditional) (3h)
- **TASK-006**: Blog #3 - 50% structure preservation gap (3h)

### Phase 3: Content - Tier 2 (Week 2-4, 14h)
- **TASK-007**: Blog #4 - Domain-specific rankings (4h)
- **TASK-008**: Blog #5 - Evaluation framework (4h)
- **TASK-009**: Blog #6 - Multi-metric evaluation (3h)
- **TASK-010**: Blog #7 - Creating corpora (3h, optional)

### Phase 4: GitHub Polish (Week 3-4, 12h)
- **TASK-011**: Update README with 278-doc results (2h)
- **TASK-012**: Create visualizations (15-20 charts) (6h)
- **TASK-013**: Documentation + examples (4h)

### Phase 5: Rollout (Week 5-8, 8h)
- **TASK-014**: Publish blog posts on schedule (6h)
- **TASK-015**: Community engagement (2h, ongoing)

---

## Critical Path

```
TASK-001 (benchmark) 
    → TASK-002 (domain analysis) 
        → TASK-004-010 (blog posts) 
            → TASK-014 (publishing)
```

**Everything depends on TASK-001 completing successfully**

---

## Parallel Opportunities

1. **Week 1**: Run TASK-001 overnight, work on TASK-013 (docs) during day
2. **Analysis**: TASK-002 and TASK-003 are independent, run in parallel
3. **Tier 1 blogs**: TASK-004, TASK-005, TASK-006 can be written in parallel
4. **Tier 2 blogs**: TASK-007-010 can be written in parallel
5. **GitHub polish**: TASK-011-013 independent of blog writing

---

## Key Deliverables

### Technical
- 278-doc benchmark results (comprehensive_278docs_full.json)
- Domain-specific leaderboards (4 domains)
- OmniDocBench comparison (18 docs)

### Content
- 6-7 blog posts (2,000-4,000 words each)
- 15-20 publication-quality visualizations
- Updated GitHub README + documentation

### Business
- 5-10 inbound consulting inquiries
- 100+ GitHub stars
- HN front page (1-2 posts)

---

## Success Metrics

**Technical**:
- ✅ 278-doc benchmark complete (all 6 metrics)
- ✅ Domain leaderboards show ranking changes
- ✅ OmniDocBench comparison validates complementarity

**Content**:
- ✅ 6-7 high-quality blog posts published
- ✅ GitHub updated with actual results
- ✅ Documentation polished

**Business**:
- ✅ 5-10 qualified consulting inquiries
- ✅ 100+ GitHub stars (8 weeks)
- ✅ HN front page (100+ upvotes)
- ✅ Industry citations/discussion

---

## Risk Management

### CRITICAL: TASK-001 Failure
**Risk**: 8h benchmark run fails, blocks everything
**Mitigation**: 
- Monitor with restart capability
- Save intermediate results
- Fallback: use 31-doc results if needed

### Medium: Docling High Failure Rate
**Risk**: 23% → 40% failure rate
**Mitigation**: 
- Document as reliability trade-off
- Frame as "high quality, lower reliability"
- Becomes feature, not bug

### Low: Blog Posts Take Longer
**Risk**: 3-4h → 6-8h per post
**Mitigation**:
- Quality > quantity (6 excellent > 7 rushed)
- Drop optional TASK-010 if time-constrained
- Extend timeline by 2 weeks

---

## Next Actions

1. Review implementation-plan.md (detailed plan)
2. Review state.json (machine-readable tasks)
3. Run `/next` to start TASK-001 (benchmark)
4. Monitor overnight benchmark run
5. Run `/next` iteratively for remaining tasks

---

## Strategic Context

This work unit executes the content marketing strategy documented in:
- `.claude/reference/content_marketing_strategy.md` - Overall strategy
- `.claude/work/251120_001_review/10_parser_comprehensive_results.md` - 31-doc baseline
- `.claude/work/251120_001_review/evaluation.md` - Technical framework

**Positioning**: Complementary to OmniDocBench (not competitive)
**Audience**: Enterprise AI decision-makers + technical practitioners
**Value Prop**: "We show enterprises how to bridge the gap between promising benchmark results and confident production deployment"

---

**Created**: 2025-11-20
**Ready to Execute**: Yes
**Estimated Completion**: 8 weeks from start

Run `/next` to begin.
