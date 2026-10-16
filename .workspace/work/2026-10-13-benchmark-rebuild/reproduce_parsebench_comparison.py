"""Rebuild frozen public inputs and runtimes, execute and regrade in a fresh directory."""

import argparse
import json
import runpy
import shutil
import subprocess
import tempfile
from pathlib import Path


def reproduce(output_parent: Path) -> Path:
    unit = Path(__file__).resolve().parent
    root_repo = unit.parents[2]
    helpers = runpy.run_path(str(root_repo / "scripts/parsebench_runtime.py"))
    checkpoint = json.loads((unit / "parsebench-run-checkpoint.json").read_bytes())
    original_plan = unit / checkpoint["plan"]
    if helpers["digest"](original_plan / "plan.json") != checkpoint["plan_sha256"]:
        raise ValueError("Public replay plan identity changed")
    output_parent.mkdir(exist_ok=True, parents=True)
    root = Path(tempfile.mkdtemp(prefix="parsebench-replay-", dir=output_parent)).resolve()
    parser_python = helpers["install_environment"](
        root / "parser-environment",
        unit / "invoice-runtime-artifacts-v3",
        "3.13.5",
        ["pdfsmith-0.2.0-py3-none-any.whl", "pdf_bench-1.0.0-py3-none-any.whl"],
    )
    native_python = helpers["install_environment"](
        root / "native-environment",
        unit / "parsebench-runtime-artifacts",
        "3.14.3",
        ["parse_bench-1.0.5-py3-none-any.whl"],
    )
    plan_root = root / "plan"
    shutil.copytree(original_plan, plan_root)
    sources = helpers["hydrate_sources"](original_plan, root / "downloaded-inputs")
    plan = json.loads((plan_root / "plan.json").read_bytes())
    for case in plan["cases"]:
        target = plan_root / case["input"]
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(sources[case["source_path"]], target)
    harness = plan_root / "harness.py"
    subprocess.run(
        [
            str(parser_python),
            "-I",
            str(harness),
            "run",
            str(plan_root),
            str(root / "runs"),
            str(native_python),
        ],
        cwd=root,
        check=True,
    )
    pointer = json.loads((root / "runs/latest.json").read_bytes())
    bundle = (root / "runs" / pointer["bundle"]).resolve()
    if not bundle.is_relative_to(root / "runs"):
        raise ValueError("Public replay pointer escapes its output directory")
    if helpers["digest"](bundle / "completion.json") != pointer["completion_sha256"]:
        raise ValueError("Public replay completion identity changed")
    program = (
        "import json,runpy,sys; from pathlib import Path; "
        "module=runpy.run_path(sys.argv[1]); "
        "print(json.dumps(module['compare_runs'](Path(sys.argv[2]),Path(sys.argv[3]))))"
    )
    compared = subprocess.run(
        [
            str(parser_python),
            "-I",
            "-c",
            program,
            str(harness),
            str(unit / checkpoint["primary_bundle"]),
            str(bundle),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    fresh = json.loads(compared.stdout)
    view = root / "offline-evidence"
    shutil.copytree(bundle, view)
    shutil.rmtree(view / "frozen-plan/inputs")
    for directory in (view / "attempts").glob("*/parser-output"):
        shutil.rmtree(directory)
    program = (
        "import json,runpy,sys; from pathlib import Path; "
        "module=runpy.run_path(sys.argv[1]); "
        "print(json.dumps(module['regrade_run'](Path(sys.argv[2]),Path(sys.argv[3]))))"
    )
    result = subprocess.run(
        [
            str(parser_python),
            "-I",
            "-c",
            program,
            str(harness),
            str(view),
            str(native_python),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    offline = json.loads(result.stdout)
    if len(fresh["matching_pairs"]) != 100 or offline["pairs_regraded"] != 100:
        raise ValueError("Public replay did not verify every frozen pair")
    (root / "verification.json").write_text(
        json.dumps(
            {
                "fresh_comparison": fresh,
                "offline_regrade": offline,
                "offline_input_pdfs_present": (view / "frozen-plan/inputs").exists(),
                "scope": (
                    "Two local parser configurations on the fixed 30-content/20-table subset; "
                    "native upstream metrics, no paid calls"
                ),
            },
            indent=2,
        )
        + "\n"
    )
    shutil.rmtree(root / "parser-environment")
    shutil.rmtree(root / "native-environment")
    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-parent", type=Path, default=Path(__file__).resolve().parents[3] / "data_exports"
    )
    print(reproduce(parser.parse_args().output_parent))
