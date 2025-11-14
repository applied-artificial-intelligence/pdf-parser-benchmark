# Exploration Summary: PDF-Bench Implementation

## Codebase Analysis

**Current State**: Empty project (newly initialized)

**Project Context**:
- Location: `/home/stefan/projects/pdf-bench/`
- Configuration: Claude Code configured with standard Python development setup
- MCP Servers: chrome-devtools, serena, context7, sequential-thinking available
- No existing code or dependencies yet

## Requirements Analysis Summary

This is a **substantial, production-grade project** with the following complexity profile:

### Scope Classification
- **Size**: Large (estimated 5,000-10,000 LOC for MVP)
- **Complexity**: High (multi-domain: corpus building, metric computation, parser orchestration)
- **Timeline**: 4-8 weeks for v0.1 MVP (single developer)
- **Strategic Value**: High (thought leadership, client tool, community asset)

### Core Components (5 Major Systems)

1. **Corpus Builder Pipeline** (builders/)
   - LaTeX→Markdown (academic track): LaTeXML integration
   - HTML→Markdown (business track): Web scraping, HTML parsing
   - Synthetic generation (DOCX/MD→PDF): Template system
   - Download orchestration, caching, validation

2. **Ground Truth Management** (ground_truth/, datasets/)
   - Markdown normalization engine
   - YAML metadata schema and validation
   - Corpus versioning and integrity checks
   - Dataset card (DATASHEET.md) generation

3. **Parser Adapter Framework** (pdf_bench/systems/)
   - Abstract base class (BaseParser)
   - 7+ concrete adapters (Marker, Nougat, AWS, Azure, Google, Unstructured, PyMuPDF)
   - API rate limiting, retry logic, cost tracking
   - Output caching (hash-based)

4. **Metric Computation Engine** (pdf_bench/metrics/)
   - Text metrics: Normalized Edit Distance, chrF++
   - Structure metrics: AST Tree-Edit Distance, Element F1
   - Table metrics: TEDS wrapper, cell content F1
   - Math metrics: Normalized LaTeX matching
   - Performance metrics: latency, throughput, cost

5. **Benchmark Runner & Reporting** (pdf_bench/core.py, report.py, cli.py)
   - Benchmark configuration (YAML)
   - Parallel execution orchestration
   - Result aggregation and persistence
   - HTML/Markdown report generation (leaderboards, breakdowns, failure analysis)
   - CLI interface (Typer)

## Technical Architecture Assessment

### Strengths of Proposed Design
1. **Clear Separation of Concerns**: Builder → GT → Adapters → Metrics → Reports
2. **Extensibility**: Plugin architecture for parsers and metrics
3. **Legal Safety**: "Recipes-only" approach avoids redistribution issues
4. **Metric Rigor**: Multi-layered evaluation (text, structure, domain-specific)

### Implementation Challenges

#### Challenge 1: LaTeX Processing Complexity
**Issue**: LaTeX→Markdown conversion is non-trivial
- LaTeXML is Perl-based (subprocess management required)
- Complex macro expansion, bibliography handling
- Inconsistent arXiv source quality

**Recommendation**:
- Start with well-formed arXiv papers (recent submissions)
- Implement robust error handling and fallback to Pandoc
- Manual validation for initial 10-20 documents to establish quality baseline

#### Challenge 2: Table Ground Truth Ambiguity
**Issue**: Complex tables have multiple valid Markdown representations
- HTML table ordering (row-first vs column-first)
- Whitespace in cells
- Merged cell semantics

**Recommendation**:
- Implement canonical HTML table normalization (lowercase tags, sorted attrs)
- Use TEDS metric (structural similarity) rather than exact match
- Document ambiguity cases in DATASHEET.md

#### Challenge 3: Metric Implementation Dependencies
**Issue**: Some metrics require complex dependencies
- AST Tree-Edit Distance: requires `zss` or `apted` (graph algorithms)
- TEDS: requires `table-recognition-metric` (may have OpenCV deps)
- chrF++: requires `sacrebleu`

**Recommendation**:
- Use Poetry for dependency management (handles complex dependency graphs)
- Make advanced metrics "optional extras" (e.g., `pip install pdfbench[metrics]`)
- Provide fallback implementations for basic metrics

#### Challenge 4: Commercial API Adapter Maintenance
**Issue**: Cloud APIs change frequently
- Breaking changes in response schemas
- Deprecation of features
- Rate limit variations

