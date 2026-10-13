"""Source-first, uncached smoke comparison of installed lightweight PDF parsers."""

import argparse
import hashlib
import inspect
import json
import platform
import re
import signal
import subprocess
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

from pdf_bench.config import (
    BenchmarkConfig,
    DocumentFilter,
    MetricConfig,
    OutputConfig,
    ParserConfig,
)
from pdf_bench.loader import DocumentInfo, LoadedConfig
from pdf_bench.persistence import save_results, write_json_atomic
from pdf_bench.runner import BenchmarkRunner
from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.metadata import DocumentMetadata

FIELDS = {
    "Invoice ID": "INV-2026-013",
    "Vendor": "Example Components",
    "Total": "1275.40",
    "Currency": "USD",
    "Due date": "2026-11-12",
}
DOCUMENT_IDS = ("inline", "columns", "raster", "corrupt")
BACKENDS = ("pypdf", "pdfplumber")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_documents(directory: Path) -> list[DocumentInfo]:
    """Render explicit semantic references before any parser sees an input."""
    import pymupdf
    from reportlab.pdfgen.canvas import Canvas

    directory.mkdir(parents=True, exist_ok=False)
    reference = "Invoice summary\n" + "\n".join(f"{k}: {v}" for k, v in FIELDS.items())
    for doc_id in ("inline", "columns"):
        canvas = Canvas(str(directory / f"{doc_id}.pdf"), invariant=1)
        canvas.setFont("Helvetica", 12)
        canvas.drawString(60, 760, "Invoice summary")
        for index, (label, value) in enumerate(FIELDS.items()):
            y = 720 - 30 * index
            text = f"{label}: {value}" if doc_id == "inline" else f"{label}:"
            canvas.drawString(60, y, text)
        if doc_id == "columns":
            for index, value in enumerate(FIELDS.values()):
                canvas.drawString(220, 720 - 30 * index, value)
        canvas.save()

    with pymupdf.open(directory / "inline.pdf") as source:
        image = source[0].get_pixmap(dpi=144).tobytes("png")
        with pymupdf.open() as raster:
            page = raster.new_page(width=source[0].rect.width, height=source[0].rect.height)
            page.insert_image(page.rect, stream=image)
            raster.save(directory / "raster.pdf", deflate=True, no_new_id=True)
    (directory / "corrupt.pdf").write_bytes(b"%PDF-1.7\ntruncated upload\n")

    documents = []
    for doc_id in DOCUMENT_IDS:
        (directory / f"{doc_id}.md").write_text(reference, encoding="utf-8")
        fields = FIELDS if doc_id != "corrupt" else None
        (directory / f"{doc_id}.json").write_text(
            json.dumps({"document_id": doc_id, "fields": fields}, indent=2), encoding="utf-8"
        )
        documents.append(
            DocumentInfo(
                doc_id=doc_id,
                input_path=directory / f"{doc_id}.pdf",
                ground_truth_path=directory / f"{doc_id}.md",
                metadata=DocumentMetadata(doc_id=doc_id, corpus="synthetic", domain="pandoc"),
            )
        )
    return documents


class FreshLocalParser(BaseParser):
    """Use the installed PDFsmith backend without reading or writing its adapter cache."""

    def __init__(self, backend_name: str, timeout_seconds: int = 15) -> None:
        from pdfsmith import get_backend

        if backend_name not in BACKENDS:
            raise ValueError(f"Only these local backends are allowed: {BACKENDS}")
        self.backend_name = backend_name
        self.timeout_seconds = timeout_seconds
        self.backend = get_backend(backend_name)

    @property
    def name(self) -> str:
        return f"fresh-pdfsmith-{self.backend_name}"

    @property
    def version(self) -> str:
        return version(self.backend_name)

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        def timeout_handler(signum: int, frame: Any) -> None:
            raise TimeoutError(f"Parser exceeded {self.timeout_seconds} seconds")

        previous_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.timeout_seconds)
        try:
            markdown = self.backend.parse(pdf_path)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)
        output_path = output_dir / self.name / f"{pdf_path.stem}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        return output_path


def loaded_config(documents: list[DocumentInfo], output_dir: Path) -> LoadedConfig:
    config = BenchmarkConfig(
        name="Source-first invoice field smoke comparison",
        description="Shared inputs, no cache, two local parsers, explicit failure control",
        corpus_dir=str(documents[0].input_path.parent),
        document_filter=DocumentFilter(include_doc_ids=list(DOCUMENT_IDS)),
        parser_config=ParserConfig(parsers=list(BACKENDS)),
        metric_config=MetricConfig(metrics=["edit_similarity", "chrf++", "teds"]),
        output_config=OutputConfig(results_dir=str(output_dir)),
        parallel_workers=1,
    )
    return LoadedConfig(config, documents, [FreshLocalParser(p) for p in BACKENDS], output_dir)


