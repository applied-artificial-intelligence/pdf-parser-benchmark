"""Freeze, execute and validate a fixed-population uncached invoice comparison."""

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import platform
import shutil
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from pdf_bench.execution import execute_parser
from pdf_bench.invoice_extraction import extract_invoice
from pdf_bench.invoice_references import POPULATION, validate_reference_bundle
from pdf_bench.invoice_task import aggregate_grades, grade_invoice, task_protocol
from pdf_bench.persistence import write_json_atomic
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter

OUTCOMES = {
    "success_content",
    "success_empty",
    "parser_failure",
    "initialization_failure",
    "enforced_timeout",
    "incompatible",
}
DEFAULT_OPTIONS = {
    "pypdf": {"extraction_mode": "plain"},
    "pdfplumber": {"layout": False, "x_tolerance": 3.0, "y_tolerance": 3.0},
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def runtime_identity() -> dict:
    """Capture installed versions and actual source bytes, including editable PDFsmith."""
    sources = {}
    for package in ["pdfsmith", "pypdf", "pdfplumber", "pdfminer"]:
        spec = importlib.util.find_spec(package)
        if spec is None or spec.origin is None:
            raise ValueError(f"Missing execution dependency: {package}")
        root = Path(spec.origin).parent
        paths = (
            [
                root / name
                for name in [
                    "__init__.py",
                    "api.py",
                    "_inputs.py",
                    "errors.py",
                    "config.py",
                    "backends/__init__.py",
                    "backends/registry.py",
                    "backends/pypdf_backend.py",
                    "backends/pdfplumber_backend.py",
                ]
            ]
            if package == "pdfsmith"
            else sorted(root.rglob("*.py"))
        )
        sources[package] = {path.relative_to(root).as_posix(): digest(path) for path in paths}
    root = Path(__file__).parent
    sources["pdf_bench"] = {
        name: digest(root / name)
        for name in [
            "execution.py",
            "systems/pdfsmith_adapter.py",
            "systems/base_parser.py",
            "invoice_comparison.py",
        ]
    }
    import pdfsmith

    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "logical_cpus": os.cpu_count(),
        "processor": platform.processor(),
        "resources": "No explicit CPU/memory cap; per-attempt enforced wall deadline",
        "pdfsmith_distribution": importlib.metadata.version("pdfsmith"),
        "pdfsmith_source_version": pdfsmith.__version__,
        "installed_distributions": dict(
            sorted(
                (dist.metadata["Name"], dist.version) for dist in importlib.metadata.distributions()
            )
        ),
        "source_files": sources,
        "backend_dependencies": {
            name: importlib.metadata.version(name)
            for name in [
                "pypdf",
                "pdfplumber",
                "pdfminer.six",
                "pillow",
                "pypdfium2",
                "charset-normalizer",
                "cryptography",
                "cffi",
                "pycparser",
            ]
        },
    }


def implementation_identity(environment: dict) -> str:
    return identity(
        {
            key: environment[key]
            for key in [
                "python",
                "implementation",
                "pdfsmith_distribution",
                "pdfsmith_source_version",
                "source_files",
                "backend_dependencies",
            ]
        }
    )


def _verify_files(directory: Path, files: dict) -> None:
    for name, expected in files.items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory.resolve()) or digest(path) != expected:
            raise ValueError(f"Artifact hash/location mismatch: {name}")


def _task_matches(protocol: dict) -> None:
    if any(protocol.get(key) != value for key, value in task_protocol().items()):
        raise ValueError("Frozen task protocol does not match the current extractor/grader")