**Recommendation**:
- Pin API client library versions in adapters
- Implement adapter versioning (e.g., `AWSTextractParserV2`)
- Comprehensive integration tests with mocked responses
- Version compatibility matrix in docs

## Implementation Strategy

### Phase 1: Foundation (Week 1-2)
**Goal**: Establish core infrastructure

1. **Project Setup**
   - Poetry configuration (pyproject.toml)
   - Directory structure
   - CI/CD skeleton (GitHub Actions for linting, testing)

2. **BaseParser Interface & Simple Adapter**
   - Define abstract interface
   - Implement PyMuPDFParser (baseline, no external API)
   - Basic caching mechanism

3. **Simple Metric Implementation**
   - Normalized Edit Distance (text-only)
   - Basic Element F1 (count heading/paragraph types)

4. **Minimal CLI**
   - `pdfbench run` with hardcoded test case
   - JSON output

**Deliverable**: Can run PyMuPDF on a single test PDF, compute basic metrics, output JSON

### Phase 2: Corpus Builder - Synthetic Track (Week 2-3)
**Goal**: Create reproducible, known-good ground truth

1. **Markdown→PDF Pipeline**
   - 5-10 hand-crafted Markdown documents (varying complexity)
   - Pandoc integration with Eisvogel template
   - Round-trip validation

2. **DOCX→PDF Pipeline**
   - 3-5 DOCX templates (simple report, table-heavy, multi-column)
   - python-docx-template integration
   - LibreOffice headless conversion

3. **Ground Truth Validation**
   - Checksum verification
   - Metadata YAML schema validation
   - Human review process

**Deliverable**: ~20 synthetic documents with perfect ground truth

### Phase 3: Core Metrics & Open-Source Adapters (Week 3-4)
**Goal**: Complete MVP evaluation framework

1. **Advanced Metrics**
   - AST Tree-Edit Distance (using mistune + zss)
   - TEDS implementation (using table-recognition-metric)

2. **Open-Source Adapters**
   - MarkerParser
   - NougatParser
   - UnstructuredParser

3. **Benchmark Runner**
   - YAML config loading
   - Parallel execution (multiprocessing)
   - Progress tracking

**Deliverable**: Can benchmark 3 open-source parsers on synthetic corpus

### Phase 4: Reporting & Business Corpus (Week 4-6)
**Goal**: Complete MVP feature set

1. **HTML Report Generation**
   - Jinja2 templates
   - Leaderboard, metric breakdown
   - Per-document diff viewer

2. **GOV.UK Scraper**
   - BeautifulSoup-based HTML extraction
   - URL → Ground Truth pipeline
   - 20-30 documents harvested

3. **SEC EDGAR Scraper**
   - HTML/XBRL parsing
   - Table extraction focus
   - 10-20 financial filings

**Deliverable**: Full HTML report on mixed corpus (~50-70 docs)

### Phase 5: Academic Corpus & Commercial Adapters (Week 6-8)
**Goal**: Complete v0.1 MVP

1. **arXiv Pipeline**
   - LaTeXML integration
   - arXiv API for metadata/download
   - 30-50 papers processed

2. **Commercial API Adapters**
   - AWS Textract (boto3)
   - Azure Document Intelligence (azure-ai-formrecognizer)
   - Cost tracking and estimation

3. **Documentation**
   - DATASHEET.md (dataset card)
   - CONTRIBUTING.md
   - README.md with examples

**Deliverable**: Full v0.1 release ready for open-source launch

## Technology Stack Recommendations

### Core Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.10"
# CLI
typer = "^0.9.0"
rich = "^13.0.0"  # Beautiful terminal output

# Document Processing
beautifulsoup4 = "^4.12.0"
lxml = "^4.9.0"
python-docx = "^1.0.0"
python-docx-template = "^0.16.0"

# Markdown Processing
mistune = "^3.0.0"  # Fast, extensible MD parser
PyYAML = "^6.0"

# Metrics
python-Levenshtein = "^0.21.0"
sacrebleu = "^2.3.0"
zss = "^1.2.0"  # Tree edit distance

# Optional heavy dependencies
[tool.poetry.group.metrics.dependencies]
table-recognition-metric = "^1.0.0"  # TEDS

# Parser adapters
[tool.poetry.group.parsers.dependencies]
pymupdf = "^1.23.0"
# marker - install from git
# nougat - install from git
unstructured = "^0.10.0"

