"""Freeze a proportional screening population and reuse identified parser outputs."""

import argparse
import hashlib
import json
import shutil
import tempfile
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from pdf_bench.parsebench_full import digest, interleaved_inputs, retained_attempts
from pdf_bench.persistence import write_json_atomic

SEED = "pdf-bench-parsebench-screen-20261017-v1"


def select_inputs(inputs: list[dict], count: int) -> tuple[list[dict], dict]:
    if not 0 < count <= len(inputs) or len({r["source_path"] for r in inputs}) != len(inputs):
        raise ValueError("Invalid sample size or duplicate population inputs")
    strata = defaultdict(list)
    for row in inputs:
        key = "/".join(
            [
                row["groups"][0],
                row["source_format"],
                "sparse" if row["text_characters"] < 100 else "text",
                "+".join(sorted(set(row["tags"]) & {"easy", "hard", "3d_chart", "need_estimate"}))
                or "unlabelled",
            ]
        )
        strata[key].append(row)
    quotas = {key: count * len(rows) // len(inputs) for key, rows in strata.items()}
    remainder = count - sum(quotas.values())
    order = sorted(strata, key=lambda key: (-(count * len(strata[key]) % len(inputs)), key))
    for key in order[:remainder]:
        quotas[key] += 1
    selected = []
    for key, rows in sorted(strata.items()):
        selected.extend(
            sorted(
                rows, key=lambda r: hashlib.sha256((SEED + r["source_path"]).encode()).hexdigest()
            )[: quotas[key]]
        )
    return interleaved_inputs(selected), {
        key: {"population": len(rows), "selected": quotas[key]}
        for key, rows in sorted(strata.items())
    }


def prepare(unit: Path, count: int = 208) -> dict:
    policy_path = unit / "overnight-policy.json"
    policy = json.loads(policy_path.read_text())
    if policy.get("screening_selection"):
        raise ValueError(
            "Screening plans already frozen; preserve them rather than replacing identities"
        )
    coverage = json.loads((unit / "parsebench-source-coverage.json").read_text())
    inventory = json.loads((unit / "parsebench-inventory.json").read_text())
    selected, strata = select_inputs(coverage["inputs"], count)
    chosen = {r["source_path"]: r["sha256"] for r in selected}
    cases = [c for c in inventory["cases"] if c["source_path"] in chosen]
    dimensions = dict(Counter(c["group"] for c in cases))
    if set(dimensions) != {"chart", "layout", "table", "text_content", "text_formatting"}:
        raise ValueError("Screening population must cover every dimension")
    root = unit / "full-comparison-evidence"
    parents = []
    for job in policy["jobs"]:
        target = root / job["run"]
        if digest(target / "plan.json") != job["plan_sha256"]:
            raise ValueError("Frozen parent plan changed")
        plan = json.loads((target / "plan.json").read_text())
        expected = {r["source_path"]: r["sha256"] for r in plan["inputs"]}
        if any(expected.get(name) != sha for name, sha in chosen.items()):
            raise ValueError("Sample bytes differ from frozen parent population")
        parents.append((job, target, plan, retained_attempts(target, plan)))
    selection = {
        "seed": SEED,
        "method": "Proportional largest-remainder allocation; SHA256 ordering within strata",
        "strata": strata,
        "input_paths": count,
        "population_paths": len(coverage["inputs"]),
        "unique_sha256": len(set(chosen.values())),
        "case_count": len(cases),
        "dimension_cases": dimensions,
        "inputs": selected,
        "coverage_sha256": digest(unit / "parsebench-source-coverage.json"),
        "inventory_sha256": digest(unit / "parsebench-inventory.json"),
        "interpretation": (
            "Initial paired parser screen. Not a full-benchmark leaderboard "
            "or a business-family prevalence estimate."
        ),
        "selection_independence": (
            "Selects by input metadata. Reused outputs require identity and byte validation."
        ),
    }
    selection_path = unit / "parsebench-screening-selection.json"
    write_json_atomic(selection_path, selection)
    jobs, reused = [], {}
    for job, parent, plan, rows in parents:
        target = root / (f"sample-{count}-" + job["backend"] + "-" + uuid.uuid4().hex)
        staging = Path(tempfile.mkdtemp(prefix=".screen-incomplete-", dir=root))
        sample_plan = {
            **plan,
            "protocol": "parsebench-pdfsmith-screen-v1",
            "parent_run": parent.name,
            "parent_plan_sha256": job["plan_sha256"],
            "selection_sha256": digest(selection_path),
            "inputs": [
                {k: row[k] for k in ("source_path", "sha256", "page_count")} for row in selected
            ],
            "case_count": len(cases),
            "dimension_cases": dimensions,
            "full_population_inputs": len(coverage["inputs"]),
            "input_order": "Shared dimension-interleaved frozen screening population",
            "workers": job["workers"],
            "started_at": datetime.now(timezone.utc).isoformat(),
            "harness_sha256": digest(Path(__file__).with_name("parsebench_full.py")),
            "timing_policy": (
                "Reused and new cold API calls have distinct provenance; no latency ranking"
            ),
        }
        write_json_atomic(staging / "plan.json", sample_plan)
        shutil.copyfile(
            Path(__file__).with_name("parsebench_full.py"), staging / "frozen-harness.py"
        )
        (staging / ".gitignore").write_text(
            "attempts/\nnative-references/\nnative-grade-*/details.json\ntiming-pilot*/\nresumptions/\n"
        )
        reused[job["backend"]] = 0
        for source, row in rows.items():
            if source not in chosen:
                continue
            key = hashlib.sha256(source.encode()).hexdigest()[:24]
            directory = staging / "attempts" / key
            directory.mkdir(parents=True)
            copied = {**row, "reused_from": {"run": parent.name, "plan_sha256": job["plan_sha256"]}}
            if row.get("output_path"):
                shutil.copyfile(parent / row["output_path"], directory / "retained-output.md")
                copied["output_path"] = (
                    (directory / "retained-output.md").relative_to(staging).as_posix()
                )
            write_json_atomic(directory / "attempt.json", copied)
            reused[job["backend"]] += 1
        retained_attempts(staging, sample_plan)
        staging.rename(target)
        jobs.append({**job, "run": target.name, "plan_sha256": digest(target / "plan.json")})
    timing_sample = unit / policy["sample"]
    temporary = timing_sample.with_suffix(".json.incomplete")
    temporary.write_text(
        json.dumps(
            [r["source_path"] for r in selected if r["source_format"] == "pdf"][:10], indent=2
        )
        + "\n"
    )
    temporary.replace(timing_sample)
    policy.update(
        {
            "jobs": jobs,
            "screening_selection": selection_path.name,
            "full_population_policy": "Deferred until the screen identifies an unresolved decision",
            "reused_attempts": reused,
        }
    )
    write_json_atomic(policy_path, policy)
    return {
        "inputs": count,
        "cases": len(cases),
        "dimensions": dimensions,
        "reused": reused,
        "new_calls": count * len(jobs) - sum(reused.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--count", type=int, default=208)
    args = parser.parse_args()
    print(json.dumps(prepare(args.unit.resolve(), args.count), indent=2))


if __name__ == "__main__":
    main()