def freeze_plan(
    qualified: Path,
    protocol_path: Path,
    output: Path,
    *,
    document_ids: list[str] | None = None,
    timeout_seconds: float = 60,
    pipeline_options: dict[str, dict] | None = None,
) -> Path:
    """Publish the population and backend options before any backend initialization."""
    reference_manifest = validate_reference_bundle(qualified, require_qualified=True)
    ids = list(POPULATION) if document_ids is None else document_ids
    if not ids or len(set(ids)) != len(ids) or not set(ids) <= set(POPULATION):
        raise ValueError("Invalid invoice plan population")
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("Invalid attempt timeout")
    protocol = read_json(protocol_path)
    _task_matches(protocol)
    environment = runtime_identity()
    output.mkdir(parents=True, exist_ok=False)
    documents, files = [], {}
    for doc_id in ids:
        row = next(row for row in reference_manifest["documents"] if row["document_id"] == doc_id)
        for name in [f"inputs/{doc_id}.pdf", f"references/{doc_id}.json"]:
            target = output / name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(qualified / name, target)
            files[name] = digest(target)
            if files[name] != reference_manifest["files"][name]:
                raise ValueError("Qualified input changed during plan preparation")
        documents.append(
            {
                key: row[key]
                for key in [
                    "document_id",
                    "pdf_sha256",
                    "reference_sha256",
                    "source_sha256",
                    "template_style",
                    "complexity",
                    "eligibility",
                ]
            }
        )
    shutil.copyfile(protocol_path, output / "task-protocol.json")
    write_json_atomic(output / "environment.json", environment)
    for name in ["task-protocol.json", "environment.json"]:
        files[name] = digest(output / name)
    pipelines = [
        {
            "pipeline_id": name,
            "options": {
                **DEFAULT_OPTIONS[name],
                **(pipeline_options or {}).get(name, {}),
                "backend_name": name,
                "cache_mode": "bypass",
            },
        }
        for name in ["pypdf", "pdfplumber"]
    ]
    plan = {
        "schema_version": 1,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "scope": "primary" if ids == list(POPULATION) else "mechanism_test",
        "reference_manifest_sha256": digest(qualified / "manifest.json"),
        "task_protocol_sha256": files["task-protocol.json"],
        "runtime_identity": implementation_identity(environment),
        "documents": documents,
        "pipelines": pipelines,
        "timeout_seconds": timeout_seconds,
        "execution": "sequential fresh spawned worker per pair; cache reads/writes disabled",
        "timing": "call/read/retention after backend initialization; wall includes cold startup",
        "parser_denied_read_components": [
            "references",
            "ground_truth",
            "ground_truth_backup",
            "sources",
            "metadata",
        ],
        "planned_pairs": [
            {"document_id": doc_id, "pipeline_id": pipeline["pipeline_id"]}
            for pipeline in pipelines
            for doc_id in ids
        ],
        "files": files,
    }
    write_json_atomic(output / "plan.json", plan)
    validate_plan(output)
    return output


def validate_plan(directory: Path) -> dict:
    plan = read_json(directory / "plan.json")
    _verify_files(directory, plan["files"])
    ids = [row["document_id"] for row in plan["documents"]]
    pipelines = [row["pipeline_id"] for row in plan["pipelines"]]
    expected = [(pipeline, doc_id) for pipeline in pipelines for doc_id in ids]
    actual = [(row["pipeline_id"], row["document_id"]) for row in plan["planned_pairs"]]
    if (
        len(ids) != len(set(ids))
        or len(pipelines) != len(set(pipelines))
        or not ids
        or not pipelines
        or actual != expected
        or len(actual) != len(set(actual))
    ):
        raise ValueError("Plan has duplicate, missing or foreign pairs")
    if not set(ids) <= set(POPULATION) or pipelines != ["pypdf", "pdfplumber"]:
        raise ValueError("Unsupported invoice document/pipeline identity")
    if plan["scope"] == "primary" and (ids != list(POPULATION) or len(actual) != 200):
        raise ValueError("Primary invoice plan must contain exactly 200 unique pairs")
    required = {"task-protocol.json", "environment.json"}
    for row in plan["documents"]:
        doc_id = row["document_id"]
        for name, key in [
            (f"inputs/{doc_id}.pdf", "pdf_sha256"),
            (f"references/{doc_id}.json", "reference_sha256"),
        ]:
            required.add(name)
            if plan["files"].get(name) != row[key] or row["eligibility"] != "eligible":
                raise ValueError("Plan does not bind qualified input/reference bytes")
    if not required <= set(plan["files"]):
        raise ValueError("Plan is missing required artifacts")
    if plan["task_protocol_sha256"] != digest(directory / "task-protocol.json") or plan[
        "runtime_identity"
    ] != implementation_identity(read_json(directory / "environment.json")):
        raise ValueError("Plan protocol/runtime identity mismatch")
    return plan


