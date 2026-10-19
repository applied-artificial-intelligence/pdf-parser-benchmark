"""Recompute invoice predictions and grades with only frozen artifacts and the standard library."""

import argparse
import hashlib
import importlib
import json
import os
import sys
import sysconfig
import types
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regrade(bundle: Path) -> dict:
    bundle = bundle.resolve()
    standard_library = Path(sysconfig.get_path("stdlib")).resolve()

    def isolated(event, arguments):
        if event == "open" and isinstance(arguments[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(arguments[0])).resolve()
            mode = arguments[1]
            if isinstance(mode, str) and any(flag in mode for flag in "wax+"):
                raise PermissionError("Offline regrading is read-only")
            if not path.is_relative_to(bundle) and not path.is_relative_to(standard_library):
                raise PermissionError("Only frozen evidence and standard-library reads are allowed")
        if event.startswith(("socket.", "subprocess.", "os.system")):
            raise PermissionError(
                "Network and subprocesses are unavailable during offline regrading"
            )
        if event == "import" and arguments[0].split(".")[0] in {
            "pdfsmith",
            "pypdf",
            "pdfplumber",
            "pdfminer",
            "pymupdf",
        }:
            raise PermissionError("Parser imports are unavailable during offline regrading")

    sys.dont_write_bytecode = True
    sys.addaudithook(isolated)
    completion = json.loads((bundle / "completion.json").read_bytes())
    if completion["status"] != "complete":
        raise ValueError("Cannot regrade incomplete evidence")

    def verified(name: str) -> Path:
        target = (bundle / name).resolve()
        if not target.is_relative_to(bundle) or digest(target) != completion["files"][name]:
            raise ValueError(f"Frozen artifact changed or is missing: {name}")
        return target

    def read(name: str) -> dict:
        return json.loads(verified(name).read_bytes())

    plan = read("frozen-plan/plan.json")
    protocol = read("frozen-plan/task-protocol.json")
    for name in ["invoice_extraction.py", "invoice_task.py"]:
        verified(f"frozen-plan/evaluation-code/{name}")
    if (
        digest(bundle / "frozen-plan/evaluation-code/invoice_extraction.py")
        != protocol["extractor_sha256"]
    ):
        raise ValueError("Frozen extractor differs from the declared protocol")
    package = types.ModuleType("pdf_bench")
    package.__path__ = [str(bundle / "frozen-plan/evaluation-code")]
    sys.modules["pdf_bench"] = package
    extractor = importlib.import_module("pdf_bench.invoice_extraction")
    task = importlib.import_module("pdf_bench.invoice_task")
    if any(protocol.get(key) != value for key, value in task.task_protocol().items()):
        raise ValueError("Frozen code/runtime does not implement the task protocol")
    rows = read("journal.json")["attempts"]
    expected_pairs = [(p["pipeline_id"], p["document_id"]) for p in plan["planned_pairs"]]
    actual_pairs = [(r["pipeline_id"], r["document_id"]) for r in rows]
    if actual_pairs != expected_pairs or len(set(actual_pairs)) != len(actual_pairs):
        raise ValueError("Offline population differs from the frozen planned pairs")
    grades, prediction_count = {}, 0
    for row in rows:
        base = f"attempts/{row['pair_id']}"
        if row["output_path"] is not None:
            raw_path = verified(row["output_path"])
            if digest(raw_path) != row["output_sha256"]:
                raise ValueError("Parser-output identity mismatch")
            raw = raw_path.read_text()
        else:
            raw = ""
        prediction = extractor.extract_invoice(raw)
        if prediction != read(f"{base}/prediction.json"):
            raise ValueError(f"Prediction mismatch: {row['pair_id']}")
        reference = read(f"frozen-plan/references/{row['document_id']}.json")
        grade = task.grade_invoice(prediction, reference)
        if grade != read(f"{base}/grade.json")["grade"]:
            raise ValueError(f"Grade mismatch: {row['pair_id']}")
        grades[row["pair_id"]] = grade
        prediction_count += 1
    stored = read("summary.json")
    tasks = {}
    ids = [doc["document_id"] for doc in plan["documents"]]
    for pipeline in plan["pipelines"]:
        name = pipeline["pipeline_id"]
        tasks[name] = task.aggregate_grades(
            {
                row["document_id"]: grades[row["pair_id"]]
                for row in rows
                if row["pipeline_id"] == name
            },
            ids,
        )
        if tasks[name] != stored[name]["task"]:
            raise ValueError(f"Aggregate mismatch: {name}")
    return {
        "completion_sha256": digest(bundle / "completion.json"),
        "pairs_regraded": prediction_count,
        "task_aggregates": tasks,
        "restrictions": "-I -S; standard library and frozen evidence only; no parser imports, "
        "network, subprocesses, original source files or ambient caches",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    print(json.dumps(regrade(args.bundle), sort_keys=True, allow_nan=False, indent=2))
