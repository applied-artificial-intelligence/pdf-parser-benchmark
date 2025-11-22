# PDF-Bench Content Marketing: Implementation Plan

**Work Unit ID**: 251120_003_content_marketing
**Created**: 2025-11-20
**Status**: Ready to Execute
**Timeline**: 2-week MVP + 8-week rollout = 10 weeks total
**Estimated Effort**: 60 hours

---

## Executive Summary

This plan executes the PDF-Bench content marketing initiative to showcase document intelligence expertise through:

1. **Comprehensive Evaluation**: 278-document benchmark across 10 parsers with 6 metrics
2. **Domain Analysis**: Demonstrate parser rankings change by document type
3. **Framework Positioning**: Position as complementary to OmniDocBench (not competitive)
4. **Content Creation**: 6-7 high-quality blog posts establishing technical credibility
5. **Community Engagement**: GitHub polish, social promotion, lead capture

**Goal**: Generate 5-10 qualified consulting inquiries through thought leadership

---

## Critical Path

The work follows a clear dependency chain:

```
TASK-001 (Benchmark) → TASK-002 (Domain Analysis) → TASK-004+ (Blog Posts) → TASK-014 (Publishing)
                     ↘ TASK-003 (OmniDocBench) ↗
```

**Critical milestones**:
- Week 1: Complete 278-doc benchmark (8h runtime, overnight)
- Week 2: Domain analysis + OmniDocBench comparison (6h)
- Week 2-4: Write 6-7 blog posts (23h)
- Week 3-4: GitHub polish + visualizations (12h)
- Week 5-8: Publish on schedule + community engagement (8h)

**Total**: ~60 hours over 8 weeks

---

## Phase 1: Complete Benchmark Evaluation (Week 1, 14h)

### TASK-001: Run 278-Document Comprehensive Benchmark ⚠️ CRITICAL
**Status**: Ready | **Hours**: 8 (runtime) | **Priority**: Critical

**What**: Execute full benchmark: 278 documents × 10 parsers × 6 metrics = 16,680 data points

**Deliverables**:
- `benchmarks/comprehensive_278docs.yaml` - benchmark config
- `benchmarks/results/comprehensive_278docs_full.json` - complete results
- `benchmarks/results/comprehensive_278docs_summary.txt` - quick stats

**Implementation**:
1. Create benchmark config including all 10 parsers:
   - docling, marker_ollama, pymupdf4llm, pdfplumber, pypdf
   - pypdfium2, extractous, unstructured, pymupdf, pdfminer
2. Include all 6 metrics: edit_similarity, chrf++, character_error_rate, tree_similarity, element_f1, TEDS
3. Set `parallel_workers: 8` for speed
4. Run overnight (estimated 8-12 hours)
5. Handle docling's 23% failure rate gracefully (document failures)
6. Preserve per-domain metadata (synthetic, legal, invoices, HR)

**Acceptance Criteria**:
- ✅ All 10 parsers tested on 278 documents
- ✅ Success rate >95% (failures documented)
- ✅ All 6 metrics computed correctly
- ✅ Per-domain results preserved for analysis
- ✅ Results saved in structured JSON format

**Parallel Opportunity**: While this runs overnight, start on TASK-013 (documentation structure)

---

### TASK-002: Domain-Specific Analysis
**Status**: Blocked by TASK-001 | **Hours**: 3 | **Priority**: High

**What**: Analyze results by domain to create domain-specific leaderboards

**Deliverables**:
- `analysis/domain_leaderboards.md` - comprehensive analysis
- `analysis/domain_rankings.csv` - machine-readable rankings
- `analysis/ranking_changes.md` - key insights on domain variation

**Implementation**:
1. Create `analyze_domain_performance.py` script
2. Load `results/comprehensive_278docs_full.json`
3. Group by document metadata (domain: synthetic, legal, invoices, HR)
4. Calculate per-domain averages for all 6 metrics
5. Identify statistically significant ranking changes
6. Create domain leaderboard tables (Markdown + CSV)

