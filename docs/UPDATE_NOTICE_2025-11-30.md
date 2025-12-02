# PDF-Bench Update Notice: Frontier LLM Benchmarks

**Date**: 2025-11-30
**Version**: 2.3
**Status**: Ready for content marketing review

---

## Summary of Changes

Major benchmark update adding **Frontier LLM parsers** (GPT-5.1, Gemini 3 Pro, Claude Sonnet 4.5) and **LlamaParse** to our evaluation. This significantly expands our coverage and enables new content angles.

---

## New Benchmark Data

### Premium Frontier LLMs (28 documents tested)

| Model | Edit Similarity | ChrF++ | Tree Similarity | Est. Cost/Page |
|-------|-----------------|--------|-----------------|----------------|
| **GPT-5.1** | **92%** | **93.0** | 44% | ~$0.05 |
| Gemini 3 Pro | 87% | 86.2 | 43% | ~$0.03 |
| Claude Sonnet 4.5 | 80% | 81.7 | 44% | ~$0.04 |

### Budget LLMs + LlamaParse (30 documents tested)

| Model | Edit Similarity | ChrF++ | Tree Similarity | Cost/Page |
|-------|-----------------|--------|-----------------|-----------|
| **LlamaParse** | **78%** | **83.4** | **39%** | $0.003 |
| Gemini 2.0 Flash | 77% | 80.3 | 35% | ~$0.001 |
| GPT-4o-mini | 75% | 76.7 | **13%** | ~$0.002 |
| Claude 3.5 Haiku | 68% | 69.7 | 33% | ~$0.002 |

### Reference: Best Open Source (353 documents)

| Parser | Edit Similarity | ChrF++ | Tree Similarity | Cost |
|--------|-----------------|--------|-----------------|------|
| pypdfium2 | 78% | 90.4 | 40% | Free |
| pypdf | 78% | 90.4 | 40% | Free |

---

## Key Findings for Content

### 1. The 14-Point Premium Gap
- GPT-5.1 (92%) vs best open-source (78%) = **14 percentage points**
- First time we've seen >90% edit similarity
- Worth it for high-value, low-volume documents

### 2. LlamaParse: The Sweet Spot
- **78% edit similarity** - matches best open-source
- **$0.003/page** - 10x cheaper than premium LLMs, 16x cheaper than GPT-5.1
- Purpose-built for PDF (not a general LLM doing PDF on the side)
- Free tier: 1,000 pages/day for testing
- **Recommendation**: Default choice for most use cases

### 3. GPT-4o-mini's Hidden Problem
- 75% edit similarity looks acceptable
- BUT only **13% tree similarity** (vs 35%+ for others)
- **Destroys document structure** while extracting text
- **Avoid for RAG pipelines** where structure matters

### 4. ChrF++ vs Edit Similarity Disconnect
- Open source parsers score **90+ ChrF++** but **70s edit similarity**
- ChrF++ measures text fidelity (characters match)
- Edit similarity captures structure preservation
- Need both metrics to evaluate properly

---

## Updated Files

| File | Changes |
|------|---------|
| `README.md` | Added NEW section on Frontier LLMs at top, updated parser count |
| `docs/LEADERBOARDS.md` | Added full LLM leaderboard section with rankings and guide |
| `docs/CONTENT_MARKETING_FRAMEWORK.md` | Added Tier 0/0.5 for LLMs, 4 new blog post ideas |

---

## New Blog Post Ideas

1. **"GPT-5.1 vs Open Source: The 14-Point Quality Gap"**
   - When is $0.05/page worth it?
   - Decision framework by use case

2. **"LlamaParse: The $0.003/page Sweet Spot"**
   - Best quality/cost ratio
   - Comparison with frontier LLMs

3. **"Why GPT-4o-mini Destroys Your Document Structure"**
   - The 13% tree similarity problem
   - Implications for RAG pipelines

4. **"The Metric That Lies: ChrF++ vs Edit Similarity"**
   - Why you need multiple metrics
   - What each actually measures

---

## Decision Matrix (Updated)

| Use Case | Recommended | Alternative | Avoid |
|----------|-------------|-------------|-------|
| **Max quality, low volume** | GPT-5.1 | Gemini 3 Pro | Open source |
| **Quality + cost balance** | **LlamaParse** | Gemini 2.0 Flash | GPT-4o-mini |
| **Budget, structure needed** | pypdfium2 | docling | GPT-4o-mini |
| **Budget, text only** | pypdfium2 | GPT-4o-mini | - |
| **RAG pipelines** | LlamaParse/docling | pymupdf4llm | GPT-4o-mini |
| **High volume processing** | pypdfium2 | pymupdf | Premium LLMs |

---

## Raw Data Location

- `results/frontier_premium_300p.json` - Premium LLM results
- `results/frontier_unified_30docs.json` - Budget LLM + LlamaParse results
- `results/full_corpus_353docs.json` - Open source baseline

---

## Action Items for Content Marketing

1. [ ] Update PDF benchmarking report with LLM section
2. [ ] Add decision matrix visualization
3. [ ] Consider blog post: "Frontier LLMs vs Traditional Parsers"
4. [ ] Update any existing cost comparisons
5. [ ] Add LlamaParse to recommendations

---

**Questions?** See updated `docs/LEADERBOARDS.md` for full details.
