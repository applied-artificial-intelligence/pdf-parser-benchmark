"""Install frozen inputs in a fresh directory, execute all pairs and verify offline replay."""

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(output_parent: Path) -> Path:
    unit = Path(__file__).resolve().parent
    checkpoint = json.loads((unit / "invoice-run-checkpoint.json").read_bytes())
    for name, expected in checkpoint["runtime_artifacts"].items():
        path = (unit / name).resolve()
        if (
            not path.is_relative_to(unit)
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected
        ):
            raise ValueError(f"Runtime artifact changed: {name}")
    original_plan = unit / checkpoint["plan"]
    if hashlib.sha256(original_plan.read_bytes()).hexdigest() != checkpoint["plan_sha256"]:
        raise ValueError("Frozen plan identity changed")
    output_parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="invoice-replay-", dir=output_parent)).resolve()
    environment = root / "environment"
    python = environment / "bin/python"
    artifacts = unit / "invoice-runtime-artifacts-v3"
    subprocess.run(["uv", "venv", "--python", "3.13.5", str(environment)], check=True)
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--require-hashes",
            "-r",
            str(artifacts / "requirements.lock"),
        ],
        check=True,
    )
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--no-deps",
            str(artifacts / "pdfsmith-0.2.0-py3-none-any.whl"),
            str(artifacts / "pdf_bench-1.0.0-py3-none-any.whl"),
        ],
        check=True,
    )
    shutil.copytree(original_plan.parent, root / "frozen-plan")
    subprocess.run(
        [
            str(python),
            "-I",
            "-m",
            "pdf_bench.invoice_comparison",
            "run",
            str(root / "frozen-plan"),
            str(root / "results"),
        ],
        cwd=root,
        check=True,
    )
    pointer = json.loads((root / "results/latest.json").read_bytes())
    bundle = (root / "results" / pointer["bundle"]).resolve()
    if not bundle.is_relative_to(root / "results"):
        raise ValueError("Unsafe replay pointer")
    if (
        hashlib.sha256((bundle / "completion.json").read_bytes()).hexdigest()
        != pointer["completion_sha256"]
    ):
        raise ValueError("Replay pointer identity mismatch")
    program = (
        "import json,sys; from pathlib import Path; "
        "from pdf_bench.invoice_reproduction import compare_runs; "
        "print(json.dumps(compare_runs(Path(sys.argv[1]),Path(sys.argv[2]))))"
    )
    compared = subprocess.run(
        [str(python), "-I", "-c", program, str(unit / checkpoint["primary_bundle"]), str(bundle)],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    reproduction = json.loads(compared.stdout)
    (root / "fresh-reproduction.json").write_text(json.dumps(reproduction, indent=2))
    view = root / "offline-evidence"
    shutil.copytree(bundle, view)
    shutil.rmtree(view / "frozen-plan/inputs")
    for directory in (view / "attempts").glob("*/parser-output"):
        shutil.rmtree(directory)
    regraded = subprocess.run(
        [str(python), "-I", "-S", str(view / "frozen-plan/offline-regrade.py"), str(view)],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    offline = json.loads(regraded.stdout)
    (root / "offline-regrade.json").write_text(json.dumps(offline, indent=2))
    if len(reproduction["matching_pairs"]) != 200 or offline["pairs_regraded"] != 200:
        raise ValueError("Replay did not verify every frozen pair")
    (root / "verification.json").write_text(
        json.dumps(
            {
                "matching_fresh_pairs": 200,
                "offline_regraded_pairs": 200,
                "frozen_plan_sha256": checkpoint["plan_sha256"],
                "source_completion_sha256": reproduction["first_completion_sha256"],
                "replay_completion_sha256": reproduction["second_completion_sha256"],
                "offline_input_pdfs_present": (view / "frozen-plan/inputs").exists(),
                "temporary_environment_removed_after_verification": True,
            },
            indent=2,
        )
    )
    shutil.rmtree(environment)
    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-parent", type=Path, default=Path(__file__).resolve().parents[3] / "data_exports"
    )
    args = parser.parse_args()
    print(run(args.output_parent))
