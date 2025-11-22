# PDF-Bench Content Marketing: Task Overview

## Visual Timeline (8 Weeks)

```
Week 1: PHASE-1 Benchmark Evaluation
├─ TASK-001 [CRITICAL] Run 278-doc benchmark (8h runtime, overnight)
├─ TASK-002 Domain-specific analysis (3h) ← depends on TASK-001
└─ TASK-003 OmniDocBench comparison (3h) ← depends on TASK-001

Week 1-2: PHASE-2 Content - Tier 1 (Credibility)
├─ TASK-004 Blog #1: Comprehensive 10-parser comparison (4h) ← depends on TASK-001, TASK-003
├─ TASK-005 Blog #2: Docling vs Marker (traditional ML > VLM) (3h) ← depends on TASK-001
└─ TASK-006 Blog #3: 50% structure preservation gap (3h) ← depends on TASK-001

Week 2-4: PHASE-3 Content - Tier 2 (Methodology)
├─ TASK-007 Blog #4: Domain-specific rankings (4h) ← depends on TASK-002
├─ TASK-008 Blog #5: Evaluation framework (4h) ← depends on TASK-001, TASK-002, TASK-003
├─ TASK-009 Blog #6: Multi-metric evaluation (3h) ← depends on TASK-001
└─ TASK-010 Blog #7: Creating corpora (3h, OPTIONAL) ← depends on TASK-001

Week 3-4: PHASE-4 GitHub & Docs
├─ TASK-011 Update README (2h) ← depends on TASK-001, TASK-002
├─ TASK-012 Create visualizations (6h) ← depends on TASK-001, TASK-002
└─ TASK-013 Documentation polish (4h) ← depends on TASK-001

Week 5-8: PHASE-5 Rollout
├─ TASK-014 Publish blog posts on schedule (6h) ← depends on TASK-004-010
└─ TASK-015 Community engagement (2h, ongoing) ← depends on TASK-014
```

---

## Dependency Graph

```
                    TASK-001 (278-doc benchmark) [CRITICAL]
                    /     |     \     \     \     \     \
                   /      |      \     \     \     \     \
                  /       |       \     \     \     \     \
            TASK-002  TASK-003  TASK-005  TASK-006  TASK-009  TASK-010  TASK-011
          (domain)  (OmniDB)   (Blog#2)  (Blog#3)  (Blog#6)  (Blog#7)  (README)
                |        |                                        |
                |        |                                        |
            TASK-007  TASK-004                                TASK-012
          (Blog#4)  (Blog#1)                                (charts)
                |        |                                        |
                |        |                                        |
            TASK-008     |                                        |
          (Blog#5) ------+                                        |
                |                                                 |
                |                                                 |
            TASK-014 (publish all blogs) <-----------------------+
                |
                |
            TASK-015 (community engagement)
                
        TASK-013 (docs) can run anytime after TASK-001
```

---

## Task Status Matrix

| Task | Title | Status | Hours | Priority | Depends On | Blocks |
|------|-------|--------|-------|----------|------------|--------|
| 001 | Run 278-doc benchmark | READY | 8 | CRITICAL | - | 002,003,004,005,006,007,008,009,010,011,012 |
| 002 | Domain analysis | BLOCKED | 3 | HIGH | 001 | 007,011,012 |
| 003 | OmniDocBench comparison | BLOCKED | 3 | MEDIUM | 001 | 004 |
| 004 | Blog #1: 10-parser comparison | BLOCKED | 4 | HIGH | 001,003 | 014 |
| 005 | Blog #2: Docling vs Marker | BLOCKED | 3 | HIGH | 001 | 014 |
| 006 | Blog #3: Structure gap | BLOCKED | 3 | HIGH | 001 | 014 |
| 007 | Blog #4: Domain rankings | BLOCKED | 4 | MEDIUM | 002 | 014 |
| 008 | Blog #5: Evaluation framework | BLOCKED | 4 | MEDIUM | 001,002,003 | 014 |
| 009 | Blog #6: Multi-metric | BLOCKED | 3 | MEDIUM | 001 | 014 |
| 010 | Blog #7: Creating corpora | BLOCKED | 3 | LOW | 001 | 014 |
| 011 | Update README | BLOCKED | 2 | MEDIUM | 001,002 | - |
| 012 | Create visualizations | BLOCKED | 6 | MEDIUM | 001,002 | - |
| 013 | Documentation polish | BLOCKED | 4 | LOW | 001 | - |
| 014 | Publish blog posts | BLOCKED | 6 | MEDIUM | 004-010 | 015 |
| 015 | Community engagement | BLOCKED | 2 | LOW | 014 | - |

**Total**: 58 hours estimated (60h with buffer)

---

## Parallel Execution Groups

### Group 1: Benchmark + Prep (Week 1)
```
TASK-001 (background, 8h) || TASK-013 (foreground, 4h)
```
While benchmark runs overnight, prepare documentation structure.

### Group 2: Analysis Tasks (Week 1, post-benchmark)
```
TASK-002 (3h) || TASK-003 (3h)
```
Independent analysis tasks, can run in parallel.

### Group 3: Tier 1 Blog Posts (Week 1-2)
```
TASK-004 (4h) || TASK-005 (3h) || TASK-006 (3h)
```
Once benchmark complete, write all 3 in parallel (10h total, can split across 2-3 days).

### Group 4: Tier 2 Blog Posts (Week 2-4)
```
TASK-007 (4h) || TASK-008 (4h) || TASK-009 (3h) || TASK-010 (3h)
```
Can write in parallel once dependencies satisfied (14h total).

