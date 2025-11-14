# TASK-004: BaseParser Design Decisions

**Task**: Define BaseParser Abstract Class
**Date**: 2025-11-14
**Status**: Completed

## Overview

This document records the architectural decisions made while implementing the BaseParser abstract base class for the PDF-Bench benchmarking system.

## Interface Design

### Final Interface

```python
class BaseParser(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the parser's unique identifier (e.g., 'marker', 'pymupdf')."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the parser's version string (e.g., '0.2.0')."""
        pass

    @abstractmethod
    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output."""
        pass
```

## Key Decisions

### 1. Separate `name` and `version` Properties

**Decision**: Use separate properties instead of a combined "marker-v0.2.0" string.

**Rationale**:
- **Clarity**: Clear separation of concerns
- **Flexibility**: Programmatic access to each component
- **Caching**: Cache key construction needs both components separately: `hash(name + version + pdf_hash + config)`
- **Extensibility**: Easier to version-compare (e.g., "0.2.0" vs "0.3.0")

**Alternatives Considered**:
- Single `name` property returning "parser-version" format
  - Rejected: Less flexible, requires string parsing
- `full_name` property for "parser-version"
  - Rejected: Redundant, can be constructed as f"{name}-{version}"

### 2. Synchronous `parse()` Method

**Decision**: Keep parse() synchronous, not async.

**Rationale**:
- **Simplicity**: Most parsers are synchronous (subprocess, library-based)
- **Consistency**: Uniform interface across all parser types
- **Implementation Freedom**: Commercial API adapters can use async internally, expose sync interface
- **Orchestration**: BenchmarkRunner can handle parallelism at higher level

**Alternatives Considered**:
- Async parse() method
  - Rejected: Adds complexity, doesn't benefit subprocess/library parsers
  - Commercial APIs can still use asyncio internally

### 3. Return `Path` from `parse()`, Not String Content

**Decision**: parse() returns Path to generated Markdown file, not the string content.

**Rationale**:
- **Memory Efficiency**: Large documents don't need to be held in memory
- **Caching Integration**: Caching system stores files on disk, needs paths
- **Explicit I/O**: Clear that file I/O is happening
- **Standard Pattern**: Common pattern in file-processing libraries

**Alternatives Considered**:
- Return Markdown string content
  - Rejected: Memory inefficient, doesn't match caching design
- Return tuple (Path, str)
  - Rejected: Over-engineered, caller can read file if needed

### 4. No Input Validation in Base Class

**Decision**: No validation of pdf_path existence or output_dir writability in BaseParser.

**Rationale**:
- **Flexibility**: Some parsers might work with URLs, streams, or special inputs
- **Implementation Freedom**: Each parser knows its requirements best
- **Simplicity**: Keeps base class minimal
- **Error Handling**: Natural exceptions (FileNotFoundError) from implementations are sufficient

**Alternatives Considered**:
- Validate inputs in base class
  - Rejected: Overly restrictive, limits implementation flexibility

### 5. No Configuration in `parse()` Method

**Decision**: Configuration (API keys, model parameters) passed via constructor, not parse().

**Rationale**:
- **Immutability**: Parser configuration should be stable for a benchmark run
- **Clean Interface**: parse() signature is simple and focused
- **Caching**: Configuration is part of cache key, should be stable
- **Pattern**: Standard pattern in Python (configure at init, use via methods)

**Example**:
```python
# Good: Configuration at construction
parser = AWSTextractParser(api_key="...", region="us-east-1")
result = parser.parse(pdf_path, output_dir)

# Bad: Configuration per-call (not supported)
# result = parser.parse(pdf_path, output_dir, api_key="...")
```

### 6. Properties Are Read-Only (No Setters)

**Decision**: `name` and `version` are read-only properties without setters.

**Rationale**:
- **Immutability**: Parser identity should not change during its lifetime
- **Predictability**: Safer for caching and benchmarking
- **Simplicity**: Less state management complexity

### 7. Minimal Interface for MVP

**Decision**: No optional methods for batch processing, progress callbacks, timeouts, or element extraction.

**Rationale**:
- **YAGNI**: You Aren't Gonna Need It - implement only what's required for MVP
- **Extensibility**: Can add later without breaking changes
- **Simplicity**: Easier to understand and implement
- **Focus**: Core requirement is single-document full-text conversion

**Deferred Features** (for future versions):
- `parse_batch(pdf_paths, output_dir) -> List[Path]`
- Progress callbacks: `parse(pdf_path, output_dir, callback=...)`
- Timeout handling: `parse(pdf_path, output_dir, timeout=...)`
- Element extraction: `extract_tables(pdf_path) -> List[Table]`

## Type Safety

### Strict Type Annotations

All methods and properties have complete type annotations:
- `name: str`
- `version: str`
- `parse(pdf_path: Path, output_dir: Path) -> Path`

This enables:
- mypy strict mode checking
- IDE autocomplete and hints
- Runtime type validation (with type checkers)

### Using `pathlib.Path` Over `str`

**Decision**: Use `pathlib.Path` for all file system paths.

**Rationale**:
- **Type Safety**: Path operations are type-checked
- **Cross-Platform**: Path handles OS differences automatically
- **Modern Python**: Path is the recommended approach (PEP 519)
- **Rich API**: Better than string manipulation

