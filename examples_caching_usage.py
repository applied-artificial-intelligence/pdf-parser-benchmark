#!/usr/bin/env python3
"""Example usage of the PDF-Bench caching system.

This script demonstrates how parsers should integrate with the caching system
to avoid redundant parsing operations.
"""

from pathlib import Path
from pdf_bench.utils.caching import cache_key, get_cached, store_cached, get_cache_stats


def example_parser_integration() -> None:
    """Demonstrate typical parser integration with caching."""
    # Simulated inputs
    pdf_path = Path("document.pdf")
    parser_name = "marker"
    parser_version = "0.2.0"
    cache_dir = Path(".cache")
    output_dir = Path("output")

    # Step 1: Generate cache key
    key = cache_key(pdf_path, parser_name, parser_version)
    print(f"Cache key: {key}")

    # Step 2: Check for cached result
    cached_result = get_cached(key, cache_dir)

    if cached_result is not None:
        # Cache hit - use cached result
        print(f"Cache hit! Using cached result: {cached_result}")
        markdown_path = cached_result
    else:
        # Cache miss - parse the document
        print("Cache miss. Parsing document...")

        # Simulate parsing (in real code, this would call the parser)
        markdown_path = output_dir / f"{pdf_path.stem}.md"
        # (parsing logic here)
        # markdown_path.write_text(parsed_content)

        # Store result in cache
        print("Storing result in cache...")
        cached_path = store_cached(key, markdown_path, cache_dir)
        print(f"Cached at: {cached_path}")

    # Step 3: Use the result
    print(f"Using markdown from: {markdown_path}")

    # Step 4: View cache statistics
    stats = get_cache_stats(cache_dir)
    print("\nCache Statistics:")
    print(f"  Total hits: {stats['total_hits']}")
    print(f"  Total misses: {stats['total_misses']}")
    print(f"  Hit rate: {stats['hit_rate']:.2%}")
    for parser, data in stats['parsers'].items():
        print(f"\n  {parser}:")
        print(f"    Hits: {data['hits']}")
        print(f"    Misses: {data['misses']}")
        print(f"    Entries: {data['entries']}")
        print(f"    Size: {data['total_size_bytes']:,} bytes")


if __name__ == "__main__":
    example_parser_integration()