def stage_identities(
    pair: dict, plan: dict, output_hash: str | None, prediction_hash: str, reference_hash: str
) -> dict:
    pipeline = next(p for p in plan["pipelines"] if p["pipeline_id"] == pair["pipeline_id"])
    document = next(d for d in plan["documents"] if d["document_id"] == pair["document_id"])
    raw = identity(
        {
            "input": document["pdf_sha256"],
            "pipeline": pipeline,
            "runtime": plan["runtime_identity"],
            "timeout": plan["timeout_seconds"],
        }
    )
    return {
        "parse": raw,
        "prediction": identity(
            {"parse": raw, "output": output_hash, "extractor": pair["extractor_sha256"]}
        ),
        "grade": identity(
            {
                "prediction": prediction_hash,
                "reference": reference_hash,
                "grader": pair["grader_sha256"],
            }
        ),
    }


def summarize(plan: dict, rows: list[dict], grades: dict[str, dict | None]) -> dict:
    expected = [(p["pipeline_id"], p["document_id"]) for p in plan["planned_pairs"]]
    actual = [(r["pipeline_id"], r["document_id"]) for r in rows]
    if actual != expected or len(set(actual)) != len(actual):
        raise ValueError("Incomplete execution or duplicate/foreign terminal pairs")
    result = {}
    ids = [d["document_id"] for d in plan["documents"]]
    for pipeline in plan["pipelines"]:
        name = pipeline["pipeline_id"]
        selected = [r for r in rows if r["pipeline_id"] == name]
        counts = {
            outcome: [r["document_id"] for r in selected if r["outcome"] == outcome]
            for outcome in sorted(OUTCOMES)
        }
        result[name] = {
            "planned_ids": ids,
            "reference_eligible_ids": ids,
            "attempted_ids": [r["document_id"] for r in selected if r["worker_pid"] is not None],
            "terminal_ids": [r["document_id"] for r in selected],
            "incomplete_ids": [],
            "outcome_ids": counts,
            "counts": {
                **{key: len(value) for key, value in counts.items()},
                "planned": len(ids),
                "reference_eligible": len(ids),
                "scored": sum(grades[r["pair_id"]] is not None for r in selected),
            },
            "task": aggregate_grades(
                {r["document_id"]: grades[r["pair_id"]] for r in selected}, ids
            ),
        }
    result["common_content_ids"] = [
        doc_id
        for doc_id in ids
        if all(
            any(
                r["document_id"] == doc_id
                and r["pipeline_id"] == p["pipeline_id"]
                and r["outcome"] == "success_content"
                for r in rows
            )
            for p in plan["pipelines"]
        )
    ]
    return result