**Key Questions to Answer**:
- Does pdfplumber dominate on invoices (table-heavy)?
- Do legal documents (complex hierarchy) change rankings?
- Is docling's #1 overall consistent across all domains?
- Which parsers are domain-specialists vs generalists?

**Acceptance Criteria**:
- ✅ Results segmented by 4 domains with sample sizes (33, 108, 100, 34)
- ✅ Domain-specific leaderboards created
- ✅ Ranking changes quantified (e.g., "Parser X: #2 overall, #5 on legal")
- ✅ Statistical significance tested (not just noise)

---

### TASK-003: OmniDocBench Integration & Comparison
**Status**: Blocked by TASK-001 | **Hours**: 3 | **Priority**: Medium
**Can run in parallel with TASK-002**

**What**: Run top 5 parsers on OmniDocBench demo data (18 docs) and compare rankings

**Deliverables**:
- `analysis/omnidocbench_comparison.md` - comprehensive comparison
- `benchmarks/results/omnidocbench_18docs.json` - ODB results
- `analysis/framework_complementarity.md` - positioning document

**Implementation**:
1. Download OmniDocBench demo dataset (18 documents)
2. Convert OmniDocBench ground truth (JSON) to PDF-Bench format (Markdown)
3. Run top 5 parsers: docling, marker_ollama, pymupdf4llm, pdfplumber, pypdf
4. Compare rankings: OmniDocBench vs PDF-Bench (synthetic) vs PDF-Bench (business)
5. Focus on TEDS comparison (11.5% gap already documented)
6. Document where rankings agree vs diverge with explanations

**Key Positioning**:
- Frame as "Phase I validation" (OmniDocBench) + "Phase II validation" (PDF-Bench)
- NOT competition: "Both benchmarks necessary for production confidence"
- Different benchmarks measure different things (real-world vs domain-specific)

**Acceptance Criteria**:
- ✅ OmniDocBench demo data tested with same parsers
- ✅ Rankings compared across 3 contexts (ODB, synthetic, business)
- ✅ Key divergences documented with explanations
- ✅ Complementarity validated (not positioned as better/worse)

---

## Phase 2: Content Creation - Tier 1 (Week 1-2, 10h)

**Goal**: Establish technical credibility with 3 attention-getting posts

### TASK-004: Blog Post #1 - Comprehensive 10-Parser Comparison
**Status**: Blocked by TASK-001, TASK-003 | **Hours**: 4 | **Priority**: High
**Flagship post, most important**

**Length**: 3,000-4,000 words
**Target**: Senior engineers, ML practitioners, technical decision-makers

**Structure**:
1. Introduction: Why parser evaluation matters for RAG/LLM pipelines
2. Methodology: Two benchmarks (ODB + PDF-Bench), 10 parsers, 6 metrics
3. Overall Results: Leaderboard table with all metrics
4. **Key Finding 1**: 50% structure preservation gap (83% text, 33% structure)
5. **Key Finding 2**: Docling beats Marker on structure (traditional ML > VLM)
6. **Key Finding 3**: Rankings change by domain (synthetic vs legal vs invoices)
7. Parser Profiles: Detailed breakdown of top 5
8. Decision Framework: How to choose based on use case
9. Conclusion: Both benchmarks necessary (baseline + domain-specific)

**Deliverables**:
- `blog/01_comprehensive_parser_comparison.md`
- `blog/assets/01_leaderboard_table.png`
- `blog/assets/01_structure_gap_chart.png`

**Key Messages**:
- "Public benchmarks (OmniDocBench) prove baseline competence"
- "Domain-specific validation (PDF-Bench) proves production readiness"
- "You need both, not one or the other"

---

### TASK-005: Blog Post #2 - Docling vs Marker (Traditional ML Beats VLM)
**Status**: Blocked by TASK-001 | **Hours**: 3 | **Priority**: High
**Attention-grabbing, HN front-page potential**

**Length**: 2,000-2,500 words
**Angle**: Surprising finding challenges VLM hype

