"""Legal numbering system for authentic contract formatting.

Supports 5-level hierarchical numbering used in legal contracts:
- Level 1: 1, 2, 3, ... (Articles/Major Sections)
- Level 2: 1.1, 1.2, 2.1, ... (Subsections)
- Level 3: 1.1.1, 1.1.2, ... (Paragraphs)
- Level 4: (a), (b), (c), ... (Subparagraphs)
- Level 5: (i), (ii), (iii), ... (Clauses)

Example:
    1. Services
    1.1 Service Description
    1.1.1 The Service Provider shall provide the following services:
        (a) Design and implementation
        (b) Ongoing maintenance including:
            (i) Software updates
            (ii) Security patches
"""

from dataclasses import dataclass, field


def _int_to_lower_alpha(n: int) -> str:
    """Convert integer to lowercase letter (a, b, c, ..., z, aa, ab, ...)."""
    result = ""
    while n > 0:
        n -= 1
        result = chr(ord("a") + (n % 26)) + result
        n //= 26
    return result


def _int_to_roman(n: int) -> str:
    """Convert integer to lowercase Roman numerals (i, ii, iii, iv, v, ...)."""
    values = [
        (1000, "m"),
        (900, "cm"),
        (500, "d"),
        (400, "cd"),
        (100, "c"),
        (90, "xc"),
        (50, "l"),
        (40, "xl"),
        (10, "x"),
        (9, "ix"),
        (5, "v"),
        (4, "iv"),
        (1, "i"),
    ]
    result = ""
    for value, numeral in values:
        count = n // value
        if count:
            result += numeral * count
            n -= value * count
    return result


@dataclass
class NumberedItem:
    """A numbered item in a legal document."""

    level: int  # 1-5
    number_str: str  # e.g., "1.2.3" or "(a)" or "(ii)"
    title: str  # Section title/heading (empty for list items)
    content: str = ""  # Content text (if any)
    children: list["NumberedItem"] = field(default_factory=list)

    @property
    def full_reference(self) -> str:
        """Get full reference for cross-referencing (e.g., 'Section 1.2.3')."""
        if self.level <= 3:
            if self.title:
                return f"Section {self.number_str}"
            else:
                return f"Section {self.number_str}"
        elif self.level == 4:
            return f"Section {self.number_str}"
        else:  # level 5
            return f"clause {self.number_str}"

    def get_markdown_line(self, indent_level: int = 0) -> str:
        """Get formatted markdown line for this item.

        Args:
            indent_level: Base indentation level (for nested items)

        Returns:
            Formatted markdown string
        """
        # Calculate indentation based on level
        if self.level == 1:
            indent = ""
            prefix = f"**{self.number_str}. {self.title}**" if self.title else f"{self.number_str}."
        elif self.level == 2:
            indent = "  "
            prefix = f"**{self.number_str} {self.title}**" if self.title else f"{self.number_str}"
        elif self.level == 3:
            indent = "    "
            prefix = f"{self.number_str}" if not self.title else f"{self.number_str} {self.title}"
        elif self.level == 4:
            indent = "      "
            prefix = f"{self.number_str}"
        else:  # level 5
            indent = "        "
            prefix = f"{self.number_str}"

        # Combine prefix and content
        if self.content:
            line = f"{indent}{prefix} {self.content}"
        elif self.title and self.level > 2:
            line = f"{indent}{prefix}"
        elif self.title:
            line = f"{indent}{prefix}"
        else:
            line = f"{indent}{prefix}"

        return line


