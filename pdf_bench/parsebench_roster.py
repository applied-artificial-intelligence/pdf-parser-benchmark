"""Exercise local PDFSmith integrations without calling commercial providers."""

import argparse
import hashlib
import importlib.metadata
import json
import sys
import uuid
from dataclasses import asdict
from pathlib import Path

from pdf_bench.execution import execute_parser
from pdf_bench.persistence import write_json_atomic
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter


def runtime_identity() -> dict:
    import pdfsmith

    root = Path(pdfsmith.__file__).parent
    names = sorted({d.metadata["Name"] for d in importlib.metadata.distributions()})
    return {
        "python": sys.version,
        "executable": sys.executable,
        "pdfsmith_source_version": pdfsmith.__version__,
        "pdfsmith_sources": {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*.py"))
        },
        "distributions": {name: importlib.metadata.version(name) for name in names},
    }


def local_roster() -> list[dict]:
    from pdfsmith.backends.registry import BACKEND_REGISTRY

    rows = []
    for name, info in BACKEND_REGISTRY.items():
        row = {
            "backend": name,
            "weight": info.weight,
            "package": info.package,
            "dependencies_installed": info.is_available(),
            "python_supported": info.supports_python(),
            "paid": info.weight == "commercial",
        }
        if not row["paid"]:
            try:
                backend = info.loader()()
                row["options"] = getattr(backend, "effective_options", {})
                row["output_contract"] = "markdown_string_without_grounding_sidecar"
            except Exception as error:
                row["initialization_error"] = f"{type(error).__name__}: {error}"
        rows.append(row)
    return rows


def probe(unit: Path, inputs: list[Path], backends: list[str] | None = None) -> Path:
    target = unit / "roster-readiness" / ("probe-" + uuid.uuid4().hex)
    target.mkdir(parents=True)
    rows = local_roster()
    if backends and set(backends) - {r["backend"] for r in rows if not r["paid"]}:
        raise ValueError("Only explicitly local PDFSmith backends may be probed")
    plan = {
        "runtime": runtime_identity(),
        "roster": rows,
        "inputs": [str(p.resolve()) for p in inputs],
    }
    write_json_atomic(target / "plan.json", plan)
    attempts = []
    for row in rows:
        name = row["backend"]
        if row["paid"] or (backends and name not in backends):
            continue
        for index, path in enumerate(inputs):
            attempt = execute_parser(
                PdfsmithAdapter,
                {"backend_name": name, "cache_mode": "bypass", **row.get("options", {})},
                path,
                target / f"{name}-{index}",
                timeout_seconds=180,
            )
            result = {
                "backend": name,
                "input": str(path),
                **{k: str(v) if isinstance(v, Path) else v for k, v in asdict(attempt).items()},
            }
            attempts.append(result)
            write_json_atomic(target / "results.json", {"attempts": attempts})
            print(json.dumps(result), flush=True)
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, nargs="+", required=True)
    parser.add_argument("--backends", nargs="*")
    args = parser.parse_args()
    print(probe(args.unit, args.inputs, args.backends))


if __name__ == "__main__":
    main()
