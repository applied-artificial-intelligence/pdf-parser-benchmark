#!/usr/bin/env python
"""Simple benchmark runner that bypasses Rich progress bar issues."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

from pdfsmith.backends.registry import BACKEND_REGISTRY

# Document list from benchmark config - use actual paths
DOCS = [
    # Synthetic - 6 docs
    "corpus/synthetic/14_table_financial.pdf",
    "corpus/synthetic/19_list_mixed_types.pdf",
    "corpus/synthetic/21_column_two_column.pdf",
    "corpus/synthetic/24_column_newsletter.pdf",
    "corpus/synthetic/27_mixed_business_report.pdf",
    "corpus/synthetic/32_mixed_comprehensive.pdf",
]

# Parsers to test (using backend classes directly)
PARSERS = {
    "openai_gpt_4o": {"backend": "openai", "model": "gpt-4o"},
    "gemini_2_flash": {"backend": "gemini", "model": "gemini-2.0-flash"},
    "anthropic_sonnet_4_5": {"backend": "anthropic", "model": "claude-sonnet-4-5"},
}


def get_backend_instance(backend_name: str, model: str = None):
    """Get a configured backend instance."""
    info = BACKEND_REGISTRY.get(backend_name)
    if info is None:
        raise ValueError(f"Unknown backend: {backend_name}")

    # Use loader to get class and instantiate with model
    backend_class = info.loader()
    if model:
        return backend_class(model=model)
    return backend_class()


def main():
    results = []
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    checkpoint_path = output_dir / "premium_test.checkpoint.json"
    final_path = output_dir / "premium_test.json"

    total_tasks = len(DOCS) * len(PARSERS)
    completed = 0
    success = 0
    failed = 0

    print(f"Running {total_tasks} tasks ({len(DOCS)} docs × {len(PARSERS)} parsers)")
    print("=" * 60)

    for doc_path in DOCS:
        pdf = Path(doc_path)
        if not pdf.exists():
            print(f"SKIP: {pdf} not found")
            continue

        doc_id = pdf.stem

        for parser_name, parser_config in PARSERS.items():
            completed += 1
            print(f"[{completed}/{total_tasks}] {parser_name} / {doc_id}...", end=" ", flush=True)

            start = time.time()
            try:
                backend = get_backend_instance(parser_config["backend"], parser_config.get("model"))
                md = backend.parse(pdf)
                elapsed = time.time() - start

                results.append(
                    {
                        "document_id": doc_id,
                        "parser_name": parser_name,
                        "success": True,
                        "metrics": {},  # Would compute metrics here if needed
                        "error": None,
                        "parse_time_seconds": elapsed,
                        "output_length": len(md),
                    }
                )
                success += 1
                print(f"SUCCESS ({elapsed:.1f}s, {len(md)} chars)")

            except Exception as e:
                elapsed = time.time() - start
                results.append(
                    {
                        "document_id": doc_id,
                        "parser_name": parser_name,
                        "success": False,
                        "metrics": {},
                        "error": str(e),
                        "parse_time_seconds": elapsed,
                        "output_length": 0,
                    }
                )
                failed += 1
                print(f"FAILED ({elapsed:.1f}s): {e}")

            # Save checkpoint every 5 results
            if completed % 5 == 0:
                save_checkpoint(results, checkpoint_path)
                print(f"  -> Checkpoint saved ({completed} tasks)")

    # Final save
    output = {
        "benchmark": {
            "name": "premium_test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "results": results,
        "summary": {
            "total": completed,
            "success": success,
            "failed": failed,
        },
    }

    save_checkpoint(results, checkpoint_path)
    with open(final_path, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 60)
    print(f"COMPLETED: {success} success, {failed} failed")
    print(f"Results saved to: {final_path}")


def save_checkpoint(results, path):
    output = {
        "benchmark": {
            "name": "premium_gap_fill_21docs",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "results": results,
    }
    with open(path, "w") as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    main()