### Group 5: GitHub Polish (Week 3-4)
```
TASK-011 (2h) || TASK-012 (6h) || TASK-013 (4h)
```
Independent of blog writing, can work on anytime (12h total).

---

## Critical Path (Minimum Time)

```
Day 1:    TASK-001 starts (run overnight)
Day 2:    TASK-001 completes
          TASK-002 + TASK-003 in parallel (6h)
Day 3:    TASK-004 + TASK-005 + TASK-006 in parallel (10h over 2-3 days)
Day 5:    TASK-007 + TASK-008 + TASK-009 in parallel (11h over 2 days)
Day 7:    TASK-011 + TASK-012 in parallel (8h)
Day 8:    TASK-014 (publish, 6h spread over weeks)
Week 5-8: TASK-015 (ongoing engagement)
```

**Fastest completion**: 2 weeks for technical work, 8 weeks for full rollout

---

## Phase Breakdown

### PHASE-1: Benchmark Evaluation (Week 1, 14h)
**Goal**: Complete comprehensive evaluation with domain analysis

**Tasks**: 001, 002, 003
**Critical Path**: TASK-001 → TASK-002 → (enables blog posts)
**Deliverables**:
- comprehensive_278docs_full.json (278 docs × 10 parsers × 6 metrics)
- Domain leaderboards (4 domains)
- OmniDocBench comparison (18 docs)

### PHASE-2: Content - Tier 1 (Week 1-2, 10h)
**Goal**: Establish technical credibility with attention-getting posts

**Tasks**: 004, 005, 006
**Parallel**: All 3 can be written simultaneously after TASK-001
**Deliverables**:
- Blog #1: Comprehensive comparison (3,000-4,000 words)
- Blog #2: Docling vs Marker VLM (2,000-2,500 words)
- Blog #3: Structure gap (2,000-2,500 words)

### PHASE-3: Content - Tier 2 (Week 2-4, 14h)
**Goal**: Demonstrate methodology and domain expertise

**Tasks**: 007, 008, 009, 010
**Parallel**: All can be written simultaneously
**Deliverables**:
- Blog #4: Domain rankings (2,500-3,000 words)
- Blog #5: Evaluation framework (3,000-3,500 words)
- Blog #6: Multi-metric evaluation (2,500-3,000 words)
- Blog #7: Creating corpora (2,500-3,000 words, optional)

### PHASE-4: GitHub & Docs (Week 3-4, 12h)
**Goal**: Polish GitHub presence and documentation

**Tasks**: 011, 012, 013
**Parallel**: All independent, can work on anytime
**Deliverables**:
- Updated README with 278-doc results
- 15-20 publication-quality visualizations
- Comprehensive documentation (QUICKSTART, API, examples)

### PHASE-5: Rollout (Week 5-8, 8h)
**Goal**: Publish and promote content, capture leads

**Tasks**: 014, 015
**Sequential**: Must publish before engagement
**Deliverables**:
- Blog posts published on schedule (2-week cadence)
- Social media promotion (HN, Reddit, LinkedIn, Twitter)
- Lead tracking and engagement metrics

---

## Resource Requirements

### Compute
- **TASK-001**: 8 CPU cores, 16GB RAM, 8-12 hours runtime
- **TASK-002-003**: Standard laptop, 6 hours total
- **TASK-004-010**: Writing, no compute
- **TASK-011-013**: Standard laptop, 12 hours total
- **TASK-014-015**: No compute (publishing/engagement)

### Data
- **Input**: 278 YAML metadata files + 278 PDFs (existing)
- **Output**: ~500MB JSON results + 15-20 PNG/SVG charts
- **Storage**: ~1GB total for all deliverables

### Skills
- **Technical**: Python scripting (analysis), Markdown (writing), matplotlib (charts)
- **Content**: Technical writing (3,000+ word blog posts)
- **Marketing**: Social media promotion, community engagement

---

## Quality Gates

### Gate 1: After TASK-001
**Validation**:
- ✅ Success rate >95% (failures documented)
- ✅ All 6 metrics computed correctly
- ✅ Per-domain metadata preserved
- ✅ Results reproducible

**Decision**: Proceed to analysis (TASK-002, TASK-003) or debug

### Gate 2: After TASK-002
**Validation**:
- ✅ Domain leaderboards show statistically significant ranking changes
- ✅ At least 2 parsers change ±2 positions across domains
- ✅ Key insights documented

**Decision**: Proceed to blog writing (TASK-004-010) or adjust narrative

### Gate 3: After TASK-004-006
**Validation**:
- ✅ Blog posts 2,000+ words with data tables
- ✅ Key findings clearly articulated
- ✅ Positioned as complementary to OmniDocBench

**Decision**: Proceed to Tier 2 blogs or iterate

### Gate 4: Before TASK-014
**Validation**:
- ✅ All blog posts complete and reviewed
- ✅ Visualizations publication-ready
- ✅ GitHub README updated
- ✅ Social media promotion plan ready

**Decision**: Proceed to publishing or polish

---

## Next Steps

1. Read implementation-plan.md (detailed specifications)
2. Review state.json (machine-readable tasks)
3. Run `/next` to start TASK-001
4. Monitor benchmark overnight
5. Run `/next` iteratively for remaining tasks

**First command**: `/next`

---

**Created**: 2025-11-20
**Status**: Ready to Execute
**Complexity**: Medium (clear dependencies, no external blockers)
**Risk Level**: Low (fallbacks defined for all risks)

Let's ship this.
