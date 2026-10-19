#!/usr/bin/env bash
set -euo pipefail
unit_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec uv run --no-project --python 3.13.5 "$unit_dir/reproduce_parsebench_comparison.py" "$@"
