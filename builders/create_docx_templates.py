"""Create DOCX templates for synthetic corpus generation.

This script creates three DOCX templates using python-docx:
1. Simple report template
2. Table-heavy template
3. Multi-column layout template

These templates use Jinja2 syntax compatible with python-docx-template
for variable substitution.
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches


def create_simple_report_template(output_path: Path) -> None:
    """Create a simple report template with basic structure.

    Args:
        output_path: Path to save the template DOCX file
    """
    doc = Document()

    # Title
    title = doc.add_heading("{{ title }}", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata section
    doc.add_paragraph("Author: {{ author }}")
    doc.add_paragraph("Date: {{ date }}")
    doc.add_paragraph("Report ID: {{ report_id }}")

    # Executive Summary
    doc.add_heading("Executive Summary", level=1)
    doc.add_paragraph("{{ executive_summary }}")

    # Introduction
    doc.add_heading("Introduction", level=1)
    doc.add_paragraph("{{ introduction }}")

    # Main Content Sections
    doc.add_heading("Background", level=1)
    doc.add_paragraph("{{ background }}")

    doc.add_heading("Methodology", level=1)
    doc.add_paragraph("{{ methodology }}")

    doc.add_heading("Findings", level=2)
    doc.add_paragraph("{{ findings }}")

    doc.add_heading("Key Observations", level=3)
    para = doc.add_paragraph()
    para.add_run("{% for observation in observations %}\n")
    para.add_run("• {{ observation }}\n")
    para.add_run("{% endfor %}")

    # Results
    doc.add_heading("Results", level=1)
    doc.add_paragraph("{{ results }}")

    # Conclusion
    doc.add_heading("Conclusion", level=1)
    doc.add_paragraph("{{ conclusion }}")

    # Recommendations
    doc.add_heading("Recommendations", level=1)
    para = doc.add_paragraph()
    para.add_run("{% for rec in recommendations %}\n")
    para.add_run("{{ loop.index }}. {{ rec }}\n")
    para.add_run("{% endfor %}")

    # References
    doc.add_heading("References", level=1)
    doc.add_paragraph("{{ references }}")

    # Save
    doc.save(str(output_path))
    print(f"Created simple report template: {output_path}")


def create_table_heavy_template(output_path: Path) -> None:
    """Create a table-heavy document template.

    Args:
        output_path: Path to save the template DOCX file
    """
    doc = Document()

    # Title
    title = doc.add_heading("{{ title }}", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata
    doc.add_paragraph("Prepared by: {{ author }}")
    doc.add_paragraph("Date: {{ date }}")

    # Introduction
    doc.add_heading("Data Summary", level=1)
    doc.add_paragraph("{{ introduction }}")

    # Table 1: Simple 3x4 table
    doc.add_heading("TABLE-01: Basic Data Table", level=2)
    table1 = doc.add_table(rows=4, cols=3)
    table1.style = 'Light Grid Accent 1'
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr_cells = table1.rows[0].cells
    hdr_cells[0].text = "Metric"
    hdr_cells[1].text = "Value"
    hdr_cells[2].text = "Unit"

    # Data rows with Jinja2 placeholders
    table1.rows[1].cells[0].text = "{{ metric_1_name }}"
    table1.rows[1].cells[1].text = "{{ metric_1_value }}"
    table1.rows[1].cells[2].text = "{{ metric_1_unit }}"

    table1.rows[2].cells[0].text = "{{ metric_2_name }}"
    table1.rows[2].cells[1].text = "{{ metric_2_value }}"
    table1.rows[2].cells[2].text = "{{ metric_2_unit }}"

    table1.rows[3].cells[0].text = "{{ metric_3_name }}"
    table1.rows[3].cells[1].text = "{{ metric_3_value }}"
    table1.rows[3].cells[2].text = "{{ metric_3_unit }}"

    doc.add_paragraph()  # Spacing

    # Table 2: Financial table with alignment
    doc.add_heading("TABLE-02: Financial Summary (Q1-Q4)", level=2)
    table2 = doc.add_table(rows=5, cols=5)
    table2.style = 'Medium Grid 1 Accent 1'

    # Header
    hdr = table2.rows[0].cells
    hdr[0].text = "Quarter"
    hdr[1].text = "Revenue"
    hdr[2].text = "Expenses"
    hdr[3].text = "Net Income"
    hdr[4].text = "Margin %"

    # Quarters data
    for i, quarter in enumerate(['Q1', 'Q2', 'Q3', 'Q4'], start=1):
        cells = table2.rows[i].cells
        cells[0].text = quarter
        cells[1].text = f"{{{{ q{i}_revenue }}}}"
        cells[2].text = f"{{{{ q{i}_expenses }}}}"
        cells[3].text = f"{{{{ q{i}_net_income }}}}"
        cells[4].text = f"{{{{ q{i}_margin }}}}"

    doc.add_paragraph()

    # Table 3: Comparison table with merged cells concept
    doc.add_heading("TABLE-03: Regional Performance", level=2)
    doc.add_paragraph("{{ regional_intro }}")

    table3 = doc.add_table(rows=6, cols=4)
    table3.style = 'Light List Accent 1'

    # Header
    hdr = table3.rows[0].cells
    hdr[0].text = "Region"
    hdr[1].text = "Sales"
    hdr[2].text = "Growth"
    hdr[3].text = "Market Share"

    # Regions
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Africa']
    for i, region in enumerate(regions, start=1):
        cells = table3.rows[i].cells
        cells[0].text = region
        cells[1].text = f"{{{{ {region.lower().replace(' ', '_')}_sales }}}}"
        cells[2].text = f"{{{{ {region.lower().replace(' ', '_')}_growth }}}}"
        cells[3].text = f"{{{{ {region.lower().replace(' ', '_')}_share }}}}"

    doc.add_paragraph()

    # Table 4: Wide table (7 columns)
    doc.add_heading("TABLE-04: Product Metrics (Wide Table)", level=2)
    table4 = doc.add_table(rows=4, cols=7)
    table4.style = 'Medium Grid 1 Accent 1'

    # Header
    headers = ["Product", "Units Sold", "Price", "Revenue", "Cost", "Profit", "ROI %"]
    for i, header in enumerate(headers):
        table4.rows[0].cells[i].text = header

    # Product rows
    for row_idx in range(1, 4):
        table4.rows[row_idx].cells[0].text = f"{{{{ product_{row_idx}_name }}}}"
        table4.rows[row_idx].cells[1].text = f"{{{{ product_{row_idx}_units }}}}"
        table4.rows[row_idx].cells[2].text = f"{{{{ product_{row_idx}_price }}}}"
        table4.rows[row_idx].cells[3].text = f"{{{{ product_{row_idx}_revenue }}}}"
        table4.rows[row_idx].cells[4].text = f"{{{{ product_{row_idx}_cost }}}}"
        table4.rows[row_idx].cells[5].text = f"{{{{ product_{row_idx}_profit }}}}"
        table4.rows[row_idx].cells[6].text = f"{{{{ product_{row_idx}_roi }}}}"

    doc.add_paragraph()

    # Table 5: Nested information (using lists within table cells)
    doc.add_heading("TABLE-05: Team Assignments", level=2)
    table5 = doc.add_table(rows=4, cols=3)
    table5.style = 'Light Grid Accent 1'

    # Header
    hdr = table5.rows[0].cells
    hdr[0].text = "Team"
    hdr[1].text = "Lead"
    hdr[2].text = "Focus Areas"

    for i in range(1, 4):
        table5.rows[i].cells[0].text = f"{{{{ team_{i}_name }}}}"
        table5.rows[i].cells[1].text = f"{{{{ team_{i}_lead }}}}"
        table5.rows[i].cells[2].text = f"{{{{ team_{i}_focus }}}}"

    # Conclusion
    doc.add_heading("Summary", level=1)
    doc.add_paragraph("{{ summary }}")

    # Save
    doc.save(str(output_path))
    print(f"Created table-heavy template: {output_path}")


def create_multicolumn_template(output_path: Path) -> None:
    """Create a multi-column layout template.

    Note: python-docx has limited support for columns. We'll create
    a layout that simulates columns using tables and sections.

    Args:
        output_path: Path to save the template DOCX file
    """
    doc = Document()

    # Title (full width)
    title = doc.add_heading("{{ title }}", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Subtitle
    subtitle = doc.add_heading("{{ subtitle }}", level=2)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Author and date (centered)
    meta = doc.add_paragraph("{{ author }} | {{ date }}")
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Abstract (full width)
    doc.add_heading("Abstract", level=1)
    doc.add_paragraph("{{ abstract }}")

    # Keywords
    doc.add_paragraph()
    keywords_para = doc.add_paragraph()
    keywords_para.add_run("Keywords: ").bold = True
    keywords_para.add_run("{{ keywords }}")

    # Two-column section using table
    doc.add_heading("Main Content", level=1)
    doc.add_paragraph("{{ intro_paragraph }}")

    # Create 2-column layout using a borderless table
    col_table = doc.add_table(rows=1, cols=2)
    col_table.autofit = False
    col_table.allow_autofit = False

    # Set column widths (approximate 2-column layout)
    for cell in col_table.rows[0].cells:
        cell.width = Inches(3.0)

    # Left column content
    left_cell = col_table.rows[0].cells[0]
    left_para = left_cell.add_paragraph()
    left_para.add_run("Section 1: {{ section_1_title }}").bold = True
    left_cell.add_paragraph("{{ section_1_content }}")

    left_cell.add_paragraph()
    left_para2 = left_cell.add_paragraph()
    left_para2.add_run("Section 2: {{ section_2_title }}").bold = True
    left_cell.add_paragraph("{{ section_2_content }}")

    # Right column content
    right_cell = col_table.rows[0].cells[1]
    right_para = right_cell.add_paragraph()
    right_para.add_run("Section 3: {{ section_3_title }}").bold = True
    right_cell.add_paragraph("{{ section_3_content }}")

    right_cell.add_paragraph()
    right_para2 = right_cell.add_paragraph()
    right_para2.add_run("Section 4: {{ section_4_title }}").bold = True
    right_cell.add_paragraph("{{ section_4_content }}")

    # Remove table borders for cleaner look
    for row in col_table.rows:
        for cell in row.cells:
            cell_element = cell._element
            tc_pr = cell_element.get_or_add_tcPr()
            tc_borders = tc_pr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcBorders')
            if tc_borders is None:
                from docx.oxml import OxmlElement
                tc_borders = OxmlElement('w:tcBorders')
                tc_pr.append(tc_borders)

            # Set all borders to none
            for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
                border = tc_borders.find(f'.//{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{border_name}')
                if border is None:
                    from docx.oxml import OxmlElement
                    border = OxmlElement(f'w:{border_name}')
                    tc_borders.append(border)
                border.set(
                    '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val',
                    'none'
                )

    # Back to full width
    doc.add_heading("Comparative Analysis", level=1)

    # Comparison table
    comp_table = doc.add_table(rows=4, cols=3)
    comp_table.style = 'Light Grid Accent 1'

    # Header
    hdr = comp_table.rows[0].cells
    hdr[0].text = "Aspect"
    hdr[1].text = "Approach A"
    hdr[2].text = "Approach B"

    # Comparison rows
    aspects = ["Performance", "Cost", "Scalability"]
    for i, aspect in enumerate(aspects, start=1):
        cells = comp_table.rows[i].cells
        cells[0].text = aspect
        cells[1].text = f"{{{{ approach_a_{aspect.lower()} }}}}"
        cells[2].text = f"{{{{ approach_b_{aspect.lower()} }}}}"

    doc.add_paragraph()

    # Three-column layout for key points using table
    doc.add_heading("Key Points", level=1)

    key_table = doc.add_table(rows=1, cols=3)
    key_table.autofit = False

    for i, cell in enumerate(key_table.rows[0].cells, start=1):
        cell.width = Inches(2.0)
        cell_para = cell.add_paragraph()
        cell_para.add_run(f"Point {i}").bold = True
        cell.add_paragraph(f"{{{{ key_point_{i} }}}}")

    # Remove borders
    for row in key_table.rows:
        for cell in row.cells:
            cell_element = cell._element
            tc_pr = cell_element.get_or_add_tcPr()
            tc_borders = tc_pr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcBorders')
            if tc_borders is None:
                from docx.oxml import OxmlElement
                tc_borders = OxmlElement('w:tcBorders')
                tc_pr.append(tc_borders)

            for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
                border = tc_borders.find(f'.//{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}{border_name}')
                if border is None:
                    from docx.oxml import OxmlElement
                    border = OxmlElement(f'w:{border_name}')
                    tc_borders.append(border)
                border.set(
                    '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val',
                    'none'
                )

    # Conclusion (full width)
    doc.add_heading("Conclusion", level=1)
    doc.add_paragraph("{{ conclusion }}")

    # Future Work
    doc.add_heading("Future Work", level=1)
    future_para = doc.add_paragraph()
    future_para.add_run("{% for item in future_work %}\n")
    future_para.add_run("• {{ item }}\n")
    future_para.add_run("{% endfor %}")

    # Save
    doc.save(str(output_path))
    print(f"Created multi-column template: {output_path}")


def main() -> None:
    """Create all three DOCX templates."""
    templates_dir = Path("corpus/synthetic/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    print("Creating DOCX templates for synthetic corpus...")
    print()

    # Create templates
    create_simple_report_template(templates_dir / "01_simple_report.docx")
    create_table_heavy_template(templates_dir / "02_table_heavy.docx")
    create_multicolumn_template(templates_dir / "03_multicolumn.docx")

    print()
    print("✓ All templates created successfully!")
    print(f"  Location: {templates_dir.absolute()}")
    print()
    print("Templates:")
    print("  1. 01_simple_report.docx - Standard business report structure")
    print("  2. 02_table_heavy.docx   - Document with 5 diverse tables")
    print("  3. 03_multicolumn.docx   - Multi-column layout with tables")
    print()
    print("Next step: Implement DOCX→PDF pipeline (TASK-015)")


if __name__ == "__main__":
    main()
