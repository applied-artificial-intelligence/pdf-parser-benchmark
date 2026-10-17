"""Freeze public cases, retain real local calls and run pinned native evaluation."""

import argparse
import json
import math
import shutil
import subprocess
import time
import uuid
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from pdf_bench.execution import execute_parser
from pdf_bench.invoice_comparison import (
    DEFAULT_OPTIONS,
    OUTCOMES,
    digest,
    identity,
    implementation_identity,
    read_json,
    runtime_identity,
)
from pdf_bench.persistence import write_json_atomic
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter

METRICS = {"text_content": "content_faithfulness", "table": "grits_trm_composite"}
EVALUATOR_OPTIONS = {
    "enable_rule_based": True,
    "enable_text_similarity": False,
    "enable_teds": False,
    "enable_grits": True,
    "enable_header_accuracy": False,
    "enable_structural_consistency": True,
    "enable_table_record_match": True,
    "enable_table_composite": True,
    "grits_pair_workers": 1,
}


def verify_files(root: Path, files: dict, inputs: bool = True) -> None:
    for name, expected in files.items():
        if not inputs and name.startswith(("inputs/", "frozen-plan/inputs/")):
            continue
        p = (root / name).resolve()
        if not p.is_relative_to(root.resolve()) or not p.is_file() or digest(p) != expected:
            raise ValueError(f"Public comparison artifact changed or missing: {name}")