**Structure**:
1. Hook: "VLMs are the future" narrative challenged
2. The Matchup: Docling (IBM, traditional CV/ML) vs Marker+Ollama (VLM)
3. **Results**: Docling wins element_f1 (84.1% vs 69.4%), tree_sim (61.2% vs 49.3%)
4. Why Traditional ML Won: Document structure is geometric, not semantic
5. Where VLMs Excel: Text recognition (89.9% vs 87.4%)
6. Trade-offs: Speed (docling 3× faster), reliability (marker 7% better)
7. Implications: Don't assume VLMs beat everything; test on YOUR domain
8. Conclusion: Hybrid approaches may be optimal

**Headline Options**:
- "Traditional ML Beats VLMs on Document Structure: IBM's Docling vs Marker+Ollama"
- "Why VLMs Don't Automatically Win: Document Structure Is a Solved CV Problem"
- "84.1% vs 69.4%: How Traditional Parsing Beats Vision-Language Models"

**Deliverables**:
- `blog/02_docling_vs_marker_vml.md`
- `blog/assets/02_head_to_head_table.png`
- `blog/assets/02_metric_breakdown_chart.png` (radar chart)

---

### TASK-006: Blog Post #3 - The 50% Structure Preservation Gap
**Status**: Blocked by TASK-001 | **Hours**: 3 | **Priority**: High
**Problem definition, sets up later solutions**

**Length**: 2,000-2,500 words
**Angle**: Industry-wide problem no one talks about

**Structure**:
1. The Problem: "My parser has 90% accuracy" is misleading
2. The Data: All 10 parsers show 50-point structure gap
3. What Gets Lost: Heading levels, list nesting, section hierarchy, reading order
4. Real-World Impact: RAG chunks lose context, LLMs miss document structure
5. Why This Is Hard: PDF stores coordinates, not semantics
6. Case Studies: Multi-column layouts, nested lists, complex tables
7. What Success Looks Like: Docling at 61.2% is still failing 40% of structure
8. Recommendations: Measure structure, choose parsers accordingly, hybrid strategies

**Key Insight**:
- Average text accuracy: 83.2%
- Average structure preservation: 33.2%
- **Gap: 50 percentage points across ALL parsers**

**Deliverables**:
- `blog/03_structure_preservation_gap.md`
- `blog/assets/03_gap_visualization.png` (83% vs 33% chart)
- `blog/assets/03_example_failures.png` (side-by-side examples)

---

## Phase 3: Content Creation - Tier 2 (Week 2-4, 14h)

**Goal**: Demonstrate methodology and domain-specific expertise

### TASK-007: Blog Post #4 - Why Parser Rankings Change by Domain
**Status**: Blocked by TASK-002 | **Hours**: 4 | **Priority**: Medium

**Length**: 2,500-3,000 words
**Data-driven**: 4 domain-specific leaderboards

**Structure**:
1. Setup: The "Best Parser" Question
2. Methodology: 278 documents across 4 domains (synthetic, legal, invoices, HR)
3. Overall Leaderboard: Docling #1, but...
4. Synthetic Leaderboard: Controlled conditions favor X
5. Legal Leaderboard: Complex hierarchy changes rankings
6. Invoice Leaderboard: pdfplumber dominates (table specialist)
7. HR Leaderboard: Resume formats favor Y
8. Key Insights: 30% of parsers change ±2 positions across domains
9. Production Implications: Test on YOUR document types, not general benchmarks
10. Framework: OmniDocBench (baseline) → domain corpus (validation)

**Deliverables**:
- `blog/04_domain_specific_rankings.md`
- `blog/assets/04_domain_leaderboards.png` (4 leaderboard comparison)
- `blog/assets/04_ranking_shift_heatmap.png` (parser rank changes)

---

### TASK-008: Blog Post #5 - How to Evaluate PDF Parsers (Framework)
**Status**: Blocked by TASK-001, TASK-002, TASK-003 | **Hours**: 4 | **Priority**: Medium
**Most actionable for enterprises**

**Length**: 3,000-3,500 words
**Value**: Replicable step-by-step process

