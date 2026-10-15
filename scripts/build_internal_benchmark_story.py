"""Generate immutable registry-backed historical evidence and a validated latest pointer."""

import argparse
from pathlib import Path

from pdf_bench.inventory import publish_registry

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data_exports/reconstruction"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)
    pointer = publish_registry(args.repo_root, args.output_dir)
    print(f"Completed registry bundle: {args.output_dir / pointer['bundle']}")


if __name__ == "__main__":
    main()
