"""Build the authorized review packet from an explicit, non-secret source allowlist."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
REVIEWED = "d9305d6100e5288fa2fc255e088bfd8e22664b98"
PRIOR_RUN = ROOT / ".workspace/work/2026-10-13-local-parser-evaluation/run-03/comparison.json"
EXCERPTS = {
    "pdf_bench/persistence.py": [(25, 69)],
    "pdf_bench/systems/pdfsmith_adapter.py": [(65, 108), (114, 162)],
    "pdf_bench/utils/caching.py": [(102, 135)],
    "pdf_bench/runner.py": [(170, 235), (300, 350)],
    "pdf_bench/inventory.py": [(566, 653)],
    "scripts/build_internal_benchmark_story.py": [(44, 71), (201, 266)],
    "pdf_bench/local_evaluation.py": [(44, 85), (141, 156), (181, 225), (239, 272)],
    "tests/test_local_evaluation.py": [(1, 80)],
    "builders/generate_invoice_corpus.py": [(78, 124), (253, 311)],
    "builders/invoice/data_generators.py": [(184, 195)],
    "benchmarks/sec_filings_47docs.yaml": [(1, 8), (65, 91)],
    "benchmarks/invoices_100docs_fresh.yaml": [(1, 7), (106, 131)],
    ".workspace/work/2026-10-13-local-parser-evaluation/technical-report.md": [(1, 91)],
}
RESULTS = (
    "sec_filings_47docs.json",
    "invoices_100docs_fresh.json",
    "presentations_30docs.json",
    "business_synthetic_investor_decks_subset_refresh.json",
    "arxiv_10docs_fresh.json",
    "frontier_unified_30docs.json",
    "frontier_premium_300p.json",
    "sec_filings_screen_all.json",
    "sec_filings_commercial_5docs.json",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def check(command: list[str]) -> dict:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def replace_owned(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.preparing")
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    source_files = {name: (ROOT / name).read_bytes() for name in EXCERPTS}
    documents = {
        name: (UNIT / name).read_bytes()
        for name in ("start-here.txt", "review-context.txt", "spec.md", "plan.md")
    }
    checks = [
        check(
            [
                "uv",
                "run",
                "--no-sync",
                "pytest",
                "-o",
                "addopts=",
                "-W",
                "error",
                "tests/test_runner.py",
                "tests/test_persistence.py",
                "tests/test_local_evaluation.py",
                "-q",
            ]
        ),
        check(["verification", "terms", "check", str(UNIT / "spec.md")]),
        check(
            [
                "uv",
                "run",
                "--no-sync",
                "python",
                "/home/stefan/.codex/skills/decompose/check_plan.py",
                str(UNIT / "plan.md"),
            ]
        ),
        *[
            check(["verification", group, action, str(UNIT / "plan.md")])
            for group, action in (("premises", "check"), ("claims", "list"), ("closure", "check"))
        ],
        check(["uv", "run", "--no-sync", "ruff", "format", "--check", "."]),
        check(["uv", "run", "--no-sync", "ruff", "check", ".", "--output-format", "json"]),
        check(["git", "diff", "--check"]),
    ]
    if any(result["exit_code"] for result in checks[:6]):
        raise RuntimeError("Focused baseline or specification/plan validation failed")

    versions = {}
    for name in ("pdfsmith", "pypdf", "pdfplumber", "PyMuPDF", "pymupdf4llm", "reportlab"):
        versions[name] = importlib.metadata.version(name)

    summaries = []
    evidence_files = {}
    for name in RESULTS:
        relative = f"results/{name}"
        raw = (ROOT / relative).read_bytes()
        evidence_files[relative] = raw
        data = json.loads(raw)
        rows = data.get("results", [])
        summaries.append(
            {
                "artifact": relative,
                "sha256": digest(raw),
                "benchmark": data.get("benchmark"),
                "environment": data.get("environment"),
                "declared_summary": data.get("summary"),
                "actual_rows": len(rows),
                "rows_by_parser": dict(Counter(row.get("parser_name", "unknown") for row in rows)),
                "success_rows": sum(row.get("success") is True for row in rows),
                "failure_rows": sum(row.get("success") is False for row in rows),
                "first_row_pointer": "/results/0",
                "first_row": rows[0] if rows else None,
                "provenance_note": (
                    "Recorded historical fields, not independently reconstructed truth"
                ),
            }
        )

    prior_bytes = PRIOR_RUN.read_bytes()
    prior = json.loads(prior_bytes)
    evidence_files[str(PRIOR_RUN.relative_to(ROOT))] = prior_bytes
    inputs = {
        name: {"sha256": digest(raw), "bytes": len(raw)}
        for name, raw in {**source_files, **evidence_files}.items()
    }
    inputs.update(
        {
            str((UNIT / name).relative_to(ROOT)): {"sha256": digest(raw), "bytes": len(raw)}
            for name, raw in documents.items()
        }
    )
    copied_checkpoint_files = (
        "pdf_bench/local_evaluation.py",
        "pdf_bench/persistence.py",
        "pdf_bench/systems/tika_parser.py",
        "tests/test_runner.py",
        "tests/test_local_evaluation.py",
    )
    checkpoint_matches = {}
    for relative in copied_checkpoint_files:
        committed = subprocess.check_output(["git", "show", f"{REVIEWED}:{relative}"], cwd=ROOT)
        current = (ROOT / relative).read_bytes()
        checkpoint_matches[relative] = {
            "reviewed_sha256": digest(committed),
            "working_sha256": digest(current),
            "matches": committed == current,
        }
    pdfsmith_root = ROOT.parent / "pdfsmith"
    pdfsmith_source = (pdfsmith_root / "src/pdfsmith/__init__.py").read_bytes()
    pdfsmith_project = (pdfsmith_root / "pyproject.toml").read_bytes()
    declared = re.search(r'^__version__ = "([^"]+)"', pdfsmith_source.decode(), re.MULTILINE)
    project_version = re.search(r'^version = "([^"]+)"', pdfsmith_project.decode(), re.MULTILINE)
    if declared is None or project_version is None:
        raise RuntimeError("PDFsmith source/project versions could not be established")
    snapshot = {
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "base_revision": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "origin_main_observed": git("rev-parse", "origin/main"),
        "reviewed_revision": REVIEWED,
        "source_identity_warning": (
            "Dirty working tree: base revision alone does not version inputs"
        ),
        "tracked_diff_sha256": digest(
            subprocess.check_output(["git", "diff", "--binary"], cwd=ROOT)
        ),
        "inputs": inputs,
        "reviewed_checkpoint_matches": checkpoint_matches,
        "observed_package_versions": versions,
        "observed_pdfsmith_source_declared_version": declared.group(1),
        "observed_pdfsmith_project_version": project_version.group(1),
        "pdfsmith_source_sha256": digest(pdfsmith_source),
        "pdfsmith_project_sha256": digest(pdfsmith_project),
        "pdfsmith_version_note": (
            "Editable metadata/project version and source declaration disagree; recorded explicitly"
        ),
        "external_code_revision": "d423e529ae329317bcd33c650b367acfb60e6620",
        "external_dataset_revision": "2805a1d940f95a203e0ae4b88be9934f7765b3fc",
        "prior_smoke_comparison_sha256": digest(prior_bytes),
        "new_specification_reviews": "pending; none returned",
    }
    if not all(record["matches"] for record in checkpoint_matches.values()):
        raise RuntimeError("Mirrored checkpoint differs; investigate before packaging")
    if digest(prior_bytes) != "1b7ca15e231de50ea303e34e9b9ef20c759ad09533687605ad2f3c8129f7f242":
        raise RuntimeError("Retained independently reviewed evidence differs")
    changed = [name for name, raw in source_files.items() if (ROOT / name).read_bytes() != raw]
    if changed:
        raise RuntimeError(f"Source changed while preparing packet: {changed}")

    parts = [
        "PDF-Bench external specification/plan review packet\n",
        "Prepared from explicit source allowlists; excludes credentials, private contacts, "
        "production dumps, client documents and unrelated project reports.\n",
    ]
    for name, raw in documents.items():
        parts.append(f"\n===== COMPLETE {name}; SHA-256 {digest(raw)} =====\n")
        parts.append(raw.decode("utf-8"))
    parts.append("\n===== EXACT REVIEW INPUT MANIFEST =====\n" + json.dumps(snapshot, indent=2))
    parts.append("\n===== FRESH BASELINE CHECKS =====\n")
    for result in checks:
        if result["command"][-1] == "json":
            findings = json.loads(result["stdout"])
            summary = {
                "command": result["command"],
                "exit_code": result["exit_code"],
                "inherited_lint_findings": len(findings),
                "counts_by_rule": dict(Counter(row["code"] for row in findings)),
                "note": "Complete locations retained in baseline-checks.json; no source repair yet",
            }
            parts.append(json.dumps(summary, indent=2))
        else:
            parts.append(json.dumps(result, indent=2))
        parts.append("\n")
    parts.append("\n===== RETAINED TRACK SUMMARIES, NOT NEW RUNS =====\n")
    parts.append(json.dumps(summaries, indent=2))
    parts.append("\n===== INDEPENDENTLY REVIEWED SMOKE COMPARISON =====\n")
    parts.append(
        json.dumps(
            {
                key: prior[key]
                for key in (
                    "executed_at",
                    "versions",
                    "pdfsmith_declared_version",
                    "cache_policy",
                    "inputs",
                    "attempts",
                    "summary",
                    "limitations",
                )
            },
            indent=2,
        )
    )
    for name, ranges in EXCERPTS.items():
        lines = source_files[name].decode("utf-8").splitlines()
        parts.append(f"\n===== ACTUAL SOURCE EXCERPTS: {name} =====\n")
        for start, end in ranges:
            parts.append(f"Lines {start}-{min(end, len(lines))}; partial, not the entire file\n")
            parts.extend(
                f"{number}: {lines[number - 1]}".rstrip() + "\n"
                for number in range(start, min(end, len(lines)) + 1)
            )
    packet = "\n".join(parts).encode("utf-8")
    replace_owned(UNIT / "review-inputs.json", (json.dumps(snapshot, indent=2) + "\n").encode())
    replace_owned(UNIT / "baseline-checks.json", (json.dumps(checks, indent=2) + "\n").encode())
    replace_owned(UNIT / "external-review-packet.txt", packet)
    replace_owned(
        UNIT / "external-review-packet.sha256",
        (digest(packet) + "  external-review-packet.txt\n").encode(),
    )
    print(f"Packet: {len(packet)} bytes, SHA-256 {digest(packet)}")
    print("Focused baseline and plan checks passed; inherited hygiene failures recorded")


if __name__ == "__main__":
    main()
