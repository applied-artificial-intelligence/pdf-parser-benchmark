"""Abstract base class for PDF-to-Markdown parsers.

This module defines the BaseParser interface that all parser implementations
must follow. The interface ensures consistency across different parsing systems
(open-source libraries, commercial APIs, etc.) and enables the benchmarking
framework to treat all parsers uniformly.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseParser(ABC):
    """Abstract base class for PDF-to-Markdown parsers.

    All parser implementations must inherit from this class and implement
    the required abstract methods and properties. This ensures a consistent
    interface for the benchmarking framework.

    The parser interface is intentionally minimal to support a wide variety
    of parsing systems:
    - Local library-based parsers (PyMuPDF, Unstructured)
    - Subprocess-based parsers (Marker, Nougat)
    - Commercial API-based parsers (AWS Textract, Azure Document Intelligence)

    Examples:
        >>> class MyParser(BaseParser):
        ...     @property
        ...     def name(self) -> str:
        ...         return "myparser"
        ...
        ...     @property
        ...     def version(self) -> str:
        ...         return "1.0.0"
        ...
        ...     def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        ...         # Implementation here
        ...         output_path = output_dir / f"{pdf_path.stem}.md"
        ...         # ... parsing logic ...
        ...         return output_path

    Notes:
        - Parsers should handle their own configuration (API keys, model
          parameters, etc.) through constructor arguments.
        - Error handling is the responsibility of each implementation.
          Common exceptions include FileNotFoundError, PermissionError,
          and RuntimeError.
        - The parse() method should be synchronous. Async operations
          (e.g., API calls) should be handled internally and exposed
          via a synchronous interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the parser's unique identifier.

        The name should be a lowercase, alphanumeric string that uniquely
        identifies the parser. It should not include version information.

        Returns:
            str: Parser name (e.g., 'marker', 'nougat', 'pymupdf', 'aws_textract').

        Examples:
            >>> parser.name
            'marker'
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the parser's version string.

        The version should follow semantic versioning (MAJOR.MINOR.PATCH)
        when possible. This is used for cache invalidation and result
        reproducibility.

        Returns:
            str: Parser version (e.g., '0.2.0', '1.0.0-beta', '2024.11.14').

        Examples:
            >>> parser.version
            '0.2.0'
        """
        pass

    @abstractmethod
    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output.

        This method processes the input PDF and saves the resulting Markdown
        to a file in the specified output directory. The implementation is
        responsible for:
        - Reading the PDF from pdf_path
        - Converting content to Markdown format
        - Generating an appropriate output filename
        - Writing the Markdown to output_dir
        - Returning the path to the generated file

        Args:
            pdf_path: Path to the input PDF file. Must exist and be readable.
            output_dir: Directory where the output Markdown file should be saved.
                Must exist and be writable.

        Returns:
            Path: Path to the generated Markdown file.

        Raises:
            FileNotFoundError: If pdf_path does not exist or is not accessible.
            PermissionError: If output_dir is not writable.
            RuntimeError: If parsing fails for any reason (corrupted PDF,
                parser error, API failure, etc.).

        Examples:
            >>> pdf_file = Path("document.pdf")
            >>> output_directory = Path(".cache/marker")
            >>> result_path = parser.parse(pdf_file, output_directory)
            >>> result_path
            PosixPath('.cache/marker/document.md')
            >>> result_path.exists()
            True
        """
        pass

    def __repr__(self) -> str:
        """Return a string representation of the parser.

        Returns:
            str: String in the format "ParserName(name-version)".
        """
        return f"{self.__class__.__name__}({self.name}-{self.version})"
