#!/usr/bin/env python3
"""
Extract visual examples of parser outputs for publication.

Creates markdown files showing:
1. Good examples (high scores)
2. Bad examples (low scores)
3. Failure modes (multi-column, tables, structure)
4. Side-by-side comparisons

Output: docs/examples/ directory with markdown files
"""

import json
from pathlib import Path

RESULTS_DIR = Path("results")
OUTPUT_DIR = Path("docs/examples")
CACHE_DIR = Path(".cache")
CORPUS_DIR = Path("corpus")

# Create output directories
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
(OUTPUT_DIR / "good").mkdir(exist_ok=True)
(OUTPUT_DIR / "bad").mkdir(exist_ok=True)
(OUTPUT_DIR / "failure_modes").mkdir(exist_ok=True)
(OUTPUT_DIR / "comparisons").mkdir(exist_ok=True)


def load_benchmark_results(filename: str) -> dict:
    """Load benchmark results JSON file."""
    filepath = RESULTS_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath) as f:
        return json.load(f)


def find_cached_output(parser_name: str, doc_id: str) -> Path | None:
    """Find cached parser output for a document."""
    cache_path = CACHE_DIR / parser_name / f"{doc_id}.md"
    if cache_path.exists():
        return cache_path
    return None


def find_ground_truth(doc_id: str) -> Path | None:
    """Find ground truth markdown for a document."""
    # Try multiple corpus locations
    patterns = [
        CORPUS_DIR / "business" / "cuad" / "ground_truth" / f"{doc_id}.md",
        CORPUS_DIR / "business" / "invoices" / "ground_truth" / f"{doc_id}.md",
        CORPUS_DIR / "business" / "hr" / "ground_truth" / f"{doc_id}.md",
        CORPUS_DIR / "business" / "legal" / "ground_truth" / f"{doc_id}.md",
        CORPUS_DIR / "academic" / "sample" / f"{doc_id}.md",
        CORPUS_DIR / "synthetic" / f"{doc_id}.md",
    ]

    for path in patterns:
        if path.exists():
            return path
    return None


def create_comparison_markdown(
    doc_id: str,
    parser_name: str,
    score: float,
    output_path: Path,
    ground_truth_path: Path,
    title: str
) -> str:
    """Create a markdown file with side-by-side comparison."""
    # Read files
    with open(output_path) as f:
        parser_output = f.read()
    with open(ground_truth_path) as f:
        ground_truth = f.read()

    # Truncate if too long
    max_lines = 100
    parser_lines = parser_output.split('\n')
    gt_lines = ground_truth.split('\n')

    if len(parser_lines) > max_lines:
        parser_output = '\n'.join(parser_lines[:max_lines]) + f"\n\n... (truncated, showing {max_lines}/{len(parser_lines)} lines)"
    if len(gt_lines) > max_lines:
        ground_truth = '\n'.join(gt_lines[:max_lines]) + f"\n\n... (truncated, showing {max_lines}/{len(gt_lines)} lines)"

    # Create comparison markdown
    comparison = f"""# {title}

**Document**: `{doc_id}`
**Parser**: `{parser_name}`
**Edit Similarity Score**: {score:.2%}

## Ground Truth

```markdown
{ground_truth}
```

## Parser Output

```markdown
{parser_output}
```

---

*Generated for PDF-Bench publication*
"""
    return comparison


