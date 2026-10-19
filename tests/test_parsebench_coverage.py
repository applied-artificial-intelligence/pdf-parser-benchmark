import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image
from reportlab.pdfgen.canvas import Canvas

from pdf_bench.parsebench_coverage import (
    acquire_population,
    build_workload_index,
    classify,
    inspect_source,
)


def source(tmp_path: Path) -> tuple[Path, dict]:
    path = tmp_path / "invoice.pdf"
    canvas = Canvas(str(path))
    canvas.drawString(50, 700, "Insurance annual report: financial statements and cash flows")
    canvas.showPage()
    canvas.save()
    data = path.read_bytes()
    return path, {
        "path": "docs/text/invoice.pdf",
        "oid": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
        "size": len(data),
    }


def test_family_candidates_use_document_content_and_leave_unidentified_sources_unknown(tmp_path):
    path, asset = source(tmp_path)
    row = inspect_source(path, asset, ["text_content"], [])
    assert row["page_count"] == 1
    assert "financial_reporting" in row["family_classification"]["candidates"]
    assert "insurance" in row["family_classification"]["candidates"]
    assert "transactional_records" not in row["family_classification"]["candidates"]
    assert row["original_document_identity"] is None
    assert classify("")["status"] == "unknown"


def test_changed_pdf_bytes_cannot_reuse_pinned_coverage_identity(tmp_path):
    path, asset = source(tmp_path)
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="pinned identity"):
        inspect_source(path, asset, ["text_content"], [])


def test_visual_labels_cannot_be_applied_to_a_different_source_rendition(tmp_path):
    path, asset = source(tmp_path)
    row = inspect_source(path, asset, ["text_content"], [])
    review = {"source_path": row["source_path"], "source_sha256": row["sha256"], "form": "report"}
    index = build_workload_index({"inputs": [row]}, [review])
    assert index["inputs"][0]["classification_status"] == "visually_observed"
    review["source_sha256"] = "different rendition"
    with pytest.raises(ValueError, match="qualified source bytes"):
        build_workload_index({"inputs": [row]}, [review])


def test_omitted_source_does_not_publish_incomplete_full_coverage(tmp_path):
    snapshot = tmp_path / "snapshot.json"
    inventory = tmp_path / "inventory.json"
    output = tmp_path / "coverage.json"
    snapshot.write_text(json.dumps({"assets": {}}))
    inventory.write_text(
        json.dumps({"cases": [], "totals": {"group_cases": 1, "unique_input_paths": 1}})
    )
    output.write_text("previous valid inventory")
    with pytest.raises(ValueError, match="membership"):
        acquire_population(snapshot, inventory, tmp_path / "cache", output)
    assert output.read_text() == "previous valid inventory"


def test_image_inputs_are_not_reported_as_physical_pdf_pages(tmp_path):
    pdf, pdf_asset = source(tmp_path)
    image = tmp_path / "scan.jpg"
    Image.new("RGB", (200, 300), "white").save(image)
    data = image.read_bytes()
    image_asset = {
        "path": "docs/layout/scan.jpg",
        "size": len(data),
        "oid": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
    }
    assets = [pdf_asset, image_asset]
    for path, asset in [(pdf, pdf_asset), (image, image_asset)]:
        target = tmp_path / "cache/sources" / asset["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    snapshot = tmp_path / "snapshot.json"
    inventory = tmp_path / "inventory.json"
    snapshot.write_text(
        json.dumps(
            {
                "dataset_revision": "fixture",
                "code_revision": "fixture",
                "assets": {a["path"]: a for a in assets},
            }
        )
    )
    inventory.write_text(
        json.dumps(
            {
                "cases": [
                    {"source_path": a["path"], "group": "layout", "tags": []} for a in assets
                ],
                "totals": {"group_cases": 2, "unique_input_paths": 2},
            }
        )
    )
    result = acquire_population(snapshot, inventory, tmp_path / "cache", tmp_path / "output.json")
    assert result["summary"]["pdf_inputs"] == 1
    assert result["summary"]["image_inputs"] == 1
    assert result["summary"]["physical_pdf_pages"] == 1
    assert result["summary"]["page_or_image_units"] == 2
    index = build_workload_index(result, [])
    assert index["input_paths"] == 2
    assert index["visually_reviewed_inputs"] == 0
    assert all(
        r["classification_status"] == "automatic_candidates_or_unknown" for r in index["inputs"]
    )
