"""Markdown AST parser for structural analysis.

This module implements Markdown Abstract Syntax Tree (AST) parsing using mistune.
It provides structured access to document elements for metrics like tree-edit distance,
element F1 score, and structural similarity.

The parser extracts a hierarchical representation of Markdown documents, identifying
element types (headings, lists, tables, etc.) and their nesting relationships. This
enables structural comparison beyond simple character-level metrics.

Key Features:
- AST generation from Markdown text using mistune 3.x
- Support for GFM extensions (tables, strikethrough, task lists)
- Element type extraction and counting
- Hierarchical structure preservation
- Type-safe element representation

Example:
    >>> from pdf_bench.metrics.ast_parser import MarkdownASTParser
    >>> parser = MarkdownASTParser()
    >>> ast = parser.parse("# Hello\\n\\nParagraph text")
    >>> counts = parser.count_elements(ast)
    >>> counts
    {'heading': 1, 'paragraph': 1}
"""

from collections import Counter
from dataclasses import dataclass
from typing import Any, cast

import mistune


@dataclass
class Element:
    """Structured representation of a Markdown AST element.

    Attributes:
        type: Element type (heading, paragraph, list, table, etc.)
        level: Heading level (1-6) or list depth, None for other elements
        children: Count of direct child elements
        raw_text: Extracted text content (for leaf nodes)
        attrs: Additional attributes (e.g., ordered=True for lists, info for code blocks)
    """

    type: str
    level: int | None = None
    children: int = 0
    raw_text: str | None = None
    attrs: dict[str, Any] | None = None


class MarkdownASTParser:
    """Parser for converting Markdown to Abstract Syntax Tree.

    Uses mistune 3.x with GFM extensions to parse Markdown into a structured
    token tree. Supports analysis of document structure for advanced metrics.

    The parser enables plugins for:
    - Tables (GFM table syntax)
    - Strikethrough (~~text~~)
    - Task lists (- [ ] item)

    Attributes:
        _markdown: Configured mistune parser instance
        _plugins: List of enabled plugin names
    """

    def __init__(self, plugins: list[str] | None = None) -> None:
        """Initialize the AST parser.

        Args:
            plugins: List of mistune plugins to enable. Defaults to
                ['table', 'strikethrough', 'task_lists'] for GFM support.
        """
        if plugins is None:
            plugins = ["table", "strikethrough", "task_lists"]

        self._plugins = plugins
        self._markdown = mistune.create_markdown(renderer="ast", plugins=plugins)

    def parse(self, text: str) -> list[dict[str, Any]]:
        """Parse Markdown text into an Abstract Syntax Tree.

        Args:
            text: Markdown text to parse

        Returns:
            List of token dictionaries representing the AST. Each token
            has a 'type' field and may have 'children', 'attrs', 'raw', etc.

        Example:
            >>> parser = MarkdownASTParser()
            >>> ast = parser.parse("# Heading\\n\\nParagraph")
            >>> [token['type'] for token in ast if token['type'] != 'blank_line']
            ['heading', 'paragraph']
        """
        # mistune with renderer='ast' always returns list, but type checker doesn't know
        return cast(list[dict[str, Any]], self._markdown(text))

    def extract_elements(self, ast: list[dict[str, Any]]) -> list[Element]:
        """Extract structured element information from AST.

        Recursively traverses the AST to extract element information including
        type, level/depth, child count, and text content.

        Args:
            ast: AST tokens from parse()

        Returns:
            List of Element objects representing document structure

        Example:
            >>> parser = MarkdownASTParser()
            >>> ast = parser.parse("# Title\\n\\n- Item 1\\n- Item 2")
            >>> elements = parser.extract_elements(ast)
            >>> [(e.type, e.level) for e in elements if e.type != 'blank_line']
            [('heading', 1), ('list', 0), ('list_item', None), ('list_item', None)]
        """
        elements: list[Element] = []
        self._extract_recursive(ast, elements)
        return elements

    def _extract_recursive(self, tokens: list[dict[str, Any]], elements: list[Element]) -> None:
        """Recursively extract elements from token tree.

        Args:
            tokens: List of token dictionaries to process
            elements: Accumulator list for extracted elements
        """
        for token in tokens:
            element = self._token_to_element(token)
            elements.append(element)

            # Recurse into children
            if "children" in token and isinstance(token["children"], list):
                self._extract_recursive(token["children"], elements)

    def _token_to_element(self, token: dict[str, Any]) -> Element:
        """Convert a single AST token to an Element.

        Args:
            token: Token dictionary from AST

        Returns:
            Element object with extracted information
        """
        token_type = token.get("type", "unknown")
        level = None
        children_count = 0
        raw_text = None
        attrs = {}

        # Extract type-specific information
        if token_type == "heading":
            level = token.get("attrs", {}).get("level")
        elif token_type == "list":
            level = token.get("attrs", {}).get("depth", 0)
            attrs["ordered"] = token.get("attrs", {}).get("ordered", False)
        elif token_type == "block_code":
            attrs["info"] = token.get("attrs", {}).get("info", "")
            raw_text = token.get("raw", "")
        elif token_type == "text":
            raw_text = token.get("raw", "")

        # Count direct children
        if "children" in token and isinstance(token["children"], list):
            children_count = len(token["children"])

        return Element(
            type=token_type,
            level=level,
            children=children_count,
            raw_text=raw_text,
            attrs=attrs if attrs else None,
        )

    def count_elements(self, ast: list[dict[str, Any]]) -> dict[str, int]:
        """Count element types in the AST.

        Args:
            ast: AST tokens from parse()

        Returns:
            Dictionary mapping element types to counts

        Example:
            >>> parser = MarkdownASTParser()
            >>> ast = parser.parse("# H1\\n## H2\\n\\nText")
            >>> counts = parser.count_elements(ast)
            >>> counts['heading']
            2
            >>> counts['paragraph']
            1
        """
        elements = self.extract_elements(ast)
        # Filter out blank_line tokens as they're not meaningful for counting
        meaningful_elements = [e for e in elements if e.type != "blank_line"]
        return dict(Counter(e.type for e in meaningful_elements))

    def count_by_type_and_level(
        self, ast: list[dict[str, Any]]
    ) -> dict[tuple[str, int | None], int]:
        """Count elements by type and level/depth.

        Useful for detailed structural analysis, e.g., counting H1 vs H2 headings
        or top-level vs nested lists.

        Args:
            ast: AST tokens from parse()

        Returns:
            Dictionary mapping (type, level) tuples to counts

        Example:
            >>> parser = MarkdownASTParser()
            >>> ast = parser.parse("# H1\\n## H2\\n## H2 again")
            >>> counts = parser.count_by_type_and_level(ast)
            >>> counts[('heading', 1)]
            1
            >>> counts[('heading', 2)]
            2
        """
        elements = self.extract_elements(ast)
        meaningful_elements = [e for e in elements if e.type != "blank_line"]
        return dict(Counter((e.type, e.level) for e in meaningful_elements))