def extract_good_examples(results: dict, n: int = 5):
    """Extract examples of parsers performing well."""
    print(f"Extracting {n} good examples...")

    # Find high-scoring results
    scores = []
    for result in results.get("results", []):
        if result["success"] and result["metrics"].get("edit_similarity"):
            scores.append({
                "doc_id": result["document_id"],
                "parser": result["parser_name"],
                "score": result["metrics"]["edit_similarity"]
            })

    # Sort by score and take top N with diversity
    scores.sort(key=lambda x: x["score"], reverse=True)

    # Select diverse examples (different parsers and documents)
    selected = []
    seen_parsers = set()
    seen_docs = set()

    for item in scores:
        if len(selected) >= n:
            break
        # Prefer examples from different parsers and documents
        if item["parser"] not in seen_parsers or item["doc_id"] not in seen_docs:
            selected.append(item)
            seen_parsers.add(item["parser"])
            seen_docs.add(item["doc_id"])

    # Generate comparison files
    for i, item in enumerate(selected, 1):
        output_path = find_cached_output(item["parser"], item["doc_id"])
        gt_path = find_ground_truth(item["doc_id"])

        if not output_path or not gt_path:
            continue

        comparison = create_comparison_markdown(
            item["doc_id"],
            item["parser"],
            item["score"],
            output_path,
            gt_path,
            f"Good Example #{i}: {item['parser']} on {item['doc_id']}"
        )

        out_file = OUTPUT_DIR / "good" / f"example_{i}_{item['parser']}_{item['doc_id']}.md"
        with open(out_file, 'w') as f:
            f.write(comparison)

        print(f"  ✓ Created {out_file.name} (score: {item['score']:.2%})")


def extract_bad_examples(results: dict, n: int = 5):
    """Extract examples of parsers performing poorly."""
    print(f"Extracting {n} bad examples...")

    # Find low-scoring results (but successful parses)
    scores = []
    for result in results.get("results", []):
        if result["success"] and result["metrics"].get("edit_similarity"):
            score = result["metrics"]["edit_similarity"]
            if score < 0.7:  # Only include poor performers
                scores.append({
                    "doc_id": result["document_id"],
                    "parser": result["parser_name"],
                    "score": score
                })

    # Sort by score (worst first) and take bottom N with diversity
    scores.sort(key=lambda x: x["score"])

    selected = []
    seen_parsers = set()

    for item in scores:
        if len(selected) >= n:
            break
        if item["parser"] not in seen_parsers:
            selected.append(item)
            seen_parsers.add(item["parser"])

    # Generate comparison files
    for i, item in enumerate(selected, 1):
        output_path = find_cached_output(item["parser"], item["doc_id"])
        gt_path = find_ground_truth(item["doc_id"])

        if not output_path or not gt_path:
            continue

        comparison = create_comparison_markdown(
            item["doc_id"],
            item["parser"],
            item["score"],
            output_path,
            gt_path,
            f"Bad Example #{i}: {item['parser']} on {item['doc_id']}"
        )

        out_file = OUTPUT_DIR / "bad" / f"example_{i}_{item['parser']}_{item['doc_id']}.md"
        with open(out_file, 'w') as f:
            f.write(comparison)

        print(f"  ✓ Created {out_file.name} (score: {item['score']:.2%})")