class LegalNumbering:
    """Manages hierarchical legal numbering system."""

    def __init__(self):
        self.items: list[NumberedItem] = []
        self.current_path: list[int] = [0, 0, 0, 0, 0]  # Counters for each level
        self.reference_map: dict[str, NumberedItem] = {}  # For cross-references

    def add_section(self, level: int, title: str = "", content: str = "") -> NumberedItem:
        """Add a numbered section at the specified level.

        Args:
            level: Numbering level (1-5)
            title: Section title/heading (typically for levels 1-3)
            content: Content text

        Returns:
            Created NumberedItem
        """
        if level < 1 or level > 5:
            raise ValueError(f"Level must be 1-5, got {level}")

        # Increment counter at this level
        self.current_path[level - 1] += 1

        # Reset all deeper levels
        for i in range(level, 5):
            self.current_path[i] = 0

        # Generate number string based on level
        number_str = self._format_number(level)

        # Create item
        item = NumberedItem(
            level=level,
            number_str=number_str,
            title=title,
            content=content,
        )

        # Store for cross-references
        self.reference_map[number_str] = item

        # Add to items list
        self.items.append(item)

        return item

    def _format_number(self, level: int) -> str:
        """Format number string based on level and current counters.

        Args:
            level: Numbering level (1-5)

        Returns:
            Formatted number string
        """
        if level == 1:
            return str(self.current_path[0])
        elif level == 2:
            return f"{self.current_path[0]}.{self.current_path[1]}"
        elif level == 3:
            return f"{self.current_path[0]}.{self.current_path[1]}.{self.current_path[2]}"
        elif level == 4:
            letter = _int_to_lower_alpha(self.current_path[3])
            return f"({letter})"
        else:  # level 5
            roman = _int_to_roman(self.current_path[4])
            return f"({roman})"

    def add_subsection(self, title: str = "", content: str = "") -> NumberedItem:
        """Add a subsection (level 2).

        Args:
            title: Subsection title
            content: Content text

        Returns:
            Created NumberedItem
        """
        return self.add_section(2, title, content)

    def add_paragraph(self, content: str = "") -> NumberedItem:
        """Add a paragraph (level 3).

        Args:
            content: Paragraph content

        Returns:
            Created NumberedItem
        """
        return self.add_section(3, content=content)

    def add_subparagraph(self, content: str) -> NumberedItem:
        """Add a subparagraph with letter numbering (level 4).

        Args:
            content: Subparagraph content

        Returns:
            Created NumberedItem
        """
        return self.add_section(4, content=content)

    def add_clause(self, content: str) -> NumberedItem:
        """Add a clause with Roman numeral numbering (level 5).

        Args:
            content: Clause content

        Returns:
            Created NumberedItem
        """
        return self.add_section(5, content=content)

    def get_reference(self, number_str: str) -> str:
        """Get formatted reference text for cross-referencing.

        Args:
            number_str: Number string to reference (e.g., "1.2.3")

        Returns:
            Formatted reference (e.g., "Section 1.2.3")
        """
        item = self.reference_map.get(number_str)
        if not item:
            return number_str  # Fallback if not found

        return item.full_reference

    def generate_toc(self, max_level: int = 2) -> list[str]:
        """Generate table of contents.

        Args:
            max_level: Maximum level to include in TOC (typically 1-2)

        Returns:
            List of TOC lines
        """
        toc_lines = ["**Table of Contents**\n"]

        for item in self.items:
            if item.level <= max_level and item.title:
                indent = "  " * (item.level - 1)
                if item.level == 1:
                    line = f"{indent}{item.number_str}. {item.title}"
                else:
                    line = f"{indent}{item.number_str} {item.title}"
                toc_lines.append(line)

        return toc_lines

    def to_markdown(self) -> str:
        """Convert all numbered items to markdown format.

        Returns:
            Markdown-formatted document with proper numbering
        """
        lines = []

        for item in self.items:
            lines.append(item.get_markdown_line())

        return "\n".join(lines)

    def reset(self):
        """Reset the numbering system to start fresh."""
        self.items = []
        self.current_path = [0, 0, 0, 0, 0]
        self.reference_map = {}

    def get_current_section(self) -> str:
        """Get the current section number (level 1).

        Returns:
            Current section number as string
        """
        return str(self.current_path[0])

    def get_current_subsection(self) -> str:
        """Get the current subsection number (level 1.2).

        Returns:
            Current subsection number as string
        """
        return f"{self.current_path[0]}.{self.current_path[1]}"

    def get_current_paragraph(self) -> str:
        """Get the current paragraph number (level 1.2.3).

        Returns:
            Current paragraph number as string
        """
        return f"{self.current_path[0]}.{self.current_path[1]}.{self.current_path[2]}"


class ContractNumbering(LegalNumbering):
    """Specialized numbering for legal contracts with common patterns."""

    def add_article(self, title: str) -> NumberedItem:
        """Add a top-level article with title.

        Args:
            title: Article title (e.g., "Definitions", "Services")

        Returns:
            Created NumberedItem
        """
        return self.add_section(1, title=title)

    def add_definition(self, term: str, definition: str) -> NumberedItem:
        """Add a definition in proper legal format.

        Args:
            term: Term being defined
            definition: Definition text

        Returns:
            Created NumberedItem
        """
        content = f'"{term}" means {definition}.'
        return self.add_paragraph(content)

    def add_obligation(self, party: str, obligation: str) -> NumberedItem:
        """Add an obligation clause.

        Args:
            party: Party with obligation
            obligation: Obligation description

        Returns:
            Created NumberedItem
        """
        content = f"{party} shall {obligation}."
        return self.add_paragraph(content)

    def add_list_items(self, intro: str, items: list[str], level: int = 4) -> list[NumberedItem]:
        """Add an introduction followed by a list of items.

        Args:
            intro: Introduction text
            items: List of item texts
            level: Level for list items (4 or 5)

        Returns:
            List of created NumberedItems
        """
        # Add intro as paragraph
        self.add_paragraph(intro)

        # Add items at specified level
        created_items = []
        for item_text in items:
            item = self.add_section(level, content=item_text)
            created_items.append(item)

        return created_items

    def add_recital(self, recital_text: str) -> tuple[str, str]:
        """Add a WHEREAS recital clause.

        Recitals are traditionally not numbered, but we track them for TOC.

        Args:
            recital_text: Recital content

        Returns:
            Tuple of (formatted recital, reference key)
        """
        # Recitals use WHEREAS format
        formatted = f"WHEREAS, {recital_text};"
        return formatted, "recital"


# Example usage
if __name__ == "__main__":
    # Create a sample contract structure
    numbering = ContractNumbering()

    # Article 1: Definitions
    numbering.add_article("Definitions")
    numbering.add_definition("Services", "the consulting services described in Exhibit A")
    numbering.add_definition("Fees", "the amounts payable as set forth in Section 3")

    # Article 2: Services
    numbering.add_article("Services")
    numbering.add_subsection("Scope of Services")
    numbering.add_paragraph("Consultant shall provide the Services in a professional manner.")

    numbering.add_subsection("Deliverables")
    numbering.add_list_items(
        "Consultant shall deliver the following:",
        [
            "Design documents within 30 days",
            "Prototype within 60 days",
            "Final product within 90 days",
        ],
    )

    # Article 3: Compensation
    numbering.add_article("Compensation")
    numbering.add_subsection("Fees")
    numbering.add_paragraph("Client shall pay Consultant the Fees as follows:")
    numbering.add_subparagraph("$10,000 upon execution of this Agreement")
    numbering.add_subparagraph("$20,000 upon delivery of prototype")
    numbering.add_subparagraph("$20,000 upon final delivery")

    # Generate markdown
    print(numbering.to_markdown())
    print("\n" + "=" * 60 + "\n")

    # Generate TOC
    toc = numbering.generate_toc(max_level=2)
    print("\n".join(toc))