## Documentation Standards

### Google-Style Docstrings

**Decision**: Use Google-style docstrings throughout.

**Example**:
```python
def parse(self, pdf_path: Path, output_dir: Path) -> Path:
    """Parse a PDF file and generate Markdown output.

    Args:
        pdf_path: Path to the input PDF file.
        output_dir: Directory where the output should be saved.

    Returns:
        Path to the generated Markdown file.

    Raises:
        FileNotFoundError: If pdf_path does not exist.
        RuntimeError: If parsing fails.
    """
```

**Rationale**:
- **Readability**: Clean, easy to scan
- **Tooling**: Well-supported by Sphinx, pdoc, etc.
- **Examples**: Can include code examples inline
- **Consistency**: Matches project standards from pyproject.toml

## Error Handling Strategy

### Let Exceptions Propagate

**Decision**: No custom exception hierarchy in BaseParser. Let implementation exceptions bubble up.

**Rationale**:
- **Simplicity**: No exception translation layer
- **Debugging**: Original stack traces preserved
- **Flexibility**: Each parser can define its own exceptions if needed
- **Orchestration**: BenchmarkRunner will handle errors uniformly

**Common Exceptions** (documented in docstrings):
- `FileNotFoundError`: PDF doesn't exist
- `PermissionError`: Output directory not writable
- `RuntimeError`: Generic parsing failures
- Parser-specific exceptions as appropriate

## Testing Strategy

### Comprehensive Unit Tests

Created test suite covering:
1. **Abstract class cannot be instantiated**
2. **Missing implementations fail at instantiation**
3. **Complete implementations work correctly**
4. **Properties are read-only**
5. **Type contracts are enforced**
6. **Various naming and versioning conventions**

Test categories:
- `TestBaseParserAbstractness`: Abstract class behavior
- `TestConcreteParserImplementation`: Valid implementations
- `TestParserInterfaceContract`: Interface contracts
- `TestParserVersioningScenarios`: Version format flexibility
- `TestParserNamingConventions`: Name format flexibility

## Integration Points

### Caching System (TASK-005)

Cache key will be constructed as:
```python
cache_key = f"{parser.name}-{parser.version}-{pdf_hash}-{config_hash}"
```

BaseParser provides `name` and `version` for this purpose.

### BenchmarkRunner (TASK-039)

Runner will:
1. Instantiate parsers
2. Iterate over documents
3. Call `parser.parse(pdf_path, cache_dir)` for each
4. Collect results (paths to Markdown files)
5. Handle exceptions uniformly

### Parser Adapters (TASK-008, TASK-030, etc.)

Each parser adapter will:
```python
class MarkerParser(BaseParser):
    @property
    def name(self) -> str:
        return "marker"

    @property
    def version(self) -> str:
        return "0.2.0"  # From marker.__version__ or CLI

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        # Implementation-specific logic
        # - Validate inputs if needed
        # - Call subprocess/library/API
        # - Save output to output_dir
        # - Return path to generated file
        pass
```

## Future Considerations

### Potential Extensions (v1.0+)

1. **Batch Processing Interface**:
   ```python
   def parse_batch(self, pdf_paths: List[Path], output_dir: Path) -> List[Path]:
       """Parse multiple PDFs in one call (optional optimization)."""
   ```

2. **Capabilities Declaration**:
   ```python
   def supports(self) -> Set[str]:
       """Return set of supported features: {'tables', 'math', 'figures'}."""
   ```

3. **Progress Callbacks**:
   ```python
   def parse(self, pdf_path: Path, output_dir: Path,
             progress_callback: Optional[Callable[[float], None]] = None) -> Path:
       """Optional progress reporting."""
   ```

4. **Timeout Handling**:
   ```python
   def parse(self, pdf_path: Path, output_dir: Path,
             timeout_seconds: Optional[int] = None) -> Path:
       """Optional timeout for long-running documents."""
   ```

These can be added without breaking existing implementations (backward compatible).

## Validation Results

### Acceptance Criteria

- ✅ `pdf_bench/systems/base_parser.py` created
- ✅ Abstract methods defined (`name`, `version`, `parse`)
- ✅ Type hints complete (using `pathlib.Path` and `typing`)
- ✅ Docstrings written (Google-style with examples)
- ✅ Unit tests for interface validation created

### Code Quality

- **Linting**: Passes ruff with line-length=100
- **Type Checking**: Passes mypy strict mode
- **Testing**: Comprehensive test coverage
- **Documentation**: Complete docstrings with examples

## Lessons Learned

1. **Keep It Minimal**: Resist over-engineering. The simplest interface that works is best.
2. **Separation of Concerns**: name/version separation provides more flexibility than initially obvious.
3. **Documentation Matters**: Comprehensive docstrings with examples help future implementers.
4. **Testing Abstract Classes**: Testing that abstract classes properly enforce implementation is critical.

## References

- Implementation Plan: `.claude/work/current/001_pdf_bench_exploration/implementation-plan.md`
- Requirements: `.claude/work/current/001_pdf_bench_exploration/requirements.md`
- Python ABC Documentation: https://docs.python.org/3/library/abc.html
- PEP 519 (pathlib): https://peps.python.org/pep-0519/