def execute_plan(plan_dir: Path, output: Path) -> Path:
    plan = validate_plan(plan_dir)
    protocol = read_json(plan_dir / "task-protocol.json")
    _task_matches(protocol)
    if implementation_identity(runtime_identity()) != plan["runtime_identity"]:
        raise ValueError("Execution runtime differs from the frozen plan")
    output.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex
    staging, final = output / f".incomplete-{run_id}", output / f"run-{run_id}"
    staging.mkdir()
    shutil.copytree(plan_dir, staging / "frozen-plan")
    rows, grades = [], {}
    write_json_atomic(staging / "journal.json", {"status": "incomplete", "attempts": rows})
    started = time.perf_counter()
    for index, pair in enumerate(plan["planned_pairs"]):
        pair_id = f"{pair['pipeline_id']}--{pair['document_id']}"
        directory = staging / "attempts" / pair_id
        pipeline = next(p for p in plan["pipelines"] if p["pipeline_id"] == pair["pipeline_id"])
        attempt = execute_parser(
            PdfsmithAdapter,
            pipeline["options"],
            staging / "frozen-plan/inputs" / f"{pair['document_id']}.pdf",
            directory,
            plan["timeout_seconds"],
            denied_read_components=tuple(plan["parser_denied_read_components"]),
        )
        row = {**pair, "pair_id": pair_id, "order": index, **asdict(attempt)}
        row["output_path"] = (
            attempt.output_path.relative_to(staging).as_posix()
            if attempt.output_path is not None
            else None
        )
        # The backend's temporary absolute return path is diagnostic only and not a dependency.
        row["returned_path"] = (
            Path(attempt.returned_path).relative_to(staging).as_posix()
            if attempt.returned_path
            else None
        )
        row["extractor_sha256"] = protocol["extractor_sha256"]
        row["grader_sha256"] = protocol["grader_sha256"]
        write_json_atomic(directory / "attempt.json", row)
        rows.append(row)
        write_json_atomic(staging / "journal.json", {"status": "incomplete", "attempts": rows})
    if implementation_identity(runtime_identity()) != plan["runtime_identity"]:
        raise ValueError("Execution implementation changed during the run")
    # Parsing finishes before prediction or reference loading begins.
    for row in rows:
        directory = staging / "attempts" / row["pair_id"]
        error = None
        try:
            raw = (staging / row["output_path"]).read_bytes() if row["output_path"] else b""
            prediction = extract_invoice(raw.decode("utf-8"))
            write_json_atomic(directory / "prediction.json", prediction)
        except Exception as exception:
            error = {
                "stage": "prediction",
                "type": type(exception).__name__,
                "error": str(exception),
            }
            prediction = None
            write_json_atomic(directory / "prediction.json", {"evaluation_error": error})
        reference = read_json(staging / "frozen-plan/references" / f"{row['document_id']}.json")
        try:
            grade = grade_invoice(prediction, reference) if prediction is not None else None
        except Exception as exception:
            error = {"stage": "grading", "type": type(exception).__name__, "error": str(exception)}
            grade = None
        write_json_atomic(directory / "grade.json", {"grade": grade, "evaluation_error": error})
        grades[row["pair_id"]] = grade
        row["stage_identities"] = stage_identities(
            row,
            plan,
            row["output_sha256"],
            digest(directory / "prediction.json"),
            digest(staging / "frozen-plan/references" / f"{row['document_id']}.json"),
        )
        write_json_atomic(directory / "attempt.json", row)
    write_json_atomic(staging / "journal.json", {"status": "terminal", "attempts": rows})
    summary = summarize(plan, rows, grades)
    write_json_atomic(staging / "summary.json", summary)
    files = {
        p.relative_to(staging).as_posix(): digest(p)
        for p in sorted(staging.rglob("*"))
        if p.is_file()
    }
    manifest = {
        "status": "complete",
        "run_id": run_id,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "plan_sha256": digest(staging / "frozen-plan/plan.json"),
        "total_wall_seconds": time.perf_counter() - started,
        "files": files,
    }
    write_json_atomic(staging / "completion.json", manifest)
    validate_run(staging)
    staging.rename(final)
    write_json_atomic(
        output / "latest.json",
        {
            "bundle": final.name,
            "completion_sha256": digest(final / "completion.json"),
        },
    )
    return final


