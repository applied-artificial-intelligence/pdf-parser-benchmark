"""Hash-based disk-backed caching system for parser outputs.

This module provides a caching layer for PDF parser outputs to prevent redundant
parsing during benchmarking runs. The cache uses SHA256-based keys derived from
PDF content and parser identity, ensuring deterministic and collision-resistant
caching.

Cache Storage Structure:
    .cache/
    ├── marker/
    │   ├── abc123def456.md
    │   └── metadata.json
    ├── pymupdf/
    │   └── abc123def456.md
    └── cache_stats.json

The cache is designed to be:
- Thread-safe for statistics updates
- Resilient to filesystem errors
- Transparent to users (failures don't break benchmarking)

Examples:
    >>> from pathlib import Path
    >>> cache_dir = Path(".cache")
    >>> pdf_path = Path("document.pdf")
    >>>
    >>> # Generate cache key
    >>> key = cache_key(pdf_path, "marker", "0.2.0")
    >>>
    >>> # Check for cached result
    >>> cached = get_cached(key, cache_dir)
    >>> if cached is None:
    ...     # Parse and store
    ...     result = parse_pdf(pdf_path)
    ...     stored = store_cached(key, result, cache_dir)
    >>>
    >>> # Get statistics
    >>> stats = get_cache_stats(cache_dir)
    >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
"""

import hashlib
import json
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

# Thread lock for statistics file updates
_stats_lock = threading.Lock()

# Default cache directory
DEFAULT_CACHE_DIR = Path(".cache")

# Statistics file name
STATS_FILE = "cache_stats.json"


