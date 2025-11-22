"""Convert ar5iv HTML to Markdown ground truth using Pandoc.

Uses pandoc for conversion with minimal post-processing to clean up formatting.
"""

import re
import subprocess
from pathlib import Path


def convert_html_to_markdown(html_path: Path, output_path: Path, cleanup: bool = True) -> bool:
    """
    Convert ar5iv HTML to Markdown using pandoc.

    Args:
        html_path: Path to ar5iv HTML file
        output_path: Path to save Markdown output
        cleanup: Whether to apply post-processing cleanup

    Returns:
        True if successful, False otherwise
    """
    try:
        # Run pandoc conversion
        subprocess.run(
            [
                "pandoc",
                str(html_path),
                "-f",
                "html",
                "-t",
                "markdown",
                "--wrap=none",  # Don't wrap long lines
                "-o",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )

        if cleanup:
            apply_cleanup(output_path)

        return True

    except subprocess.CalledProcessError as e:
        print(f"Pandoc conversion failed: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Conversion error: {e}")
        return False


def apply_cleanup(md_path: Path) -> None:
    """
    Apply minimal post-processing cleanup to pandoc output.

    - Remove excessive pandoc div markers
    - Clean up multiple blank lines
    - Remove HTML class attributes from headers
    - Remove table wrappers around equations
    - Remove LaTeX spacing commands
    - Remove inline CSS classes
    """
    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    # Remove pandoc div markers (keep content, remove ::: wrappers)
    content = re.sub(r"^::: \{[^}]+\}\s*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"^:::\s*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"^::: [a-z_]+\s*$", "", content, flags=re.MULTILINE)

    # Remove table wrappers around equations (Pandoc adds these)
    # Example:   -- ---- --\n  $$...$$ \n  -- ---- --
    # These appear as lines with dashes and spaces
    content = re.sub(r"^\s*-+\s+-+\s*$", "", content, flags=re.MULTILINE)

    # Remove inline CSS classes and spans
    # Example: [Text]{.ltx_class} -> Text
    # Example: [2](#ref){.ltx_ref} -> 2
    content = re.sub(r"\[([^\]]+)\]\([^)]*\)\{[^}]+\}", r"\1", content)  # Links with classes
    content = re.sub(r"\[([^\]]+)\]\{[^}]+\}", r"\1", content)  # Spans with classes

    # Remove LaTeX spacing commands
    content = re.sub(r"\\hspace\{0pt\}", "", content)

    # Remove excessive braces around function arguments
    # Example: \text{u}{(x,t)} -> \text{u}(x,t)
    content = re.sub(r"(\w)\{(\([^}]+\))\}", r"\1\2", content)

    # Remove HTML class/id attributes from headers
    # Example: ## [1. ]{.ltx_tag} Title {#id} -> ## 1. Title
    content = re.sub(r"(\#{1,6}\s+.+?)\s+\{[^}]+\}", r"\1", content)

    # Clean up multiple blank lines (max 2 consecutive)
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    # Remove leading/trailing whitespace per line (preserve indentation for code)
    lines = content.split("\n")
    lines = [line.rstrip() for line in lines]
    content = "\n".join(lines)

    # Save cleaned content
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)


def convert_all_arxiv_samples(
    sample_dir: Path = Path("corpus/academic/sample"), output_dir: Path | None = None
) -> dict:
    """
    Convert all ar5iv HTML files in sample directory to Markdown.

    Args:
        sample_dir: Directory containing ar5iv HTML files
        output_dir: Output directory (default: sample_dir/ground_truth)

    Returns:
        Dictionary with conversion results
    """
    if output_dir is None:
        output_dir = sample_dir / "ground_truth"

    output_dir.mkdir(parents=True, exist_ok=True)

    html_files = sorted(sample_dir.glob("*.html"))

    if not html_files:
        print(f"❌ No HTML files found in {sample_dir}")
        return {}

    print("🔄 Converting ar5iv HTML → Markdown Ground Truth")
    print("=" * 70)
    print(f"Input: {sample_dir}")
    print(f"Output: {output_dir}")
    print(f"Files: {len(html_files)}")
    print("=" * 70)
    print()

    results = {}

    for i, html_path in enumerate(html_files, 1):
        arxiv_id = html_path.stem
        output_path = output_dir / f"{arxiv_id}.md"

        print(f"[{i}/{len(html_files)}] {arxiv_id}")
        print(f"   HTML: {html_path.name} ({html_path.stat().st_size / 1024:.1f} KB)")

        success = convert_html_to_markdown(html_path, output_path, cleanup=True)

        if success:
            md_size = output_path.stat().st_size / 1024
            print(f"   ✓ Markdown: {output_path.name} ({md_size:.1f} KB)")
            results[arxiv_id] = {
                "success": True,
                "html_path": str(html_path),
                "md_path": str(output_path),
                "html_size_kb": round(html_path.stat().st_size / 1024, 1),
                "md_size_kb": round(md_size, 1),
            }
        else:
            print("   ❌ Conversion failed")
            results[arxiv_id] = {"success": False, "html_path": str(html_path)}

        print()

    # Summary
    print("=" * 70)
    print("📊 Conversion Summary")
    print("=" * 70)
    successful = sum(1 for r in results.values() if r["success"])
    print(f"Successful: {successful}/{len(html_files)}")

    if successful > 0:
        total_html_kb = sum(r["html_size_kb"] for r in results.values() if r["success"])
        total_md_kb = sum(r["md_size_kb"] for r in results.values() if r["success"])
        print(f"Total HTML: {total_html_kb:.1f} KB")
        print(f"Total Markdown: {total_md_kb:.1f} KB")
        print(f"Compression: {(1 - total_md_kb / total_html_kb) * 100:.1f}%")

    print()
    print("✅ Conversion complete")
    print(f"Ground truth saved to: {output_dir}")

    return results


def main():
    """Convert ar5iv sample HTML files to Markdown."""
    results = convert_all_arxiv_samples()

    # Print any failures
    failures = [arxiv_id for arxiv_id, r in results.items() if not r["success"]]
    if failures:
        print()
        print("⚠️  Failed conversions:")
        for arxiv_id in failures:
            print(f"  - {arxiv_id}")


if __name__ == "__main__":
    main()
