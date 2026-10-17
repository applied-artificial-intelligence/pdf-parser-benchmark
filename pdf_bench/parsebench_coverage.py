"""Measure the complete pinned source population without using parser scores."""

import argparse
import csv
import hashlib
import json
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pdf_bench.parsebench import download_source
from pdf_bench.persistence import write_json_atomic

FAMILIES = {
    "insurance": r"\b(insurance|insurer|underwriting|policyholder|serff|premium rates?)\b",
    "financial_reporting": (
        r"\b(financial statements?|annual report|balance sheets?|"
        r"cash flows?|shareholders?|form 10-k)\b"
    ),
    "agreements_and_law": (
        r"\b(agreement|hereby|plaintiff|defendant|statute|legislation|"
        r"contractor|contract)\b"
    ),
    "government_and_regulation": (
        r"\b(department of|regulation|regulatory|municipal|"
        r"federal register|government|ministry)\b"
    ),
    "transactional_records": (
        r"\b(invoice|purchase order|timesheet|change order|bill to|"
        r"remit to|receipt)\b"
    ),
    "presentations": (
        r"\b(presentation|earnings call|investor day|"
        r"forward-looking statements|all rights reserved.*slide)\b"
    ),
    "technical_and_academic": (
        r"\b(abstract|references|doi:|arxiv|algorithm|theorem|"
        r"proceedings|experiment)\b"
    ),
    "healthcare": (
        r"\b(patient|clinical|medication|medical|hospital|healthcare|"
        r"medicare|medicaid)\b"
    ),
    "operational_and_hr": (
        r"\b(job description|employee|meeting minutes|agenda|"
        r"curriculum vitae|resume|application form)\b"
    ),
}


def source_identity(data: bytes, asset: dict) -> None:
    lfs = asset.get("lfs", {}).get("oid")
    value = (
        hashlib.sha256(data).hexdigest()
        if lfs
        else hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    )
    if value != (lfs or asset["oid"]) or len(data) != asset["size"]:
        raise ValueError(f"Source bytes differ from pinned identity: {asset['path']}")


def classify(text: str) -> dict:
    matches = {}
    for family, pattern in FAMILIES.items():
        found = list(re.finditer(pattern, text, re.I))
        if found:
            matches[family] = {
                "matches": len(found),
                "evidence": [text[max(0, m.start() - 45) : m.end() + 65] for m in found[:3]],
            }
    return {
        "method": "content_keyword_candidates_v1",
        "status": "candidate_labels_require_review" if matches else "unknown",
        "candidates": matches,
    }


def build_workload_index(coverage: dict, observations: list[dict]) -> dict:
    sources = {r["source_path"]: r for r in coverage["inputs"]}
    reviewed: dict[str, list[dict]] = {}
    for row in observations:
        name = row["source_path"]
        if name not in sources or row["source_sha256"] != sources[name]["sha256"]:
            raise ValueError("Visual classification does not match qualified source bytes")
        reviewed.setdefault(name, []).append(row)
    rows = []
    for name, source in sorted(sources.items()):
        rows.append(
            {
                "source_path": name,
                "sha256": source["sha256"],
                "source_format": source["source_format"],
                "page_count": source["page_count"],
                "groups": source["groups"],
                "tags": source["tags"],
                "text_characters": source["text_characters"],
                "family_candidates": list(source["family_classification"]["candidates"]),
                "candidate_evidence": source["family_classification"]["candidates"],
                "visual_observations": reviewed.get(name, []),
                "classification_status": "visually_observed"
                if name in reviewed
                else "automatic_candidates_or_unknown",
            }
        )
    return {
        "inputs": rows,
        "input_paths": len(rows),
        "visually_reviewed_inputs": len(reviewed),
        "classification_limits": (
            "Automatic keyword candidates are retrieval aids, not verified domain prevalence. "
            "Visual forms do not certify annotation correctness or original-document identity."
        ),
    }


def inspect_source(path: Path, asset: dict, groups: list[str], tags: list[str]) -> dict:
    import pymupdf

    data = path.read_bytes()
    source_identity(data, asset)
    with pymupdf.open(stream=data, filetype="pdf") as document:
        if document.needs_pass:
            raise ValueError(f"Encrypted public input: {asset['path']}")
        pages = []
        texts = []
        for page in document:
            text = page.get_text(sort=True)
            texts.append(text)
            pages.append(
                {
                    "page": page.number + 1,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "text_characters": len(text.strip()),
                    "image_count": len(page.get_images()),
                }
            )
        text = "\n".join(texts).encode("utf-8", "backslashreplace").decode("utf-8")
        metadata = {
            k: v.encode("utf-8", "backslashreplace").decode("utf-8") if isinstance(v, str) else v
            for k, v in document.metadata.items()
        }
        return {
            "source_path": asset["path"],
            "source_format": Path(asset["path"]).suffix.lower().lstrip("."),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "groups": sorted(groups),
            "tags": sorted(tags),
            "page_count": len(document),
            "pages": pages,
            "pdf_metadata": metadata,
            "unicode_policy": "Invalid PDF Unicode surrogates retained as literal escapes",
            "text_characters": len(text.strip()),
            "text_excerpt": text[:1800],
            "family_classification": classify(text),
            "original_document_identity": None,
            "original_language": None,
        }


