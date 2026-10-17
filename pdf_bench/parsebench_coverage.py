"""Measure the complete pinned source population without using parser scores."""

import argparse
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
            "physical_pages_over_paths": sum(r["page_count"] for r in rows),
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
    args = parser.parse_args()
    result = acquire_population(
        args.unit / "parsebench-snapshot.json",
        args.unit / "parsebench-inventory.json",
        args.cache,
        args.unit / "parsebench-source-coverage.json",
    )
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
