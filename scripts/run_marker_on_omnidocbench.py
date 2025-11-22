#!/usr/bin/env python3
"""Run Marker parser on OmniDocBench demo images for framework comparison."""

import sys
from pathlib import Path

from tqdm import tqdm

# Add pdf_bench to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_bench.systems.marker_ollama import MarkerOllamaParser


def main():
    # Paths
    omnidoc_images = Path("/home/stefan/projects/OmniDocBench/demo_data/omnidocbench_demo/images")
    output_dir = Path("/home/stefan/projects/OmniDocBench/demo_data/pdfbench_marker_output")
    output_dir.mkdir(exist_ok=True)

    # Get all image files
    images = sorted(omnidoc_images.glob("*.jpg"))
    print(f"Found {len(images)} images to process")

    # Initialize parser
    parser = MarkerOllamaParser()

    # Process each image
    for img_path in tqdm(images, desc="Processing images"):
        try:
            # Parse image to markdown
            output_path = parser.parse(img_path, output_dir)
            print(f"✓ {img_path.name} → {output_path.name}")
        except Exception as e:
            print(f"✗ {img_path.name}: {e}")


if __name__ == "__main__":
    main()