def acquire_population(snapshot: Path, inventory: Path, cache: Path, output: Path) -> dict:
    manifest = json.loads(snapshot.read_text())
    indexed = json.loads(inventory.read_text())
    cases = indexed["cases"]
    membership = sorted({c["source_path"] for c in cases})
    if (
        len(cases) != indexed["totals"]["group_cases"]
        or len(membership) != indexed["totals"]["unique_input_paths"]
    ):
        raise ValueError("Incomplete annotation membership")
    source_dir = cache / "sources"
    objects = cache / "objects"
    source_dir.mkdir(parents=True, exist_ok=True)

    def acquire(name: str) -> tuple[str, Path]:
        asset = manifest["assets"][name]
        target = source_dir / name
        if target.exists():
            source_identity(target.read_bytes(), asset)
        else:
            for attempt in range(5):
                try:
                    downloaded = download_source(objects, asset)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(downloaded.read_bytes())
                    break
                except Exception:
                    if attempt == 4:
                        raise
                    time.sleep(2**attempt)
        return name, target

    rows = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        for name, target in executor.map(acquire, membership):
            matching = [c for c in cases if c["source_path"] == name]
            rows.append(
                inspect_source(
                    target,
                    manifest["assets"][name],
                    [c["group"] for c in matching],
                    sorted({t for c in matching for t in c["tags"]}),
                )
            )
            if len(rows) % 100 == 0:
                print(f"Verified and inspected {len(rows)}/{len(membership)} inputs", flush=True)

    result = {
        "dataset_revision": manifest["dataset_revision"],
        "code_revision": manifest["code_revision"],
        "snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        "inventory_sha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
        "classification": "Automatic content candidates; not verified family prevalence",
        "source_root": str(source_dir.resolve()),
        "inputs": rows,
        "summary": {
            "input_paths": len(rows),
            "unique_sha256": len({r["sha256"] for r in rows}),
            "pdf_inputs": sum(r["source_format"] == "pdf" for r in rows),
            "image_inputs": sum(r["source_format"] != "pdf" for r in rows),
            "physical_pdf_pages": sum(r["page_count"] for r in rows if r["source_format"] == "pdf"),
            "page_or_image_units": sum(r["page_count"] for r in rows),
            "page_count_note": "Image files are page-like units, excluded from physical_pdf_pages.",
            "page_counts": dict(Counter(r["page_count"] for r in rows)),
            "no_text_layer_inputs": sum(r["text_characters"] == 0 for r in rows),
            "sparse_text_layer_inputs_below_100_characters": sum(
                r["text_characters"] < 100 for r in rows
            ),
            "family_candidate_counts_overlapping": dict(
                Counter(k for r in rows for k in r["family_classification"]["candidates"])
            ),
            "unknown_family_inputs": sum(
                r["family_classification"]["status"] == "unknown" for r in rows
            ),
        },
    }
    write_json_atomic(output, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--index-only", action="store_true")
    args = parser.parse_args()
    result = (
        json.loads((args.unit / "parsebench-source-coverage.json").read_text())
        if args.index_only
        else acquire_population(
            args.unit / "parsebench-snapshot.json",
            args.unit / "parsebench-inventory.json",
            args.cache,
            args.unit / "parsebench-source-coverage.json",
        )
    )
    observations = []
    for name in (
        "parsebench-inspection-observations.json",
        "parsebench-comparison-qualified-selection.json",
        "coverage-sparse-review-observations.json",
    ):
        value = json.loads((args.unit / name).read_text())
        for row in value.get("observations", value.get("inputs", [])):
            observations.append(
                {
                    "source_path": row["source_path"],
                    "source_sha256": row.get("source_sha256", row.get("sha256")),
                    "form": row.get("observed_document_form", row.get("page_form_observation")),
                    "reviewed_pages": row["reviewed_pages"],
                }
            )
    index = build_workload_index(result, observations)
    write_json_atomic(args.unit / "parsebench-workload-index.json", index)
    target = args.unit / "parsebench-workload-index.csv"
    temporary = target.with_suffix(".csv.incomplete")
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(
            [
                "source",
                "sha256",
                "format",
                "pages",
                "dimensions",
                "tags",
                "text_characters",
                "family_candidates_unverified",
                "visual_form",
                "classification_status",
            ]
        )
        for row in index["inputs"]:
            writer.writerow(
                [
                    row["source_path"],
                    row["sha256"],
                    row["source_format"],
                    row["page_count"],
                    ";".join(row["groups"]),
                    ";".join(row["tags"]),
                    row["text_characters"],
                    ";".join(row["family_candidates"]),
                    "; ".join(r["form"] for r in row["visual_observations"]),
                    row["classification_status"],
                ]
            )
    temporary.replace(target)
    print(json.dumps(result["summary"], indent=2))
    print("Visually reviewed distinct inputs:", index["visually_reviewed_inputs"])


if __name__ == "__main__":
    main()
