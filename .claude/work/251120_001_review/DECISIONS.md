# Strategic Decisions for Content Marketing Execution

**Date**: 2025-11-20
**Decision Phase**: Exploration Complete, Ready for Planning

---

## Decision 1: Benchmark Scope

**Question**: Run full 278-doc evaluation or strategic subset?

**Options Evaluated**:
- A: Full 278 docs (31 synthetic + 108 legal + 100 invoices + 34 HR + 5 academic)
- B: Strategic 50-doc subset (10 from each domain)
- C: Expanded synthetic (100+ synthetic docs only)

**Decision**: **OPTION A - Full 278-doc evaluation**

**Rationale**:
- Marketing strategy explicitly requires domain-specific validation ("rankings change by domain")
- Only 8 additional hours beyond current 31-doc work (already done feasibility analysis)
- Enables all 12 blog posts as planned
- Provides authoritative data for credibility claims
- Cost is minimal (compute time only, no additional resources)
- Domain-specific leaderboards are core to positioning

**Impact**: Blocks nothing, enables everything

**Alternative Rejected**:
- Subset would undermine "domain-specific validation" claim
- Would require rewriting marketing strategy

---

## Decision 2: Parser Selection

**Question**: Which parsers to test? All 10 or just top performers?

**Options Evaluated**:
- A: All 10 open-source parsers (docling, marker_ollama, pdfplumber, pymupdf4llm, pymupdf, pypdfium2, pypdf, pdfminer, extractous, unstructured)
- B: Top 5 only (docling, marker_ollama, pdfplumber, pymupdf4llm, pdfminer)
- C: Mix of open-source + commercial (requires API setup)

**Decision**: **OPTION A - All 10 open-source parsers**

**Rationale**:
- Minimal additional time (~30 minutes per run for slower parsers)
- Shows breadth of evaluation landscape
- Demonstrates where different parsers excel/fail
- Supports "comprehensive evaluation of 10 PDF parsers" claim in marketing
- No commercial API setup required (deferred to later phase)
- Enables "there's a right tool for every use case" narrative

**Impact**: 
- Runtime: 9-10 hours (vs 4-5 if top 5 only)
- Analysis work: minimal increase
- Content value: significant increase

**Alternative Rejected**:
- Top 5 only would limit findings
- Would miss interesting domain-specific insights
- Wouldn't demonstrate full parser landscape

---

## Decision 3: OmniDocBench Integration

**Question**: How deep to integrate OmniDocBench? All 10 parsers or subset?

**Options Evaluated**:
- A: All 10 parsers on OmniDocBench (full comparison)
- B: Top 5 parsers on OmniDocBench (comparative analysis)
- C: Skip OmniDocBench for MVP (focus on PDF-Bench)

**Decision**: **OPTION B - Top 5 parsers on OmniDocBench demo images**

**Parsers**: docling, marker_ollama, pdfplumber, pymupdf4llm, pymupdf

**Rationale**:
- Answers critical research question: "Do rankings change on real-world docs?"
- Provides credibility (evaluated on independent benchmark)
- Documents synthetic vs real-world gap (11.5% already identified)
- ~2-3 hours additional runtime (manageable)
- Diminishing returns for all 10 (focus on insights)
- Top 5 provide sufficient comparison for marketing claims

**Impact**:
- Runtime: 2-3 hours
- Analysis: 1-2 hours for comparative insights
- Blog content: Enables claim "validated on OmniDocBench"

**Alternative Rejected**:
- All 10: Overkill, diminishing returns on additional parsers
- Skip: Would miss opportunity for dual-benchmark positioning

---

## Decision 4: Content Strategy

**Question**: Write all 12 blog posts or strategic subset?

**Options Evaluated**:
- A: Write all 12 full-length blog posts (5-8 min read each)
- B: 6-7 full posts + 3-5 summary outlines (expandable later)
- C: 3 mega-posts covering all material
- D: Wait until content marketing firm helps

**Decision**: **OPTION B - 6-7 full posts + summary outlines**

**MVP Phase (Weeks 1-4)**:
- 3 Tier 1 posts: Credibility establishment (full length, ~5-8 min)
- 3 Tier 2 posts: Methodology demonstration (full length, ~8-10 min)
- 3+ Tier 3 summaries: Domain-specific results (bullet points, expandable)

