# Updated Parser Integration Plan

## Parsers to Include (8 total)

### Open Source Parsers (4)
1. **PyMuPDF** (baseline) - ✅ COMPLETE (TASK-008)
2. **pdfplumber** - ❌ NOT IN PLAN - Need to add
3. **Marker** (Meta) - ❌ TASK-029, TASK-030
4. **Unstructured.io** - ❌ TASK-033, TASK-034

**Removed from plan:**
- Nougat (Meta) - Academic-focused, heavy dependencies, slow inference
- Reason: Good for arXiv but redundant with Marker, adds complexity

### Commercial Cloud APIs (3)
5. **AWS Textract** - ❌ TASK-067
6. **Azure Document Intelligence** - ❌ TASK-068
7. **Google Document AI** - ❌ TASK-069 (currently optional)

### Platform-Integrated (1)
8. **Databricks `ai_parse_document`** - ❌ NOT IN PLAN - Need to add

## Databricks ai_parse_document Details

### What It Is
- SQL function: `ai_parse_document(content)`
- Built into Databricks platform (no separate API)
- Uses LLMs for document understanding
- Stores results in Unity Catalog (Delta tables)

### Key Capabilities
- Extracts text, tables, figures with bounding boxes
- AI-generated descriptions for figures/diagrams
- Spatial metadata preserved
- Supports: PDF, JPG/JPEG, PNG, DOC/DOCX, PPT/PPTX

### Competitive Claims
- "3-5x lower cost than AWS/Azure/Google"
- "Matches or exceeds quality of leading systems"
- Launched: Late 2024 (very new)

### Requirements
- Databricks workspace (US or EU region)
- Databricks Runtime 17.1+
- Access to Mosaic AI Model Serving
- Files must be stored as BINARY in Delta tables

### Integration Approach
**Challenge:** Requires Databricks environment, not just API calls

**Options:**
1. **Databricks-native adapter** - Requires Databricks account, workspace setup
2. **Document with setup instructions** - User must have Databricks
3. **Optional integration** - Include if user has Databricks access

**Recommendation:** Make it optional, document requirements clearly

### Limitations (per Databricks docs)
- Slow for dense documents
- Non-Latin alphabets may underperform
- Digital signatures may not process accurately
- "LLMs are emerging technology and may produce errors"

## pdfplumber Details

### What It Is
- Rule-based PDF extraction (like PyMuPDF, but different approach)
- Focus: Table extraction via visual layout analysis
- Python library: `pdfplumber`
- Maintained by BuzzFeed News (now independent)

### Key Capabilities
- Text extraction with character-level positioning
- **Strong table extraction** (visual layout analysis)
- Line, rectangle, curve detection
- Word/line clustering algorithms

### Why Include It
- Excellent table extraction (often better than PyMuPDF)
- Different approach than ML-based parsers
- Fast, deterministic, no GPU needed
- Free, open-source

### Integration Complexity
- Low (similar to PyMuPDF)
- Pure Python library
- Estimated: 3-4 hours (TASK-XXX)

## Updated Task Breakdown

### New Tasks to Add

**TASK-086: Implement pdfplumber Parser Adapter**
- Description: Create pdfplumber adapter implementing BaseParser interface
- Type: feature
- Phase: 4
- Dependencies: TASK-004, TASK-005
- Estimated: 3 hours
- Priority: high
- Acceptance Criteria:
  - pdf_bench/systems/pdfplumber.py created
  - Implements BaseParser interface
  - Text extraction with positioning
  - Table extraction via visual analysis
  - Cache integration
  - Integration tests

**TASK-087: Implement Databricks ai_parse_document Adapter**
- Description: Create Databricks adapter with workspace integration
- Type: feature
- Phase: 9 (commercial integrations)
- Dependencies: TASK-004, TASK-005
- Estimated: 6 hours (higher due to platform complexity)
- Priority: medium (optional)
- Acceptance Criteria:
  - pdf_bench/systems/databricks.py created
  - Implements BaseParser interface
  - Databricks SQL integration
  - Binary file handling
  - Unity Catalog result retrieval
  - Documentation for workspace setup
  - Integration tests (mock or requires Databricks account)

### Removed Tasks
- TASK-031: Install and Test Nougat Locally (redundant with Marker)
- TASK-032: Implement NougatParser Adapter (redundant with Marker)

### Updated Phase 4 Timeline

**Phase 4: Parser Integration (revised)**
- TASK-029: Install Marker (2h)
- TASK-030: Marker adapter (4h)
- TASK-033: Install Unstructured (2h)
- TASK-034: Unstructured adapter (4h)
- TASK-086: pdfplumber adapter (3h) - NEW
- **Subtotal: 15 hours for open-source parsers**

**Phase 9: Commercial APIs (revised)**
- TASK-067: AWS Textract (4h)
- TASK-068: Azure DI (4h)
- TASK-069: Google DocAI (4h) - keep as optional
- TASK-087: Databricks (6h) - NEW, optional
- TASK-070: Cost estimation (3h)
- TASK-071: Commercial tests (2h)
- TASK-072: Documentation (1h)
- **Subtotal: 24 hours (18h if skip Google + Databricks)**

## Final Parser List (Leaderboard)

**Tier 1: Always Include (6 parsers)**
1. PyMuPDF (baseline) ✅
2. pdfplumber (table-focused)
3. Marker (ML-based, open)
4. Unstructured.io (enterprise open)
5. AWS Textract (commercial leader)
6. Azure DI (commercial)

**Tier 2: Optional (2 parsers)**
7. Google DocAI (commercial alternative)
8. Databricks ai_parse_document (platform-specific)

**Total work for Tier 1: ~33 hours**
**Total work for Tier 1+2: ~43 hours**

## Credibility Impact

### With 6 Parsers (Tier 1):
- 2 rule-based (PyMuPDF, pdfplumber)
- 2 ML-based open-source (Marker, Unstructured)
- 2 commercial cloud (AWS, Azure)
- **Credibility: 8/10** - Comprehensive, balanced

### With 8 Parsers (Tier 1+2):
- Add Google + Databricks
- **Credibility: 9/10** - Industry-leading coverage

## Recommendations

1. **Start with Tier 1** (6 parsers) - covers all major categories
2. **Make Google optional** - can add later if needed
3. **Make Databricks optional** - requires platform access, document clearly
4. **Remove Nougat** - redundant with Marker, heavy dependencies

## Updated Timeline Estimate

**Open-source parsers:** 15 hours
**Commercial APIs:** 18 hours (skip Google/Databricks initially)
**Total Phase 4+9:** ~33 hours

Combined with:
- **Phase 5 (Runner):** 23 hours
- **Phase 6+8 (GOV.UK + arXiv):** 28 hours (skip SEC initially)

**Total to credible leaderboard: ~84 hours (~2 weeks full-time, 4 weeks part-time)**
