# PDF Parser Benchmark: Content Brief

*Last Updated: 2025-12-02*

**Single entry point for content marketing.** This document provides quick data access and references detailed docs where needed.

## Quick Numbers

| Category | Count |
|----------|-------|
| Parsers with results | 26 (15 open source, 4 commercial, 7 frontier LLM) |
| Total results | 7,507 |
| Documents | 358 across 7 domains |
| Metrics | 6 (edit_similarity, chrf++, tree_similarity, CER, TEDS, element_f1) |

**Coverage by parser type:**
- Open source: 358 docs each
- Commercial APIs: 208 docs each
- Frontier LLMs: 28-30 docs each

## Current Leaders (December 2025)

### Text Accuracy (edit_similarity)

| Rank | Parser | Score | Docs | Type | Cost |
|------|--------|-------|------|------|------|
| 1 | GPT-5.1 | 92.0% | 28 | frontier_llm | ~$0.05/page |
| 2 | Gemini 3 Pro | 87.2% | 28 | frontier_llm | ~$0.03/page |
| 3 | GPT-4o | 81.0% | 28 | frontier_llm | ~$0.02/page |
| 4 | pypdfium2 | 80.6% | 358 | open_source | free |
| 5 | pypdf | 80.6% | 358 | open_source | free |

### Commercial APIs (208 docs each)

| Rank | Parser | Score | Speed | Notes |
|------|--------|-------|-------|-------|
| 1 | Databricks | 64.1% | 10.1s | Best commercial |
| 2 | Azure Doc Intelligence | 63.0% | 3.4s | Fastest commercial |
| 3 | AWS Textract | 56.0% | 1.6s | |
| 4 | Google Document AI | 54.8% | 3.4s | |

**Key insight**: Commercial OCR APIs score 17-26 points *lower* than free open source parsers on text extraction. They're optimized for OCR/forms, not digital PDFs.

### Structure Recovery (tree_similarity)

| Rank | Parser | Score | Notes |
|------|--------|-------|-------|
| 1 | marker_ollama | 50.7% | Best overall |
| 2 | Claude Sonnet 4.5 | 44.5% | Best frontier LLM |
| 3 | GPT-5.1 | 44.2% | Close second |
| 4 | tika | 43.6% | Best pure open source |
| 5 | GPT-4o-mini | 13.3% | **Destroys structure** |

### Speed (median parse time)

| Rank | Parser | Time | Category |
|------|--------|------|----------|
| 1 | pymupdf | 0.7ms | Local, no features |
| 2 | Gemini 2.0 Flash | 3.8s | Fastest LLM |
| 3 | GPT-5.1 | 9.8s | Best accuracy |
| 4 | marker | 14.7s | Best open source OCR |

## Key Content Angles

### 1. "The 12-Point Accuracy Gap"
GPT-5.1 (92%) vs best open source (80%). When is $0.05/page worth it?

### 2. "GPT-4o-mini Destroys Your Document Structure"
81% text accuracy but only 13% structure preservation. Hidden danger for RAG.

### 3. "LlamaParse: The $0.003/page Sweet Spot"
78% accuracy at 1/15th the cost of GPT-5.1. Purpose-built beats general-purpose.

### 4. "Open Source Holds Its Own"
pypdfium2 at 80.6% is only 12 points behind GPT-5.1, at 0 cost and 10,000x speed.

### 5. "The Metric That Lies: ChrF++ vs Edit Similarity"
Open source scores 90+ ChrF++ but 70s edit similarity. Why you need multiple metrics.

### 6. "Commercial OCR APIs Are Losing to Free Tools"
AWS, Azure, Google, Databricks score 54-64% vs 80% for free open source. They're built for scanned docs, not digital PDFs.

## Pareto Frontier Summary

Three distinct clusters:
1. **Speed-optimized**: pymupdf, pypdf (sub-ms, 80% accuracy, free)
2. **Balanced**: LlamaParse, Gemini 2.0 Flash (seconds, 77-78% accuracy, $0.001-0.003)
3. **Quality-optimized**: GPT-5.1, Gemini 3 Pro (10-30s, 87-92% accuracy, $0.03-0.05)

No parser dominates all dimensions. Choice depends on volume, budget, and quality requirements.

## Data Files

All in `data_exports/`:

| File | Use For |
|------|---------|
| `parser_scores_text_extraction.csv` | Main accuracy comparison |
| `leaderboard_structure.csv` | Structure preservation ranking |
| `leaderboard_speed.csv` | Speed ranking |
| `parser_capabilities.csv` | Parser metadata and features |
| `detailed_results.csv` | All 7,507 individual results |

See `data_exports/README.md` for complete file descriptions.

## Pareto Frontier Visualization

**Status: Data ready, chart needs creation**

The Pareto frontier (speed vs accuracy trade-off) is a key visualization. Data is in `parser_scores_text_extraction.csv`:

```
Columns needed:
- parser (label)
- type (color: open_source, frontier_llm, commercial)
- avg_parse_time_ms (X axis, log scale)
- avg_edit_similarity (Y axis)
```

To create the chart:
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data_exports/parser_scores_text_extraction.csv')
# X: avg_parse_time_ms (log scale)
# Y: avg_edit_similarity
# Color by: type
# Label key points: pymupdf (fastest), GPT-5.1 (most accurate), LlamaParse (best value)
```

Existing charts in `docs/charts/` are **outdated** (Nov 24, pre-frontier models).

## Detailed References

| Topic | Document |
|-------|----------|
| Presentation guidelines | `docs/CONTENT_MARKETING_FRAMEWORK.md` |
| Metric definitions | `docs/METRICS.md` |
| Corpus details | `docs/CORPORA.md` |
| Key findings | `docs/FINDINGS.md` |
| Full results analysis | `docs/RESULTS.md` |

## Regenerating Data

```bash
uv run python scripts/export_visualization_data.py
```

## Caveats

1. Frontier LLMs tested on 28-30 docs (indicative, not statistically robust)
2. Commercial APIs tested on 208 docs (statistically meaningful)
3. GPT-4o structure score (3.3%) may be prompt/format issue - needs investigation
4. Table extraction data limited (12 docs with tables)
5. Landing AI and Gemini 1.5 Pro failed all tests (billing/model deprecation) - no data
6. Commercial APIs optimized for OCR/forms - low scores on digital PDFs are expected behavior