def freeze(
    selection: Path,
    snapshot: Path,
    objects: Path,
    source_map: Path,
    evaluator_python: Path,
    worker: Path,
    target: Path,
) -> Path:
    """Freeze source bytes and selected upstream annotation rows before any parser call."""
    if target.exists():
        raise ValueError("Public plan destination already exists")
    chosen = read_json(selection)
    if chosen["status"] != "visually_qualified_before_comparison_outputs":
        raise ValueError("Public cases need pre-output visual qualification")
    manifest = read_json(snapshot)
    sources = read_json(source_map)
    rows, source_files = [], {}
    for case in chosen["cases"]:
        case_id = case["group"] + "-" + identity({"path": case["source_path"]})[:12]
        source = Path(sources[case["source_path"]])
        observation = next(
            r for r in chosen["observations"] if r["source_path"] == case["source_path"]
        )
        if digest(source) != observation["source_sha256"]:
            raise ValueError("Selected source differs from visual qualification")
        row = {
            **case,
            "case_id": case_id,
            "input_sha256": digest(source),
            "input": f"inputs/{case_id}.pdf",
            "observed_document_form": observation["observed_document_form"],
        }
        rows.append(row)
        source_files[row["input"]] = source
    if len({r["case_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate public case identity")
    native_identity = json.loads(
        subprocess.check_output(
            [str(evaluator_python.absolute()), "-I", str(worker.resolve()), "--identity"], text=True
        )
    )
    staging = target.parent / (".incomplete-public-plan-" + uuid.uuid4().hex)
    staging.mkdir(parents=True)
    for name, source in source_files.items():
        p = staging / name
        p.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, p)
    for group in sorted({r["group"] for r in rows}):
        annotation = manifest["files"][group + ".jsonl"]
        original = objects / annotation["sha256"]
        if digest(original) != annotation["sha256"]:
            raise ValueError("Original upstream annotations changed")
        paths = {r["source_path"] for r in rows if r["group"] == group}
        lines = [
            line for line in original.read_bytes().splitlines() if json.loads(line)["pdf"] in paths
        ]
        expected = sum(r["annotation_count"] for r in rows if r["group"] == group)
        if len(lines) != expected:
            raise ValueError("Selected native annotations are incomplete")
        directory = staging / "references"
        directory.mkdir(exist_ok=True)
        (directory / (group + ".jsonl")).write_bytes(b"\n".join(lines) + b"\n")
    shutil.copyfile(selection, staging / "selection.json")
    shutil.copyfile(worker, staging / "native-worker.py")
    shutil.copyfile(__file__, staging / "harness.py")
    write_json_atomic(staging / "environment.json", runtime_identity())
    plan = {
        "dataset_revision": manifest["dataset_revision"],
        "code_revision": manifest["code_revision"],
        "cases": rows,
        "pipelines": DEFAULT_OPTIONS,
        "planned_pairs": [
            f"{pipeline}--{r['case_id']}" for r in rows for pipeline in DEFAULT_OPTIONS
        ],
        "runtime_identity": implementation_identity(runtime_identity()),
        "evaluator_environment": native_identity,
        "evaluator_options": EVALUATOR_OPTIONS,
        "metric_protocol": {
            "primary_metrics": METRICS,
            "normalization": "off",
            "table_format": "pinned LiteParseProvider._convert_md_tables_to_html on both pipelines",
            "aggregation": (
                "Unweighted case mean within each dimension; every planned pair retained; "
                "unavailable metrics invalidate aggregate, never silently dropped"
            ),
            "scope": chosen["limits"],
        },
        "timeout_seconds": 120,
        "cache_mode": "bypass",
        "files": {
            p.relative_to(staging).as_posix(): digest(p) for p in staging.rglob("*") if p.is_file()
        },
    }
    write_json_atomic(staging / "plan.json", plan)
    staging.rename(target)
    return target


def validate_plan(root: Path, inputs: bool = True) -> dict:
    plan = read_json(root / "plan.json")
    verify_files(root, plan["files"], inputs)
    expected = [
        f"{pipeline}--{r['case_id']}" for r in plan["cases"] for pipeline in plan["pipelines"]
    ]
    if expected != plan["planned_pairs"] or len(set(expected)) != len(expected):
        raise ValueError("Public frozen population is incomplete or duplicated")
    return plan


def summarize(plan: dict, attempts: list, native: dict) -> dict:
    if [r["pair_id"] for r in attempts] != plan["planned_pairs"]:
        raise ValueError("Public comparison lacks a planned attempt")
    if [r["pair_id"] for r in native["pairs"]] != plan["planned_pairs"]:
        raise ValueError("Native evaluation lacks a planned pair")
    if native["protocol"] != plan["metric_protocol"]:
        raise ValueError("Native score protocol differs from the frozen plan")
    by_pair = {r["pair_id"]: r for r in native["pairs"]}
    output: dict = {}
    for pipeline in plan["pipelines"]:
        output[pipeline] = {}
        for group, metric in METRICS.items():
            selected = [r for r in attempts if r["pipeline_id"] == pipeline and r["group"] == group]
            values, unavailable = [], []
            for row in selected:
                result = by_pair[row["pair_id"]]["result"]
                found = [m["value"] for m in result["metrics"] if m["metric_name"] == metric]
                if not result["success"] or len(found) != 1 or not math.isfinite(found[0]):
                    unavailable.append(row["pair_id"])
                else:
                    values.append(found[0])
            output[pipeline][group] = {
                "metric": metric,
                "planned_pairs": [r["pair_id"] for r in selected],
                "planned_count": len(selected),
                "scored_count": len(values),
                "unavailable_pairs": unavailable,
                "valid": not unavailable,
                "mean": sum(values) / len(selected) if selected and not unavailable else None,
                "outcomes": dict(Counter(r["outcome"] for r in selected)),
            }
    return output


def native_grade(bundle: Path, evaluator_python: Path) -> dict:
    plan = validate_plan(bundle / "frozen-plan", inputs=False)
    worker = bundle / "frozen-plan/native-worker.py"
    result = subprocess.run(
        [str(evaluator_python.absolute()), "-I", str(worker.resolve()), str(bundle.resolve())],
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )
    if result.returncode:
        raise ValueError(f"Native evaluation failed: {result.stderr[-4000:]}")
    payload: dict = json.loads(result.stdout)
    if payload["protocol"] != plan["metric_protocol"]:
        raise ValueError("Changed native metric protocol")
    return payload


def execute(plan_root: Path, output: Path, evaluator_python: Path) -> Path:
    plan_root, output = plan_root.resolve(), output.resolve()
    plan = validate_plan(plan_root)
    if digest(Path(__file__)) != plan["files"]["harness.py"]:
        raise ValueError("Public execution harness differs from frozen code")
    environment = runtime_identity()
    if implementation_identity(environment) != plan["runtime_identity"]:
        raise ValueError("Public parser runtime differs from frozen code")
    output.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex
    bundle = output / (".incomplete-" + run_id)
    bundle.mkdir()
    shutil.copytree(plan_root, bundle / "frozen-plan")
    write_json_atomic(bundle / "execution-environment.json", environment)
    attempts: list[dict] = []
    write_json_atomic(bundle / "journal.json", {"attempts": attempts})
    started = time.perf_counter()
    for case in plan["cases"]:
        for pipeline, options in plan["pipelines"].items():
            pair = f"{pipeline}--{case['case_id']}"
            attempt = execute_parser(
                PdfsmithAdapter,
                {"backend_name": pipeline, "cache_mode": "bypass", **options},
                bundle / "frozen-plan" / case["input"],
                bundle / "attempts" / pair,
                timeout_seconds=plan["timeout_seconds"],
                denied_read_components=("references",),
            )
            row = {
                **asdict(attempt),
                "pair_id": pair,
                "case_id": case["case_id"],
                "upstream_test_id": case["upstream_test_id"],
                "group": case["group"],
                "pipeline_id": pipeline,
                "order_index": len(attempts),
                "input_sha256": case["input_sha256"],
                "options": options,
            }
            row["output_path"] = (
                attempt.output_path.relative_to(bundle).as_posix() if attempt.output_path else None
            )
            attempts.append(row)
            write_json_atomic(bundle / "journal.json", {"attempts": attempts})
    write_json_atomic(
        bundle / "timing.json",
        {
            "sequential_wall_seconds": time.perf_counter() - started,
            "scope": (
                "Parser worker startup, parse, retention and journal writes; "
                "native grading excluded"
            ),
        },
    )
    native = native_grade(bundle, evaluator_python)
    write_json_atomic(bundle / "native-results.json", native)
    write_json_atomic(bundle / "summary.json", summarize(plan, attempts, native))
    if implementation_identity(runtime_identity()) != plan["runtime_identity"]:
        raise ValueError("Public parser implementation changed during execution")
    completion = {
        "plan_sha256": digest(bundle / "frozen-plan/plan.json"),
        "files": {
            p.relative_to(bundle).as_posix(): digest(p)
            for p in bundle.rglob("*")
            if p.is_file() and "parser-output" not in p.parts
        },
    }
    write_json_atomic(bundle / "completion.json", completion)
    validate_run(bundle)
    final = output / ("run-" + run_id)
    bundle.rename(final)
    write_json_atomic(
        output / "latest.json",
        {"bundle": final.name, "completion_sha256": digest(final / "completion.json")},
    )
    return final


def validate_run(bundle: Path, inputs: bool = True) -> dict:
    completion = read_json(bundle / "completion.json")
    verify_files(bundle, completion["files"], inputs)
    plan = validate_plan(bundle / "frozen-plan", inputs)
    if digest(bundle / "frozen-plan/plan.json") != completion["plan_sha256"]:
        raise ValueError("Public completion uses a different plan")
    if (
        implementation_identity(read_json(bundle / "execution-environment.json"))
        != plan["runtime_identity"]
    ):
        raise ValueError("Recorded public parser implementation differs from plan")
    required = {
        "frozen-plan/plan.json",
        "journal.json",
        "execution-environment.json",
        "native-results.json",
        "summary.json",
        "timing.json",
    }
    required.update("frozen-plan/" + name for name in plan["files"])
    attempts = read_json(bundle / "journal.json")["attempts"]
    for index, row in enumerate(attempts):
        if row["outcome"] not in OUTCOMES or row["order_index"] != index:
            raise ValueError("Public terminal outcome or order is invalid")
        case = next(c for c in plan["cases"] if c["case_id"] == row["case_id"])
        if (
            row["group"] != case["group"]
            or row["upstream_test_id"] != case["upstream_test_id"]
            or row["pair_id"] != f"{row['pipeline_id']}--{case['case_id']}"
        ):
            raise ValueError("Public attempt case identity differs from plan")
        if (
            row["input_sha256"] != case["input_sha256"]
            or row["options"] != plan["pipelines"][row["pipeline_id"]]
        ):
            raise ValueError("Public attempt source/configuration identity differs")
        if row["output_path"]:
            required.add(row["output_path"])
            if completion["files"].get(row["output_path"]) != row["output_sha256"]:
                raise ValueError("Public output identity differs")
        elif row["outcome"] in {"success_content", "success_empty"}:
            raise ValueError("Public success has no retained output")
    if required - completion["files"].keys():
        raise ValueError("Public completion omits required artifacts")
    calculated = summarize(plan, attempts, read_json(bundle / "native-results.json"))
    if calculated != read_json(bundle / "summary.json"):
        raise ValueError("Public summary differs from native scores")
    return calculated


def compare_runs(first: Path, second: Path) -> dict:
    left, right = validate_run(first, inputs=False), validate_run(second, inputs=False)
    if digest(first / "frozen-plan/plan.json") != digest(second / "frozen-plan/plan.json"):
        raise ValueError("Public reproductions used different frozen plans")
    if left != right or read_json(first / "native-results.json") != read_json(
        second / "native-results.json"
    ):
        raise ValueError("Public native metrics differ between fresh executions")
    rows = [read_json(p / "journal.json")["attempts"] for p in [first, second]]
    for a, b in zip(*rows, strict=True):
        if any(
            a[key] != b[key]
            for key in ["pair_id", "outcome", "output_sha256", "input_sha256", "options"]
        ):
            raise ValueError("Public fresh attempts differ")
    return {
        "matching_pairs": [r["pair_id"] for r in rows[0]],
        "first_completion_sha256": digest(first / "completion.json"),
        "second_completion_sha256": digest(second / "completion.json"),
        "plan_sha256": digest(first / "frozen-plan/plan.json"),
        "comparison": (
            "Exact outputs, outcomes, configuration and native scores; "
            "duration equality not required"
        ),
    }


def regrade_run(bundle: Path, evaluator_python: Path) -> dict:
    validate_run(bundle, inputs=False)
    actual = native_grade(bundle, evaluator_python)
    if actual != read_json(bundle / "native-results.json"):
        raise ValueError("Offline native regrade differs from retained scores")
    return {
        "pairs_regraded": len(actual["pairs"]),
        "plan_sha256": digest(bundle / "frozen-plan/plan.json"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("freeze")
    for name in [
        "selection",
        "snapshot",
        "objects",
        "source_map",
        "evaluator_python",
        "worker",
        "target",
    ]:
        f.add_argument(name, type=Path)
    r = sub.add_parser("run")
    for name in ["plan_root", "output", "evaluator_python"]:
        r.add_argument(name, type=Path)
    args = vars(parser.parse_args())
    command = args.pop("command")
    print(freeze(**args) if command == "freeze" else execute(**args))
