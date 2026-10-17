"""Retain the used editable PDFsmith implementation as a local replay wheel and dependency pins."""

import argparse
import base64
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import zipfile
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from pdf_bench.invoice_comparison import runtime_identity


def freeze(output: Path) -> dict:
    snapshot = runtime_identity()
    spec = importlib.util.find_spec("pdfsmith")
    root = Path(spec.origin).parent
    distribution = importlib.metadata.distribution("pdfsmith")
    version = distribution.version
    info = f"pdfsmith-{version}.dist-info"
    files = {}
    for name, expected in snapshot["source_files"]["pdfsmith"].items():
        data = (root / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("Used PDFsmith source changed while snapshotting")
        files[f"pdfsmith/{name}"] = data
    files[f"{info}/METADATA"] = distribution.read_text("METADATA").encode()
    files[f"{info}/WHEEL"] = (
        b"Wheel-Version: 1.0\nGenerator: PDF-Bench scoped editable-install snapshot\n"
        b"Root-Is-Purelib: true\nTag: py3-none-any\n"
    )
    record = []
    for name, data in sorted(files.items()):
        encoded = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
        record.append(f"{name},sha256={encoded},{len(data)}")
    record.append(f"{info}/RECORD,,")
    files[f"{info}/RECORD"] = ("\n".join(record) + "\n").encode()
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as wheel:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (2026, 10, 15, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            wheel.writestr(entry, data)
    output.mkdir(parents=True, exist_ok=False)
    wheel_name = f"pdfsmith-{version}-py3-none-any.whl"
    (output / wheel_name).write_bytes(archive.getvalue())
    required = [
        Requirement(value)
        for value in importlib.metadata.requires("pdf-bench")
        if Requirement(value).marker is None or Requirement(value).marker.evaluate({"extra": ""})
    ]
    required += [Requirement(name) for name in ["pypdf", "pdfplumber", "PyMuPDF", "reportlab"]]
    pins = {}
    while required:
        requirement = required.pop()
        name = canonicalize_name(requirement.name)
        if name in pins:
            continue
        dependency = importlib.metadata.distribution(name)
        if requirement.specifier and dependency.version not in requirement.specifier:
            raise ValueError(f"Installed dependency does not satisfy its contract: {requirement}")
        pins[name] = dependency.version
        for value in dependency.requires or []:
            child = Requirement(value)
            if child.marker is None or child.marker.evaluate({"extra": ""}):
                required.append(child)
    (output / "requirements-pins.in").write_text(
        "".join(f"{name}=={version}\n" for name, version in sorted(pins.items()))
    )
    manifest = {
        "purpose": "Local replay of the two used backends; not an official PDFsmith release",
        "scope": "Exact used shared modules and pypdf/pdfplumber backends only; no paid providers",
        "pdfsmith_distribution_version": version,
        "pdfsmith_source_version": snapshot["pdfsmith_source_version"],
        "wheel": wheel_name,
        "wheel_sha256": hashlib.sha256(archive.getvalue()).hexdigest(),
        "used_pdfsmith_source_sha256": snapshot["source_files"]["pdfsmith"],
        "python": snapshot["python"],
        "requirements": pins,
        "distribution_metadata_sha256": hashlib.sha256(files[f"{info}/METADATA"]).hexdigest(),
    }
    (output / "runtime-provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    result = freeze(arguments.output)
    print(
        json.dumps(
            {
                "directory": str(arguments.output),
                "wheel_sha256": result["wheel_sha256"],
                "pinned_dependencies": len(result["requirements"]),
            }
        )
    )
