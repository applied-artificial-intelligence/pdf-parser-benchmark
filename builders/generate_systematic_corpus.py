"""Generate systematic corpus with 24 documents testing specific features.

This script creates 24 synthetic documents across 4 categories:
1. Tables (6 docs) - Simple → Complex table structures
2. Lists (6 docs) - Simple bullets → Deep nesting
3. Multi-column (6 docs) - Reading order challenges
4. Mixed (6 docs) - Real-world document complexity

Each category tests progressively harder challenges for parsers.
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def add_page_break(doc: Document) -> None:
    """Add a page break to the document."""
    doc.add_page_break()


def create_table_category() -> list[tuple[str, Document]]:
    """Create 6 documents testing table extraction progressively.

    Returns:
        List of (filename, Document) tuples
    """
    docs = []

    # TABLE-01: Simple 3x4 grid
    doc = Document()
    doc.add_heading("Table Test 01: Simple Grid", 0)
    doc.add_paragraph("This document contains a basic 3-column, 4-row table.")

    table = doc.add_table(rows=4, cols=3)
    table.style = 'Light Grid Accent 1'

    # Header row
    header_cells = table.rows[0].cells
    header_cells[0].text = "Product"
    header_cells[1].text = "Quantity"
    header_cells[2].text = "Price"

    # Data rows
    data = [
        ("Widget A", "100", "$1,250"),
        ("Widget B", "75", "$980"),
        ("Widget C", "150", "$2,100"),
    ]
    for i, (product, qty, price) in enumerate(data, 1):
        row = table.rows[i]
        row.cells[0].text = product
        row.cells[1].text = qty
        row.cells[2].text = price

    docs.append(("09_table_simple_grid", doc))

    # TABLE-02: Table with merged cells (colspan)
    doc = Document()
    doc.add_heading("Table Test 02: Merged Columns", 0)
    doc.add_paragraph("This document tests horizontal cell merging (colspan).")

    table = doc.add_table(rows=4, cols=3)
    table.style = 'Light Grid Accent 1'

    # Merge cells in header for "Sales Data"
    header_cells = table.rows[0].cells
    header_cells[0].text = "Region"
    header_cells[1].merge(header_cells[2])
    header_cells[1].text = "Sales Data"

    # Sub-headers
    row1_cells = table.rows[1].cells
    row1_cells[0].text = ""
    row1_cells[1].text = "Q1"
    row1_cells[2].text = "Q2"

    # Data
    data = [
        ("North America", "$1.2M", "$1.4M"),
        ("Europe", "$980K", "$1.1M"),
    ]
    for i, (region, q1, q2) in enumerate(data, 2):
        row = table.rows[i]
        row.cells[0].text = region
        row.cells[1].text = q1
        row.cells[2].text = q2

    docs.append(("10_table_colspan", doc))

    # TABLE-03: Wide table (7 columns)
    doc = Document()
    doc.add_heading("Table Test 03: Wide Table", 0)
    doc.add_paragraph("This document contains a wide table with 7 columns.")

    table = doc.add_table(rows=3, cols=7)
    table.style = 'Light Grid Accent 1'

    headers = ["Product", "Units", "Price", "Revenue", "Cost", "Profit", "ROI"]
    for i, header in enumerate(headers):
        table.rows[0].cells[i].text = header

    data = [
        ("Product A", "1,000", "$50", "$50,000", "$30,000", "$20,000", "67%"),
        ("Product B", "500", "$120", "$60,000", "$45,000", "$15,000", "33%"),
    ]
    for row_idx, row_data in enumerate(data, 1):
        for col_idx, value in enumerate(row_data):
            table.rows[row_idx].cells[col_idx].text = value

    docs.append(("11_table_wide", doc))

    # TABLE-04: Multiple tables in one document
    doc = Document()
    doc.add_heading("Table Test 04: Multiple Tables", 0)
    doc.add_paragraph("This document contains multiple tables separated by text.")

    # First table
    doc.add_heading("Quarterly Revenue", 2)
    table1 = doc.add_table(rows=3, cols=3)
    table1.style = 'Light Grid Accent 1'
    table1.rows[0].cells[0].text = "Quarter"
    table1.rows[0].cells[1].text = "Revenue"
    table1.rows[0].cells[2].text = "Growth"
    table1.rows[1].cells[0].text = "Q1"
    table1.rows[1].cells[1].text = "$2.5M"
    table1.rows[1].cells[2].text = "15%"
    table1.rows[2].cells[0].text = "Q2"
    table1.rows[2].cells[1].text = "$2.8M"
    table1.rows[2].cells[2].text = "12%"

    doc.add_paragraph("\n")
    doc.add_paragraph("Analysis shows consistent growth across both quarters.")
    doc.add_paragraph("\n")

    # Second table
    doc.add_heading("Regional Breakdown", 2)
    table2 = doc.add_table(rows=3, cols=2)
    table2.style = 'Light Grid Accent 1'
    table2.rows[0].cells[0].text = "Region"
    table2.rows[0].cells[1].text = "Contribution"
    table2.rows[1].cells[0].text = "Americas"
    table2.rows[1].cells[1].text = "60%"
    table2.rows[2].cells[0].text = "EMEA"
    table2.rows[2].cells[1].text = "40%"

    docs.append(("12_table_multiple", doc))

    # TABLE-05: Nested table structure
    doc = Document()
    doc.add_heading("Table Test 05: Complex Structure", 0)
    doc.add_paragraph("This document tests complex table with multi-level headers.")

    table = doc.add_table(rows=5, cols=4)
    table.style = 'Light Grid Accent 1'

    # Complex header structure
    table.rows[0].cells[0].merge(table.rows[1].cells[0])  # Merge "Region" vertically
    table.rows[0].cells[0].text = "Region"

    table.rows[0].cells[1].merge(table.rows[0].cells[3])  # Merge "Performance Metrics"
    table.rows[0].cells[1].text = "Performance Metrics"

    # Second level headers
    table.rows[1].cells[1].text = "Sales"
    table.rows[1].cells[2].text = "Profit"
    table.rows[1].cells[3].text = "Growth"

    # Data rows
    data = [
        ("North", "$1.2M", "$400K", "12%"),
        ("South", "$980K", "$310K", "8%"),
        ("East", "$1.5M", "$520K", "15%"),
    ]
    for row_idx, row_data in enumerate(data, 2):
        for col_idx, value in enumerate(row_data):
            table.rows[row_idx].cells[col_idx].text = value

    docs.append(("13_table_complex_headers", doc))

    # TABLE-06: Financial table with formatting
    doc = Document()
    doc.add_heading("Table Test 06: Financial Statement", 0)
    doc.add_paragraph("This document contains a formatted financial table with totals.")

    table = doc.add_table(rows=6, cols=3)
    table.style = 'Light Grid Accent 1'

    # Headers
    table.rows[0].cells[0].text = "Line Item"
    table.rows[0].cells[1].text = "2024"
    table.rows[0].cells[2].text = "2025"

    # Data
    items = [
        ("Revenue", "$5,000,000", "$5,750,000"),
        ("Cost of Goods Sold", "$(3,200,000)", "$(3,450,000)"),
        ("Gross Profit", "$1,800,000", "$2,300,000"),
        ("Operating Expenses", "$(1,200,000)", "$(1,400,000)"),
        ("Net Income", "$600,000", "$900,000"),
    ]
    for row_idx, (item, val2024, val2025) in enumerate(items, 1):
        table.rows[row_idx].cells[0].text = item
        table.rows[row_idx].cells[1].text = val2024
        table.rows[row_idx].cells[2].text = val2025

    docs.append(("14_table_financial", doc))

    return docs


def create_list_category() -> list[tuple[str, Document]]:
    """Create 6 documents testing list detection and nesting.

    Returns:
        List of (filename, Document) tuples
    """
    docs = []

    # LIST-01: Simple bullets
    doc = Document()
    doc.add_heading("List Test 01: Simple Bullets", 0)
    doc.add_paragraph("This document contains simple bulleted lists.")

    doc.add_heading("Project Goals", 1)
    goals = [
        "Improve customer satisfaction by 20%",
        "Reduce operational costs by 15%",
        "Launch three new products",
        "Expand to two new markets",
    ]
    for goal in goals:
        doc.add_paragraph(goal, style='List Bullet')

    docs.append(("15_list_simple_bullets", doc))

    # LIST-02: Simple numbered list
    doc = Document()
    doc.add_heading("List Test 02: Numbered Steps", 0)
    doc.add_paragraph("This document contains a numbered procedural list.")

    doc.add_heading("Setup Instructions", 1)
    steps = [
        "Download the installation package from the website",
        "Extract the archive to your preferred location",
        "Run the setup wizard and follow prompts",
        "Configure initial settings in the admin panel",
        "Verify installation by checking version number",
    ]
    for step in steps:
        doc.add_paragraph(step, style='List Number')

    docs.append(("16_list_numbered", doc))

    # LIST-03: Two-level nesting
    doc = Document()
    doc.add_heading("List Test 03: Two-Level Nesting", 0)
    doc.add_paragraph("This document contains two levels of list nesting.")

    doc.add_heading("Product Categories", 1)
    doc.add_paragraph("Electronics", style='List Bullet')
    doc.add_paragraph("Laptops", style='List Bullet 2')
    doc.add_paragraph("Desktop Computers", style='List Bullet 2')
    doc.add_paragraph("Tablets", style='List Bullet 2')

    doc.add_paragraph("Home Goods", style='List Bullet')
    doc.add_paragraph("Furniture", style='List Bullet 2')
    doc.add_paragraph("Kitchenware", style='List Bullet 2')
    doc.add_paragraph("Bedding", style='List Bullet 2')

    docs.append(("17_list_nested_2level", doc))

    # LIST-04: Three-level nesting
    doc = Document()
    doc.add_heading("List Test 04: Three-Level Nesting", 0)
    doc.add_paragraph("This document contains three levels of list nesting.")

    doc.add_heading("Organizational Structure", 1)
    doc.add_paragraph("Executive Team", style='List Bullet')
    doc.add_paragraph("CEO Office", style='List Bullet 2')
    doc.add_paragraph("Chief of Staff", style='List Bullet 3')
    doc.add_paragraph("Executive Assistant", style='List Bullet 3')
    doc.add_paragraph("CFO Office", style='List Bullet 2')
    doc.add_paragraph("Controller", style='List Bullet 3')
    doc.add_paragraph("Treasury Manager", style='List Bullet 3')

    doc.add_paragraph("Engineering", style='List Bullet')
    doc.add_paragraph("Backend Team", style='List Bullet 2')
    doc.add_paragraph("API Development", style='List Bullet 3')
    doc.add_paragraph("Database Engineering", style='List Bullet 3')
    doc.add_paragraph("Frontend Team", style='List Bullet 2')
    doc.add_paragraph("UI Development", style='List Bullet 3')
    doc.add_paragraph("UX Design", style='List Bullet 3')

    docs.append(("18_list_nested_3level", doc))

    # LIST-05: Mixed numbered and bullets
    doc = Document()
    doc.add_heading("List Test 05: Mixed List Types", 0)
    doc.add_paragraph("This document contains both numbered and bulleted lists.")

    doc.add_heading("Implementation Plan", 1)
    doc.add_paragraph("Phase 1: Requirements Gathering", style='List Number')
    doc.add_paragraph("Stakeholder interviews", style='List Bullet 2')
    doc.add_paragraph("Market research", style='List Bullet 2')
    doc.add_paragraph("Competitive analysis", style='List Bullet 2')

    doc.add_paragraph("Phase 2: Design", style='List Number')
    doc.add_paragraph("System architecture", style='List Bullet 2')
    doc.add_paragraph("UI/UX mockups", style='List Bullet 2')
    doc.add_paragraph("Database schema", style='List Bullet 2')

    doc.add_paragraph("Phase 3: Implementation", style='List Number')
    doc.add_paragraph("Backend development", style='List Bullet 2')
    doc.add_paragraph("Frontend development", style='List Bullet 2')
    doc.add_paragraph("Testing and QA", style='List Bullet 2')

    docs.append(("19_list_mixed_types", doc))

    # LIST-06: Lists with inline text
    doc = Document()
    doc.add_heading("List Test 06: Lists with Paragraphs", 0)
    doc.add_paragraph("This document mixes lists with regular paragraphs.")

    doc.add_heading("Key Findings", 1)
    doc.add_paragraph("Our research identified three critical areas for improvement:")

    doc.add_paragraph("Customer Experience", style='List Bullet')
    doc.add_paragraph("The current checkout process has a 35% abandonment rate. "
                     "Streamlining the flow could reduce this significantly.")

    doc.add_paragraph("System Performance", style='List Bullet')
    doc.add_paragraph("Database queries are the primary bottleneck. Implementing "
                     "caching would improve response times by an estimated 60%.")

    doc.add_paragraph("Mobile Optimization", style='List Bullet')
    doc.add_paragraph("Mobile traffic represents 70% of visitors but only 40% of "
                     "conversions. The interface needs responsive design improvements.")

    doc.add_paragraph("\n")
    doc.add_paragraph("These findings form the basis for our Q3 roadmap priorities.")

    docs.append(("20_list_with_paragraphs", doc))

    return docs


def create_multicolumn_category() -> list[tuple[str, Document]]:
    """Create 6 documents testing reading order with columns.

    Note: python-docx doesn't support true multi-column sections well,
    so we'll use tables with borderless cells to simulate columns.

    Returns:
        List of (filename, Document) tuples
    """
    docs = []

    # COLUMN-01: Two-column layout (simulated)
    doc = Document()
    doc.add_heading("Column Test 01: Two-Column Text", 0)
    doc.add_paragraph("This document simulates two-column layout for reading order testing.")

    # Use borderless table for two columns
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    table.allow_autofit = False

    # Remove borders
    for row in table.rows:
        for cell in row.cells:
            cell.width = Inches(3.0)
            # Remove cell borders (borderless table)
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'none')
                tcBorders.append(border)
            tcPr.append(tcBorders)

    # Left column
    left_cell = table.rows[0].cells[0]
    left_para1 = left_cell.add_paragraph("Column 1 - Paragraph 1")
    left_para2 = left_cell.add_paragraph("This is the first column of text. "
                                         "It should be read before the second column.")
    left_para3 = left_cell.add_paragraph("Column 1 - Paragraph 2")
    left_para4 = left_cell.add_paragraph("More content in the left column to test "
                                         "vertical reading flow.")

    # Right column
    right_cell = table.rows[0].cells[1]
    right_para1 = right_cell.add_paragraph("Column 2 - Paragraph 1")
    right_para2 = right_cell.add_paragraph("This is the second column. It should be "
                                          "read after all the left column content.")
    right_para3 = right_cell.add_paragraph("Column 2 - Paragraph 2")
    right_para4 = right_cell.add_paragraph("Additional content in the right column.")

    docs.append(("21_column_two_column", doc))

    # COLUMN-02: Three-column layout
    doc = Document()
    doc.add_heading("Column Test 02: Three-Column Layout", 0)

    table = doc.add_table(rows=1, cols=3)

    # Remove borders
    for row in table.rows:
        for cell in row.cells:
            cell.width = Inches(2.0)
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'none')
                tcBorders.append(border)
            tcPr.append(tcBorders)

    # Column 1
    table.rows[0].cells[0].add_paragraph("Column 1 Content")
    table.rows[0].cells[0].add_paragraph("First column text flows here.")

    # Column 2
    table.rows[0].cells[1].add_paragraph("Column 2 Content")
    table.rows[0].cells[1].add_paragraph("Middle column text.")

    # Column 3
    table.rows[0].cells[2].add_paragraph("Column 3 Content")
    table.rows[0].cells[2].add_paragraph("Last column text.")

    docs.append(("22_column_three_column", doc))

    # COLUMN-03: Mixed full-width and column sections
    doc = Document()
    doc.add_heading("Column Test 03: Mixed Width Sections", 0)

    doc.add_paragraph("This is full-width introductory text that spans the entire page.")
    doc.add_paragraph("It should be read first, before the columnar content below.")

    # Two-column section
    table = doc.add_table(rows=1, cols=2)
    for row in table.rows:
        for cell in row.cells:
            cell.width = Inches(3.0)
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'none')
                tcBorders.append(border)
            tcPr.append(tcBorders)

    table.rows[0].cells[0].add_paragraph("Left column section with multiple paragraphs "
                                         "to test reading order.")
    table.rows[0].cells[1].add_paragraph("Right column section that should be read "
                                         "after the left column.")

    doc.add_paragraph("\n")
    doc.add_paragraph("This is concluding full-width text. It should be read last, "
                     "after both columns.")

    docs.append(("23_column_mixed_width", doc))

    # COLUMN-04: Newsletter-style layout
    doc = Document()
    doc.add_heading("Newsletter: Company Updates", 0)
    doc.add_paragraph("Volume 5, Issue 12 - November 2025")

    # Create two-column "articles"
    doc.add_heading("Headlines", 1)

    table = doc.add_table(rows=1, cols=2)
    for row in table.rows:
        for cell in row.cells:
            cell.width = Inches(3.0)
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'none')
                tcBorders.append(border)
            tcPr.append(tcBorders)

    # Left article
    left = table.rows[0].cells[0]
    left.add_paragraph("Q4 Results Exceed Expectations").bold = True
    left.add_paragraph("Revenue growth of 25% demonstrates strong market position. "
                      "CEO comments on strategic initiatives driving results.")

    # Right article
    right = table.rows[0].cells[1]
    right.add_paragraph("New Product Launch Scheduled").bold = True
    right.add_paragraph("Innovation team announces upcoming release for Q1 2026. "
                       "Beta testing shows promising user engagement metrics.")

    docs.append(("24_column_newsletter", doc))

    # COLUMN-05: Academic paper style
    doc = Document()
    doc.add_heading("Research Paper: Multi-Column Format", 0)
    doc.add_paragraph("Abstract: This document tests academic paper layout with "
                     "abstract, columns, and references.")

    doc.add_heading("Abstract", 1)
    doc.add_paragraph("Full-width abstract section describing the research methodology "
                     "and key findings in a single column.")

    doc.add_heading("Introduction", 1)

    # Two-column body
    table = doc.add_table(rows=1, cols=2)
    for row in table.rows:
        for cell in row.cells:
            cell.width = Inches(3.0)
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'none')
                tcBorders.append(border)
            tcPr.append(tcBorders)

    table.rows[0].cells[0].add_paragraph("Introduction text in left column. "
                                         "Background and context provided here.")
    table.rows[0].cells[1].add_paragraph("Continuation in right column. "
                                         "Methodology and approach described.")

    doc.add_paragraph("\n")
    doc.add_heading("References", 1)
    doc.add_paragraph("[1] Smith, J. (2024). Sample Reference.")
    doc.add_paragraph("[2] Jones, M. (2025). Another Citation.")

    docs.append(("25_column_academic", doc))

    # COLUMN-06: Marketing brochure
    doc = Document()
    doc.add_heading("Product Brochure: Features Overview", 0)

    # Three-column feature grid
    table = doc.add_table(rows=1, cols=3)
    for row in table.rows:
        for cell in row.cells:
            cell.width = Inches(2.0)
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'none')
                tcBorders.append(border)
            tcPr.append(tcBorders)

    # Feature 1
    table.rows[0].cells[0].add_paragraph("Fast Performance").bold = True
    table.rows[0].cells[0].add_paragraph("Lightning-quick response times with "
                                         "optimized caching.")

    # Feature 2
    table.rows[0].cells[1].add_paragraph("Easy Integration").bold = True
    table.rows[0].cells[1].add_paragraph("RESTful API with comprehensive "
                                         "documentation.")

    # Feature 3
    table.rows[0].cells[2].add_paragraph("Secure by Default").bold = True
    table.rows[0].cells[2].add_paragraph("Enterprise-grade encryption and "
                                         "compliance.")

    docs.append(("26_column_brochure", doc))

    return docs


def create_mixed_category() -> list[tuple[str, Document]]:
    """Create 6 documents with mixed content (real-world complexity).

    Returns:
        List of (filename, Document) tuples
    """
    docs = []

    # MIXED-01: Report with tables and lists
    doc = Document()
    doc.add_heading("Quarterly Business Review", 0)
    doc.add_paragraph("Q3 2025 Performance Analysis")

    doc.add_heading("Executive Summary", 1)
    doc.add_paragraph("This quarter showed strong performance across key metrics:")
    doc.add_paragraph("Revenue increased 18% year-over-year", style='List Bullet')
    doc.add_paragraph("Customer acquisition cost decreased 12%", style='List Bullet')
    doc.add_paragraph("Net promoter score improved to 72", style='List Bullet')

    doc.add_heading("Financial Performance", 1)
    table = doc.add_table(rows=4, cols=3)
    table.style = 'Light Grid Accent 1'
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "Q2 2025"
    table.rows[0].cells[2].text = "Q3 2025"
    table.rows[1].cells[0].text = "Revenue"
    table.rows[1].cells[1].text = "$4.2M"
    table.rows[1].cells[2].text = "$4.95M"
    table.rows[2].cells[0].text = "Profit"
    table.rows[2].cells[1].text = "$1.1M"
    table.rows[2].cells[2].text = "$1.4M"
    table.rows[3].cells[0].text = "Margin"
    table.rows[3].cells[1].text = "26%"
    table.rows[3].cells[2].text = "28%"

    doc.add_heading("Next Steps", 1)
    doc.add_paragraph("Expand marketing spend by 20%", style='List Number')
    doc.add_paragraph("Launch product line extension", style='List Number')
    doc.add_paragraph("Hire 5 additional sales representatives", style='List Number')

    docs.append(("27_mixed_business_report", doc))

    # MIXED-02: Technical documentation
    doc = Document()
    doc.add_heading("API Integration Guide", 0)

    doc.add_heading("Authentication", 1)
    doc.add_paragraph("The API supports two authentication methods:")
    doc.add_paragraph("API Key - Include key in X-API-Key header", style='List Bullet')
    doc.add_paragraph("OAuth 2.0 - Use bearer token authentication", style='List Bullet')

    doc.add_heading("Endpoint Reference", 1)
    table = doc.add_table(rows=4, cols=3)
    table.style = 'Light Grid Accent 1'
    table.rows[0].cells[0].text = "Endpoint"
    table.rows[0].cells[1].text = "Method"
    table.rows[0].cells[2].text = "Description"
    table.rows[1].cells[0].text = "/api/users"
    table.rows[1].cells[1].text = "GET"
    table.rows[1].cells[2].text = "List all users"
    table.rows[2].cells[0].text = "/api/users/{id}"
    table.rows[2].cells[1].text = "GET"
    table.rows[2].cells[2].text = "Get user by ID"
    table.rows[3].cells[0].text = "/api/users"
    table.rows[3].cells[1].text = "POST"
    table.rows[3].cells[2].text = "Create new user"

    doc.add_heading("Rate Limits", 1)
    doc.add_paragraph("Standard Tier: 1,000 requests/hour", style='List Bullet')
    doc.add_paragraph("Premium Tier: 10,000 requests/hour", style='List Bullet')
    doc.add_paragraph("Enterprise: Custom limits", style='List Bullet')

    docs.append(("28_mixed_technical_docs", doc))

    # MIXED-03: Policy document
    doc = Document()
    doc.add_heading("Employee Handbook: Section 5", 0)

    doc.add_heading("5.1 Time Off Policy", 1)
    doc.add_paragraph("Employees are entitled to the following time off benefits:")

    doc.add_paragraph("Vacation Time", style='List Bullet')
    doc.add_paragraph("0-2 years: 15 days/year", style='List Bullet 2')
    doc.add_paragraph("3-5 years: 20 days/year", style='List Bullet 2')
    doc.add_paragraph("6+ years: 25 days/year", style='List Bullet 2')

    doc.add_paragraph("Sick Leave", style='List Bullet')
    doc.add_paragraph("Unlimited sick days", style='List Bullet 2')
    doc.add_paragraph("Doctor's note required after 3 consecutive days", style='List Bullet 2')

    doc.add_heading("5.2 Holiday Schedule", 1)
    table = doc.add_table(rows=6, cols=2)
    table.style = 'Light Grid Accent 1'
    table.rows[0].cells[0].text = "Holiday"
    table.rows[0].cells[1].text = "Date 2026"
    table.rows[1].cells[0].text = "New Year's Day"
    table.rows[1].cells[1].text = "January 1"
    table.rows[2].cells[0].text = "Independence Day"
    table.rows[2].cells[1].text = "July 4"
    table.rows[3].cells[0].text = "Thanksgiving"
    table.rows[3].cells[1].text = "November 26"
    table.rows[4].cells[0].text = "Christmas Eve"
    table.rows[4].cells[1].text = "December 24"
    table.rows[5].cells[0].text = "Christmas Day"
    table.rows[5].cells[1].text = "December 25"

    docs.append(("29_mixed_policy_doc", doc))

    # MIXED-04: Meeting minutes
    doc = Document()
    doc.add_heading("Product Team Meeting Minutes", 0)
    doc.add_paragraph("Date: November 14, 2025")
    doc.add_paragraph("Attendees: Sarah Chen (PM), Mike Rodriguez (Eng), Lisa Park (Design)")

    doc.add_heading("Agenda Items", 1)

    doc.add_heading("1. Sprint Review", 2)
    doc.add_paragraph("Completed 23 of 25 planned story points")
    doc.add_paragraph("Carried over items:", style='List Bullet')
    doc.add_paragraph("User profile redesign (5 points)", style='List Bullet 2')
    doc.add_paragraph("API performance optimization (3 points)", style='List Bullet 2')

    doc.add_heading("2. Q4 Roadmap", 2)
    table = doc.add_table(rows=4, cols=3)
    table.style = 'Light Grid Accent 1'
    table.rows[0].cells[0].text = "Feature"
    table.rows[0].cells[1].text = "Priority"
    table.rows[0].cells[2].text = "Target"
    table.rows[1].cells[0].text = "Mobile app launch"
    table.rows[1].cells[1].text = "High"
    table.rows[1].cells[2].text = "December"
    table.rows[2].cells[0].text = "Advanced search"
    table.rows[2].cells[1].text = "Medium"
    table.rows[2].cells[1].text = "January"
    table.rows[3].cells[0].text = "Export functionality"
    table.rows[3].cells[1].text = "Low"
    table.rows[3].cells[2].text = "February"

    doc.add_heading("Action Items", 1)
    doc.add_paragraph("Sarah: Create detailed mobile app spec", style='List Number')
    doc.add_paragraph("Mike: Investigate search optimization options", style='List Number')
    doc.add_paragraph("Lisa: Prepare design system updates", style='List Number')

    docs.append(("30_mixed_meeting_minutes", doc))

    # MIXED-05: Research summary
    doc = Document()
    doc.add_heading("Market Research Summary", 0)
    doc.add_paragraph("Consumer Behavior Study - November 2025")

    doc.add_heading("Methodology", 1)
    doc.add_paragraph("This study employed multiple research methods:")
    doc.add_paragraph("Online surveys (n=1,200)", style='List Bullet')
    doc.add_paragraph("Focus groups (8 sessions, 6-8 participants each)", style='List Bullet')
    doc.add_paragraph("In-depth interviews (15 subjects)", style='List Bullet')

    doc.add_heading("Key Findings", 1)
    doc.add_paragraph("Demographic Preferences")

    table = doc.add_table(rows=4, cols=4)
    table.style = 'Light Grid Accent 1'
    table.rows[0].cells[0].text = "Age Group"
    table.rows[0].cells[1].text = "Mobile"
    table.rows[0].cells[2].text = "Desktop"
    table.rows[0].cells[3].text = "Tablet"
    table.rows[1].cells[0].text = "18-34"
    table.rows[1].cells[1].text = "75%"
    table.rows[1].cells[2].text = "20%"
    table.rows[1].cells[3].text = "5%"
    table.rows[2].cells[0].text = "35-54"
    table.rows[2].cells[1].text = "45%"
    table.rows[2].cells[2].text = "40%"
    table.rows[2].cells[3].text = "15%"
    table.rows[3].cells[0].text = "55+"
    table.rows[3].cells[1].text = "25%"
    table.rows[3].cells[2].text = "60%"
    table.rows[3].cells[3].text = "15%"

    doc.add_heading("Recommendations", 1)
    doc.add_paragraph("Prioritize mobile-first design", style='List Number')
    doc.add_paragraph("Optimize checkout flow for speed", style='List Number')
    doc.add_paragraph("Implement personalization features", style='List Number')

    docs.append(("31_mixed_research_summary", doc))

    # MIXED-06: Comprehensive document with all elements
    doc = Document()
    doc.add_heading("Annual Report 2025", 0)
    doc.add_paragraph("Company Performance Review")

    doc.add_heading("Letter from the CEO", 1)
    doc.add_paragraph("Dear Shareholders, 2025 was a transformative year for our "
                     "organization. We achieved record revenue, expanded into new "
                     "markets, and launched innovative products that position us "
                     "for continued growth.")

    doc.add_heading("Financial Highlights", 1)
    table = doc.add_table(rows=5, cols=3)
    table.style = 'Light Grid Accent 1'
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "2024"
    table.rows[0].cells[2].text = "2025"
    table.rows[1].cells[0].text = "Revenue"
    table.rows[1].cells[1].text = "$18.5M"
    table.rows[1].cells[2].text = "$23.2M"
    table.rows[2].cells[0].text = "Net Income"
    table.rows[2].cells[1].text = "$2.8M"
    table.rows[2].cells[2].text = "$4.1M"
    table.rows[3].cells[0].text = "EBITDA"
    table.rows[3].cells[1].text = "$4.2M"
    table.rows[3].cells[2].text = "$6.3M"
    table.rows[4].cells[0].text = "EPS"
    table.rows[4].cells[1].text = "$1.45"
    table.rows[4].cells[2].text = "$2.12"

    doc.add_heading("Strategic Achievements", 1)
    doc.add_paragraph("Market Expansion", style='List Bullet')
    doc.add_paragraph("Entered Asia-Pacific region", style='List Bullet 2')
    doc.add_paragraph("Opened offices in Singapore and Tokyo", style='List Bullet 2')

    doc.add_paragraph("Product Innovation", style='List Bullet')
    doc.add_paragraph("Launched AI-powered analytics platform", style='List Bullet 2')
    doc.add_paragraph("Released mobile app (1M+ downloads)", style='List Bullet 2')

    doc.add_paragraph("Operational Excellence", style='List Bullet')
    doc.add_paragraph("Achieved ISO 27001 certification", style='List Bullet 2')
    doc.add_paragraph("Reduced carbon footprint by 30%", style='List Bullet 2')

    doc.add_heading("2026 Outlook", 1)
    doc.add_paragraph("We project 20-25% revenue growth driven by:")
    doc.add_paragraph("Continued geographic expansion", style='List Number')
    doc.add_paragraph("New product launches in Q2 and Q4", style='List Number')
    doc.add_paragraph("Strategic partnerships with industry leaders", style='List Number')
    doc.add_paragraph("Investment in R&D and innovation", style='List Number')

    docs.append(("32_mixed_comprehensive", doc))

    return docs


def main():
    """Generate all 24 systematic documents."""
    corpus_dir = Path("corpus/synthetic")
    corpus_dir.mkdir(parents=True, exist_ok=True)

    print("🏭 Systematic Corpus Generator")
    print("=" * 60)
    print("Generating 24 documents across 4 categories:")
    print("  - Tables: 6 documents")
    print("  - Lists: 6 documents")
    print("  - Multi-column: 6 documents")
    print("  - Mixed: 6 documents")
    print("=" * 60)
    print()

    all_docs = []
    all_docs.extend(create_table_category())
    all_docs.extend(create_list_category())
    all_docs.extend(create_multicolumn_category())
    all_docs.extend(create_mixed_category())

    print(f"📝 Saving {len(all_docs)} documents...")
    for filename, doc in all_docs:
        docx_path = corpus_dir / f"{filename}.docx"
        doc.save(str(docx_path))
        print(f"  ✓ {filename}.docx")

    print()
    print("=" * 60)
    print(f"✅ Generated {len(all_docs)} DOCX files")
    print(f"📁 Location: {corpus_dir}")
    print()
    print("Next steps:")
    print("1. Convert to PDF: uv run python builders/convert_synthetic_to_pdf.py")
    print("2. Extract ground truth: (creates .md files)")
    print("3. Run benchmark: python run_benchmark.py")


if __name__ == "__main__":
    main()
