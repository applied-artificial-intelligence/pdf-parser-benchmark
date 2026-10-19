"""Install retained evaluator artifacts and hydrate byte-verified public inputs."""

import hashlib
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def install_environment(target: Path, artifacts: Path, version: str, wheels: list[str]) -> Path:
    manifest = json.loads((artifacts / "artifact-hashes.json").read_bytes())
    for name, expected in manifest.items():
        p = (artifacts / name).resolve()
        if not p.is_relative_to(artifacts.resolve()) or digest(p) != expected:
            raise ValueError(f"Runtime artifact changed: {name}")
    if target.exists():
        raise ValueError("Fresh runtime destination already exists")
    subprocess.run(
        ["uv", "venv", "--python", version, str(target)], check=True, capture_output=True
    )
    python = target.absolute() / "bin/python"
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
        capture_output=True,
    )
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--no-deps",
            *[str(artifacts / name) for name in wheels],
        ],
        check=True,
        capture_output=True,
    )
    return python


def hydrate_sources(plan_root: Path, target: Path, wanted: set[str] | None = None) -> dict:
    plan = json.loads((plan_root / "plan.json").read_bytes())
    target.mkdir(parents=True, exist_ok=True)
    sources = {}
    for case in plan["cases"]:
        if wanted is not None and case["source_path"] not in wanted:
            continue
        original = plan_root / case["input"]
        p = original if original.is_file() else target / (case["input_sha256"] + ".pdf")
        if not p.exists():
            prefix = "https://huggingface.co/datasets/llamaindex/ParseBench/resolve/"
            if not case["source_url"].startswith(prefix + plan["dataset_revision"] + "/"):
                raise ValueError("Public source URL differs from frozen revision")
            with urlopen(case["source_url"], timeout=90) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != case["input_sha256"]:
                raise ValueError("Downloaded public source changed")
            p.write_bytes(data)
        if digest(p) != case["input_sha256"]:
            raise ValueError("Hydrated public source changed")
        sources[case["source_path"]] = str(p.absolute())
    return sources
