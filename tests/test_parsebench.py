"""Prevent rule counts, filename guesses and stale bytes from becoming coverage claims."""

import json
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from pdf_bench import parsebench

FIXTURE = Path(__file__).parent / "fixtures" / "parsebench"


@pytest.fixture
def snapshot(tmp_path):
    manifest = json.loads((FIXTURE / "manifest.json").read_text())
    cache = tmp_path / "objects"
    cache.mkdir()
    for name, info in manifest["files"].items():
        data = (FIXTURE / name.replace(".md", ".txt")).read_bytes()
        (cache / info["sha256"]).write_bytes(data)
    return cache, manifest


def test_rule_ids_reused_on_other_pages_do_not_drop_cases(snapshot):
    cache, manifest = snapshot
    result = parsebench.build_inventory(cache, manifest)
    assert result["groups"]["chart"]["cases"] == 2
    assert result["groups"]["chart"]["annotation_rows"] == 3
    assert result["totals"]["annotation_rows"] == 11
    assert result["totals"]["group_cases"] == 7
    assert result["totals"]["unique_input_paths"] == 6
    assert result["totals"]["original_document_count"] is None
    assert result["totals"]["verified_total_pages"] is None
    chart = [c for c in result["cases"] if c["group"] == "chart"]
    assert sorted(c["annotation_count"] for c in chart) == [1, 2]
    assert all(c["source_content_id"] and c["source_url"] for c in chart)


def test_shared_text_and_same_named_group_files_keep_distinct_identities(snapshot):
    cache, manifest = snapshot
    result = parsebench.build_inventory(cache, manifest)
    table = next(c for c in result["cases"] if c["source_path"] == "docs/table/0000027_page1.pdf")
    layout = next(c for c in result["cases"] if c["source_path"] == "docs/layout/0000027_page1.pdf")
    assert table["group"] != layout["group"]
    assert table["upstream_test_id"] != layout["upstream_test_id"]
    text = [c for c in result["cases"] if c["source_path"] == "docs/text/text_dense__baoutou.pdf"]
    assert {c["group"] for c in text} == {"text_content", "text_formatting"}
    assert len({c["source_content_id"] for c in text}) == 1
    assert len({c["upstream_test_id"] for c in text}) == 1


def test_unlabelled_business_domain_stays_unknown_despite_enterprise_filename(snapshot):
    cache, manifest = snapshot
    result = parsebench.build_inventory(cache, manifest)
    chart = next(c for c in result["cases"] if "E-Government" in c["source_path"])
    assert chart["domain"] is None
    assert chart["language"] is None
    assert chart["source_document_identity"] is None
    assert chart["source_page_count"] is None
    assert chart["tags"] == []
    assert chart["rule_types"] == {"chart_data_point": 2}
    assert chart["annotation_line_ranges"] == [[1, 2]]
    assert result["totals"]["unique_input_paths"] < result["totals"]["group_cases"]


def test_cli_rejects_changed_annotation_bytes_before_replacing_valid_inventory(snapshot, tmp_path):
    cache, manifest = snapshot
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(manifest))
    output = tmp_path / "inventory.json"
    args = [
        sys.executable,
        "-m",
        "pdf_bench.parsebench",
        "inventory",
        "--cache",
        str(cache),
        "--manifest",
        str(path),
        "--output",
        str(output),
    ]
    subprocess.run(args, check=True, capture_output=True)
    before = output.read_bytes()
    obj = cache / manifest["files"]["table.jsonl"]["sha256"]
    obj.write_bytes(obj.read_bytes() + b"\n")
    attempt = subprocess.run(args, capture_output=True, text=True)
    assert attempt.returncode != 0
    assert "hash/size mismatch" in attempt.stderr
    assert output.read_bytes() == before


def test_missing_annotation_group_is_not_reported_as_zero_coverage(snapshot):
    cache, manifest = snapshot
    del manifest["files"]["chart.jsonl"]
    with pytest.raises(ValueError, match="Incomplete annotation"):
        parsebench.build_inventory(cache, manifest)


def test_observed_fit_does_not_classify_uninspected_inputs_or_invent_global_coverage(snapshot):
    cache, manifest = snapshot
    work = Path(__file__).parents[1] / ".workspace/work/2026-10-13-benchmark-rebuild"
    recorded = json.loads((work / "parsebench-inspection-artifacts.json").read_text())
    notes = json.loads((work / "parsebench-inspection-observations.json").read_text())
    artifact = next(r for r in recorded["inputs"] if r["index"] == 1)
    note = next(r for r in notes["inputs"] if r["source_path"] == artifact["source_path"])
    artifacts = {**recorded, "inputs": [artifact]}
    observations = {**notes, "inputs": [note]}
    inventory = parsebench.build_inventory(cache, manifest)
    result = parsebench.build_assessment(inventory, artifacts, observations)
    assert result["inspected_inputs"] == 1
    assert result["observations"][0]["observed_document_form"] == "government report"
    assert result["global_business_coverage_fraction"] is None
    assert len(result["uninspected_inputs"]) == 5
    assert {r["coverage"] for r in result["uninspected_inputs"]} == {"unknown"}
    assert result["observations"][0]["artifact"]["pages"][0]["image_sha256"]
    observations["inputs"] = [{**note, "source_sha256": "changed-bytes"}]
    with pytest.raises(ValueError, match="different source bytes"):
        parsebench.build_assessment(inventory, artifacts, observations)


def test_acquisition_uses_pagination_and_validates_before_publishing(
    snapshot, tmp_path, monkeypatch
):
    _, manifest = snapshot
    web = tmp_path / "web"
    web.mkdir()
    for name in manifest["files"]:
        (web / name).write_bytes((FIXTURE / name.replace(".md", ".txt")).read_bytes())
    assets = list(manifest["assets"].values())

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/docs?"):
                second = "cursor=second" in self.path
                self.send_response(200)
                if not second:
                    self.send_header("Link", f'<{server_url}/docs?cursor=second>; rel="next"')
                self.end_headers()
                self.wfile.write(json.dumps(assets[2:] if second else assets[:2]).encode())
            else:
                super().do_GET()

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(web)))
    server_url = f"http://127.0.0.1:{server.server_port}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(parsebench, "DATA_BASE", server_url + "/")
    monkeypatch.setattr(parsebench, "API_BASE", server_url)
    try:
        target = tmp_path / "published.json"
        cache = tmp_path / "acquired"
        acquired = parsebench.acquire_annotations(cache, target)
        assert acquired["assets"] == manifest["assets"]
        assert parsebench.build_inventory(cache, acquired)["totals"]["annotation_rows"] == 11
        before = target.read_bytes()
        (web / "layout.jsonl").write_bytes(b'{"pdf":')
        with pytest.raises(ValueError):
            parsebench.acquire_annotations(cache, target)
        assert target.read_bytes() == before
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