def grade_fields(text: str, expected: dict[str, str]) -> dict[str, Any]:
    """Check label/value associations, not mere occurrence of expected value tokens."""
    actual = {}
    for label in expected:
        matches = re.findall(rf"(?m)^{re.escape(label)}:[ \t]*(.+)$", text)
        values = {value.strip() for value in matches}
        actual[label] = next(iter(values)) if len(values) == 1 else None
    correct = {key: actual[key] == value for key, value in expected.items()}
    return {
        "extracted_fields": actual,
        "correct_fields": correct,
        "field_accuracy": sum(correct.values()) / len(expected),
        "all_fields_correct": all(correct.values()),
    }


def run_comparison(output_dir: Path) -> dict[str, Any]:
    """Execute once in a new directory; retained benchmark results are never overwritten."""
    import pdfsmith

    output_dir.mkdir(parents=True, exist_ok=False)
    documents = build_documents(output_dir / "inputs")
    inputs = {
        doc.doc_id: {
            "input_sha256": file_hash(doc.input_path),
            "text_reference_sha256": file_hash(doc.ground_truth_path),
            "field_reference_sha256": file_hash(doc.input_path.with_suffix(".json")),
            "reference_available": doc.doc_id != "corrupt",
        }
        for doc in documents
    }
    config = loaded_config(documents, output_dir / "outputs")
    results = BenchmarkRunner(config, parallel_workers=1).run()
    save_results(
        results,
        output_dir / "runner-results.json",
        parser_versions={parser.name: parser.version for parser in config.parser_instances},
    )
    attempts = []
    for result in results.results:
        output = config.results_dir / result.parser_name / f"{result.document_id}.md"
        status = "success" if result.success else "failed"
        if result.error and "exceeded" in result.error:
            status = "timeout"
        attempt = {
            "document_id": result.document_id,
            "parser": result.parser_name,
            "status": status,
            "error": result.error,
            "execution_mode": "fresh-uncached",
            "parse_time_seconds": result.parse_time_seconds if result.success else None,
            "output_sha256": file_hash(output) if result.success else None,
            "task_metrics": None,
        }
        if result.success and result.document_id != "corrupt":
            attempt["task_metrics"] = grade_fields(output.read_text(encoding="utf-8"), FIELDS)
        attempts.append(attempt)
    common = [
        doc_id
        for doc_id in DOCUMENT_IDS
        if doc_id != "corrupt"
        and all(
            any(
                a["document_id"] == doc_id and a["parser"] == p.name and a["status"] == "success"
                for a in attempts
            )
            for p in config.parser_instances
        )
    ]
    summary = {}
    for parser in config.parser_instances:
        rows = [a for a in attempts if a["parser"] == parser.name]
        comparable = [a["task_metrics"] for a in rows if a["document_id"] in common]
        summary[parser.name] = {
            "attempted": len(rows),
            "parse_successes": sum(a["status"] == "success" for a in rows),
            "parse_failures": sum(a["status"] == "failed" for a in rows),
            "timeouts": sum(a["status"] == "timeout" for a in rows),
            "common_scored_documents": len(comparable),
            "mean_field_accuracy": (
                sum(a["field_accuracy"] for a in comparable) / len(comparable)
                if comparable
                else None
            ),
            "task_successes": sum(a["all_fields_correct"] for a in comparable),
        }
    repo = Path(__file__).resolve().parents[1]
    implementation_paths = [
        Path(__file__),
        repo / "pdf_bench/runner.py",
        repo / "pdf_bench/persistence.py",
        repo / "pdf_bench/systems/tika_parser.py",
        repo / "pdf_bench/loader.py",
        repo / "pdf_bench/config.py",
        Path(pdfsmith.__file__),
        *(Path(inspect.getfile(type(p.backend))) for p in config.parser_instances),
    ]
    pack = {
        "schema_version": 1,
        "executed_at": results.timestamp,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True
        ).strip(),
        "source_is_dirty": bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=repo, text=True).strip()
        ),
        "implementation_sha256": {str(p): file_hash(p) for p in implementation_paths},
        "versions": {
            p: version(p) for p in ("pdfsmith", "pypdf", "pdfplumber", "reportlab", "PyMuPDF")
        },
        "pdfsmith_declared_version": pdfsmith.__version__,
        "python": platform.python_version(),
        "backend_options": {},
        "cache_policy": "No adapter cache calls, no checkpoint reuse, each input parsed once",
        "timeout_seconds": 15,
        "inputs": inputs,
        "attempts": attempts,
        "common_valid_inputs": common,
        "summary": summary,
        "limitations": [
            "Three synthetic variants and one corrupt control; not a population estimate",
            "The fixed label/value extractor is a baseline, not a universal invoice extractor",
            "Raster inputs require OCR; these backends do not perform OCR",
            "Text similarity is diagnostic; field association determines the declared task score",
            "Timing includes local wrapper work and first-import effects, not a latency ranking",
            "Existing SEC, invoice, presentation, arXiv and paid tracks are retained separately",
        ],
    }
    write_json_atomic(output_dir / "comparison.json", pack)
    return pack


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pack = run_comparison(args.output)
    print(json.dumps(pack["summary"], indent=2))


if __name__ == "__main__":
    main()
