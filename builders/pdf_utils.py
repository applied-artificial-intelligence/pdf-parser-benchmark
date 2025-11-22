"""PDF utility functions for corpus generation.

This module provides utilities for PDF manipulation, particularly
for ensuring compatibility with various PDF parsers.
"""

from pathlib import Path

import pypdf


def normalize_pdf(pdf_path: Path) -> None:
    """Normalize a PDF to ensure compatibility with all parsers.

    Some PDF generators (e.g., LaTeX via xdvipdfmx, LibreOffice) create PDFs
    with object streams (PDF 1.5+ feature) where page metadata like /MediaBox
    is stored in compressed objects. While standard readers handle this fine,
    some parsers (notably docling-parse) cannot read these PDFs.

    This function re-saves the PDF without object streams, making all page
    metadata visible as plain text in the PDF structure.

    Args:
        pdf_path: Path to PDF file to normalize (modified in place)

    Raises:
        FileNotFoundError: If pdf_path doesn't exist
        pypdf.errors.PdfReadError: If PDF is corrupted
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Read the PDF
    reader = pypdf.PdfReader(pdf_path)
    writer = pypdf.PdfWriter()

    # Copy all pages
    for page in reader.pages:
        writer.add_page(page)

    # Copy metadata if present
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    # Write back without object streams
    # pypdf writes in a format that doesn't use object streams by default
    with open(pdf_path, "wb") as f:
        writer.write(f)


def normalize_pdf_safe(pdf_path: Path) -> bool:
    """Normalize a PDF, returning success status instead of raising.

    Args:
        pdf_path: Path to PDF file to normalize

    Returns:
        True if normalization succeeded, False otherwise
    """
    try:
        normalize_pdf(pdf_path)
        return True
    except Exception as e:
        print(f"Warning: Failed to normalize {pdf_path}: {e}")
        return False


def normalize_all_pdfs(directory: Path, recursive: bool = False) -> dict[str, int]:
    """Normalize all PDFs in a directory.

    Args:
        directory: Directory containing PDFs
        recursive: If True, search subdirectories

    Returns:
        Dict with 'success' and 'failed' counts
    """
    pattern = "**/*.pdf" if recursive else "*.pdf"
    pdfs = sorted(directory.glob(pattern))

    results = {"success": 0, "failed": 0}

    for pdf in pdfs:
        if normalize_pdf_safe(pdf):
            results["success"] += 1
        else:
            results["failed"] += 1

    return results
