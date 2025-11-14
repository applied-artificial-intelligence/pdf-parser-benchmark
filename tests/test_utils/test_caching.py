"""Unit tests for the caching module.

This module tests all aspects of the hash-based disk-backed caching system,
including cache key generation, cache hit/miss tracking, statistics management,
error handling, and thread safety.
"""

import threading
from pathlib import Path

import pytest

from pdf_bench.utils.caching import (
    cache_key,
    clear_cache,
    get_cache_stats,
    get_cached,
    store_cached,
)


class TestCacheKey:
    """Test cache key generation."""

    def test_cache_key_format(self, tmp_path: Path) -> None:
        """Test that cache key has expected format."""
        # Create a temporary PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        key = cache_key(pdf_file, "marker", "0.2.0")

        # Check format: parser-version-hash[:16]
        parts = key.split("-")
        assert len(parts) == 3
        assert parts[0] == "marker"
        assert parts[1] == "0.2.0"
        assert len(parts[2]) == 16  # First 16 chars of hash

    def test_cache_key_deterministic(self, tmp_path: Path) -> None:
        """Test that cache key is deterministic for same inputs."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        key1 = cache_key(pdf_file, "marker", "0.2.0")
        key2 = cache_key(pdf_file, "marker", "0.2.0")

        assert key1 == key2

    def test_cache_key_different_content(self, tmp_path: Path) -> None:
        """Test that different PDF content produces different keys."""
        pdf1 = tmp_path / "test1.pdf"
        pdf1.write_bytes(b"content 1")

        pdf2 = tmp_path / "test2.pdf"
        pdf2.write_bytes(b"content 2")

        key1 = cache_key(pdf1, "marker", "0.2.0")
        key2 = cache_key(pdf2, "marker", "0.2.0")

        assert key1 != key2

    def test_cache_key_different_parser(self, tmp_path: Path) -> None:
        """Test that different parser names produce different keys."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        key1 = cache_key(pdf_file, "marker", "0.2.0")
        key2 = cache_key(pdf_file, "pymupdf", "0.2.0")

        assert key1 != key2

    def test_cache_key_different_version(self, tmp_path: Path) -> None:
        """Test that different parser versions produce different keys."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        key1 = cache_key(pdf_file, "marker", "0.2.0")
        key2 = cache_key(pdf_file, "marker", "0.3.0")

        assert key1 != key2

    def test_cache_key_lowercase_parser(self, tmp_path: Path) -> None:
        """Test that parser name is normalized to lowercase."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        key1 = cache_key(pdf_file, "MARKER", "0.2.0")
        key2 = cache_key(pdf_file, "marker", "0.2.0")

        assert key1 == key2
        assert "MARKER" not in key1

    def test_cache_key_missing_file(self, tmp_path: Path) -> None:
        """Test that cache_key raises FileNotFoundError for missing file."""
        pdf_file = tmp_path / "nonexistent.pdf"

        with pytest.raises(FileNotFoundError):
            cache_key(pdf_file, "marker", "0.2.0")


