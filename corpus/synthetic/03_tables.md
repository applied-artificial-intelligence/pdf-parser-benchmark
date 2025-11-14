Tables in PDF Parsing - Comprehensive Test
Tables in PDF Parsing
Tables are one of the most challenging structures for PDF parsers to extract
correctly. This document provides comprehensive table testing with both GFM
and HTML formats, labeled for diagnostic purposes.
Simple GFM Tables
TABLE-01: Basic 4-Column Table
Comparison of PDF parsing systems:
System
Type
Strengths
Weaknesses
PyMuPDF
Open-
source
Fast, lightweight
Limited structure
detection
Marker
Open-
source
Good layout analysis
Requires GPU for best
results
Nougat
Open-
source
Excellent for
academic papers
Slow, domain-specific
AWS Textract
Commercial
High accuracy,
robust
Cost per page
Azure DI
Commercial
Form extraction
Complex API
TABLE-02: Column Alignment
Table with left, center, and right alignment:
Left Aligned
Center Aligned
Right Aligned
Text
Text
Text
More text
More text
More text
Even more
Even more
Even more
1

TABLE-03: Numeric Data with Right Alignment
Performance metrics for baseline parser:
Metric
Score
Threshold
Edit Distance Similarity
0.89
0.85
Character Error Rate
0.11
0.15
Precision
0.92
0.90
Recall
0.88
0.85
F1 Score
0.90
0.87
TABLE-04: Multi-Line Cell Content
Complex table with longer content:
Feature
Description
Status
Text Extraction
Extract plain text from PDF
documents with character-level
accuracy
Complete
Structure
Detection
Identify headings, paragraphs,
lists, and tables
In Progress
Math Parsing
Extract and preserve LaTeX
mathematical notation
Planned
Image Handling
Detect and describe embedded
images
Planned
TABLE-05: Empty Cells (Sparse Data)
Testing sparse data handling:
Parser
v1.0
v2.0
v3.0
PyMuPDF
0.85
0.87
0.89
Marker
0.91
0.93
Nougat
0.88
TABLE-06: Wide Table with Many Columns
Category
Source
Count
Avg Pages
License
Format
Year
Synthetic
Pandoc
50
3.2
MIT
PDF
2024
Business
GOV.UK
30
12.5
OGL
v3.0
PDF
2023
2

Category
Source
Count
Avg Pages
License
Format
Year
Financial
SEC
EDGAR
20
45.3
Public
Domain
PDF
2023
Academic
arXiv
50
8.7
CC-BY
4.0
PDF
2024
Total
Multiple
150
15.6
Various
PDF
2023-
24
HTML Tables with Merged Cells
TABLE-07: Colspan (Header Spanning Multiple Columns)
Parser
Performance Metrics
Name
Speed
Accuracy
Cost
PyMuPDF
Fast
0.85
Free
Marker
Medium
0.93
Free
AWS Textract
Fast
0.95
$$$
TABLE-08: Rowspan (Cells Spanning Multiple Rows)
Category
System
License
3

Open Source
PyMuPDF
AGPL
Marker
GPL
Nougat
MIT
Commercial
AWS Textract
Proprietary
Azure DI
Proprietary
TABLE-09: Complex Merged Cells (Colspan + Rowspan)
Document Type
Open Source
Commercial
PyMuPDF
Marker
Textract
Azure DI
Simple Text
0.89
0.91
0.93
0.92
Tables
0.65
0.82
0.91
0.89
4

Math
0.45
0.71
0.78
0.76
Average
0.66
0.81
0.87
0.86
TABLE-10: Financial Table (Realistic Business Use Case)
Quarterly Revenue Breakdown (in millions USD)
Region
2024
YoY Change
Q1
Q2
Q3
Q4
North America
45.2
48.7
52.1
58.3
+12.5%
Europe
32.8
34.1
35.9
38.2
5

+8.3%
Asia Pacific
28.5
31.2
34.8
39.1
+18.7%
Total
106.5
114.0
122.8
135.6
+13.2%
Nested Tables
TABLE-11: Table Within Table Cells
Parser Comparison
Performance Details
Open Source Options
Name
Score
PyMuPDF
0.85
Marker
0.91
Commercial Options
Name
Score
AWS Textract
0.95
Azure DI
6

0.93
Tables with Rich Content
TABLE-12: Table with Embedded Lists
Parser
Strengths
Weaknesses
PyMuPDF
Fast performance
Lightweight
Easy to install
Limited structure detection
No layout analysis
Marker
Excellent layout analysis
Preserves structure
Good table extraction
Requires GPU for speed
Larger dependencies
TABLE-13: Styled HTML Table
Metric
Description
Range
Best Value
Edit Distance
Character-level similarity
0.0 - 1.0
1.0
AST-TED
Structure preservation
7

0.0 - 1.0
1.0
TEDS
Table structure accuracy
0.0 - 1.0
1.0
LaTeX F1
Math equation extraction
0.0 - 1.0
1.0
Diagnostic Summary
This document provides comprehensive table testing with 13 distinct table
structures, each labeled for diagnostic purposes:
GFM Tables (TABLE-01 through TABLE-06)
• TABLE-01: Basic 4-column table
• TABLE-02: Column alignment testing (left, center, right)
• TABLE-03: Numeric data with right alignment
• TABLE-04: Multi-line cell content
• TABLE-05: Empty cells (sparse data)
• TABLE-06: Wide table (7 columns)
HTML Tables with Merged Cells (TABLE-07 through TABLE-10)
• TABLE-07: Colspan (header spanning columns)
• TABLE-08: Rowspan (cells spanning rows)
• TABLE-09: Complex merged cells (both colspan and rowspan)
• TABLE-10: Financial table with realistic business data
Advanced Structures (TABLE-11 through TABLE-13)
• TABLE-11: Nested tables (tables within cells)
• TABLE-12: Tables containing lists
• TABLE-13: CSS-styled HTML table
Diagnostic Features
When a parser fails on tables, the labeled structure allows identification of:
1. Which specific table failed (TABLE-01 through TABLE-13)
8

2. What feature caused the failure (GFM vs HTML, colspan/rowspan,
nesting, etc.)
3. Where in the document the failure occurred
4. Parser capability gaps (e.g., “Parser X fails on all rowspan tables”)
This enables targeted parser improvements and accurate capability reporting.
9