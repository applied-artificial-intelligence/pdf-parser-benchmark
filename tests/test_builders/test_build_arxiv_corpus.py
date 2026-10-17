"""Exercise the retained arXiv downloader instead of an absent LaTeX builder."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

from builders.arxiv_client import ArxivClient
from builders.download_arxiv_corpus import ArxivCorpusDownloader


@pytest.fixture
def downloader(tmp_path):
    requests = []
    faults = set()
    pdf = (Path(__file__).parents[1] / "fixtures/sample.pdf").read_bytes()
    atom = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry>
<title>Local paper</title><summary>Local abstract</summary>
<author><name>Test Author</name></author><category term="cs.AI"/>
<published>2025-01-01</published><updated>2025-01-02</updated>
</entry></feed>"""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            if self.path.split("?")[0] in faults:
                self.send_error(503)
                return
            if self.path.startswith("/api?"):
                data, kind = atom, "application/atom+xml"
            elif self.path.startswith("/pdf/"):
                data, kind = pdf, "application/pdf"
            elif self.path.startswith("/source/"):
                data, kind = b"local retained source archive", "application/gzip"
            else:
                data, kind = b"<html><body>Local paper</body></html>", "text/html"
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    paper = {"id": "arxiv_001", "arxiv_id": "2303.18223", "title": "Local paper"}
    target = tmp_path / "targets.yaml"
    target.write_text(yaml.safe_dump({"documents": [paper]}))
    builder = ArxivCorpusDownloader(target, tmp_path / "corpus", rate_limit=0)
    client = ArxivClient(rate_limit=0, max_retries=0)
    base = f"http://127.0.0.1:{server.server_port}"
    client.API_BASE, client.PDF_BASE = base + "/api", base + "/pdf"
    client.SOURCE_BASE, client.AR5IV_BASE = base + "/source", base + "/html"
    builder.client = client
    try:
        yield builder, requests, faults, paper
    finally:
        client.session.close()
        server.shutdown()
        server.server_close()
        thread.join()


def test_download_all_retains_actual_pdf_source_html_and_counts(downloader):
    builder, requests, _, _ = downloader
    builder.download_all()
    report = json.loads((builder.output_dir / "download_results.json").read_text())
    assert report["summary"] == {"total": 1, "successful": 1, "failed": 0, "success_rate": 1.0}
    assert (builder.pdf_dir / "2303.18223.pdf").read_bytes().startswith(b"%PDF-")
    assert (
        builder.source_dir / "2303.18223.tar.gz"
    ).read_bytes() == b"local retained source archive"
    assert "<body>Local paper" in (builder.ar5iv_dir / "2303.18223.html").read_text()
    assert len(requests) == 4
    assert builder.results["metadata"]["2303.18223"]["authors"] == ["Test Author"]


def test_failed_source_does_not_count_partial_paper_as_success(downloader):
    builder, _, faults, _ = downloader
    faults.add("/source/2303.18223")
    builder.download_all()
    report = json.loads((builder.output_dir / "download_results.json").read_text())
    assert report["summary"] == {"total": 1, "successful": 0, "failed": 1, "success_rate": 0.0}
    assert "Source download failed" in report["failed"][0]["errors"][0]
    assert (builder.pdf_dir / "2303.18223.pdf").exists()
    assert (builder.ar5iv_dir / "2303.18223.html").exists()
    assert not (builder.source_dir / "2303.18223.tar.gz").exists()


def test_existing_downloads_are_retained_on_repeat(downloader):
    builder, requests, faults, paper = downloader
    assert builder.download_paper(paper)
    before = (builder.pdf_dir / "2303.18223.pdf").read_bytes()
    faults.update({"/pdf/2303.18223", "/source/2303.18223", "/html/2303.18223"})
    assert builder.download_paper(paper)
    assert len(requests) == 5
    assert (builder.pdf_dir / "2303.18223.pdf").read_bytes() == before


def test_empty_target_population_has_zero_counts_without_division_error(downloader):
    builder, requests, _, _ = downloader
    builder.targets_path.write_text("documents: []\n")
    builder.download_all()
    report = json.loads((builder.output_dir / "download_results.json").read_text())
    assert report["summary"] == {"total": 0, "successful": 0, "failed": 0, "success_rate": 0}
    assert requests == []


def test_missing_target_is_not_silently_reported_as_empty(downloader):
    builder, requests, _, _ = downloader
    builder.targets_path.unlink()
    with pytest.raises(FileNotFoundError):
        builder.download_all()
    assert requests == []
    assert not (builder.output_dir / "download_results.json").exists()
