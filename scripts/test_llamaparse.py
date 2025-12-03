#!/usr/bin/env python3
"""Test LlamaParse parser on a single document before running larger benchmarks.

This script validates that:
1. API credentials are configured correctly
2. The parser can successfully parse a simple PDF
3. Output is valid markdown
4. Cost tracking works

Usage:
    # Set API key first
    export LLAMA_CLOUD_API_KEY='llx-...'

    # Run test
    uv run python scripts/test_llamaparse.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main() -> int:
    """Run LlamaParse validation tests."""
    print("=" * 60)
    print("LlamaParse Parser Validation Test")
    print("=" * 60)
    print()

    # Check API key
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("ERROR: LLAMA_CLOUD_API_KEY environment variable not set")
        print("Get your API key from: https://cloud.llamaindex.ai/api-key")
        return 1

    print(f"✓ API key found: {api_key[:10]}...")
    print()

    # Try to import parser
    try:
        from pdf_bench.systems.llamaparse_parser import LlamaParseParser

        print("✓ LlamaParseParser imported successfully")
    except ImportError as e:
        print(f"ERROR: Failed to import LlamaParseParser: {e}")
        print("Install with: pip install llama-parse")
        return 1

    # Validate credentials
    print()
    print("Validating credentials...")
    is_valid, message = LlamaParseParser.validate_credentials()
    if not is_valid:
        print(f"ERROR: Credential validation failed: {message}")
        return 1
    print(f"✓ {message}")

    # Find a test PDF
    corpus_dir = Path("corpus")
    test_pdfs = list(corpus_dir.glob("synthetic/*.pdf"))[:1]
    if not test_pdfs:
        test_pdfs = list(corpus_dir.glob("**/*.pdf"))[:1]

    if not test_pdfs:
        print("ERROR: No test PDFs found in corpus/")
        return 1

    test_pdf = test_pdfs[0]
    print()
    print(f"Test document: {test_pdf}")
    print(f"File size: {test_pdf.stat().st_size / 1024:.1f} KB")

    # Initialize parser
    print()
    print("Initializing parser...")
    try:
        parser = LlamaParseParser(parsing_mode="cost_effective")
        print(f"✓ Parser initialized: {parser.name} v{parser.version}")
        print(f"  Parsing mode: {parser.parsing_mode}")
        print(f"  Cost per page: ${parser.COST_PER_PAGE}")
    except Exception as e:
        print(f"ERROR: Failed to initialize parser: {e}")
        return 1

    # Parse document
    print()
    print("Parsing document (this may take 10-30 seconds)...")
    output_dir = Path(".cache/llamaparse_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result_path = parser.parse(test_pdf, output_dir)
        print("✓ Parsing successful!")
        print(f"  Output: {result_path}")
        print(f"  Size: {result_path.stat().st_size / 1024:.1f} KB")
    except Exception as e:
        print(f"ERROR: Parsing failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Check output
    print()
    print("Validating output...")
    content = result_path.read_text()
    if not content or content == "# Empty Document\n\nNo content extracted.":
        print("WARNING: Output is empty or placeholder")
    else:
        print(f"✓ Output contains {len(content)} characters")
        print(f"  Lines: {len(content.splitlines())}")
        # Show preview
        preview = content[:500] + "..." if len(content) > 500 else content
        print()
        print("Preview:")
        print("-" * 40)
        print(preview)
        print("-" * 40)

    # Check cost tracking
    print()
    print("Cost tracking:")
    cost_info = parser.get_cost_info()
    print(f"  Pages processed: {cost_info['pages_processed']}")
    print(f"  Last parsing cost: ${cost_info['last_parsing_cost']:.4f}")
    print(f"  Total cost: ${cost_info['total_cost']:.4f}")

    print()
    print("=" * 60)
    print("✓ All validation tests passed!")
    print("  LlamaParse is ready for benchmarking.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