class TestGetCached:
    """Test cache retrieval."""

    def test_get_cached_miss(self, tmp_path: Path) -> None:
        """Test cache miss returns None."""
        cache_dir = tmp_path / "cache"
        result = get_cached("marker-0.2.0-abc123def456", cache_dir)

        assert result is None

    def test_get_cached_hit(self, tmp_path: Path) -> None:
        """Test cache hit returns correct path."""
        cache_dir = tmp_path / "cache"
        parser_dir = cache_dir / "marker"
        parser_dir.mkdir(parents=True)

        # Create cached file
        cache_key_str = "marker-0.2.0-abc123def456"
        cached_file = parser_dir / f"{cache_key_str}.md"
        cached_file.write_text("# Cached content")

        result = get_cached(cache_key_str, cache_dir)

        assert result is not None
        assert result == cached_file
        assert result.exists()
        assert result.read_text() == "# Cached content"

    def test_get_cached_updates_hit_stats(self, tmp_path: Path) -> None:
        """Test that cache hit updates statistics."""
        cache_dir = tmp_path / "cache"
        parser_dir = cache_dir / "marker"
        parser_dir.mkdir(parents=True)

        # Create cached file
        cache_key_str = "marker-0.2.0-abc123def456"
        cached_file = parser_dir / f"{cache_key_str}.md"
        cached_file.write_text("# Cached content")

        # Get cached (should be a hit)
        get_cached(cache_key_str, cache_dir)

        # Check statistics
        stats = get_cache_stats(cache_dir)
        assert stats["total_hits"] == 1
        assert stats["total_misses"] == 0
        assert "marker" in stats["parsers"]
        assert stats["parsers"]["marker"]["hits"] == 1
        assert stats["parsers"]["marker"]["misses"] == 0

    def test_get_cached_updates_miss_stats(self, tmp_path: Path) -> None:
        """Test that cache miss updates statistics."""
        cache_dir = tmp_path / "cache"

        # Get cached (should be a miss)
        result = get_cached("marker-0.2.0-abc123def456", cache_dir)

        assert result is None

        # Check statistics
        stats = get_cache_stats(cache_dir)
        assert stats["total_hits"] == 0
        assert stats["total_misses"] == 1
        assert "marker" in stats["parsers"]
        assert stats["parsers"]["marker"]["hits"] == 0
        assert stats["parsers"]["marker"]["misses"] == 1

    def test_get_cached_directory_as_file(self, tmp_path: Path) -> None:
        """Test that directory with cache key name is treated as miss."""
        cache_dir = tmp_path / "cache"
        parser_dir = cache_dir / "marker"
        parser_dir.mkdir(parents=True)

        # Create directory instead of file
        cache_key_str = "marker-0.2.0-abc123def456"
        (parser_dir / f"{cache_key_str}.md").mkdir()

        result = get_cached(cache_key_str, cache_dir)

        assert result is None


class TestStoreCached:
    """Test cache storage."""

    def test_store_cached_creates_file(self, tmp_path: Path) -> None:
        """Test that store_cached creates file in correct location."""
        cache_dir = tmp_path / "cache"
        markdown_file = tmp_path / "output.md"
        markdown_file.write_text("# Test output")

        cache_key_str = "marker-0.2.0-abc123def456"
        result = store_cached(cache_key_str, markdown_file, cache_dir)

        expected_path = cache_dir / "marker" / f"{cache_key_str}.md"
        assert result == expected_path
        assert result.exists()
        assert result.read_text() == "# Test output"

    def test_store_cached_creates_directories(self, tmp_path: Path) -> None:
        """Test that store_cached creates necessary directories."""
        cache_dir = tmp_path / "cache"
        markdown_file = tmp_path / "output.md"
        markdown_file.write_text("# Test output")

        assert not cache_dir.exists()

        cache_key_str = "marker-0.2.0-abc123def456"
        store_cached(cache_key_str, markdown_file, cache_dir)

        assert cache_dir.exists()
        assert (cache_dir / "marker").exists()

    def test_store_cached_preserves_content(self, tmp_path: Path) -> None:
        """Test that stored content matches original."""
        cache_dir = tmp_path / "cache"
        markdown_file = tmp_path / "output.md"
        content = "# Complex Content\n\n- List item 1\n- List item 2\n\n$$E=mc^2$$"
        markdown_file.write_text(content)

        cache_key_str = "marker-0.2.0-abc123def456"
        result = store_cached(cache_key_str, markdown_file, cache_dir)

        assert result.read_text() == content

    def test_store_cached_missing_file(self, tmp_path: Path) -> None:
        """Test that store_cached raises FileNotFoundError for missing file."""
        cache_dir = tmp_path / "cache"
        markdown_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            store_cached("marker-0.2.0-abc123def456", markdown_file, cache_dir)

    def test_store_cached_updates_stats(self, tmp_path: Path) -> None:
        """Test that store_cached creates parser stats entry."""
        cache_dir = tmp_path / "cache"
        markdown_file = tmp_path / "output.md"
        markdown_file.write_text("# Test output")

        cache_key_str = "marker-0.2.0-abc123def456"
        store_cached(cache_key_str, markdown_file, cache_dir)

        stats = get_cache_stats(cache_dir)
        # store_cached doesn't update hit/miss counts (get_cached does that)
        # but it does create parser entry and update size
        assert "marker" in stats["parsers"]
        assert stats["parsers"]["marker"]["total_size_bytes"] > 0
        assert stats["parsers"]["marker"]["entries"] == 1

    def test_store_cached_overwrites_existing(self, tmp_path: Path) -> None:
        """Test that store_cached overwrites existing cache entry."""
        cache_dir = tmp_path / "cache"
        markdown_file = tmp_path / "output.md"
        markdown_file.write_text("# Original content")

        cache_key_str = "marker-0.2.0-abc123def456"
        result1 = store_cached(cache_key_str, markdown_file, cache_dir)

        # Update and store again
        markdown_file.write_text("# Updated content")
        result2 = store_cached(cache_key_str, markdown_file, cache_dir)

        assert result1 == result2
        assert result2.read_text() == "# Updated content"


