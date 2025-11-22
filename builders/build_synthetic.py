"""Build synthetic PDFs from Markdown sources using Pandoc.

This module provides functionality to convert Markdown documents to PDF
using Pandoc with LaTeX backend. It supports:

- Configurable PDF generation with Pandoc options
- SHA256 hash verification for generated PDFs
- Error handling for Pandoc failures
- Metadata integration with YAML files
"""

import hashlib
import subprocess
import sys
from pathlib import Path

import yaml


class PandocBuilder:
    """Build PDFs from Markdown using Pandoc."""

    def __init__(
        self,
        pandoc_path: str = "pandoc",
        latex_engine: str = "pdflatex",
        extra_args: list[str] | None = None,
    ):
        """Initialize Pandoc builder.

        Args:
            pandoc_path: Path to Pandoc executable (default: "pandoc")
            latex_engine: LaTeX engine to use (default: "pdflatex")
            extra_args: Additional arguments to pass to Pandoc
        """
        self.pandoc_path = pandoc_path
        self.latex_engine = latex_engine
        self.extra_args = extra_args or []

        # Verify Pandoc is available
        try:
            result = subprocess.run(
                [self.pandoc_path, "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            version_line = result.stdout.split("\n")[0]
            print(f"✅ Using {version_line}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(f"Pandoc not found or not working: {e}") from e

    def build_pdf(
        self,
        markdown_path: Path,
        output_pdf_path: Path,
        title: str | None = None,
    ) -> dict[str, str]:
        """Convert Markdown to PDF using Pandoc.

        Args:
            markdown_path: Path to source Markdown file
            output_pdf_path: Path where PDF should be written
            title: Optional document title (default: use filename)

        Returns:
            Dict with 'pdf_path' and 'pdf_hash' keys

        Raises:
            FileNotFoundError: If markdown_path doesn't exist
            subprocess.CalledProcessError: If Pandoc fails
        """
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

        # Ensure output directory exists
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Build Pandoc command
        cmd = [
            self.pandoc_path,
            str(markdown_path),
            "-o",
            str(output_pdf_path),
            f"--pdf-engine={self.latex_engine}",
            "--standalone",
        ]

        # Add title if provided
        if title:
            cmd.extend(["-M", f"title={title}"])

        # Add extra arguments
        cmd.extend(self.extra_args)

        # Run Pandoc
        print(f"🔨 Building PDF: {markdown_path.name} → {output_pdf_path.name}")
        print(f"   Command: {' '.join(cmd)}")

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            # Calculate SHA256 hash
            pdf_hash = self._calculate_hash(output_pdf_path)

            print(f"✅ PDF created: {output_pdf_path}")
            print(f"   Hash: {pdf_hash}")

            return {
                "pdf_path": str(output_pdf_path),
                "pdf_hash": pdf_hash,
            }

        except subprocess.CalledProcessError as e:
            print(f"❌ Pandoc failed for {markdown_path.name}", file=sys.stderr)
            print(f"   Return code: {e.returncode}", file=sys.stderr)
            if e.stdout:
                print(f"   Stdout: {e.stdout}", file=sys.stderr)
            if e.stderr:
                print(f"   Stderr: {e.stderr}", file=sys.stderr)
            raise

    def _calculate_hash(self, pdf_path: Path) -> str:
        """Calculate SHA256 hash of PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Hexadecimal hash string
        """
        sha256 = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def update_metadata(
        self,
        yaml_path: Path,
        pdf_hash: str,
        pdf_path: str | None = None,
    ) -> None:
        """Update YAML metadata file with PDF hash.

        Args:
            yaml_path: Path to YAML metadata file
            pdf_hash: SHA256 hash of generated PDF
            pdf_path: Optional path to PDF (for updating file_paths.pdf)
        """
        with open(yaml_path) as f:
            metadata = yaml.safe_load(f)

        # Update hash
        metadata["pdf_hash"] = pdf_hash

        # Update PDF path if provided
        if pdf_path:
            if "file_paths" not in metadata:
                metadata["file_paths"] = {}
            metadata["file_paths"]["pdf"] = pdf_path

        # Update validation status
        if "validation" not in metadata:
            metadata["validation"] = {}
        metadata["validation"]["pdf_exists"] = True

        # Write back
        with open(yaml_path, "w") as f:
            yaml.dump(metadata, f, sort_keys=False, allow_unicode=True)

        print(f"✅ Updated metadata: {yaml_path.name}")


def build_all_synthetic(
    corpus_dir: Path,
    output_dir: Path | None = None,
    latex_engine: str = "pdflatex",
) -> list[dict[str, str]]:
    """Build all synthetic PDFs from Markdown sources.

    Args:
        corpus_dir: Directory containing synthetic corpus
        output_dir: Directory for output PDFs (default: same as corpus_dir)
        latex_engine: LaTeX engine to use

    Returns:
        List of dicts with build results
    """
    if output_dir is None:
        output_dir = corpus_dir

    builder = PandocBuilder(latex_engine=latex_engine)
    results = []

    # Find all Markdown files
    markdown_files = sorted(corpus_dir.glob("*.md"))

    print(f"\n📦 Building {len(markdown_files)} synthetic PDFs")
    print("=" * 60)

    for md_path in markdown_files:
        # Skip if there's no corresponding YAML
        yaml_path = md_path.with_suffix(".yaml")
        if not yaml_path.exists():
            print(f"⚠️  Skipping {md_path.name} (no YAML metadata)")
            continue

        # Load metadata to get title
        with open(yaml_path) as f:
            metadata = yaml.safe_load(f)

        title = metadata.get("title", md_path.stem)

        # Build PDF
        pdf_path = output_dir / md_path.with_suffix(".pdf").name

        try:
            result = builder.build_pdf(md_path, pdf_path, title=title)

            # Update metadata
            builder.update_metadata(
                yaml_path,
                result["pdf_hash"],
                pdf_path=str(pdf_path),
            )

            results.append(result)

        except Exception as e:
            print(f"❌ Failed to build {md_path.name}: {e}", file=sys.stderr)
            results.append({"pdf_path": str(pdf_path), "error": str(e)})

    print("\n" + "=" * 60)
    print(f"✅ Built {len([r for r in results if 'error' not in r])}/{len(results)} PDFs")

    return results


def main() -> None:
    """CLI entry point for building synthetic corpus."""
    import argparse

    parser = argparse.ArgumentParser(description="Build synthetic PDFs from Markdown using Pandoc")
    parser.add_argument(
        "corpus_dir",
        type=Path,
        help="Directory containing synthetic Markdown files",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output directory for PDFs (default: same as corpus_dir)",
    )
    parser.add_argument(
        "--latex-engine",
        default="pdflatex",
        choices=["pdflatex", "xelatex", "lualatex"],
        help="LaTeX engine to use (default: pdflatex)",
    )

    args = parser.parse_args()

    if not args.corpus_dir.exists():
        print(f"Error: Directory not found: {args.corpus_dir}", file=sys.stderr)
        sys.exit(1)

    results = build_all_synthetic(args.corpus_dir, args.output, args.latex_engine)

    # Exit with error if any builds failed
    failed = [r for r in results if "error" in r]
    if failed:
        print(f"\n❌ {len(failed)} build(s) failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
