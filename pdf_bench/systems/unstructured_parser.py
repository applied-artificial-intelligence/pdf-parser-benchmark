"""Unstructured-based parser for PDF-to-Markdown conversion.

This module implements a parser using the Unstructured library, which provides
flexible PDF parsing with multiple strategies and element-based output.

Unstructured leverages various techniques for PDF parsing:
- Fast strategy: Quick text extraction from PDF text layer
- Auto strategy: Automatically chooses best approach
- Hi-res strategy: ML-based layout analysis and OCR (requires tesseract)

Key features:
- Multiple processing strategies (fast, auto, hi_res)
- Element-based output with categorization
- Table structure inference (hi_res only)
- Language detection and multi-language support
- Cache integration for performance

Examples:
    >>> from pathlib import Path
    >>> parser = UnstructuredParser(strategy="fast")
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(result)
    PosixPath('output/document.md')
"""

from pathlib import Path
from typing import Any

from unstructured.partition.pdf import partition_pdf

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class UnstructuredParser(BaseParser):
    """PDF parser using Unstructured library for flexible PDF-to-Markdown conversion.

    This parser uses the Unstructured library which provides multiple processing
    strategies and element-based output. It's particularly good for text extraction
    and content classification.

    The parser integrates with the caching system and provides custom markdown
    conversion to improve structure preservation.

    Attributes:
        name: Parser identifier ('unstructured')
        version: Unstructured library version string
        strategy: Processing strategy ('auto', 'fast', or 'hi_res')

    Examples:
        >>> # Fast strategy (default) - quickest processing
        >>> parser = UnstructuredParser()
        >>> result = parser.parse(Path("doc.pdf"), Path("output"))
        >>>
        >>> # Auto strategy - balance speed and quality
        >>> parser = UnstructuredParser(strategy="auto")
        >>>
        >>> # Hi-res strategy - best quality (requires tesseract)
        >>> parser = UnstructuredParser(strategy="hi_res", infer_table_structure=True)
    """

    def __init__(
        self, strategy: str = "fast", infer_table_structure: bool = False
    ) -> None:
        """Initialize the UnstructuredParser.

        Args:
            strategy: Processing strategy to use. Options:
                - 'fast': Quick text extraction (default)
                - 'auto': Automatically choose best strategy
                - 'hi_res': High-resolution ML-based parsing (requires tesseract)
            infer_table_structure: Whether to infer table structure (hi_res only).

        Raises:
            ValueError: If strategy is not one of 'fast', 'auto', 'hi_res'.
        """
        valid_strategies = ["fast", "auto", "hi_res"]
        if strategy not in valid_strategies:
            raise ValueError(
                f"Invalid strategy '{strategy}'. Must be one of {valid_strategies}"
            )

        self._strategy = strategy
        self._infer_table_structure = infer_table_structure

        # Get version from unstructured package
        try:
            import unstructured

            # Unstructured's version is in a submodule
            version_str = str(unstructured.__version__)
            # Extract version number if it's a module reference
            if "module" in version_str:
                self._version = "0.18.20"  # Fallback to known version
            else:
                self._version = version_str
        except (ImportError, AttributeError):
            self._version = "0.18.20"  # Fallback version

    @property
    def name(self) -> str:
        """Return the parser's unique identifier.

        Returns:
            str: Always returns 'unstructured'.
        """
        return "unstructured"

    @property
    def version(self) -> str:
        """Return the unstructured library version.

        Returns:
            str: Unstructured version string (e.g., '0.18.20').
        """
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using Unstructured.

        This method uses the Unstructured library to extract content from PDFs
        and converts it to Markdown format. The implementation:
        1. Checks cache for existing result
        2. If cache miss, partitions PDF into elements using Unstructured
        3. Converts elements to properly formatted Markdown
        4. Writes Markdown to output directory
        5. Stores result in cache
        6. Returns path to generated file

        Args:
            pdf_path: Path to the input PDF file. Must exist and be readable.
            output_dir: Directory where the output Markdown file should be saved.
                Must exist and be writable.

        Returns:
            Path: Path to the generated Markdown file.

        Raises:
            FileNotFoundError: If pdf_path does not exist.
            PermissionError: If pdf_path is not readable or output_dir is not writable.
            RuntimeError: If Unstructured parsing fails.

        Examples:
            >>> parser = UnstructuredParser()
            >>> pdf = Path("document.pdf")
            >>> output = Path("output")
            >>> result = parser.parse(pdf, output)
            >>> result.exists()
            True
        """
        # Validate input
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not pdf_path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")

        # Generate cache key (include strategy in version for cache invalidation)
        cache_version = f"{self.version}-{self._strategy}"
        key = cache_key(pdf_path, self.name, cache_version)

        # Check cache
        cache_dir = Path(".cache")
        cached = get_cached(key, cache_dir)
        if cached is not None:
            return cached

        # Cache miss - parse the PDF
        try:
            # Extract content using Unstructured
            markdown_content = self._extract_and_convert(pdf_path)

            # Create output directory if needed
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write markdown file
            markdown_path = output_dir / f"{pdf_path.stem}.md"
            markdown_path.write_text(markdown_content, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, markdown_path, cache_dir)

            return cached_path

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with Unstructured: {e}") from e

    def _extract_and_convert(self, pdf_path: Path) -> str:
        """Extract content from PDF and convert to Markdown.

        This method partitions the PDF into elements using Unstructured and
        converts them to well-formatted Markdown.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            str: Markdown-formatted content.

        Raises:
            RuntimeError: If partitioning fails.
        """
        # Partition PDF into elements
        elements = partition_pdf(
            filename=str(pdf_path),
            strategy=self._strategy,
            include_page_breaks=False,
            infer_table_structure=self._infer_table_structure,
        )

        # Convert elements to markdown
        markdown_content = self._elements_to_markdown(elements)

        return markdown_content

    def _elements_to_markdown(self, elements: list[Any]) -> str:
        """Convert Unstructured elements to Markdown format.

        This method converts the element list into well-formatted Markdown,
        preserving structure and formatting.

        Args:
            elements: List of Unstructured Element objects.

        Returns:
            str: Markdown-formatted text.
        """
        if not elements:
            return ""

        markdown_lines: list[str] = []
        previous_category: str | None = None

        for element in elements:
            text = element.text.strip()
            if not text:
                continue

            category = element.category

            # Add spacing between different element types
            if previous_category and previous_category != category:
                if previous_category not in ["Title", "ListItem"]:
                    markdown_lines.append("")

            # Format based on element type
            if category == "Title":
                # Use # for all titles (Unstructured doesn't distinguish levels well)
                markdown_lines.append(f"# {text}")
                markdown_lines.append("")
            elif category == "NarrativeText":
                # Regular paragraph
                markdown_lines.append(text)
                markdown_lines.append("")
            elif category == "ListItem":
                # Bullet list item
                markdown_lines.append(f"- {text}")
            elif category == "Table":
                # Table (already formatted if infer_table_structure=True)
                markdown_lines.append(text)
                markdown_lines.append("")
            else:
                # Other elements (treat as paragraph)
                markdown_lines.append(text)
                markdown_lines.append("")

            previous_category = category

        # Join and clean up extra blank lines
        markdown = "\n".join(markdown_lines)

        # Remove excessive blank lines (more than 2 consecutive)
        while "\n\n\n" in markdown:
            markdown = markdown.replace("\n\n\n", "\n\n")

        return markdown.strip() + "\n"
