"""Pinned ParseBench acquisition and annotation inventory, without parser inference."""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import quote
from urllib.request import urlopen

from pdf_bench.persistence import write_json_atomic

DATA_REVISION = "2805a1d940f95a203e0ae4b88be9934f7765b3fc"
CODE_REVISION = "d423e529ae329317bcd33c650b367acfb60e6620"
GROUPS = ("chart", "layout", "table", "text_content", "text_formatting")
DATA_BASE = f"https://huggingface.co/datasets/llamaindex/ParseBench/resolve/{DATA_REVISION}/"
API_BASE = f"https://huggingface.co/api/datasets/llamaindex/ParseBench/tree/{DATA_REVISION}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def acquire_annotations(cache: Path, manifest_path: Path) -> dict:
    """Acquire immutable annotations and complete source-file metadata before publishing."""
    cache.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in [*(f"{group}.jsonl" for group in GROUPS), "README.md", "eval.yaml"]:
        url = DATA_BASE + name
        with urlopen(url, timeout=90) as response:
            data = response.read()
        if name.endswith(".jsonl"):
            for line in data.splitlines():
                if not isinstance(json.loads(line), dict):
                    raise ValueError(f"Non-object annotation in {name}")
        digest = sha256(data)
        target = cache / digest
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f"Corrupt cached object: {digest}")
        if not target.exists():
            target.write_bytes(data)
        files[name] = {"sha256": digest, "bytes": len(data), "url": url}
    assets = {}
    url = API_BASE + "/docs?recursive=true&limit=1000"
    visited = set()
    while url:
        if url in visited or not url.startswith(API_BASE + "/docs?"):
            raise ValueError("Invalid or cyclic source inventory pagination")
        visited.add(url)
        with urlopen(url, timeout=90) as response:
            rows = json.load(response)
            next_link = re.search(r'<([^>]+)>; rel="next"', response.headers.get("Link", ""))
        for row in rows:
            if row["type"] == "file":
                if row["path"] in assets:
                    raise ValueError(f"Repeated source inventory path: {row['path']}")
                assets[row["path"]] = row
        url = next_link.group(1) if next_link else None
    manifest = {
        "dataset_revision": DATA_REVISION,
        "code_revision": CODE_REVISION,
        "files": files,
        "source_inventory_url": API_BASE + "/docs?recursive=true&limit=1000",
        "assets": dict(sorted(assets.items())),
    }
    build_inventory(cache, manifest)
    write_json_atomic(manifest_path, manifest)
    return manifest


def _read_object(cache: Path, file: dict) -> bytes:
    data = (cache / file["sha256"]).read_bytes()
    if sha256(data) != file["sha256"] or len(data) != file["bytes"]:
        raise ValueError("Annotation hash/size mismatch")
    return data


def build_inventory(cache: Path, manifest: dict) -> dict:
    """Group actual upstream rule rows into cases, keeping source identity explicit."""
    if manifest["dataset_revision"] != DATA_REVISION:
        raise ValueError("Unexpected dataset revision")
    if manifest["code_revision"] != CODE_REVISION:
        raise ValueError("Unexpected evaluator revision")
    if not set(GROUPS).issubset({Path(f).stem for f in manifest["files"]}):
        raise ValueError("Incomplete annotation inventory")
    cases = []
    groups = {}
    all_paths = set()
    content_ids = set()
    rule_ids = set()
    for group in GROUPS:
        name = f"{group}.jsonl"
        data = _read_object(cache, manifest["files"][name])
        grouped = {}
        count = 0
        for line_number, line in enumerate(data.splitlines(), 1):
            row = json.loads(line)
            rel = PurePosixPath(row["pdf"])
            if rel.is_absolute() or ".." in rel.parts or rel.parts[0] != "docs":
                raise ValueError(f"Unsafe source path at {name}:{line_number}")
            path = str(rel)
            if row["category"] != group or path not in manifest["assets"]:
                raise ValueError(f"Unknown group/source at {name}:{line_number}")
            rule_id = (group, path, row["id"])
            if rule_id in rule_ids:
                raise ValueError(f"Duplicate rule ID: {rule_id}")
            rule_ids.add(rule_id)
            rule = json.loads(row["rule"]) if isinstance(row["rule"], str) else row["rule"]
            if not isinstance(rule, dict):
                raise ValueError(f"Invalid rule at {name}:{line_number}")
            asset = manifest["assets"][path]
            content_id = asset.get("lfs", {}).get("oid") or asset["oid"]
            case = grouped.setdefault(
                path,
                {
                    "group": group,
                    "source_path": path,
                    "upstream_test_id": (
                        f"{'text' if group.startswith('text_') else group}/{rel.stem}"
                    ),
                    "source_content_id": content_id,
                    "source_bytes": asset["size"],
                    "source_url": DATA_BASE + quote(path),
                    "source_document_identity": None,
                    "source_page_count": None,
                    "domain": None,
                    "language": None,
                    "annotation_lines": [],
                    "rule_types": Counter(),
                    "tags": set(),
                    "annotation_pages": set(),
                },
            )
            case["annotation_lines"].append(line_number)
            case["rule_types"][row["type"]] += 1
            case["tags"].update(row.get("tags") or [])
            if row.get("page") is not None:
                case["annotation_pages"].add(row["page"])
            all_paths.add(path)
            content_ids.add(content_id)
            count += 1
        group_cases = []
        for _path, case in sorted(grouped.items()):
            line_numbers = case.pop("annotation_lines")
            ranges = []
            for number in line_numbers:
                if ranges and number == ranges[-1][1] + 1:
                    ranges[-1][1] = number
                else:
                    ranges.append([number, number])
            case["annotation_line_ranges"] = ranges
            case["annotation_count"] = len(line_numbers)
            case["rule_types"] = dict(sorted(case["rule_types"].items()))
            case["tags"] = sorted(case["tags"])
            case["annotation_pages"] = sorted(case["annotation_pages"])
            group_cases.append(case)
        groups[group] = {
            "annotation_rows": count,
            "cases": len(grouped),
            "tags_by_case": dict(
                sorted(Counter(t for c in group_cases for t in c["tags"]).items())
            ),
            "rule_types": dict(
                sorted(sum((Counter(c["rule_types"]) for c in group_cases), Counter()).items())
            ),
        }
        cases.extend(group_cases)
    return {
        "dataset_revision": manifest["dataset_revision"],
        "code_revision": manifest["code_revision"],
        "annotation_files": manifest["files"],
        "groups": groups,
        "totals": {
            "annotation_rows": len(rule_ids),
            "group_cases": len(cases),
            "unique_input_paths": len(all_paths),
            "unique_source_content_ids": len(content_ids),
            "original_document_count": None,
            "verified_total_pages": None,
        },
        "cases": cases,
        "unannotated_assets": sorted(set(manifest["assets"]) - all_paths),
        "limits": [
            "An upstream rule row is not a document or inference case.",
            "Input paths may be page excerpts and may duplicate content across groups.",
            "Original-document counts and page totals require additional provenance/inspection.",
            "Missing domain/language labels are unknown, not evidence of absence.",
            "No representative population or weights establish global business-use-case coverage.",
        ],
    }