**Rationale**:
- Quality over quantity (6 great posts > 12 mediocre ones)
- Prevents burnout (50-70 hours total is already aggressive)
- Allows feedback incorporation and iteration
- Creates ongoing content pipeline (summaries → full posts)
- Maintains momentum (2-3 posts per week)
- Meets "12-week content calendar" without requiring all 12 in week 1

**Timeline**:
- Week 1-2: Tier 1 (credibility)
- Week 3-4: Tier 2 (methodology)
- Week 5-6: Tier 3 summaries + expansion
- Week 7-12: Domain-specific + production expertise

**Impact**:
- Time: 18-22 hours (vs 30+ for 12 full posts)
- Quality: Higher (less rushed)
- Sustainability: Better for long-term engagement

**Alternative Rejected**:
- All 12: Would require 35+ hours of writing (unrealistic)
- Mega-posts: Would lose blog post SEO benefits and shareability
- Defer: Would lose momentum and delay market entry

---

## Decision 5: GitHub Repository Scope

**Question**: How polished should the public repo be?

**Options Evaluated**:
- A: Fully polished (comprehensive docs, examples, CI/CD, notebooks)
- B: Core + good documentation (README, QUICKSTART, RESULTS, examples)
- C: Release as-is (minimal cleanup)

**Decision**: **OPTION B - Core + Good Documentation**

**Phase 1 (Week 2-3) - MVP**:
- Updated README with actual results
- QUICKSTART.md (5-minute setup)
- RESULTS.md (summary statistics)
- METRICS.md (metric explanations)
- Example code (evaluate_single_parser.py)
- One Jupyter notebook

**Phase 2 (Week 4-5) - Polish**:
- CORPORA.md (corpus documentation)
- CONTRIBUTING.md (how to add parsers)
- Additional notebooks (3-5)
- Code cleanup

**Defer to Later**:
- Full API documentation (parsers are community projects)
- Advanced CI/CD (GitHub Actions beyond basics)
- Commercial parser setup guides
- Interactive leaderboard website

**Rationale**:
- Professional appearance critical for credibility
- Clear setup instructions essential (reduces friction)
- Example code builds trust (reproducibility)
- ~10-12 hours achievable in week 1
- Can expand with Phase 2 without blocking launch
- Focuses on "credible and usable" over "comprehensive"

**Impact**:
- Week 1: MVP launch possible
- Week 2-3: Polish and expand
- Ongoing: Community contributions and feedback

**Alternative Rejected**:
- Full polish: Would delay launch by 2+ weeks
- As-is: Would hurt credibility (looks unmaintained)

---

## Decision 6: Rollout Timeline

**Question**: Launch everything at once or phase the release?

**Options Evaluated**:
- A: Phased release (Weeks 1-8, 2-3 posts per week)
- B: Big bang (all content + repo at once)
- C: Slow burn (1 post per week over 12 weeks)

**Decision**: **OPTION A - Phased Release (8-week cycle)**

**Schedule**:

| Week | Content | Goal |
|------|---------|------|
| 1-2 | Blog #1: Comprehensive comparison | Credibility |
| 1-2 | GitHub repo (MVP) | Product launch |
| 3-4 | Blog #2: Docling vs Marker | Attention |
| 3-4 | Blog #3: Structure gap | Problem framing |
| 3-4 | Blog #4: Domain variation | Proof point |
| 5-6 | Blog #5: How to evaluate | Framework |
| 5-6 | Blog #6: Multi-dimensional | Transparency |
| 5-6 | GitHub Phase 2 docs | Expansion |
| 7-8 | Blog #7+: Domain-specific | Results |
| 7-8 | Bonus: Production case study | Expertise |

**Rationale**:
- Creates momentum (not one-time spike)
- Allows feedback incorporation
- Spreads marketing effort over 8 weeks
- Builds narrative arc: credibility → methodology → practice
- Sustainable pace (2-3 posts per week)
- Each phase can inform next phase
- Hacker News timing: Can submit multiple times

**Impact**:
- Social media: Ongoing engagement (not single spike)
- SEO: Multiple entry points over time
- Feedback loop: Improve based on response
- Team morale: Achievable weekly goals

**Alternative Rejected**:
- Big bang: Would be overwhelming, waste compounding impact
- Slow burn: Would lose momentum, allow competitors to respond

