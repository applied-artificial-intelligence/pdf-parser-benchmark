"""Run a declared PDFSmith configuration over the complete public input population."""

import argparse
import hashlib
import json
import uuid
from collections import Counter, deque
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from pdf_bench.execution import execute_parser
from pdf_bench.parsebench_roster import local_roster, runtime_identity
from pdf_bench.persistence import write_json_atomic
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_population(coverage: dict, inventory: dict) -> None:
    expected = {c["source_path"] for c in inventory["cases"]}
    observed = [r["source_path"] for r in coverage["inputs"]]
    if len(observed) != len(set(observed)) or set(observed) != expected:
        raise ValueError("Coverage differs from full annotated source population")


def validate_journal(plan: dict, rows: list[dict]) -> None:
    expected = {r["source_path"]: r["sha256"] for r in plan["inputs"]}
    observed = [r["source_path"] for r in rows]
    if len(observed) != len(set(observed)) or set(observed) != set(expected):
        raise ValueError("Incomplete or duplicate full-population attempts")
    if any(r["input_sha256"] != expected[r["source_path"]] for r in rows):
        raise ValueError("Attempt input identity differs from frozen plan")


def interleaved_inputs(inputs: list[dict]) -> list[dict]:
    queues = {}
    for group in ("chart", "layout", "table", "text_content", "text_formatting"):
        queues[group] = deque(
            sorted(
                (r for r in inputs if group in r["groups"]),
                key=lambda r: hashlib.sha256(r["source_path"].encode()).hexdigest(),
            )
        )
    rows, seen = [], set()
    while any(queues.values()):
        for queue in queues.values():
            while queue:
                row = queue.popleft()
                if row["source_path"] not in seen:
                    seen.add(row["source_path"])
                    rows.append(row)
                    break
    if len(rows) != len(inputs):
        raise ValueError("Interleaving lost input membership")
    return rows


def model_identity(backend: str) -> dict:
    roots = []
    if backend == "docling":
        roots = list((Path.home() / ".cache/huggingface/hub").glob("models--docling*"))
    if backend == "marker":
        roots = [Path.home() / ".cache/pdfsmith/marker"]
    return {
        str(p): digest(p)
        for root in roots
        for p in sorted(root.rglob("*"))
        if p.is_file() and not p.name.endswith(".lock")
    }


def retained_attempts(target: Path, plan: dict) -> dict[str, dict]:
    expected = {r["source_path"]: r["sha256"] for r in plan["inputs"]}
    rows = {}
    for path in sorted((target / "attempts").glob("*/attempt.json")):
        row = json.loads(path.read_text())
        source = row["source_path"]
        if source in rows or row["input_sha256"] != expected.get(source):
            raise ValueError("Duplicate or changed retained input identity")
        if row["outcome"] not in {
            "success_content",
            "success_empty",
            "parser_failure",
            "initialization_failure",
            "enforced_timeout",
        }:
            raise ValueError("Unknown retained terminal outcome")
        if row.get("output_path"):
            output = (target / row["output_path"]).resolve()
            if (
                not output.is_relative_to(target.resolve())
                or digest(output) != row["output_sha256"]
            ):
                raise ValueError("Retained output bytes changed")
        elif row["outcome"].startswith("success"):
            raise ValueError("Successful retained attempt has no output")
        rows[source] = row
    return rows