# Commercial APIs
[tool.poetry.group.commercial.dependencies]
boto3 = "^1.28.0"  # AWS
azure-ai-formrecognizer = "^3.3.0"  # Azure

# Development
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
ruff = "^0.1.0"
mypy = "^1.6.0"
```

### External Tools (Document via README)
- **LaTeXML**: `apt-get install latexml` or `brew install latexml`
- **Pandoc**: `apt-get install pandoc` or `brew install pandoc`
- **LibreOffice**: `apt-get install libreoffice` (for headless conversion)

## Risk Mitigation Strategies

### Risk 1: LaTeX Conversion Failures
- **Mitigation**: Multi-stage fallback (LaTeXML → Pandoc → Skip)
- **Acceptance Criteria**: 80% success rate acceptable for v0.1
- **Logging**: Detailed error logs for failed conversions

### Risk 2: Parser Adapter Breakage
- **Mitigation**: Version pinning, integration tests with recorded responses
- **Monitoring**: Weekly CI runs against live APIs (with rate limiting)

### Risk 3: Metric Disagreement
- **Mitigation**: Document metric definitions in detail
- **User Control**: Allow custom metric weights in config
- **Transparency**: Show all individual metric scores, not just composite

### Risk 4: Dataset Licensing Ambiguity
- **Mitigation**: Conservative approach - only use explicitly permissive sources
- **Documentation**: Per-document license tracking in YAML
- **Legal Review**: Consult with legal before v0.1 release

## Alternative Approaches Considered

### Alternative 1: Use OmniDocBench Despite License
**Rejected Because**: Non-commercial license is a hard blocker for consulting use case

### Alternative 2: Manual Annotation for Business Docs
**Rejected Because**: Not scalable, expensive, introduces human error
**Chosen Instead**: Synthetic generation + harvested paired HTML/PDF

### Alternative 3: Single "Magic Number" Metric
**Rejected Because**: Obscures strengths/weaknesses of parsers
**Chosen Instead**: Multi-dimensional scorecard with breakdowns

### Alternative 4: Web-Based Leaderboard (v0.1)
**Rejected Because**: Increases scope significantly, delays launch
**Deferred To**: v1.0 roadmap

## Integration Points

### MCP Tool Usage Opportunities

1. **Serena (Semantic Code Analysis)**
   - Once codebase exists: Use for refactoring, finding symbol references
   - Efficiency: 70-90% token savings during code review/debugging phases

2. **Context7 (Library Docs)**
   - Real-time lookups for: LaTeXML, mistune, sacrebleu, table-recognition-metric
   - Useful during implementation of metric adapters

3. **Sequential Thinking (Complex Reasoning)**
   - Use for: Metric algorithm design, error taxonomy creation
   - Example: "How should we normalize HTML tables for TEDS comparison?"

4. **Chrome DevTools**
   - Not directly applicable (no web scraping in MVP - uses static downloads)
   - Future use: Testing web-based report viewer (v1.0+)

## Next Steps Recommendation

Based on this exploration, the project is **ready for detailed planning**. The requirements are well-specified, but the implementation is non-trivial and requires systematic breakdown.

### Recommended Next Action

**Run `/plan` to create a detailed task breakdown with dependencies.**

Key areas requiring planning attention:
1. Phased implementation sequence (foundation → synthetic → metrics → adapters → corpus)
2. Test strategy for each component (unit, integration, E2E)
3. Corpus builder parallelization strategy (arXiv/GOV.UK scraping is I/O bound)
4. Metric implementation order (simple → complex)
5. Documentation and release checklist

### Estimated Effort (Single Developer, Full-Time)

- **MVP (v0.1)**: 6-8 weeks
- **Extended Corpus (v1.0)**: +4 weeks
- **Advanced Features (v2.0)**: +6 weeks

### Key Success Factors

1. **Start Simple**: Synthetic corpus + basic metrics first (validate architecture)
2. **Incremental Validation**: Test each corpus source independently before integration
3. **Community Early**: Open-source foundation code early for feedback
4. **Document Rigorously**: DATASHEET.md and metric definitions are critical for trust

## Conclusion

This is a **well-scoped, high-value project** with clear strategic benefits. The technical challenges are manageable with the phased approach outlined above. The "recipes-only" corpus strategy elegantly solves the licensing problem while the multi-layered metrics provide genuine value over existing benchmarks.

**Ready to proceed to planning phase.**