**Structure**:
1. The Challenge: 19 parsers, which to choose?
2. Phase I: Public Benchmark Screening (OmniDocBench)
3. Phase II: Domain-Specific Validation (PDF-Bench approach)
4. Step 1: Document Collection (100-200 representative samples)
5. Step 2: Ground Truth Creation (manual + validation)
6. Step 3: Metric Selection (text vs structure vs tables)
7. Step 4: Parser Testing (top 3-5 candidates)
8. Step 5: Analysis & Decision (trade-offs, cost, speed, accuracy)
9. Decision Trees: Use case → recommended parsers
10. Maintenance: Monitor production, detect drift

**Deliverables**:
- `blog/05_evaluation_framework.md`
- `blog/assets/05_decision_tree.png` (parser selection flowchart)
- `blog/assets/05_evaluation_process.png` (phase diagram)

---

### TASK-009: Blog Post #6 - Beyond Text Accuracy (Multi-Metric Evaluation)
**Status**: Blocked by TASK-001 | **Hours**: 3 | **Priority**: Medium
**Technical deep-dive**

**Length**: 2,500-3,000 words
**Audience**: Senior engineers (not researchers)

**Structure**:
1. The Myth: "90% accuracy" doesn't tell the whole story
2. Text Accuracy Metrics: edit_similarity, chrF++, CER
3. Structure Metrics: tree_similarity (Markdown AST), element_f1 (detection)
4. Table Metric: TEDS (Tree Edit Distance-based Similarity)
5. Example Failures: High text score, low structure score → broken document
6. Metric Trade-offs: What to prioritize for RAG vs search vs archival
7. Benchmarking Best Practices: Multiple metrics, not single score
8. PDF-Bench Implementation: Open-source, reproducible

**Deliverables**:
- `blog/06_multi_metric_evaluation.md`
- `blog/assets/06_metric_examples.png` (visual examples)
- `blog/assets/06_parser_profiles_radar.png` (multi-metric comparison)

---

### TASK-010: Blog Post #7 - Creating Domain-Specific Corpora (Optional)
**Status**: Blocked by TASK-001 | **Hours**: 3 | **Priority**: Low
**How-to guide for replication**

**Length**: 2,500-3,000 words
**Value**: Privacy-preserving corpus generation

**Structure**:
1. Why Synthetic: Privacy, control, perfect ground truth
2. Our Approach: DOCX → PDF pipeline (LibreOffice headless)
3. Document Parameterization: Fonts, colors, logos, layouts
4. Structure Variation: Tables (simple → complex), lists (flat → nested)
5. Ground Truth Extraction: DOCX internals → Markdown
6. Validation: Ensure ground truth matches semantic intent
7. Scale Considerations: 100-200 documents sufficient
8. Tools & Templates: PDF-Bench open-source corpus builders
9. Case Studies: Legal, invoices, HR corpora from PDF-Bench

**Deliverables**:
- `blog/07_creating_domain_corpora.md`
- `blog/assets/07_pipeline_diagram.png` (DOCX → PDF process)
- `blog/assets/07_parameterization_examples.png` (template variations)

---

## Phase 4: GitHub & Documentation Polish (Week 3-4, 12h)

### TASK-011: Update GitHub README with Actual Results
**Status**: Blocked by TASK-001, TASK-002 | **Hours**: 2 | **Priority**: Medium

**What**: Replace placeholder 31-doc results with comprehensive 278-doc data

**Changes**:
- Update top 5 leaderboard (docling, marker_ollama, pymupdf4llm, pdfplumber, pypdf)
- Corpus statistics: 278 docs (was 31), 4 domains
- Add links to blog posts (placeholders for unpublished)
- Update quick-start section with working examples
- Verify installation instructions

**Deliverables**:
- `README.md` - updated top-level README
- `docs/RESULTS.md` - comprehensive results tables
- `docs/QUICKSTART.md` - new quick-start guide

---

### TASK-012: Create Visualizations & Charts
**Status**: Blocked by TASK-001, TASK-002 | **Hours**: 6 | **Priority**: Medium

**What**: Generate publication-quality charts for blog posts and documentation