def download_source(cache: Path, asset: dict) -> Path:
    """Verify a pinned source against the dataset's LFS SHA256 or Git blob identity."""
    rel = PurePosixPath(asset["path"])
    if rel.is_absolute() or ".." in rel.parts or rel.parts[0] != "docs":
        raise ValueError("Unsafe source path")
    with urlopen(DATA_BASE + quote(str(rel)), timeout=90) as response:
        data = response.read()
    lfs_hash = asset.get("lfs", {}).get("oid")
    digest = (
        sha256(data)
        if lfs_hash
        else hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    )
    if digest != (lfs_hash or asset["oid"]) or len(data) != asset["size"]:
        raise ValueError("Source hash/size mismatch")
    target = cache / sha256(data)
    cache.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != data:
        raise ValueError("Corrupt cached source")
    if not target.exists():
        target.write_bytes(data)
    return target


def build_assessment(inventory: dict, artifacts: dict, observations: dict) -> dict:
    """Join inspected evidence to known cases without inferring unobserved coverage."""
    if (
        artifacts["dataset_revision"] != inventory["dataset_revision"]
        or observations["dataset_revision"] != inventory["dataset_revision"]
    ):
        raise ValueError("Inspection dataset revision mismatch")
    sources = {case["source_path"] for case in inventory["cases"]}
    identities = {case["source_path"]: case["source_content_id"] for case in inventory["cases"]}
    inspected = {row["source_path"]: row for row in artifacts["inputs"]}
    judgments = {row["source_path"]: row for row in observations["inputs"]}
    if len(inspected) != len(artifacts["inputs"]) or len(judgments) != len(observations["inputs"]):
        raise ValueError("Duplicate inspection identity")
    if set(judgments) - set(inspected) or set(inspected) - sources:
        raise ValueError("Inspection must address known source inputs")
    evidence = []
    for path, judgment in sorted(judgments.items()):
        artifact = inspected[path]
        if len(identities[path]) == 64 and artifact["source_sha256"] != identities[path]:
            raise ValueError("Inspection differs from pinned source content")
        if judgment["source_sha256"] != artifact["source_sha256"]:
            raise ValueError("Observation uses different source bytes")
        if judgment["reviewed_pages"] != [p["page"] for p in artifact["pages"]]:
            raise ValueError("Observation does not cover declared inspected pages")
        evidence.append({**judgment, "artifact": artifact})
    return {
        "dataset_revision": inventory["dataset_revision"],
        "code_revision": inventory["code_revision"],
        "inspected_inputs": len(evidence),
        "known_input_paths": len(sources),
        "observations": evidence,
        "uninspected_inputs": [
            {"source_path": path, "coverage": "unknown"}
            for path in sorted(sources - set(judgments))
        ],
        "global_business_coverage_fraction": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["acquire", "inventory"])
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.action == "acquire":
        acquire_annotations(args.cache, args.manifest)
    else:
        if args.output is None:
            parser.error("inventory requires --output")
        manifest = json.loads(args.manifest.read_text())
        write_json_atomic(args.output, build_inventory(args.cache, manifest))


if __name__ == "__main__":
    main()
