#!/usr/bin/env python3
"""Test frontier model parsers on a single document before running larger benchmarks.

This script validates that API credentials are configured and parsers work correctly.
Run this BEFORE running any paid API benchmarks to avoid wasting money on failures.

Usage:
    # Set API keys first
    export LLAMA_CLOUD_API_KEY='llx-...'
    export GOOGLE_API_KEY='...'
    export OPENAI_API_KEY='sk-...'
    export ANTHROPIC_API_KEY='sk-ant-...'

    # Run test for specific parser
    uv run python scripts/test_frontier_parsers.py llamaparse
    uv run python scripts/test_frontier_parsers.py gemini
    uv run python scripts/test_frontier_parsers.py gpt
    uv run python scripts/test_frontier_parsers.py claude

    # Run all tests
    uv run python scripts/test_frontier_parsers.py all
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()


def find_test_pdf() -> Path:
    """Find a small test PDF in the corpus."""
    corpus_dir = Path("corpus")

    # Prefer synthetic docs (small, simple)
    test_pdfs = list(corpus_dir.glob("synthetic/*.pdf"))[:1]
    if not test_pdfs:
        test_pdfs = list(corpus_dir.glob("business/invoices/pdfs/*.pdf"))[:1]
    if not test_pdfs:
        test_pdfs = list(corpus_dir.glob("**/*.pdf"))[:1]

    if not test_pdfs:
        print("ERROR: No test PDFs found in corpus/")
        sys.exit(1)

    return test_pdfs[0]


def test_llamaparse() -> bool:
    """Test LlamaParse parser."""
    print("\n" + "=" * 60)
    print("Testing LlamaParse")
    print("=" * 60)

    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("SKIP: LLAMA_CLOUD_API_KEY not set")
        print("Get your key from: https://cloud.llamaindex.ai/api-key")
        return False

    try:
        from pdf_bench.systems.llamaparse_parser import LlamaParseParser

        is_valid, msg = LlamaParseParser.validate_credentials()
        if not is_valid:
            print(f"ERROR: {msg}")
            return False

        parser = LlamaParseParser()
        test_pdf = find_test_pdf()
        output_dir = Path(".cache/test_llamaparse")
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Parsing: {test_pdf}")
        result = parser.parse(test_pdf, output_dir)

        content = result.read_text()
        print(f"✓ Success! Output: {len(content)} chars")
        print(f"  Cost: ${parser.last_parsing_cost:.4f}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_gemini() -> bool:
    """Test Gemini parser."""
    print("\n" + "=" * 60)
    print("Testing Gemini (2.5 Flash)")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("SKIP: GOOGLE_API_KEY or GEMINI_API_KEY not set")
        print("Get your key from: https://aistudio.google.com/apikey")
        return False

    try:
        from pdf_bench.systems.gemini_parser import GeminiParser

        is_valid, msg = GeminiParser.validate_credentials()
        if not is_valid:
            print(f"ERROR: {msg}")
            return False

        parser = GeminiParser(model="gemini-2.5-flash")
        test_pdf = find_test_pdf()
        output_dir = Path(".cache/test_gemini")
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Parsing: {test_pdf}")
        result = parser.parse(test_pdf, output_dir)

        content = result.read_text()
        print(f"✓ Success! Output: {len(content)} chars")
        print(f"  Cost: ${parser.last_parsing_cost:.4f}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_gpt() -> bool:
    """Test GPT parser."""
    print("\n" + "=" * 60)
    print("Testing GPT-5-mini")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("SKIP: OPENAI_API_KEY not set")
        print("Get your key from: https://platform.openai.com/api-keys")
        return False

    try:
        from pdf_bench.systems.openai_parser import OpenAIParser

        is_valid, msg = OpenAIParser.validate_credentials()
        if not is_valid:
            print(f"ERROR: {msg}")
            return False

        parser = OpenAIParser(model="gpt-5-mini")
        test_pdf = find_test_pdf()
        output_dir = Path(".cache/test_gpt")
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Parsing: {test_pdf}")
        result = parser.parse(test_pdf, output_dir)

        content = result.read_text()
        print(f"✓ Success! Output: {len(content)} chars")
        print(f"  Cost: ${parser.last_parsing_cost:.4f}")
        return True

    except ImportError:
        print("SKIP: OpenAI parser not implemented yet")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_claude() -> bool:
    """Test Claude parser."""
    print("\n" + "=" * 60)
    print("Testing Claude 3.5 Haiku")
    print("=" * 60)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("SKIP: ANTHROPIC_API_KEY not set")
        print("Get your key from: https://console.anthropic.com/settings/keys")
        return False

    try:
        from pdf_bench.systems.anthropic_parser import AnthropicParser

        is_valid, msg = AnthropicParser.validate_credentials()
        if not is_valid:
            print(f"ERROR: {msg}")
            return False

        parser = AnthropicParser(model="claude-3-5-haiku")
        test_pdf = find_test_pdf()
        output_dir = Path(".cache/test_claude")
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Parsing: {test_pdf}")
        result = parser.parse(test_pdf, output_dir)

        content = result.read_text()
        print(f"✓ Success! Output: {len(content)} chars")
        print(f"  Cost: ${parser.last_parsing_cost:.4f}")
        return True

    except ImportError:
        print("SKIP: Anthropic parser not implemented yet")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> int:
    """Run specified tests."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    target = sys.argv[1].lower()

    results = {}

    if target in ("llamaparse", "all"):
        results["llamaparse"] = test_llamaparse()

    if target in ("gemini", "all"):
        results["gemini"] = test_gemini()

    if target in ("gpt", "openai", "all"):
        results["gpt"] = test_gpt()

    if target in ("claude", "anthropic", "all"):
        results["claude"] = test_claude()

    if not results:
        print(f"Unknown target: {target}")
        print("Options: llamaparse, gemini, gpt, claude, all")
        return 1

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL/SKIP"
        print(f"  {name:15} {status}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