class TestGetCacheStats:
    """Test cache statistics."""

    def test_get_cache_stats_empty(self, tmp_path: Path) -> None:
        """Test statistics for empty cache."""
        cache_dir = tmp_path / "cache"
        stats = get_cache_stats(cache_dir)

        assert stats["total_hits"] == 0
        assert stats["total_misses"] == 0
        assert stats["hit_rate"] == 0.0
        assert stats["parsers"] == {}
        assert "last_updated" in stats

    def test_get_cache_stats_calculates_hit_rate(self, tmp_path: Path) -> None:
        """Test hit rate calculation."""
        cache_dir = tmp_path / "cache"
        parser_dir = cache_dir / "marker"
        parser_dir.mkdir(parents=True)

        cache_key_str = "marker-0.2.0-abc123def456"
        cached_file = parser_dir / f"{cache_key_str}.md"
        cached_file.write_text("# Content")

        # Generate hits and misses
        get_cached(cache_key_str, cache_dir)  # hit
        get_cached(cache_key_str, cache_dir)  # hit
        get_cached("marker-0.2.0-other123456", cache_dir)  # miss

        stats = get_cache_stats(cache_dir)
        assert stats["total_hits"] == 2
        assert stats["total_misses"] == 1
        assert stats["hit_rate"] == pytest.approx(2 / 3)

    def test_get_cache_stats_multiple_parsers(self, tmp_path: Path) -> None:
        """Test statistics with multiple parsers."""
        cache_dir = tmp_path / "cache"

        # Create cache entries for two parsers
        marker_dir = cache_dir / "marker"
        marker_dir.mkdir(parents=True)
        (marker_dir / "marker-0.2.0-abc123.md").write_text("# Marker")

        pymupdf_dir = cache_dir / "pymupdf"
        pymupdf_dir.mkdir(parents=True)
        (pymupdf_dir / "pymupdf-1.0.0-def456.md").write_text("# PyMuPDF")

        # Generate some hits/misses
        get_cached("marker-0.2.0-abc123", cache_dir)  # hit
        get_cached("pymupdf-1.0.0-def456", cache_dir)  # hit
        get_cached("marker-0.2.0-xyz999", cache_dir)  # miss

        stats = get_cache_stats(cache_dir)
        assert len(stats["parsers"]) == 2
        assert "marker" in stats["parsers"]
        assert "pymupdf" in stats["parsers"]
        assert stats["parsers"]["marker"]["hits"] == 1
        assert stats["parsers"]["marker"]["misses"] == 1
        assert stats["parsers"]["pymupdf"]["hits"] == 1
        assert stats["parsers"]["pymupdf"]["misses"] == 0

    def test_get_cache_stats_counts_entries(self, tmp_path: Path) -> None:
        """Test that statistics correctly count cache entries."""
        cache_dir = tmp_path / "cache"
        parser_dir = cache_dir / "marker"
        parser_dir.mkdir(parents=True)

        # Create multiple cache entries
        (parser_dir / "marker-0.2.0-abc123.md").write_text("# One")
        (parser_dir / "marker-0.2.0-def456.md").write_text("# Two")
        (parser_dir / "marker-0.2.0-ghi789.md").write_text("# Three")

        stats = get_cache_stats(cache_dir)
        assert stats["parsers"]["marker"]["entries"] == 3

    def test_get_cache_stats_calculates_size(self, tmp_path: Path) -> None:
        """Test that statistics calculate total size."""
        cache_dir = tmp_path / "cache"
        parser_dir = cache_dir / "marker"
        parser_dir.mkdir(parents=True)

        content1 = "# " + "A" * 100
        content2 = "# " + "B" * 200

        (parser_dir / "marker-0.2.0-abc123.md").write_text(content1)
        (parser_dir / "marker-0.2.0-def456.md").write_text(content2)

        stats = get_cache_stats(cache_dir)
        expected_size = len(content1.encode()) + len(content2.encode())
        assert stats["parsers"]["marker"]["total_size_bytes"] == expected_size

    def test_get_cache_stats_corrupted_file(self, tmp_path: Path) -> None:
        """Test that corrupted stats file returns default stats."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(parents=True)

        # Create corrupted stats file
        stats_file = cache_dir / "cache_stats.json"
        stats_file.write_text("invalid json {{{")

        stats = get_cache_stats(cache_dir)
        assert stats["total_hits"] == 0
        assert stats["total_misses"] == 0


class TestClearCache:
    """Test cache clearing."""

    def test_clear_cache_all(self, tmp_path: Path) -> None:
        """Test clearing entire cache."""
        cache_dir = tmp_path / "cache"

        # Create cache entries
        marker_dir = cache_dir / "marker"
        marker_dir.mkdir(parents=True)
        (marker_dir / "marker-0.2.0-abc123.md").write_text("# Marker")

        pymupdf_dir = cache_dir / "pymupdf"
        pymupdf_dir.mkdir(parents=True)
        (pymupdf_dir / "pymupdf-1.0.0-def456.md").write_text("# PyMuPDF")

        # Generate some stats
        get_cached("marker-0.2.0-abc123", cache_dir)

        # Clear all
        clear_cache(cache_dir)

        # Check cache is empty
        assert cache_dir.exists()  # Directory itself should exist
        assert not (marker_dir / "marker-0.2.0-abc123.md").exists()
        assert not (pymupdf_dir / "pymupdf-1.0.0-def456.md").exists()

        # Check stats are reset
        stats = get_cache_stats(cache_dir)
        assert stats["total_hits"] == 0
        assert stats["total_misses"] == 0
        assert stats["parsers"] == {}

    def test_clear_cache_specific_parser(self, tmp_path: Path) -> None:
        """Test clearing cache for specific parser."""
        cache_dir = tmp_path / "cache"

        # Create cache entries for two parsers
        marker_dir = cache_dir / "marker"
        marker_dir.mkdir(parents=True)
        (marker_dir / "marker-0.2.0-abc123.md").write_text("# Marker")

        pymupdf_dir = cache_dir / "pymupdf"
        pymupdf_dir.mkdir(parents=True)
        (pymupdf_dir / "pymupdf-1.0.0-def456.md").write_text("# PyMuPDF")

        # Clear only marker
        clear_cache(cache_dir, parser_name="marker")

        # Check marker cache is cleared but pymupdf remains
        assert not (marker_dir / "marker-0.2.0-abc123.md").exists()
        assert (pymupdf_dir / "pymupdf-1.0.0-def456.md").exists()

    def test_clear_cache_updates_stats(self, tmp_path: Path) -> None:
        """Test that clearing cache updates statistics."""
        cache_dir = tmp_path / "cache"
        parser_dir = cache_dir / "marker"
        parser_dir.mkdir(parents=True)
        (parser_dir / "marker-0.2.0-abc123.md").write_text("# Content")

        # Generate stats
        get_cached("marker-0.2.0-abc123", cache_dir)

        # Clear specific parser
        clear_cache(cache_dir, parser_name="marker")

        stats = get_cache_stats(cache_dir)
        # Hit/miss counts preserved
        assert stats["parsers"]["marker"]["hits"] == 1
        # But entries and size reset
        assert stats["parsers"]["marker"]["entries"] == 0
        assert stats["parsers"]["marker"]["total_size_bytes"] == 0

    def test_clear_cache_nonexistent(self, tmp_path: Path) -> None:
        """Test clearing nonexistent cache doesn't error."""
        cache_dir = tmp_path / "cache"

        # Should not raise
        clear_cache(cache_dir)
        clear_cache(cache_dir, parser_name="marker")

    def test_clear_cache_case_insensitive(self, tmp_path: Path) -> None:
        """Test that parser name clearing is case-insensitive."""
        cache_dir = tmp_path / "cache"
        marker_dir = cache_dir / "marker"
        marker_dir.mkdir(parents=True)
        (marker_dir / "marker-0.2.0-abc123.md").write_text("# Content")

        # Clear with uppercase (should work due to lowercase normalization)
        clear_cache(cache_dir, parser_name="MARKER")

        assert not (marker_dir / "marker-0.2.0-abc123.md").exists()


