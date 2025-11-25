#!/usr/bin/env python3
"""Improved text-to-markdown converter for legal contracts.

This module provides enhanced structure detection for converting plain text
legal contracts (from CUAD and similar sources) to properly structured markdown.

Key Improvements over original:
1. Multi-level heading hierarchy (ARTICLE → H1, Section → H2, Subsection → H3)
2. List item detection for (a), (b), (i), (ii), 1.1, 2.3 patterns
3. Legal document section keywords (RECITALS, WHEREAS, NOW THEREFORE)
4. Page marker removal (Source: ... lines)
5. Better paragraph detection and spacing

Ground Truth Quality Impact:
- Element F1 metric measures markdown structure (headings, lists, paragraphs)
- Poor ground truth biases metrics toward parsers that match the ground truth's
  structure, not necessarily the ACTUAL document structure
- This improved converter produces ground truth that better reflects real
  legal contract structure, enabling more meaningful parser comparisons
"""

import re
from pathlib import Path


def txt_to_markdown_v2(txt_path: Path) -> str:
    """Convert plain text legal contract to structured markdown.

    This enhanced converter recognizes:
    - ARTICLE/Section/Subsection hierarchy
    - Numbered sections (1., 2., 1.1, 1.2)
    - Lettered subsections ((a), (b), (i), (ii))
    - Legal preamble sections (RECITALS, WHEREAS, NOW THEREFORE)
    - Definition sections
    - Page markers to remove

    Args:
        txt_path: Path to text file

    Returns:
        Markdown string with proper structure
    """
    with open(txt_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Pre-process: normalize line endings and excessive whitespace
    content = content.replace("\r\n", "\n")
    content = re.sub(r"\n{4,}", "\n\n\n", content)  # Max 2 blank lines

    lines = content.split("\n")
    md_lines: list[str] = []

    # State tracking
    in_definitions = False
    prev_was_heading = False

    for i, line in enumerate(lines):
        original_line = line
        line = line.strip()

        # Skip empty lines but preserve paragraph breaks
        if not line:
            if not prev_was_heading:
                md_lines.append("")
            prev_was_heading = False
            continue

        # Skip page markers (Source: COMPANY, FILING, DATE)
        if _is_page_marker(line):
            continue

        # Skip page numbers (single digits or "Page X of Y")
        if _is_page_number(line):
            continue

        # Detect structure and convert
        converted, heading_level = _convert_line(line, in_definitions)

        # Track if we're in definitions section
        if "DEFINITIONS" in line.upper():
            in_definitions = True
        elif heading_level == 1 and in_definitions:
            in_definitions = False

        md_lines.append(converted)
        prev_was_heading = heading_level > 0

    # Post-process: clean up excessive blank lines
    result = "\n".join(md_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip() + "\n"


def _is_page_marker(line: str) -> bool:
    """Check if line is a page marker (Source: COMPANY, FILING, DATE)."""
    # Pattern: Source: COMPANY NAME, FILING TYPE, DATE
    if line.startswith("Source:"):
        return True
    # Pattern: CONFIDENTIAL at start of page
    if line == "CONFIDENTIAL":
        return True
    return False


def _is_page_number(line: str) -> bool:
    """Check if line is just a page number."""
    # Single digit or small number
    if re.match(r"^\d{1,3}$", line):
        return True
    # "Page X of Y"
    if re.match(r"^Page\s+\d+\s+(of\s+\d+)?$", line, re.IGNORECASE):
        return True
    return False


def _convert_line(line: str, in_definitions: bool) -> tuple[str, int]:
    """Convert a line to markdown, returning (converted_line, heading_level).

    heading_level: 0 = not a heading, 1-4 = H1-H4
    """
    # === LEVEL 1: Major document sections ===
    # ARTICLE I, ARTICLE 1, ARTICLE ONE
    if re.match(r"^ARTICLE\s+[IVXLC\d]+\.?\s*", line, re.IGNORECASE):
        # Keep the full line but make it H1
        return f"# {line}", 1

    # Major section headers (all caps, standalone)
    major_sections = [
        "RECITALS",
        "WHEREAS",
        "NOW, THEREFORE",
        "NOW THEREFORE",
        "WITNESSETH",
        "DEFINITIONS",
        "GRANT OF RIGHTS",
        "GRANT OF LICENSE",
        "TERM AND TERMINATION",
        "INDEMNIFICATION",
        "CONFIDENTIALITY",
        "REPRESENTATIONS AND WARRANTIES",
        "MISCELLANEOUS",
        "GENERAL PROVISIONS",
        "NOTICES",
        "GOVERNING LAW",
        "DISPUTE RESOLUTION",
        "SIGNATURES",
        "IN WITNESS WHEREOF",
        "EXHIBIT A",
        "EXHIBIT B",
        "SCHEDULE A",
        "SCHEDULE B",
    ]

    line_upper = line.upper().strip(".:;,")
    for section in major_sections:
        if line_upper == section or line_upper.startswith(section + " "):
            return f"# {line}", 1

    # === LEVEL 2: Numbered major sections ===
    # Pattern: "1. DEFINITIONS" or "2. GRANT OF RIGHTS"
    match = re.match(r"^(\d{1,2})\.\s+([A-Z][A-Z\s]+)$", line)
    if match:
        return f"## {line}", 2

    # Pattern: "SECTION 1" or "SECTION 1.1"
    match = re.match(r"^SECTION\s+[\d.]+\.?\s*", line, re.IGNORECASE)
    if match:
        return f"## {line}", 2

    # === LEVEL 3: Subsections ===
    # Pattern: "1.1" or "1.1." or "1.1 Term" at start of line
    match = re.match(r"^(\d{1,2})\.(\d{1,2})\.?\s+(.*)$", line)
    if match:
        # This is a subsection like "1.1 Definitions" or "2.3 Payment Terms"
        return f"### {line}", 3

    # === LEVEL 4: Sub-subsections ===
    # Pattern: "1.1.1" or deeper numbering
    match = re.match(r"^(\d{1,2})\.(\d{1,2})\.(\d{1,2})\.?\s+(.*)$", line)
    if match:
        return f"#### {line}", 4

    # === LIST ITEMS ===
    # Lettered items: (a), (b), (c)
    match = re.match(r"^\(([a-z])\)\s+(.*)$", line)
    if match:
        return f"- ({match.group(1)}) {match.group(2)}", 0

    # Roman numeral items: (i), (ii), (iii)
    match = re.match(r"^\(([ivxlc]+)\)\s+(.*)$", line, re.IGNORECASE)
    if match:
        return f"  - ({match.group(1)}) {match.group(2)}", 0  # Nested list

    # Numbered items within sections: (1), (2)
    match = re.match(r"^\((\d+)\)\s+(.*)$", line)
    if match:
        return f"- ({match.group(1)}) {match.group(2)}", 0

    # === DEFINITION ENTRIES (within definitions section) ===
    if in_definitions:
        # Pattern: "Term" means ... (quoted term followed by definition)
        match = re.match(r'^"([^"]+)"\s+(means|shall mean|refers to)', line, re.IGNORECASE)
        if match:
            return f"**{match.group(1)}**: {line}", 0

    # === ALL-CAPS LINES (potential headers) ===
    # Only if reasonably short and doesn't look like a definition
    if line.isupper() and 3 < len(line) < 80 and '"' not in line:
        return f"## {line.title()}", 2

    # === DEFAULT: Regular paragraph ===
    return line, 0


def regenerate_cuad_ground_truth(
    cuad_corpus_dir: Path,
    backup: bool = True,
) -> dict[str, int]:
    """Regenerate all CUAD ground truth files with improved structure.

    Args:
        cuad_corpus_dir: Path to corpus/business/cuad directory
        backup: Whether to backup original files first

    Returns:
        Statistics dictionary
    """
    gt_dir = cuad_corpus_dir / "ground_truth"
    if not gt_dir.exists():
        raise ValueError(f"Ground truth directory not found: {gt_dir}")

    # Find original text files (need CUAD source)
    # This function is meant for initial corpus build, not regeneration
    # For regeneration, we'd need the original .txt files

    stats = {"processed": 0, "backed_up": 0}

    # For now, just document that this would require original CUAD txt files
    print("Note: To regenerate ground truth, you need the original CUAD .txt files")
    print("Use build_cuad_corpus.py with the new txt_to_markdown_v2 function")

    return stats


def demo_conversion():
    """Demonstrate the improved conversion on sample text."""
    sample = '''Exhibit 10.1 EXCLUSIVE LICENSE AGREEMENT

THIS EXCLUSIVE LICENSE AGREEMENT (this "Agreement") is entered into as of June 12, 2019.

RECITALS

WHEREAS, Company is engaged in the business of developing pharmaceutical products;

WHEREAS, Licensor owns certain intellectual property rights;

NOW, THEREFORE, in consideration of the mutual agreements contained herein, the parties agree:

1. DEFINITIONS

1.1 "Affiliate" means any corporation that controls or is controlled by a Party.

1.2 "Agreement" means this license agreement.

1.3 "Confidential Information" shall have the meaning in Section 9.2.

2. GRANT OF LICENSE

2.1 License Grant. Licensor hereby grants to Company an exclusive license to:
(a) use the Licensed Technology in the Territory;
(b) manufacture products using the Licensed Technology;
(c) sell products in the Territory.

2.2 Sublicensing. Company may sublicense its rights under Section 2.1.

3. PAYMENTS

3.1 License Fee. Company shall pay Licensor:
(i) $1,000,000 upon execution;
(ii) $2,000,000 upon first commercial sale;
(iii) $5,000,000 upon reaching $50M in sales.

Source: COMPANY INC., 10-K, 12/15/2023

4. TERM AND TERMINATION

4.1 Term. This Agreement shall commence on the Effective Date.

4.2 Termination for Breach.
(a) Either party may terminate upon material breach.
(b) The breaching party shall have 30 days to cure.

CONFIDENTIAL

5. MISCELLANEOUS

5.1 Governing Law. This Agreement shall be governed by Delaware law.

IN WITNESS WHEREOF, the parties have executed this Agreement.
'''

    import tempfile
    from pathlib import Path

    # Write sample to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(sample)
        temp_path = Path(f.name)

    try:
        result = txt_to_markdown_v2(temp_path)
        print("=== ORIGINAL TEXT (first 500 chars) ===")
        print(sample[:500])
        print("\n" + "=" * 60 + "\n")
        print("=== CONVERTED MARKDOWN ===")
        print(result)
    finally:
        temp_path.unlink()


if __name__ == "__main__":
    demo_conversion()
