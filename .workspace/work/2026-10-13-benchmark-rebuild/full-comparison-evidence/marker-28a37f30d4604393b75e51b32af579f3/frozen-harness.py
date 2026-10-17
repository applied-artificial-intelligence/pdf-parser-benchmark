"""Run a declared PDFSmith configuration over the complete public input population."""

import argparse
import hashlib
import json
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
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
    inputs = sorted(coverage["inputs"], key=lambda r: r["source_path"])
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
        "output_contract": "PDFSmith Markdown string; no bounding-box sidecar",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "harness_sha256": digest(Path(__file__)),
        "model_files": model_identity(backend),
    }
    target.mkdir(parents=True)
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
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--options", type=json.loads, default={})
    args = parser.parse_args()
    run(args.unit.resolve(), args.backend, args.workers, args.timeout, args.options)


if __name__ == "__main__":
    main()