def resume(
    original: Path,
    workers: int,
    stop_at: datetime,
    sample: list[str] | None = None,
) -> Path:
    """Resume validated attempts; a timing sample has its own outputs and denominator."""
    if workers < 1 or stop_at.tzinfo is None:
        raise ValueError("Positive workers and a timezone-aware stop time are required")
    plan = json.loads((original / "plan.json").read_text())
    backend = plan["backend"]
    from pdfsmith.backends.registry import BACKEND_REGISTRY

    if backend not in BACKEND_REGISTRY or BACKEND_REGISTRY[backend].weight == "commercial":
        raise ValueError("Only registered local backends may resume")
    if runtime_identity() != plan["runtime"]:
        raise ValueError("Runtime differs from frozen plan")
    parser = PdfsmithAdapter(backend, cache_mode="bypass", **plan["options"])
    if getattr(parser._get_backend(), "effective_options", {}) != plan["options"]:
        raise ValueError("Effective options differ from frozen plan")
    for path, sha in plan.get("model_files", {}).items():
        if digest(Path(path)) != sha:
            raise ValueError("Frozen model bytes changed")
    source_root = Path(plan["input_root"])
    for row in plan["inputs"]:
        path = (source_root / row["source_path"]).resolve()
        if not path.is_relative_to(source_root.resolve()) or digest(path) != row["sha256"]:
            raise ValueError("Input bytes differ from frozen plan")
    pilot_name = "timing-pilot" if workers == 1 else f"timing-pilot-w{workers}"
    target = original / pilot_name if sample is not None else original
    rows = retained_attempts(target, plan)
    selected = plan["inputs"]
    if sample is not None:
        by_source = {r["source_path"]: r for r in selected}
        if len(set(sample)) != len(sample) or set(sample) - by_source.keys():
            raise ValueError("Timing sample differs from frozen population")
        selected = [by_source[p] for p in sample]
    if set(rows) - {r["source_path"] for r in selected}:
        raise ValueError("Retained timing sample membership changed")
    session = target / "resumptions" / uuid.uuid4().hex
    session.mkdir(parents=True)
    write_json_atomic(
        session / "plan.json",
        {
            "original_plan_sha256": digest(original / "plan.json"),
            "harness_sha256": digest(Path(__file__)),
            "workers": workers,
            "stop_at": stop_at.isoformat(),
            "retained_attempts": len(rows),
            "timing_sample": sample,
            "initialization_stop_policy": "Stop after three consecutive initialization failures",
            "timing_policy": (
                "Mixed earlier contention and resumed calls; not an isolated latency ranking"
            ),
            "started_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    def execute(row: dict) -> dict:
        key = hashlib.sha256(row["source_path"].encode()).hexdigest()[:24]
        directory = target / "attempts" / (key + "-" + uuid.uuid4().hex)
        attempt = execute_parser(
            PdfsmithAdapter,
            {"backend_name": backend, "cache_mode": "bypass", **plan["options"]},
            source_root / row["source_path"],
            directory,
            timeout_seconds=plan["timeout_seconds"],
            denied_read_components=("references", "qualified-invoice-truth"),
        )
        result = {
            "source_path": row["source_path"],
            "input_sha256": row["sha256"],
            "resume_session": session.name,
            **{k: str(v) if isinstance(v, Path) else v for k, v in asdict(attempt).items()},
        }
        if result["output_path"]:
            result["output_path"] = str(Path(result["output_path"]).relative_to(target.resolve()))
        write_json_atomic(directory / "attempt.json", result)
        return result

    remaining = iter(r for r in selected if r["source_path"] not in rows)
    initialization_failures = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending: set[Future] = set()
        exhausted = False
        while pending or not exhausted:
            while not exhausted and len(pending) < workers:
                # Reserve the entire enforced call deadline and cleanup before the cutoff.
                if (stop_at - datetime.now(timezone.utc)).total_seconds() <= plan[
                    "timeout_seconds"
                ] + 60:
                    exhausted = True
                    break
                row = next(remaining, None)
                if row is None:
                    exhausted = True
                    break
                pending.add(executor.submit(execute, row))
            if pending:
                finished, pending = wait(pending, return_when=FIRST_COMPLETED)
                for future in finished:
                    row = future.result()
                    rows[row["source_path"]] = row
                    initialization_failures = (
                        initialization_failures + 1
                        if row["outcome"] == "initialization_failure"
                        else 0
                    )
                    if initialization_failures >= 3:
                        raise RuntimeError(
                            "Repeated initialization failures; remaining inputs unstarted"
                        )
                write_json_atomic(
                    session / "progress.json",
                    {
                        "completed": len(rows),
                        "planned": len(selected),
                        "at": datetime.now(timezone.utc).isoformat(),
                    },
                )
    if runtime_identity() != plan["runtime"]:
        raise ValueError("Runtime changed during resumed parsing")
    if len(rows) == len(selected):
        ordered = [rows[r["source_path"]] for r in selected]
        validate_journal({"inputs": selected}, ordered)
        write_json_atomic(
            target / "journal.json",
            {
                "attempts": ordered,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        write_json_atomic(
            target / "parse-complete.json",
            {
                "plan_sha256": digest(original / "plan.json"),
                "journal_sha256": digest(target / "journal.json"),
                "inputs": len(rows),
                "timing_sample": sample,
                "outcomes": dict(Counter(r["outcome"] for r in rows.values())),
            },
        )
    return target


def run(unit: Path, backend: str, workers: int, timeout: float, options: dict) -> Path:
    if workers < 1 or timeout <= 0:
        raise ValueError("Workers and deadline must be positive")
    coverage_path = unit / "parsebench-source-coverage.json"
    inventory_path = unit / "parsebench-inventory.json"
    coverage = json.loads(coverage_path.read_text())
    inventory = json.loads(inventory_path.read_text())
    validate_population(coverage, inventory)
    roster = {r["backend"]: r for r in local_roster()}
    if backend not in roster or roster[backend]["paid"]:
        raise ValueError("This run permits only registered local backends")
    if "initialization_error" in roster[backend]:
        raise ValueError(roster[backend]["initialization_error"])
    parser = PdfsmithAdapter(backend, cache_mode="bypass", **options)
    effective = getattr(parser._get_backend(), "effective_options", {})
    inputs = interleaved_inputs(coverage["inputs"])
    source_root = Path(coverage["source_root"])
    for row in inputs:
        path = (source_root / row["source_path"]).resolve()
        if not path.is_relative_to(source_root.resolve()) or digest(path) != row["sha256"]:
            raise ValueError("Input bytes differ from qualified population")
    target = unit / "full-comparison-evidence" / (backend + "-" + uuid.uuid4().hex)
    plan = {
        "protocol": "full-parsebench-pdfsmith-v1",
        "backend": backend,
        "options": effective,
        "runtime": runtime_identity(),
        "dataset_revision": coverage["dataset_revision"],
        "code_revision": coverage["code_revision"],
        "coverage_sha256": digest(coverage_path),
        "inventory_sha256": digest(inventory_path),
        "input_root": str(source_root.resolve()),
        "inputs": [{k: r[k] for k in ("source_path", "sha256", "page_count")} for r in inputs],
        "case_count": len(inventory["cases"]),
        "dimension_cases": dict(Counter(c["group"] for c in inventory["cases"])),
        "timeout_seconds": timeout,
        "workers": workers,
        "input_order": "Round-robin dimensions with SHA256(path) ordering; shared text parsed once",
        "output_contract": "PDFSmith Markdown string; no bounding-box sidecar",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "harness_sha256": digest(Path(__file__)),
        "model_files": model_identity(backend),
    }
    target.mkdir(parents=True)
    (target / "frozen-harness.py").write_bytes(Path(__file__).read_bytes())
    write_json_atomic(target / "plan.json", plan)

    def execute(row: dict) -> dict:
        key = hashlib.sha256(row["source_path"].encode()).hexdigest()[:24]
        attempt = execute_parser(
            PdfsmithAdapter,
            {"backend_name": backend, "cache_mode": "bypass", **effective},
            source_root / row["source_path"],
            target / "attempts" / key,
            timeout_seconds=timeout,
            denied_read_components=("references", "qualified-invoice-truth"),
        )
        result = {
            "source_path": row["source_path"],
            "input_sha256": row["sha256"],
            **{k: str(v) if isinstance(v, Path) else v for k, v in asdict(attempt).items()},
        }
        if result["output_path"]:
            result["output_path"] = str(Path(result["output_path"]).relative_to(target.resolve()))
        write_json_atomic(target / "attempts" / key / "attempt.json", result)
        return result

    rows = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for row in executor.map(execute, inputs):
            rows.append(row)
            if len(rows) % 50 == 0:
                print(
                    f"{backend}: {len(rows)}/{len(inputs)} "
                    f"{dict(Counter(r['outcome'] for r in rows))}",
                    flush=True,
                )
    if runtime_identity() != plan["runtime"]:
        raise ValueError("Runtime changed during parsing; output remains incomplete evidence")
    validate_journal(plan, rows)
    journal = {"attempts": rows, "completed_at": datetime.now(timezone.utc).isoformat()}
    write_json_atomic(target / "journal.json", journal)
    write_json_atomic(
        target / "parse-complete.json",
        {
            "plan_sha256": digest(target / "plan.json"),
            "journal_sha256": digest(target / "journal.json"),
            "inputs": len(rows),
            "outcomes": dict(Counter(r["outcome"] for r in rows)),
        },
    )
    print(str(target), flush=True)
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path)
    parser.add_argument("--backend")
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--stop-at", type=datetime.fromisoformat)
    parser.add_argument("--sample", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--options", type=json.loads, default={})
    args = parser.parse_args()
    if args.resume:
        if args.stop_at is None:
            parser.error("Resumption requires --stop-at")
        resume(
            args.resume.resolve(),
            args.workers,
            args.stop_at,
            json.loads(args.sample.read_text()) if args.sample else None,
        )
    else:
        if args.unit is None or args.backend is None:
            parser.error("A new plan requires --unit and --backend")
        run(args.unit.resolve(), args.backend, args.workers, args.timeout, args.options)


if __name__ == "__main__":
    main()