**Charts Needed**:
1. Leaderboard comparison tables (OmniDocBench vs PDF-Bench)
2. Domain-specific heatmaps (parsers × domains × metrics)
3. Parser decision tree flowchart
4. Structure gap visualization (83% text vs 33% structure)
5. Radar charts for parser profiles (6 metrics)
6. Head-to-head comparison: Docling vs Marker
7. Example failure cases (side-by-side)

**Technical**:
- Use matplotlib/seaborn for charts
- Use Mermaid for flowcharts/diagrams
- Create `scripts/generate_charts.py` for reproducibility
- Style: Clean, professional, color-blind friendly
- Export: 300 DPI PNG for blog, SVG for web

**Deliverables**:
- `blog/assets/` - 15-20 charts for blog posts
- `docs/assets/` - documentation diagrams
- `scripts/generate_charts.py` - reproducible chart generation

---

### TASK-013: Documentation Polish & Examples
**Status**: Blocked by TASK-001 | **Hours**: 4 | **Priority**: Low

**What**: Create comprehensive documentation and examples

**Deliverables**:
- `docs/QUICKSTART.md` - 5-minute setup guide
- `examples/benchmark_tutorial.ipynb` - walkthrough notebook
- `docs/API.md` - API reference for key modules
- `CONTRIBUTING.md` - contribution guidelines with dev setup
- `docs/FAQ.md` - common issues and solutions

---

## Phase 5: Rollout & Engagement (Week 5-8, 8h)

### TASK-014: Blog Post Publishing Schedule
**Status**: Blocked by TASK-004-010 | **Hours**: 6 | **Priority**: Medium

**Publishing Schedule**:
- **Week 1**: Blog #1 (Comprehensive Comparison) - flagship, most important
- **Week 2**: Blog #2 (Docling vs Marker) - attention-grabbing, HN submission
- **Week 3**: Blog #3 (Structure Gap) - problem definition
- **Week 4**: Blog #4 (Domain Rankings) - methodology proof
- **Week 6**: Blog #5 (Evaluation Framework) - practical guide
- **Week 8**: Blog #6 (Multi-Metric) - technical deep-dive
- **Week 10**: Blog #7 (Corpus Creation) - replication guide (optional)

**Promotion Strategy**:
- **Hacker News**: Submit posts #1, #2, #3 (most attention-grabbing)
- **Reddit**: r/MachineLearning, r/LLMs, r/datascience
- **LinkedIn**: Target enterprise AI decision-makers
- **Twitter/X**: Tag parser authors (@marker, @docling teams) for validation
- **Dev.to / Medium**: Cross-posting for wider reach
- **Direct Outreach**: Parser maintainers for validation and amplification

**Deliverables**:
- Published blog posts on company website/blog platform
- Social media promotion threads
- Engagement metrics tracking spreadsheet

---

### TASK-015: Community Engagement & Iteration
**Status**: Blocked by TASK-014 | **Hours**: 2 | **Priority**: Low
**Ongoing throughout rollout**

**Activities**:
- Respond to HN/Reddit comments within 24 hours
- Track inbound inquiries (demo requests, consulting leads)
- Document feedback for methodology improvements
- Create GitHub issues for community feature requests
- Iterate on blog posts based on feedback (corrections, clarifications)

**Success Metrics**:
- HN upvotes: 100+ for posts #1-3 (credibility)
- GitHub stars: 100+ within 8 weeks
- Inbound leads: 5-10 qualified consulting inquiries
- Blog views: 5,000+ across all posts
- Conference talk submissions: 1-2 (optional)

**Deliverables**:
- Feedback log with action items
- Lead tracking spreadsheet
- Updated blog posts (corrections/additions)
- Community engagement metrics report

---

## Parallel Execution Opportunities

To maximize efficiency, several tasks can run in parallel:

### Group 1: Benchmark + Prep (Week 1)
- **TASK-001** (background): 8h overnight benchmark run
- **TASK-013** (foreground): Documentation structure while waiting

### Group 2: Analysis Tasks (Week 1)
- **TASK-002**: Domain analysis
- **TASK-003**: OmniDocBench comparison
(Independent tasks, can run simultaneously)