def _hash_file(file_path: Path) -> str:
    """Compute SHA256 hash of a file.

    Args:
        file_path: Path to file to hash.

    Returns:
        Hexadecimal string representation of SHA256 hash.

    Raises:
        FileNotFoundError: If file does not exist.
        PermissionError: If file is not readable.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in 64KB chunks to handle large files efficiently
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def cache_key(pdf_path: Path, parser_name: str, parser_version: str) -> str:
    """Generate unique cache key from PDF and parser identity.

    The cache key is deterministic and based on:
    1. PDF content hash (SHA256)
    2. Parser name (lowercase)
    3. Parser version

    Format: {parser_name}-{parser_version}-{pdf_hash[:16]}

    Args:
        pdf_path: Path to PDF file.
        parser_name: Parser identifier (e.g., 'marker', 'pymupdf').
        parser_version: Parser version string (e.g., '0.2.0').

    Returns:
        Cache key string, filesystem-safe and unique.

    Raises:
        FileNotFoundError: If PDF file does not exist.
        PermissionError: If PDF file is not readable.

    Examples:
        >>> pdf = Path("document.pdf")
        >>> key = cache_key(pdf, "marker", "0.2.0")
        >>> key
        'marker-0.2.0-a1b2c3d4e5f6g7h8'
    """
    pdf_hash = _hash_file(pdf_path)
    # Use first 16 characters of hash for brevity
    return f"{parser_name.lower()}-{parser_version}-{pdf_hash[:16]}"


def _get_parser_cache_dir(cache_dir: Path, cache_key_str: str) -> Path:
    """Extract parser name from cache key and return parser cache directory.

    Args:
        cache_dir: Root cache directory.
        cache_key_str: Cache key string.

    Returns:
        Path to parser-specific cache directory.
    """
    # Extract parser name from cache key (first component before first dash)
    parser_name = cache_key_str.split("-")[0]
    return cache_dir / parser_name


def _load_stats(cache_dir: Path) -> dict[str, Any]:
    """Load cache statistics from disk.

    Args:
        cache_dir: Root cache directory.

    Returns:
        Statistics dictionary. Returns default empty stats if file doesn't exist
        or is corrupted.
    """
    stats_file = cache_dir / STATS_FILE

    if not stats_file.exists():
        return {
            "total_hits": 0,
            "total_misses": 0,
            "parsers": {},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    try:
        with open(stats_file, encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
            return data
    except (json.JSONDecodeError, OSError):
        # Corrupted stats file - return default
        return {
            "total_hits": 0,
            "total_misses": 0,
            "parsers": {},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }


def _save_stats(cache_dir: Path, stats: dict[str, Any]) -> None:
    """Save cache statistics to disk.

    Args:
        cache_dir: Root cache directory.
        stats: Statistics dictionary to save.
    """
    stats_file = cache_dir / STATS_FILE
    stats["last_updated"] = datetime.now(timezone.utc).isoformat()

    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except OSError:
        # Failed to save stats - non-critical, just log and continue
        pass


def _update_stats(
    cache_dir: Path,
    parser_name: str,
    is_hit: bool,
    entry_size: int | None = None,
) -> None:
    """Update cache statistics atomically.

    Args:
        cache_dir: Root cache directory.
        parser_name: Parser name for per-parser stats.
        is_hit: True for cache hit, False for cache miss.
        entry_size: Size of cache entry in bytes (for misses/stores only).
    """
    with _stats_lock:
        stats = _load_stats(cache_dir)

        # Update global counts
        if is_hit:
            stats["total_hits"] += 1
        else:
            stats["total_misses"] += 1

        # Update per-parser stats
        if parser_name not in stats["parsers"]:
            stats["parsers"][parser_name] = {
                "hits": 0,
                "misses": 0,
                "entries": 0,
                "total_size_bytes": 0,
            }

        parser_stats = stats["parsers"][parser_name]
        if is_hit:
            parser_stats["hits"] += 1
        else:
            parser_stats["misses"] += 1

        if entry_size is not None:
            parser_stats["total_size_bytes"] += entry_size

        _save_stats(cache_dir, stats)


def _calculate_dir_size(directory: Path) -> int:
    """Calculate total size of all files in directory recursively.

    Args:
        directory: Directory to measure.

    Returns:
        Total size in bytes.
    """
    total_size = 0
    try:
        for item in directory.rglob("*"):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except OSError:
                    # Skip files we can't stat
                    continue
    except OSError:
        # Directory doesn't exist or not accessible
        pass
    return total_size


def _count_entries(parser_cache_dir: Path) -> int:
    """Count markdown files in parser cache directory.

    Args:
        parser_cache_dir: Parser-specific cache directory.

    Returns:
        Number of .md files.
    """
    if not parser_cache_dir.exists():
        return 0

    try:
        return len(list(parser_cache_dir.glob("*.md")))
    except OSError:
        return 0


def get_cached(cache_key_str: str, cache_dir: Path = DEFAULT_CACHE_DIR) -> Path | None:
    """Check if cached output exists and return path if found.

    This function updates cache statistics (hit/miss tracking).

    Args:
        cache_key_str: Cache key from cache_key().
        cache_dir: Root cache directory. Defaults to .cache/

    Returns:
        Path to cached markdown file if exists, None otherwise.

    Examples:
        >>> cached = get_cached("marker-0.2.0-a1b2c3d4", Path(".cache"))
        >>> if cached:
        ...     print(f"Cache hit: {cached}")
        ... else:
        ...     print("Cache miss")
    """
    parser_cache_dir = _get_parser_cache_dir(cache_dir, cache_key_str)
    cached_file = parser_cache_dir / f"{cache_key_str}.md"

    parser_name = cache_key_str.split("-")[0]

    if cached_file.exists() and cached_file.is_file():
        _update_stats(cache_dir, parser_name, is_hit=True)
        return cached_file
    else:
        _update_stats(cache_dir, parser_name, is_hit=False)
        return None


def store_cached(
    cache_key_str: str,
    markdown_path: Path,
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> Path:
    """Store markdown file in cache.

    Copies the markdown file to the appropriate cache location based on the
    cache key. Creates directories as needed.

    Note: This function does not update hit/miss statistics. Statistics should
    be updated by get_cached() when checking for cache existence.

    Args:
        cache_key_str: Cache key from cache_key().
        markdown_path: Path to markdown file to cache.
        cache_dir: Root cache directory. Defaults to .cache/

    Returns:
        Path to stored cache file.

    Raises:
        FileNotFoundError: If markdown_path does not exist.
        PermissionError: If cache directory is not writable.
        OSError: If copy operation fails.

    Examples:
        >>> result = Path("output.md")
        >>> cached = store_cached("marker-0.2.0-a1b2c3d4", result, Path(".cache"))
        >>> cached
        PosixPath('.cache/marker/marker-0.2.0-a1b2c3d4.md')
    """
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    parser_cache_dir = _get_parser_cache_dir(cache_dir, cache_key_str)
    parser_cache_dir.mkdir(parents=True, exist_ok=True)

    cached_file = parser_cache_dir / f"{cache_key_str}.md"

    # Copy the file to cache
    shutil.copy2(markdown_path, cached_file)

    # Note: Statistics are not updated here. The caller should have called
    # get_cached() first, which tracks the miss. We only track the file size
    # in the statistics structure.
    file_size = cached_file.stat().st_size
    parser_name = cache_key_str.split("-")[0]

    with _stats_lock:
        stats = _load_stats(cache_dir)
        if parser_name not in stats["parsers"]:
            stats["parsers"][parser_name] = {
                "hits": 0,
                "misses": 0,
                "entries": 0,
                "total_size_bytes": 0,
            }
        # Update size but not hit/miss counts (those are tracked by get_cached)
        stats["parsers"][parser_name]["total_size_bytes"] += file_size
        _save_stats(cache_dir, stats)

    return cached_file


def get_cache_stats(cache_dir: Path = DEFAULT_CACHE_DIR) -> dict[str, Any]:
    """Get cache statistics including hit/miss rates and sizes.

    Returns comprehensive statistics about cache usage, including per-parser
    breakdowns. Note that size calculations are performed on-demand for accuracy.

    Args:
        cache_dir: Root cache directory. Defaults to .cache/

    Returns:
        Dictionary containing:
        - total_hits: Total number of cache hits
        - total_misses: Total number of cache misses
        - hit_rate: Hit rate as float (0.0-1.0)
        - parsers: Per-parser statistics with hits, misses, entries, size
        - last_updated: ISO timestamp of last statistics update

    Examples:
        >>> stats = get_cache_stats()
        >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
        >>> for parser, data in stats['parsers'].items():
        ...     print(f"{parser}: {data['entries']} entries")
    """
    with _stats_lock:
        stats = _load_stats(cache_dir)

        # Calculate hit rate
        total = stats["total_hits"] + stats["total_misses"]
        stats["hit_rate"] = stats["total_hits"] / total if total > 0 else 0.0

        # Discover parsers from filesystem (in case files were created manually)
        if cache_dir.exists():
            for parser_dir in cache_dir.iterdir():
                if parser_dir.is_dir() and parser_dir.name != "__pycache__":
                    parser_name = parser_dir.name
                    if parser_name not in stats["parsers"]:
                        stats["parsers"][parser_name] = {
                            "hits": 0,
                            "misses": 0,
                            "entries": 0,
                            "total_size_bytes": 0,
                        }

        # Update per-parser sizes and entry counts (recalculate for accuracy)
        for parser_name in stats["parsers"]:
            parser_cache_dir = cache_dir / parser_name
            stats["parsers"][parser_name]["entries"] = _count_entries(parser_cache_dir)
            stats["parsers"][parser_name]["total_size_bytes"] = _calculate_dir_size(
                parser_cache_dir
            )

        return stats


def clear_cache(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    parser_name: str | None = None,
) -> None:
    """Clear entire cache or specific parser cache.

    This operation removes cached files and updates statistics accordingly.
    Use with caution - this will force re-parsing of documents.

    Args:
        cache_dir: Root cache directory. Defaults to .cache/
        parser_name: If provided, only clear cache for this parser.
                    If None, clear entire cache.

    Examples:
        >>> # Clear all cache
        >>> clear_cache()
        >>>
        >>> # Clear only marker cache
        >>> clear_cache(parser_name="marker")
    """
    with _stats_lock:
        if parser_name is None:
            # Clear entire cache
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)

            # Reset statistics
            stats = {
                "total_hits": 0,
                "total_misses": 0,
                "parsers": {},
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            _save_stats(cache_dir, stats)
        else:
            # Clear specific parser cache
            # parser_name is not None here (checked by else branch)
            assert parser_name is not None
            parser_cache_dir = cache_dir / parser_name.lower()
            if parser_cache_dir.exists():
                shutil.rmtree(parser_cache_dir)

            # Update statistics
            stats = _load_stats(cache_dir)
            parsers = cast(dict[str, Any], stats["parsers"])
            if parser_name in parsers:
                # Keep hit/miss counts but reset entries and size
                parsers[parser_name]["entries"] = 0
                parsers[parser_name]["total_size_bytes"] = 0
            _save_stats(cache_dir, stats)