def validate_run(directory: Path) -> dict:
    completion = read_json(directory / "completion.json")
    if completion["status"] != "complete":
        raise ValueError("Run is incomplete")
    _verify_files(directory, completion["files"])
    plan = validate_plan(directory / "frozen-plan")
    if digest(directory / "frozen-plan/plan.json") != completion["plan_sha256"]:
        raise ValueError("Completed plan identity mismatch")
    rows = read_json(directory / "journal.json")["attempts"]
    required = {"frozen-plan/plan.json", "journal.json", "summary.json"}
    required.update(f"frozen-plan/{name}" for name in plan["files"])
    grades = {}
    for row in rows:
        pair_id = f"{row['pipeline_id']}--{row['document_id']}"
        if row["pair_id"] != pair_id or row["outcome"] not in OUTCOMES:
            raise ValueError("Invalid terminal identity/outcome")
        protocol = read_json(directory / "frozen-plan/task-protocol.json")
        if any(row[key] != protocol[key] for key in ["extractor_sha256", "grader_sha256"]):
            raise ValueError("Attempt does not use the frozen task protocol")
        base = f"attempts/{pair_id}"
        required.update(f"{base}/{name}.json" for name in ["attempt", "prediction", "grade"])
        if read_json(directory / base / "attempt.json") != row:
            raise ValueError("Journal/terminal record disagreement")
        if row["outcome"] in {"success_content", "success_empty"}:
            expected_output = f"{base}/retained-output.md"
            required.add(expected_output)
            if (
                row["output_path"] != expected_output
                or completion["files"].get(expected_output) != row["output_sha256"]
            ):
                raise ValueError("Success lacks exact retained output")
            content = (directory / expected_output).read_text()
            if bool(content.strip()) != (row["outcome"] == "success_content"):
                raise ValueError("Empty/content outcome disagrees with returned bytes")
        elif row["output_path"] is not None or row["output_sha256"] is not None:
            raise ValueError("Failed parser claims successful output")
        duration = row["parse_time_seconds"]
        if (
            duration is not None
            and (
                not math.isfinite(duration) or duration <= 0 or duration > row["wall_time_seconds"]
            )
            or not math.isfinite(row["wall_time_seconds"])
            or row["wall_time_seconds"] <= 0
        ):
            raise ValueError("Invalid recorded timing")
        if (
            row["outcome"] == "enforced_timeout"
            and row["error_type"] != "EnforcedParseTimeoutError"
        ):
            raise ValueError("Timeout lacks actual enforcement evidence")
        expected_stages = stage_identities(
            row,
            plan,
            row["output_sha256"],
            digest(directory / base / "prediction.json"),
            digest(directory / "frozen-plan/references" / f"{row['document_id']}.json"),
        )
        if row["stage_identities"] != expected_stages:
            raise ValueError("Stage identity mismatch")
        grades[pair_id] = read_json(directory / base / "grade.json")["grade"]
    if not required <= set(completion["files"]):
        raise ValueError("Completion manifest is missing required artifacts")
    summary = summarize(plan, rows, grades)
    if read_json(directory / "summary.json") != summary:
        raise ValueError("Summary differs from its fixed-population terminal records")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    freeze = commands.add_parser("freeze")
    freeze.add_argument("qualified", type=Path)
    freeze.add_argument("protocol", type=Path)
    freeze.add_argument("output", type=Path)
    freeze.add_argument("--timeout", type=float, default=60)
    run = commands.add_parser("run")
    run.add_argument("plan", type=Path)
    run.add_argument("output", type=Path)
    check = commands.add_parser("validate")
    check.add_argument("bundle", type=Path)
    args = parser.parse_args()
    if args.command == "freeze":
        print(freeze_plan(args.qualified, args.protocol, args.output, timeout_seconds=args.timeout))
    elif args.command == "run":
        print(execute_plan(args.plan, args.output))
    else:
        print(json.dumps(validate_run(args.bundle), indent=2))


if __name__ == "__main__":
    main()