class TestThreadSafety:
    """Test thread safety of caching operations."""

    def test_concurrent_stats_updates(self, tmp_path: Path) -> None:
        """Test that concurrent statistics updates don't corrupt data."""
        cache_dir = tmp_path / "cache"
        parser_dir = cache_dir / "marker"
        parser_dir.mkdir(parents=True)

        cache_key_str = "marker-0.2.0-abc123"
        (parser_dir / f"{cache_key_str}.md").write_text("# Content")

        # Run concurrent cache operations
        def cache_operations() -> None:
            for _ in range(10):
                get_cached(cache_key_str, cache_dir)
                get_cached("marker-0.2.0-miss123", cache_dir)

        threads = [threading.Thread(target=cache_operations) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Check that stats are consistent
        stats = get_cache_stats(cache_dir)
        # 5 threads * 10 iterations * 1 hit each = 50 hits
        assert stats["total_hits"] == 50
        # 5 threads * 10 iterations * 1 miss each = 50 misses
        assert stats["total_misses"] == 50

    def test_concurrent_store_operations(self, tmp_path: Path) -> None:
        """Test that concurrent store operations work correctly."""
        cache_dir = tmp_path / "cache"

        def store_operation(thread_id: int) -> None:
            markdown_file = tmp_path / f"output_{thread_id}.md"
            markdown_file.write_text(f"# Content {thread_id}")
            cache_key_str = f"marker-0.2.0-thread{thread_id}"
            store_cached(cache_key_str, markdown_file, cache_dir)

        threads = [threading.Thread(target=store_operation, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Check that all files were stored
        stats = get_cache_stats(cache_dir)
        assert stats["parsers"]["marker"]["entries"] == 5


class TestEndToEndWorkflow:
    """Test complete caching workflow."""

    def test_full_caching_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow: key generation, miss, store, hit."""
        cache_dir = tmp_path / "cache"

        # Create PDF
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        # Generate cache key
        key = cache_key(pdf_file, "marker", "0.2.0")

        # First access - cache miss
        cached = get_cached(key, cache_dir)
        assert cached is None

        # Simulate parsing and store result
        output_file = tmp_path / "output.md"
        output_file.write_text("# Parsed Content\n\nParagraph")
        stored = store_cached(key, output_file, cache_dir)

        # Second access - cache hit
        cached = get_cached(key, cache_dir)
        assert cached is not None
        assert cached == stored
        assert cached.read_text() == "# Parsed Content\n\nParagraph"

        # Check statistics
        stats = get_cache_stats(cache_dir)
        assert stats["total_hits"] == 1
        assert stats["total_misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["parsers"]["marker"]["entries"] == 1

    def test_version_change_invalidates_cache(self, tmp_path: Path) -> None:
        """Test that changing parser version invalidates cache."""
        cache_dir = tmp_path / "cache"
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        # Store with version 0.2.0
        key_v1 = cache_key(pdf_file, "marker", "0.2.0")
        output_file = tmp_path / "output.md"
        output_file.write_text("# Version 1 output")
        store_cached(key_v1, output_file, cache_dir)

        # Access with version 0.3.0 - should be cache miss
        key_v2 = cache_key(pdf_file, "marker", "0.3.0")
        cached = get_cached(key_v2, cache_dir)
        assert cached is None
        assert key_v1 != key_v2

    def test_multiple_parsers_same_pdf(self, tmp_path: Path) -> None:
        """Test caching same PDF with different parsers."""
        cache_dir = tmp_path / "cache"
        pdf_file = tmp_path / "document.pdf"
        pdf_file.write_bytes(b"fake pdf content")

        # Parse with marker
        key_marker = cache_key(pdf_file, "marker", "0.2.0")
        output_marker = tmp_path / "marker_output.md"
        output_marker.write_text("# Marker output")
        store_cached(key_marker, output_marker, cache_dir)

        # Parse with pymupdf
        key_pymupdf = cache_key(pdf_file, "pymupdf", "1.0.0")
        output_pymupdf = tmp_path / "pymupdf_output.md"
        output_pymupdf.write_text("# PyMuPDF output")
        store_cached(key_pymupdf, output_pymupdf, cache_dir)

        # Both should be cached independently
        assert get_cached(key_marker, cache_dir) is not None
        assert get_cached(key_pymupdf, cache_dir) is not None

        # Statistics should track both
        stats = get_cache_stats(cache_dir)
        assert "marker" in stats["parsers"]
        assert "pymupdf" in stats["parsers"]
        assert stats["parsers"]["marker"]["entries"] == 1
        assert stats["parsers"]["pymupdf"]["entries"] == 1
