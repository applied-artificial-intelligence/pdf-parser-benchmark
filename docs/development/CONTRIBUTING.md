# Contributing to PDF-Bench

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/pdf-bench.git
cd pdf-bench
```

2. Install dependencies:
```bash
uv sync --extra dev
```

## Development Tools

PDF-Bench uses modern Python development tools configured in `pyproject.toml`:

### Linting with Ruff

Run linting checks:
```bash
uv run ruff check .
```

Auto-fix issues:
```bash
uv run ruff check . --fix
```

Format code:
```bash
uv run ruff format .
```

### Type Checking with MyPy

Run type checking:
```bash
uv run mypy pdf_bench/
```

### Testing with Pytest

Run tests:
```bash
uv run pytest
```

Run with coverage report:
```bash
uv run pytest --cov=pdf_bench --cov-report=html
```

View coverage report at `htmlcov/index.html`.

## Pre-commit Hooks (Optional)

Pre-commit hooks are **optional** but recommended for consistent code quality.

### Installation

1. Install pre-commit (if not already installed):
```bash
pip install pre-commit
```

2. Install the git hooks:
```bash
pre-commit install
```

### Usage

Once installed, pre-commit will automatically run on `git commit`. You can also run manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

### Manual Alternative

If you prefer not to use pre-commit hooks, simply run the tools manually before committing:

```bash
uv run ruff check . --fix
uv run ruff format .
uv run mypy pdf_bench/
uv run pytest
```

## Code Quality Standards

- **Line length**: 100 characters (enforced by ruff)
- **Type hints**: Required for all function signatures (enforced by mypy)
- **Test coverage**: Aim for >80% coverage
- **Import sorting**: isort-compatible import ordering (enforced by ruff)

## Submitting Changes

1. Ensure all linting and type checks pass
2. Add tests for new functionality
3. Update documentation as needed
4. Submit a pull request with a clear description

## Questions?

Open an issue or reach out to the maintainers.
