# Visualization Assets for Publication

Generated: 2024-11-24

## Location

All visualizations are in `docs/charts/`:

```
docs/charts/
├── parser_ranking.png/svg           # Overall leaderboard
├── domain_heatmap.png/svg            # Parser performance by domain
├── teds_comparison.png/svg           # Table extraction quality
└── metric_correlation.png/svg        # Metric relationships
```

## Usage Guide

### 1. Parser Rankings (`parser_ranking.png`)

**Purpose**: Show overall performance across 273 documents

**Key Insights**:
- pypdfium2 and pypdf lead at 78.3%
- Clear performance tiers visible
- Color gradient shows score ranges

**Use for**:
- Executive dashboard
- "Who's the best?" question
- Landing page hero section

### 2. Domain Performance Heatmap (`domain_heatmap.png`)

**Purpose**: Highlight domain-specific variance

**Key Insights**:
- No parser wins across all domains
- Invoices challenging for all parsers (<50%)
- Legal documents "solved" (>98%)

**Use for**:
- Domain variance angle
- "Choose parser by document type" narrative
- Technical deep-dive content

### 3. TEDS Comparison (`teds_comparison.png`)

**Purpose**: Table extraction capability

**Key Insights**:
- Shows parsers with table support
- Color-coded by performance tier
- TEDS metric explanation included

**Use for**:
- Table-specific content
- Technical audience
- Parser selection guide

### 4. Metric Correlation (`metric_correlation.png`)

**Purpose**: Show relationships between metrics

**Key Insights**:
- Edit Similarity vs Tree Similarity: **0.17 correlation**
- Text quality ≠ structure quality
- Validates need for multiple metrics

**Use for**:
- Methodology explanation
- "Why we use 8 metrics" justification
- Technical/academic audience

## Content Marketing Applications

### Blog Post: "We Benchmarked 20 PDF Parsers"
- Hero: parser_ranking.png
- Body: domain_heatmap.png
- Callout: metric_correlation.png

### Landing Page: PDF-Bench Project
- Above fold: parser_ranking.png (interactive version)
- Features section: All 4 charts as thumbnails
- Download CTA: Link to full report with SVG versions

### Social Media
- LinkedIn: domain_heatmap.png + caption about domain variance
- Twitter: parser_ranking.png + "No clear winner" narrative
- Technical forums: metric_correlation.png + methodology discussion

### White Paper / Long-Form
- Use all SVG versions for print quality
- Combine with real-world use case (insurance contracts)
- Add synthetic dataset examples

## Technical Specs

- **Format**: PNG (web) + SVG (print/scalable)
- **Resolution**: 150 DPI (PNG)
- **Size**: 10-14 inches width
- **Style**: seaborn whitegrid theme
- **Colors**: husl palette (color-blind friendly)

## Regeneration

To update visualizations with new benchmark data:

```bash
uv run python scripts/generate_visualizations.py
```

Input: `results/full_corpus_353docs.json`
Output: `docs/charts/*.png` and `*.svg`

## Future Enhancements

Potential additions:
1. **Coverage matrix**: Parser × Corpus heatmap (which parsers tested on which datasets)
2. **Box plots**: Score distribution per parser (show variance)
3. **Domain gap visualization**: Highlight 91-point docling-fast variance
4. **Success rate chart**: Parser reliability over time
5. **Cost vs accuracy**: Commercial vs open-source tradeoff

---

*For questions about visualizations, see `scripts/generate_visualizations.py` source code.*
