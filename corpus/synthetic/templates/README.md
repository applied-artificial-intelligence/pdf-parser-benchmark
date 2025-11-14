# DOCX Templates for Synthetic Corpus

This directory contains DOCX templates used for generating synthetic test documents via the DOCX→PDF pipeline.

## Templates Overview

### 1. `01_simple_report.docx` - Simple Report Template

**Purpose**: Standard business report structure with headings, paragraphs, and lists.

**Structure**:
- Title page with metadata
- Executive Summary
- Introduction
- Main sections (Background, Methodology, Findings, Results)
- Conclusion and Recommendations
- References

**Jinja2 Variables**:
- `title` - Report title
- `author` - Author name
- `date` - Report date
- `report_id` - Unique report identifier
- `executive_summary` - Summary text
- `introduction` - Introduction text
- `background` - Background text
- `methodology` - Methodology description
- `findings` - Findings text
- `observations` - List of observations
- `results` - Results text
- `conclusion` - Conclusion text
- `recommendations` - List of recommendations
- `references` - References text

**Features**:
- Hierarchical headings (H1, H2, H3)
- Bulleted lists
- Numbered lists
- Structured document flow

---

### 2. `02_table_heavy.docx` - Table-Heavy Template

**Purpose**: Document with diverse table structures for testing table extraction.

**Structure**:
- Title and metadata
- **TABLE-01**: Basic 3×4 data table (simple metrics)
- **TABLE-02**: Financial summary (Q1-Q4 quarterly data)
- **TABLE-03**: Regional performance (5 regions)
- **TABLE-04**: Wide table (7 columns, product metrics)
- **TABLE-05**: Team assignments (nested information)
- Summary section

**Jinja2 Variables** (partial list):
- `title`, `author`, `date`
- `introduction`, `regional_intro`, `summary`
- **TABLE-01**: `metric_N_name`, `metric_N_value`, `metric_N_unit` (N=1,2,3)
- **TABLE-02**: `qN_revenue`, `qN_expenses`, `qN_net_income`, `qN_margin` (N=1,2,3,4)
- **TABLE-03**: `{region}_sales`, `{region}_growth`, `{region}_share` for each region
- **TABLE-04**: `product_N_{field}` where field = name, units, price, revenue, cost, profit, roi
- **TABLE-05**: `team_N_name`, `team_N_lead`, `team_N_focus` (N=1,2,3)

**Features**:
- 5 different table styles
- Simple GFM-compatible tables
- Financial tables with numeric alignment
- Wide tables (7+ columns)
- Nested content in cells
- Different table styling (Grid, List)

**Diagnostic Labels**: Each table labeled TABLE-01 through TABLE-05 for precise failure identification.

---

### 3. `03_multicolumn.docx` - Multi-Column Layout Template

**Purpose**: Complex layout with simulated multi-column sections and mixed content.

**Structure**:
- Title and abstract (full width)
- Keywords
- Two-column main content section (simulated with borderless table)
- Comparative analysis table
- Three-column key points section
- Conclusion and future work

**Jinja2 Variables**:
- `title`, `subtitle`, `author`, `date`
- `abstract`, `keywords`, `intro_paragraph`
- `section_N_title`, `section_N_content` (N=1,2,3,4)
- `approach_a_{aspect}`, `approach_b_{aspect}` (aspect = performance, cost, scalability)
- `key_point_N` (N=1,2,3)
- `conclusion`
- `future_work` - List of future work items

**Features**:
- Multi-column layout (2-column and 3-column sections)
- Borderless tables for layout
- Comparison tables
- Mixed full-width and columnar sections
- Lists within template syntax

**Note**: True multi-column sections in DOCX require section breaks. This template uses borderless tables to simulate columns for better python-docx compatibility.

---

## Usage with python-docx-template

These templates are designed to work with `python-docx-template` (docxtpl). Example usage:

```python
from docxtpl import DocxTemplate
from pathlib import Path

# Load template
template = DocxTemplate("corpus/synthetic/templates/01_simple_report.docx")

# Define context with Jinja2 variables
context = {
    'title': 'Annual Performance Report',
    'author': 'John Doe',
    'date': '2025-11-14',
    'report_id': 'RPT-2025-001',
    'executive_summary': 'This report summarizes...',
    'observations': [
        'Key observation 1',
        'Key observation 2',
        'Key observation 3'
    ],
    'recommendations': [
        'First recommendation',
        'Second recommendation'
    ],
    # ... other variables
}

# Render template
template.render(context)

# Save generated document
template.save("output/report.docx")
```

## Pipeline Integration

These templates are used in the DOCX→PDF synthetic corpus generation pipeline:

1. **Template Loading**: Load .docx template
2. **Variable Substitution**: Render with test data via python-docx-template
3. **DOCX Generation**: Save rendered .docx file
4. **PDF Conversion**: Convert to PDF using LibreOffice headless
5. **Ground Truth**: Extract GT from DOCX structure
6. **Validation**: Verify PDF parseability

## Design Decisions

### Why DOCX Templates?

1. **Alternative Generation Path**: Complements Pandoc-based generation
2. **Realistic Documents**: Office-generated PDFs are common in business contexts
3. **Table Testing**: Different table rendering from Pandoc
4. **Comparison Baseline**: Provides diversity in synthetic corpus

### Template Complexity

Each template targets different complexity levels:
- **Simple**: Basic structure, minimal tables
- **Table-Heavy**: 5 diverse tables, primary focus on tabular data
- **Multi-Column**: Complex layouts, mixed content types

### Jinja2 Compatibility

Templates use python-docx-template Jinja2 syntax:
- Variable substitution: `{{ variable }}`
- Loops: `{% for item in list %}...{% endfor %}`
- Conditionals: `{% if condition %}...{% endif %}`

## File Structure

```
corpus/synthetic/templates/
├── README.md                    # This file
├── 01_simple_report.docx        # Simple report template
├── 02_table_heavy.docx          # Table-heavy template
└── 03_multicolumn.docx          # Multi-column template
```

## Generated Documents

When rendered and converted (TASK-016), these templates will produce:

```
corpus/synthetic/
├── 06_docx_simple_report.docx   # Rendered DOCX
├── 06_docx_simple_report.pdf    # Converted PDF
├── 06_docx_simple_report.yaml   # Metadata
├── 07_docx_table_heavy.docx
├── 07_docx_table_heavy.pdf
├── 07_docx_table_heavy.yaml
├── 08_docx_multicolumn.docx
├── 08_docx_multicolumn.pdf
└── 08_docx_multicolumn.yaml
```

## Next Steps

1. **TASK-015**: Implement DOCX→PDF pipeline
   - python-docx-template integration
   - LibreOffice headless conversion
   - Ground truth extraction

2. **TASK-016**: Generate synthetic DOCX documents
   - Create test data for each template
   - Render templates
   - Convert to PDF
   - Create metadata

3. **TASK-017**: Validate corpus integrity
   - Check all files exist
   - Verify hashes
   - Validate YAML schema

---

**Created**: 2025-11-14 (TASK-014)
**Templates**: 3
**Total Size**: ~111 KB
**Format**: DOCX (Office Open XML)
