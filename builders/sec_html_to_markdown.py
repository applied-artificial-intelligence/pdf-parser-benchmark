"""SEC EDGAR HTML to Markdown converter.

This module provides functions to convert SEC EDGAR filing HTML to Markdown format.
It handles SEC-specific formatting including:
- Financial tables (using sophisticated table extraction)
- XBRL tags
- Document metadata (company, filing type, date)
- Multi-level section headings
- Footnotes and legal boilerplate
- Signature blocks

The converter leverages the financial table extractor from extract_financial_tables.py
to ensure accurate conversion of complex financial statements.
"""

import logging
import re
from typing import Any

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement

from builders.extract_financial_tables import extract_tables_from_html

# Configure logging
logger = logging.getLogger(__name__)


class SECMarkdownConversionError(Exception):
    """Exception raised when SEC HTML to Markdown conversion fails."""

    pass


class SECHTMLToMarkdown:
    """Converter for SEC EDGAR filings HTML to Markdown.

    This converter is optimized for SEC 10-K, 10-Q, and other EDGAR filings.
    It uses sophisticated financial table extraction and handles SEC-specific
    formatting requirements.

    Attributes:
        use_financial_tables: Whether to use financial table extractor
        normalize_currency: Whether to normalize currency in tables
        strip_xbrl: Whether to strip XBRL tags from tables
        extract_metadata: Whether to extract and include filing metadata
    """

    def __init__(
        self,
        use_financial_tables: bool = True,
        normalize_currency: bool = True,
        strip_xbrl: bool = True,
        extract_metadata: bool = True,
    ) -> None:
        """Initialize SEC HTML to Markdown converter.

        Args:
            use_financial_tables: Use financial table extractor (default: True)
            normalize_currency: Normalize currency formatting in tables (default: True)
            strip_xbrl: Strip XBRL tags from table HTML (default: True)
            extract_metadata: Extract filing metadata (default: True)
        """
        self.use_financial_tables = use_financial_tables
        self.normalize_currency = normalize_currency
        self.strip_xbrl = strip_xbrl
        self.extract_metadata = extract_metadata

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text.

        - Converts multiple spaces to single space
        - Converts multiple newlines to maximum of 2 (paragraph break)
        - Strips leading/trailing whitespace from each line

        Args:
            text: Input text with potentially irregular whitespace

        Returns:
            Text with normalized whitespace
        """
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]

        # Join lines
        text = "\n".join(lines)

        # Replace multiple spaces with single space (within lines)
        text = re.sub(r" +", " ", text)

        # Replace 3+ newlines with exactly 2 newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _extract_filing_metadata(self, soup: BeautifulSoup) -> dict[str, str]:
        """Extract filing metadata from SEC HTML.

        Attempts to extract:
        - Company name
        - Filing type (10-K, 10-Q, etc.)
        - Filing date
        - CIK number
        - Fiscal year end

        Args:
            soup: BeautifulSoup parsed HTML

        Returns:
            Dictionary with metadata fields
        """
        metadata: dict[str, str] = {}

        # Look for common SEC metadata patterns
        # Company name often in title or meta tags
        title = soup.find("title")
        if title:
            title_text = title.get_text(strip=True)
            metadata["title"] = title_text

            # Try to extract company name from title
            # Format: "COMPANY NAME - Form TYPE"
            if " - " in title_text:
                parts = title_text.split(" - ")
                if len(parts) >= 2:
                    metadata["company_name"] = parts[0].strip()
                    metadata["form_type"] = parts[1].strip()

        # Look for meta tags with SEC information
        for meta in soup.find_all("meta"):
            name_attr = meta.get("name", "")
            name = str(name_attr).lower() if isinstance(name_attr, str) else ""
            content_attr = meta.get("content", "")
            content = str(content_attr) if isinstance(content_attr, str) else ""

            if "company" in name and content:
                metadata["company_name"] = content
            elif ("form" in name or "type" in name) and content:
                metadata["form_type"] = content
            elif "date" in name and content:
                metadata["filing_date"] = content
            elif "cik" in name and content:
                metadata["cik"] = content

        # Look for explicit filing information in document
        # SEC filings often have structured header sections
        for element in soup.find_all(["div", "p", "span"]):
            text = element.get_text(strip=True)

            # CIK number pattern
            if "CIK" in text:
                cik_match = re.search(r"CIK[:\s]+(\d+)", text, re.IGNORECASE)
                if cik_match and "cik" not in metadata:
                    metadata["cik"] = cik_match.group(1)

            # Filing date pattern
            if "Filed as of date" in text or "Filing Date" in text:
                date_match = re.search(r"(\d{4}-\d{2}-\d{2}|\d{8})", text)
                if date_match and "filing_date" not in metadata:
                    metadata["filing_date"] = date_match.group(1)

        return metadata

    def _format_metadata_header(self, metadata: dict[str, str]) -> str:
        """Format metadata as Markdown header.

        Args:
            metadata: Metadata dictionary

        Returns:
            Markdown formatted header
        """
        parts = []

        # Title/heading
        if "company_name" in metadata and "form_type" in metadata:
            parts.append(f"# {metadata['company_name']} - {metadata['form_type']}")
        elif "company_name" in metadata:
            parts.append(f"# {metadata['company_name']}")
        elif "title" in metadata:
            parts.append(f"# {metadata['title']}")

        # Metadata fields
        info_parts = []
        if "filing_date" in metadata:
            info_parts.append(f"**Filing Date**: {metadata['filing_date']}")
        if "cik" in metadata:
            info_parts.append(f"**CIK**: {metadata['cik']}")
        if "form_type" in metadata and "company_name" in metadata:
            # Already in title
            pass
        elif "form_type" in metadata:
            info_parts.append(f"**Form Type**: {metadata['form_type']}")

        if info_parts:
            parts.append("\n".join(info_parts))

        if parts:
            parts.append("---")
            return "\n\n".join(parts)

        return ""

    def _clean_html(self, soup: BeautifulSoup) -> None:
        """Remove navigation, scripts, and boilerplate from HTML.

        Modifies soup in place.

        Args:
            soup: BeautifulSoup object to clean
        """
        # Remove scripts and styles
        for element in soup.find_all(["script", "style"]):
            element.decompose()

        # Remove common SEC boilerplate/navigation elements
        # SEC viewer adds navigation div, remove it
        for nav in soup.find_all(["nav", "header", "footer"]):
            nav.decompose()

        # Remove elements with common navigation classes/IDs
        for attr in ["id", "class"]:
            for pattern in [
                "navigation",
                "nav",
                "header",
                "footer",
                "menu",
                "toc-button",
                "banner",
            ]:
                for element in soup.find_all(attrs={attr: re.compile(pattern, re.I)}):
                    element.decompose()

    def _convert_heading(self, heading: Tag) -> str:
        """Convert heading to Markdown.

        h1 → #, h2 → ##, etc.

        Args:
            heading: BeautifulSoup heading element (h1-h6)

        Returns:
            Markdown heading as string
        """
        level = int(heading.name[1])  # Extract number from h1, h2, etc.
        text = heading.get_text(strip=True)

        # Clean up common SEC heading artifacts
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        return f"{'#' * level} {text}"

    def _convert_paragraph(self, paragraph: Tag) -> str:
        """Convert paragraph to Markdown.

        Handles inline formatting:
        - Links
        - Bold/strong
        - Italic/em
        - Code
        - Superscript (for footnotes)

        Args:
            paragraph: BeautifulSoup p element

        Returns:
            Markdown paragraph as string
        """
        result_parts: list[str] = []

        def process_element(elem: PageElement) -> None:
            """Recursively process element and its children."""
            if isinstance(elem, NavigableString):
                text = str(elem).strip()
                if text:
                    result_parts.append(text)
            elif isinstance(elem, Tag):
                if elem.name == "a":
                    href = elem.get("href", "")
                    text = elem.get_text(strip=True)
                    result_parts.append(f"[{text}]({href})")
                elif elem.name in ["em", "i"]:
                    text = elem.get_text(strip=True)
                    if text:
                        result_parts.append(f"*{text}*")
                elif elem.name in ["strong", "b"]:
                    text = elem.get_text(strip=True)
                    if text:
                        result_parts.append(f"**{text}**")
                elif elem.name == "code":
                    text = elem.get_text(strip=True)
                    if text:
                        result_parts.append(f"`{text}`")
                elif elem.name == "sup":
                    # Preserve superscript for footnotes
                    text = elem.get_text(strip=True)
                    if text:
                        result_parts.append(f"^{text}")
                elif elem.name == "sub":
                    # Preserve subscript
                    text = elem.get_text(strip=True)
                    if text:
                        result_parts.append(f"_{text}")
                elif elem.name == "br":
                    result_parts.append("\n")
                else:
                    # For other elements, process children
                    for child in elem.children:
                        process_element(child)

        for child in paragraph.children:
            process_element(child)

        return " ".join(result_parts)

    def _convert_list(self, list_element: Tag, indent_level: int = 0) -> str:
        """Convert list (ul/ol) to Markdown.

        Handles nested lists recursively and inline formatting (links, bold, etc.).

        Args:
            list_element: BeautifulSoup ul or ol element
            indent_level: Current nesting level (0 = top level)

        Returns:
            Markdown list as string
        """
        is_ordered = list_element.name == "ol"
        items = []
        indent = "  " * indent_level

        list_items = list_element.find_all("li", recursive=False)

        for idx, li in enumerate(list_items, 1):
            # Get direct content (not from nested lists), handling inline formatting
            text_parts: list[str] = []

            def process_element(elem: PageElement, parts: list[str]) -> None:
                """Process element for inline formatting."""
                if isinstance(elem, NavigableString):
                    text = str(elem).strip()
                    if text:
                        parts.append(text)
                elif isinstance(elem, Tag):
                    if elem.name in ["ul", "ol"]:
                        # Skip nested lists (handled separately)
                        return
                    elif elem.name == "a":
                        href = elem.get("href", "")
                        text = elem.get_text(strip=True)
                        parts.append(f"[{text}]({href})")
                    elif elem.name in ["strong", "b"]:
                        text = elem.get_text(strip=True)
                        if text:
                            parts.append(f"**{text}**")
                    elif elem.name in ["em", "i"]:
                        text = elem.get_text(strip=True)
                        if text:
                            parts.append(f"*{text}*")
                    elif elem.name == "code":
                        text = elem.get_text(strip=True)
                        if text:
                            parts.append(f"`{text}`")
                    else:
                        # For other elements, process children
                        for child in elem.children:
                            process_element(child, parts)

            for child in li.children:
                process_element(child, text_parts)

            item_text = " ".join(text_parts)

            # Create list marker
            if is_ordered:
                marker = f"{idx}."
            else:
                marker = "-"

            items.append(f"{indent}{marker} {item_text}")

            # Handle nested lists
            nested_lists = li.find_all(["ul", "ol"], recursive=False)
            for nested in nested_lists:
                nested_md = self._convert_list(nested, indent_level + 1)
                items.append(nested_md)

        return "\n".join(items)

    def _convert_table(self, table: Tag) -> str:
        """Convert table using financial table extractor or fallback.

        Args:
            table: BeautifulSoup table element

        Returns:
            Markdown or HTML representation of table
        """
        if self.use_financial_tables:
            try:
                # Use sophisticated financial table extractor
                tables = extract_tables_from_html(
                    str(table), normalize=self.normalize_currency, strip_xbrl=self.strip_xbrl
                )

                if tables:
                    # Return the extracted table content
                    return tables[0].content
                else:
                    logger.warning("Financial table extractor returned no results, using fallback")
                    return self._simple_table_to_html(table)

            except Exception as e:
                logger.warning(f"Financial table extraction failed: {e}, using fallback")
                return self._simple_table_to_html(table)
        else:
            # Use simple HTML preservation
            return self._simple_table_to_html(table)

    def _simple_table_to_html(self, table: Tag) -> str:
        """Simple HTML preservation for tables.

        Args:
            table: BeautifulSoup table element

        Returns:
            HTML table as string
        """
        return str(table)

    def _convert_figure(self, figure: Tag) -> str:
        """Convert figure element to Markdown.

        Extracts image with alt text and caption.

        Args:
            figure: BeautifulSoup figure element

        Returns:
            Markdown figure as string
        """
        parts = []

        # Find image
        img = figure.find("img")
        if img:
            src = img.get("src", "")
            alt = img.get("alt", "")
            parts.append(f"![{alt}]({src})")

        # Find caption
        caption = figure.find("figcaption")
        if caption:
            caption_text = caption.get_text(strip=True)
            parts.append(f"\n*{caption_text}*")

        return "\n".join(parts)

    def _convert_image(self, img: Tag) -> str:
        """Convert standalone image to Markdown.

        Args:
            img: BeautifulSoup img element

        Returns:
            Markdown image as string
        """
        src = img.get("src", "")
        alt = img.get("alt", "")
        return f"![{alt}]({src})"

    def _convert_blockquote(self, blockquote: Tag) -> str:
        """Convert blockquote to Markdown.

        Args:
            blockquote: BeautifulSoup blockquote element

        Returns:
            Markdown blockquote as string
        """
        text = blockquote.get_text(strip=True)
        # Split into lines and prefix each with >
        lines = text.split("\n")
        quoted = "\n".join(f"> {line.strip()}" for line in lines if line.strip())
        return quoted

    def _convert_hr(self, hr: Tag) -> str:
        """Convert horizontal rule to Markdown.

        Args:
            hr: BeautifulSoup hr element

        Returns:
            Markdown horizontal rule
        """
        return "---"

    def _should_skip_element(self, element: Tag) -> bool:
        """Determine if element should be skipped during conversion.

        Args:
            element: BeautifulSoup element

        Returns:
            True if element should be skipped
        """
        # Skip if nested within another element we'll process
        if element.name in ["ul", "ol"]:
            # Skip if this list is nested within another list or table
            if element.find_parent(["ul", "ol", "th", "td", "figcaption"]):
                return True
        elif element.name == "table":
            # Skip if this table is nested within another table or list item
            if element.find_parent(["table", "li", "figcaption"]):
                return True
        elif element.name == "blockquote":
            # Skip if nested in another blockquote
            if element.find_parent("blockquote"):
                return True
        else:
            # For other elements, skip if nested within paragraph, list item, table cell, or caption
            if element.find_parent(["p", "li", "th", "td", "figcaption", "blockquote"]):
                return True

        return False

    def convert(self, html: str) -> str:
        """Convert SEC filing HTML to Markdown.

        This function converts SEC EDGAR filing HTML to Markdown format.
        It handles:
        - Filing metadata extraction
        - Headings (h1-h6)
        - Paragraphs with inline formatting
        - Lists (ul/ol) including nested lists
        - Tables (using financial table extractor)
        - Figures and images
        - Blockquotes
        - Horizontal rules

        Args:
            html: SEC filing HTML content

        Returns:
            Markdown content as string

        Raises:
            SECMarkdownConversionError: If conversion fails
        """
        if not html or not html.strip():
            raise SECMarkdownConversionError("HTML content is empty")

        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            raise SECMarkdownConversionError(f"Failed to parse HTML: {e}") from e

        # Extract metadata if requested
        metadata_header = ""
        if self.extract_metadata:
            metadata = self._extract_filing_metadata(soup)
            if metadata:
                metadata_header = self._format_metadata_header(metadata)
                logger.info(f"Extracted metadata: {metadata}")

        # Clean HTML
        self._clean_html(soup)

        # Find main content container
        content = soup.find("body") or soup.find("main") or soup.find("article") or soup

        if not content:
            raise SECMarkdownConversionError("No content found in HTML")

        markdown_parts = []

        # Process elements in order
        for element in content.descendants:
            # Skip non-Tag elements
            if not isinstance(element, Tag):
                continue

            # Skip nested elements
            if self._should_skip_element(element):
                continue

            # Convert based on element type
            try:
                if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    markdown_parts.append(self._convert_heading(element))
                elif element.name == "p":
                    converted = self._convert_paragraph(element)
                    if converted:  # Only add non-empty paragraphs
                        markdown_parts.append(converted)
                elif element.name in ["ul", "ol"]:
                    markdown_parts.append(self._convert_list(element))
                elif element.name == "table":
                    markdown_parts.append(self._convert_table(element))
                elif element.name == "figure":
                    markdown_parts.append(self._convert_figure(element))
                elif element.name == "img" and not element.find_parent("figure"):
                    markdown_parts.append(self._convert_image(element))
                elif element.name == "blockquote":
                    markdown_parts.append(self._convert_blockquote(element))
                elif element.name == "hr":
                    markdown_parts.append(self._convert_hr(element))
            except Exception as e:
                logger.warning(f"Failed to convert {element.name} element: {e}")
                continue

        # Join parts with double newline (paragraph separator)
        content_markdown = "\n\n".join(part for part in markdown_parts if part)

        # Apply normalization
        content_markdown = self._normalize_whitespace(content_markdown)

        # Combine metadata and content
        if metadata_header:
            markdown = f"{metadata_header}\n\n{content_markdown}"
        else:
            markdown = content_markdown

        if not markdown:
            raise SECMarkdownConversionError("Conversion resulted in empty content")

        logger.info(f"Converted SEC HTML ({len(html)} bytes) to Markdown ({len(markdown)} bytes)")
        return markdown


def convert_sec_html_to_markdown(
    html: str,
    use_financial_tables: bool = True,
    normalize_currency: bool = True,
    strip_xbrl: bool = True,
    extract_metadata: bool = True,
) -> str:
    """Convenience function to convert SEC filing HTML to Markdown.

    Args:
        html: SEC filing HTML content
        use_financial_tables: Use financial table extractor (default: True)
        normalize_currency: Normalize currency formatting (default: True)
        strip_xbrl: Strip XBRL tags from tables (default: True)
        extract_metadata: Extract filing metadata (default: True)

    Returns:
        Markdown content as string

    Raises:
        SECMarkdownConversionError: If conversion fails
    """
    converter = SECHTMLToMarkdown(
        use_financial_tables=use_financial_tables,
        normalize_currency=normalize_currency,
        strip_xbrl=strip_xbrl,
        extract_metadata=extract_metadata,
    )
    return converter.convert(html)
