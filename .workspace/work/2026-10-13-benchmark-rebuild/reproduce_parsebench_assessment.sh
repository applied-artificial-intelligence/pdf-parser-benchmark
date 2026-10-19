#!/usr/bin/env bash
set -euo pipefail
work_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$work_dir/../../.." && pwd)"
cd -- "$repo_dir"
mkdir -p data_exports/parsebench
replay_dir="$(mktemp -d "$repo_dir/data_exports/parsebench/assessment-replay.XXXXXX")"
uv run --no-sync python -m pdf_bench.parsebench acquire \
  --cache data_exports/parsebench/objects --manifest "$replay_dir/snapshot.json"
uv run --no-sync python -m pdf_bench.parsebench inventory \
  --cache data_exports/parsebench/objects --manifest "$replay_dir/snapshot.json" \
  --output "$replay_dir/inventory.json"
uv run --no-sync python "$work_dir/inspect_parsebench_sources.py" \
  --snapshot "$replay_dir/snapshot.json" \
  --selection "$work_dir/parsebench-inspection-selection.json" \
  --output "$replay_dir/inspection.json" --renders "$replay_dir/renders"
uv run --no-sync python - "$work_dir" "$replay_dir" <<'PY'
import json
import sys
from pathlib import Path
from pdf_bench.parsebench import build_assessment
from pdf_bench.persistence import write_json_atomic
work, replay = map(Path, sys.argv[1:])
inventory = json.loads((replay / 'inventory.json').read_text())
artifacts = json.loads((replay / 'inspection.json').read_text())
observations = json.loads((work / 'parsebench-inspection-observations.json').read_text())
assessment = build_assessment(inventory, artifacts, observations)
write_json_atomic(replay / 'assessment.json', assessment)
original = json.loads((work / 'parsebench-inventory.json').read_text())
assert inventory['groups'] == original['groups']
assert inventory['totals'] == original['totals']
assert inventory['cases'] == original['cases']
assert assessment['inspected_inputs'] == 43
print('Inventory and source-bound inspection observations reproduced:', replay)
PY
uv run --no-sync pytest -o addopts= tests/test_parsebench.py -q