def extract_failure_modes(results: dict):
    """Extract examples of specific failure modes."""
    print("Extracting failure mode examples...")

    # Look for specific patterns in results
    failure_patterns = {
        "multi_column": [],
        "tables": [],
        "structure": []
    }

    for result in results.get("results", []):
        if not result["success"] or not result["metrics"]:
            continue

        doc_id = result["document_id"]
        parser = result["parser_name"]
        metrics = result["metrics"]

        # Multi-column issues (low tree similarity despite ok text)
        if (metrics.get("edit_similarity", 0) > 0.7 and
            metrics.get("tree_similarity", 1) < 0.5):
            failure_patterns["multi_column"].append({
                "doc_id": doc_id,
                "parser": parser,
                "edit_sim": metrics["edit_similarity"],
                "tree_sim": metrics.get("tree_similarity", 0)
            })

        # Table issues (low TEDS)
        if metrics.get("teds") and metrics["teds"] < 0.5:
            failure_patterns["tables"].append({
                "doc_id": doc_id,
                "parser": parser,
                "teds": metrics["teds"]
            })

        # Structure issues (low element F1)
        if metrics.get("element_f1") and metrics["element_f1"] < 0.5:
            failure_patterns["structure"].append({
                "doc_id": doc_id,
                "parser": parser,
                "element_f1": metrics["element_f1"]
            })

    # Create documentation for each failure mode
    modes_found = 0

    # Multi-column failures
    if failure_patterns["multi_column"]:
        item = failure_patterns["multi_column"][0]
        output_path = find_cached_output(item["parser"], item["doc_id"])
        gt_path = find_ground_truth(item["doc_id"])

        if output_path and gt_path:
            comparison = create_comparison_markdown(
                item["doc_id"],
                item["parser"],
                item["edit_sim"],
                output_path,
                gt_path,
                "Failure Mode: Multi-Column Issues"
            )
            comparison += f"\n**Issue**: Good text extraction ({item['edit_sim']:.2%}) but poor structure ({item['tree_sim']:.2%})\n"
            comparison += "**Likely cause**: Multi-column layout not properly handled, reading order incorrect.\n"

            out_file = OUTPUT_DIR / "failure_modes" / "multi_column_failure.md"
            with open(out_file, 'w') as f:
                f.write(comparison)
            print("  ✓ Created multi_column_failure.md")
            modes_found += 1

    # Table failures
    if failure_patterns["tables"]:
        item = failure_patterns["tables"][0]
        output_path = find_cached_output(item["parser"], item["doc_id"])
        gt_path = find_ground_truth(item["doc_id"])

        if output_path and gt_path:
            comparison = f"""# Failure Mode: Table Extraction

**Document**: `{item['doc_id']}`
**Parser**: `{item['parser']}`
**TEDS Score**: {item['teds']:.2%}

**Issue**: Parser failed to preserve table structure

**Likely causes**:
- Merged cells not detected
- Table boundaries misidentified
- Cell content extracted but structure lost

See cached output at: `.cache/{item['parser']}/{item['doc_id']}.md`
Ground truth at: `{find_ground_truth(item['doc_id'])}`

---

*Generated for PDF-Bench publication*
"""
            out_file = OUTPUT_DIR / "failure_modes" / "table_extraction_failure.md"
            with open(out_file, 'w') as f:
                f.write(comparison)
            print("  ✓ Created table_extraction_failure.md")
            modes_found += 1

    print(f"  Found {modes_found} failure mode examples")


def create_index():
    """Create an index file listing all examples."""
    index_content = """# PDF-Bench Visual Examples

Generated examples of parser performance for content marketing.

## Good Examples (High Accuracy)

"""

    good_files = sorted((OUTPUT_DIR / "good").glob("*.md"))
    for f in good_files:
        index_content += f"- [{f.name}](good/{f.name})\n"

    index_content += "\n## Bad Examples (Low Accuracy)\n\n"

    bad_files = sorted((OUTPUT_DIR / "bad").glob("*.md"))
    for f in bad_files:
        index_content += f"- [{f.name}](bad/{f.name})\n"

    index_content += "\n## Failure Modes\n\n"

    failure_files = sorted((OUTPUT_DIR / "failure_modes").glob("*.md"))
    for f in failure_files:
        index_content += f"- [{f.name}](failure_modes/{f.name})\n"

    index_content += "\n---\n\n*All examples extracted from benchmark results.*\n"

    with open(OUTPUT_DIR / "INDEX.md", 'w') as f:
        f.write(index_content)

    print("✓ Created INDEX.md")


def main():
    """Extract all visual examples."""
    print("Extracting visual examples for PDF-Bench publication...\n")

    # Load full corpus results
    results = load_benchmark_results("full_corpus_353docs.json")

    if not results:
        print("❌ Could not load results/full_corpus_353docs.json")
        return

    print(f"Loaded {len(results.get('results', []))} benchmark results\n")

    # Extract examples
    extract_good_examples(results, n=5)
    extract_bad_examples(results, n=5)
    extract_failure_modes(results)

    # Create index
    create_index()

    print(f"\n✓ All examples saved to {OUTPUT_DIR}")
    print("\nGenerated files:")
    for category in ["good", "bad", "failure_modes"]:
        files = list((OUTPUT_DIR / category).glob("*.md"))
        print(f"  {category}: {len(files)} files")


if __name__ == "__main__":
    main()
