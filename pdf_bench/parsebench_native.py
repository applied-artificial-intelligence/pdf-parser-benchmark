"""Run pinned upstream ParseBench evaluation without parsing or network access."""

import ast
import contextlib
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity() -> dict:
    import parse_bench

    root = Path(parse_bench.__file__).parent
    return {
        "python": platform.python_version(),
        "distributions": dict(
            sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions())
        ),
        "upstream_sources": {
            p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob("*.py"))
        },
        "worker_sha256": digest(Path(__file__)),
    }


def table_converter() -> Callable[[str], str]:
    import parse_bench

    source = Path(parse_bench.__file__).parent / "inference/providers/parse/liteparse.py"
    tree = ast.parse(source.read_text())
    provider = next(
        n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LiteParseProvider"
    )
    method = next(
        n
        for n in provider.body
        if isinstance(n, ast.FunctionDef) and n.name == "_convert_md_tables_to_html"
    )
    method.decorator_list = []
    namespace: dict[str, Any] = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), "exec"), namespace)
    converter: Callable[[str], str] = namespace["_convert_md_tables_to_html"]
    return converter


def evaluate(bundle: Path) -> dict:
    os.environ["LLAMACLOUD_BENCH_LLM_NORMALIZATION"] = "off"

    def restricted(event: str, arguments: tuple) -> None:
        if event.startswith("socket.") or event in {"subprocess.Popen", "os.system", "os.fork"}:
            raise PermissionError("Network and parser subprocesses are unavailable in regrading")
        if event == "import" and arguments[0].split(".")[0] in {
            "pdfsmith",
            "pypdf",
            "pdfplumber",
            "pdfminer",
        }:
            raise PermissionError("Parser imports are unavailable in regrading")
        if event == "open" and isinstance(arguments[0], (str, bytes, os.PathLike)):
            p = Path(os.fsdecode(arguments[0])).resolve()
            if p.suffix.lower() == ".pdf":
                raise PermissionError("Original PDFs are unavailable in regrading")

    sys.addaudithook(restricted)
    from parse_bench.evaluation.evaluators.parse import ParseEvaluator
    from parse_bench.schemas.parse_output import ParseOutput
    from parse_bench.schemas.pipeline_io import InferenceRequest, InferenceResult
    from parse_bench.test_cases.loader import _load_jsonl_dataset

    plan_root = bundle / "frozen-plan"
    plan = json.loads((plan_root / "plan.json").read_bytes())
    if identity() != plan["evaluator_environment"]:
        raise ValueError("Native evaluator implementation differs from frozen protocol")
    for name, expected in plan["files"].items():
        if name.startswith("inputs/"):
            continue
        p = (plan_root / name).resolve()
        if not p.is_relative_to(plan_root) or digest(p) != expected:
            raise ValueError(f"Changed native evaluation artifact: {name}")
    journal = json.loads((bundle / "journal.json").read_bytes())["attempts"]
    if [r["pair_id"] for r in journal] != plan["planned_pairs"]:
        raise ValueError("Native evaluation requires every frozen pair in call order")
    cases = {c.test_id: c for c in _load_jsonl_dataset(plan_root / "references")}
    evaluator = ParseEvaluator(**plan["evaluator_options"])
    convert_tables = table_converter()
    rows = []
    for attempt in journal:
        case = cases[attempt["upstream_test_id"]]
        raw = ""
        if attempt["output_path"]:
            path = (bundle / attempt["output_path"]).resolve()
            if not path.is_relative_to(bundle) or digest(path) != attempt["output_sha256"]:
                raise ValueError("Retained public parser output changed")
            raw = path.read_text()
        normalized = convert_tables(raw)
        output = ParseOutput(
            example_id=case.test_id, pipeline_name=attempt["pipeline_id"], markdown=normalized
        )
        inference = InferenceResult(
            request=InferenceRequest(
                example_id=case.test_id, source_file_path=str(case.file_path), product_type="parse"
            ),
            pipeline_name=attempt["pipeline_id"],
            product_type="parse",
            raw_output={"markdown": raw},
            output=output,
            started_at=datetime(2000, 1, 1, tzinfo=timezone.utc),
            completed_at=datetime(2000, 1, 1, tzinfo=timezone.utc),
            latency_in_ms=0,
        )
        result = evaluator.evaluate(inference, case).model_dump(mode="json")
        result.pop("evaluated_at")
        rows.append(
            {
                "pair_id": attempt["pair_id"],
                "group": attempt["group"],
                "normalized_markdown": normalized,
                "result": result,
            }
        )
    return {"protocol": plan["metric_protocol"], "pairs": rows}


if __name__ == "__main__":
    if sys.argv[1:] == ["--identity"]:
        print(json.dumps(identity(), sort_keys=True))
    else:
        with contextlib.redirect_stdout(sys.stderr):
            result = evaluate(Path(sys.argv[1]).resolve())
        print(json.dumps(result, allow_nan=False))
