Tables in PDF Parsing
Tables in PDF Parsing
Tables are one of the most challenging structures for PDF parsers to extract
correctly. This document tests table handling.
Simple Table
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
Alignment Examples
Table with different column alignments:
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
Numeric Data
Performance metrics for baseline parser:
1

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
Multi-Line Cells
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
Dataset Statistics
Corpus composition:
Category
Source
Count
Avg Pages
License
Synthetic
Pandoc/LibreOffice
50
3.2
MIT
Business
GOV.UK
30
12.5
OGL v3.0
Financial
SEC EDGAR
20
45.3
Public Domain
Academic
arXiv
50
8.7
CC-BY 4.0
Total
Multiple
150
15.6
Various
Empty Cells
Testing sparse data:
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
2

Conclusion
This document tests table extraction including:
• Simple GFM tables
• Column alignment
• Numeric data formatting
• Multi-line cell content
• Empty cells
• Various cell content (text, numbers)
3