---

## Decision 7: Risk Mitigation Strategy

**Question**: How to handle identified risks?

**Risk #1: Docling 23% Failure Rate**
- Decision: Document failures explicitly in blog posts
- Recommendation: Use with fallback strategy (implement in examples)
- Not a blocker: Marker and pdfplumber provide alternatives
- Transparency > hiding issues

**Risk #2: Synthetic vs Real-World Gap (11.5%)**
- Decision: Already identified and explained in documentation
- Not a blocker: OmniDocBench evaluation will validate gap
- Positioning: "Need both public + domain validation"
- Demonstrates rigor: Acknowledging limitations

**Risk #3: Blog Quality Rushed**
- Decision: Focus on 6-7 excellent posts (not 12)
- Not a blocker: Can expand summaries later
- Quality control: Internal review before publication
- Sustainability: Better long-term content

**Risk #4: GitHub Repo Not Ready**
- Decision: MVP by Week 2, don't announce before README updated
- Not a blocker: Can defer repo announcement if needed
- Quality gate: README must reflect actual results
- Flexibility: Can launch blog before repo if necessary

**Risk #5: Benchmark Runtime Longer**
- Decision: Start immediately, monitor progress
- Contingency: Use partial results if needed (still valuable)
- Mitigation: Run in background, parallelize analysis

**Impact**: All risks identified and have mitigation strategies. No blocking risks.

---

## Decision 8: Success Metrics

**Question**: How do we know this worked?

**Technical Success**:
- [x] element_f1 metric working (already done)
- [ ] 278-doc benchmark >95% success rate
- [ ] OmniDocBench evaluation complete
- [ ] All analysis scripts working
- [ ] Zero NaN/null values in results

**Content Success**:
- [ ] 6-7 blog posts published with actual numbers
- [ ] All claims supported by specific metrics
- [ ] Visualizations created and embedded
- [ ] Domain-specific leaderboards generated

**Product Success**:
- [ ] GitHub repo with clear documentation
- [ ] README reflects actual results
- [ ] QUICKSTART instructions work
- [ ] Example code runs without errors

**Marketing Success** (Post-Launch):
- [ ] Hacker News front page (target: >100 points)
- [ ] Reddit discussion (r/MachineLearning, r/Python)
- [ ] 100+ GitHub stars within 2 weeks
- [ ] Blog traffic baseline established
- [ ] Industry citations/references
- [ ] Inbound inquiry interest

---

## Decision 9: Scope Boundaries (What NOT to Do)

**Explicitly Deferred**:
- ❌ Commercial parser comparison (AWS, Azure, Google)
- ❌ Interactive leaderboard website
- ❌ Full API documentation
- ❌ Advanced CI/CD pipelines
- ❌ All 12 blog posts in week 1
- ❌ OCR/scanned document evaluation
- ❌ Production deployment guide (separate project)
- ❌ Machine learning model comparisons

**Rationale**: Scope focus (50-70 hours) enables execution. Scope creep delays launch.

**Later Phases**: All deferred items are valid for phase 2-4 work.

---

## Decision 10: Go/No-Go Final Assessment

**Technical Readiness**: ✅ **GO**
- All metrics working
- All parsers implemented
- Corpus complete
- No blocking issues

**Resource Readiness**: ✅ **GO**
- 1 FTE available for 2 weeks
- Infrastructure in place
- No API costs
- GPU optional (not required)

**Feasibility**: ✅ **GO**
- 50-70 hours is achievable
- Critical path well-defined
- Parallelizable work identified
- No sequential blockers

**Risk Profile**: ✅ **MANAGED**
- All major risks identified
- Mitigation strategies documented
- Contingencies available
- No existential risks

**Strategic Alignment**: ✅ **GO**
- Positions firm as expert
- Drives inbound inquiries
- Open-source contribution
- Content for 8+ weeks

---

## Authorization

**Status**: Ready for Planning Phase

**Next Action**: Run `/plan` to translate exploration into detailed work units

**Approval Needed**: Yes, on strategic decisions 1-6 before proceeding

---

**Document Created**: 2025-11-20
**Exploration Phase Duration**: Complete (3.5 hours analysis + strategic decisions)
**Ready for Execution**: Yes
