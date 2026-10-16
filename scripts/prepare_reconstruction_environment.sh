#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
environment_path="${1:-$repo_dir/.venv}"
artifacts="$repo_dir/.workspace/work/2026-10-13-benchmark-rebuild/invoice-runtime-artifacts-v3"
UV_PROJECT_ENVIRONMENT="$environment_path" uv sync --project "$repo_dir" --python 3.13.5 --extra dev --extra light
uv pip install --python "$environment_path/bin/python" --require-hashes -r "$artifacts/requirements.lock"
uv pip install --python "$environment_path/bin/python" --no-deps "$artifacts/pdfsmith-0.2.0-py3-none-any.whl"