### Group 3: Tier 1 Blog Posts (Week 1-2)
- **TASK-004**: Comprehensive comparison
- **TASK-005**: Docling vs Marker
- **TASK-006**: Structure gap
(All depend on TASK-001, but independent of each other)

### Group 4: Tier 2 Blog Posts (Week 2-4)
- **TASK-007**: Domain rankings
- **TASK-008**: Evaluation framework
- **TASK-009**: Multi-metric evaluation
- **TASK-010**: Corpus creation
(Can be written in parallel)

### Group 5: GitHub Polish (Week 3-4)
- **TASK-011**: README update
- **TASK-012**: Visualizations
- **TASK-013**: Documentation
(Independent of blog writing)

---

## Risk Mitigation

### Risk 1: Benchmark Fails to Complete (CRITICAL)
**Risk**: TASK-001 fails after 6 hours, blocks all downstream work
**Mitigation**:
- Run with monitoring script, restart on failure
- Handle parser failures gracefully (docling 23% expected)
- Save intermediate results every hour
- Have fallback: use 31-doc results if 278-doc fails
**Impact**: Critical path blocked, 2-day delay

### Risk 2: Docling Failure Rate Higher Than Expected
**Risk**: 23% → 40% failure rate invalidates results
**Mitigation**:
- Document failures as part of reliability analysis
- Include in blog posts as trade-off discussion ("high quality, lower reliability")
- Becomes a feature, not a bug
**Impact**: Medium - adjust narrative

### Risk 3: Blog Posts Take Longer Than Estimated
**Risk**: 3-4h → 6-8h per post due to data analysis complexity
**Mitigation**:
- Focus on quality over quantity (6 excellent > 7 rushed)
- Can extend timeline by 2 weeks
- Drop TASK-010 (optional) if time-constrained
**Impact**: Low - schedule flexibility

### Risk 4: OmniDocBench Shows Contradictory Results
**Risk**: Rankings diverge dramatically, undermines complementarity positioning
**Mitigation**:
- Frame as "different benchmarks measure different things"
- Emphasize that divergence PROVES need for domain-specific validation
- Adjust messaging: "This is exactly why you need both"
**Impact**: Medium - requires messaging pivot

### Risk 5: Low Engagement on Blog Posts
**Risk**: Posts get <20 HN upvotes, no inbound leads
**Mitigation**:
- Iterate on headlines (A/B test)
- Promote more aggressively (direct outreach to parser authors)
- Engage deeply with comments to drive discussion
- Content still serves as reference material for direct sales
**Impact**: Low - content has value beyond viral reach

---

## Success Criteria

### Technical Success
- ✅ 278-doc benchmark complete with all 6 metrics
- ✅ Domain-specific leaderboards showing ranking changes
- ✅ OmniDocBench comparison validating complementarity
- ✅ All results reproducible and documented

### Content Success
- ✅ 6-7 high-quality blog posts published (3,000+ words each)
- ✅ GitHub README updated with actual results
- ✅ Documentation polished and complete
- ✅ Visualizations publication-ready

### Business Success
- ✅ 5-10 inbound consulting inquiries ("Can you help us parse OUR documents?")
- ✅ 100+ GitHub stars within 8 weeks
- ✅ HN front page for 1-2 posts (100+ upvotes)
- ✅ Industry discussion/citations (other benchmarks reference PDF-Bench)
- ✅ Conference talk submissions (1-2 accepted talks)

---

## Next Steps

To begin execution:

1. Review this plan and `state.json`
2. Run `/next` to start TASK-001 (benchmark)
3. Monitor benchmark progress overnight
4. Run `/next` iteratively for subsequent tasks
5. Use `/system:status` to track overall progress

**First command to run**:
```bash
/next
```

This will load TASK-001 and create the comprehensive benchmark configuration.

---

**Plan Status**: ✅ Ready to Execute
**Dependencies**: All tasks properly sequenced with clear acceptance criteria
**Timeline**: 8 weeks to complete, 2-week MVP possible
**Risk Level**: Low - no external dependencies, all work self-contained

Let's ship this.
