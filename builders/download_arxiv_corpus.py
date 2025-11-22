"""
Download arXiv corpus for PDF-Bench.

This script downloads all papers specified in corpus/academic/arxiv_targets.yaml:
- PDF files
- LaTeX source (.tar.gz)
- ar5iv HTML5 versions (for ground truth generation)

The script validates downloads against the target YAML and logs all progress.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

import yaml
from arxiv_client import ArxivClient, ArxivClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("arxiv_download.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class ArxivCorpusDownloader:
    """Downloads arXiv corpus papers based on targets YAML."""

    def __init__(
        self,
        targets_path: Path,
        output_dir: Path,
        rate_limit: float = 1.0,
    ) -> None:
        """
        Initialize the corpus downloader.

        Args:
            targets_path: Path to arxiv_targets.yaml
            output_dir: Base directory for downloads
            rate_limit: Rate limit in seconds between requests
        """
        self.targets_path = targets_path
        self.output_dir = output_dir
        self.client = ArxivClient(rate_limit=rate_limit)

        # Create output directories
        self.pdf_dir = output_dir / "pdfs"
        self.source_dir = output_dir / "sources"
        self.ar5iv_dir = output_dir / "ar5iv"

        for directory in [self.pdf_dir, self.source_dir, self.ar5iv_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Track download results
        self.results: dict[str, Any] = {
            "successful": [],
            "failed": [],
            "metadata": {},
        }

    def load_targets(self) -> list[dict[str, Any]]:
        """
        Load target papers from YAML file.

        Returns:
            List of paper metadata dictionaries
        """
        logger.info(f"Loading targets from {self.targets_path}")
        with open(self.targets_path) as f:
            data = yaml.safe_load(f)

        documents = data.get("documents", [])
        logger.info(f"Found {len(documents)} papers to download")
        return documents

    def download_paper(self, paper: dict[str, Any]) -> bool:
        """
        Download a single paper (PDF, source, ar5iv HTML).

        Args:
            paper: Paper metadata dictionary from YAML

        Returns:
            True if all downloads successful, False otherwise
        """
        arxiv_id = paper["arxiv_id"]
        paper_id = paper["id"]
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Processing {paper_id}: {arxiv_id}")
        logger.info(f"Title: {paper['title']}")
        logger.info(f"{'=' * 80}")

        errors = []

        try:
            # 1. Fetch and verify metadata
            logger.info(f"[{paper_id}] Fetching metadata...")
            metadata = self.client.get_paper_metadata(arxiv_id)

            # Verify title matches (basic sanity check)
            if metadata["title"].lower() != paper["title"].lower():
                logger.warning(
                    f"[{paper_id}] Title mismatch:\n"
                    f"  YAML: {paper['title']}\n"
                    f"  API:  {metadata['title']}"
                )

            # Store metadata
            self.results["metadata"][arxiv_id] = metadata
            logger.info(f"[{paper_id}] Metadata fetched successfully")

            # 2. Download PDF
            pdf_path = self.pdf_dir / f"{arxiv_id}.pdf"
            if pdf_path.exists():
                logger.info(f"[{paper_id}] PDF already exists, skipping")
            else:
                logger.info(f"[{paper_id}] Downloading PDF...")
                try:
                    self.client.download_pdf(arxiv_id, pdf_path)
                    logger.info(f"[{paper_id}] PDF downloaded: {pdf_path.stat().st_size} bytes")
                except ArxivClientError as e:
                    error_msg = f"PDF download failed: {e}"
                    logger.error(f"[{paper_id}] {error_msg}")
                    errors.append(error_msg)

            # 3. Download LaTeX source
            source_path = self.source_dir / f"{arxiv_id}.tar.gz"
            if source_path.exists():
                logger.info(f"[{paper_id}] Source already exists, skipping")
            else:
                logger.info(f"[{paper_id}] Downloading LaTeX source...")
                try:
                    self.client.download_source(arxiv_id, source_path)
                    logger.info(
                        f"[{paper_id}] Source downloaded: {source_path.stat().st_size} bytes"
                    )
                except ArxivClientError as e:
                    error_msg = f"Source download failed: {e}"
                    logger.error(f"[{paper_id}] {error_msg}")
                    errors.append(error_msg)

            # 4. Download ar5iv HTML5 (critical for ground truth)
            ar5iv_path = self.ar5iv_dir / f"{arxiv_id}.html"
            if ar5iv_path.exists():
                logger.info(f"[{paper_id}] ar5iv HTML already exists, skipping")
            else:
                logger.info(f"[{paper_id}] Downloading ar5iv HTML5...")
                try:
                    self.client.download_ar5iv_html(arxiv_id, ar5iv_path)
                    logger.info(
                        f"[{paper_id}] ar5iv HTML downloaded: {ar5iv_path.stat().st_size} bytes"
                    )
                except ArxivClientError as e:
                    error_msg = f"ar5iv download failed: {e}"
                    logger.error(f"[{paper_id}] {error_msg}")
                    errors.append(error_msg)

                    # ar5iv is critical - log warning if unavailable
                    if paper.get("ar5iv_available"):
                        logger.warning(
                            f"[{paper_id}] ar5iv marked as available but download failed!"
                        )

            # Check if all downloads succeeded
            if not errors:
                self.results["successful"].append(
                    {
                        "id": paper_id,
                        "arxiv_id": arxiv_id,
                        "title": paper["title"],
                    }
                )
                logger.info(f"[{paper_id}] ✓ All downloads successful")
                return True
            else:
                self.results["failed"].append(
                    {
                        "id": paper_id,
                        "arxiv_id": arxiv_id,
                        "title": paper["title"],
                        "errors": errors,
                    }
                )
                logger.error(f"[{paper_id}] ✗ {len(errors)} error(s) occurred")
                return False

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(f"[{paper_id}] {error_msg}", exc_info=True)
            self.results["failed"].append(
                {
                    "id": paper_id,
                    "arxiv_id": arxiv_id,
                    "title": paper["title"],
                    "errors": [error_msg],
                }
            )
            return False

    def download_all(self) -> None:
        """Download all papers from targets YAML."""
        papers = self.load_targets()

        logger.info("\nStarting corpus download...")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Rate limit: {self.client.rate_limit}s between requests")

        for i, paper in enumerate(papers, 1):
            logger.info(f"\nProgress: {i}/{len(papers)}")
            self.download_paper(paper)

        # Save results summary
        self._save_results()

    def _save_results(self) -> None:
        """Save download results to JSON file."""
        results_path = self.output_dir / "download_results.json"

        summary = {
            "total": len(self.results["successful"]) + len(self.results["failed"]),
            "successful": len(self.results["successful"]),
            "failed": len(self.results["failed"]),
            "success_rate": (
                len(self.results["successful"])
                / (len(self.results["successful"]) + len(self.results["failed"]))
                if (len(self.results["successful"]) + len(self.results["failed"])) > 0
                else 0
            ),
        }

        results = {
            "summary": summary,
            "successful": self.results["successful"],
            "failed": self.results["failed"],
        }

        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        logger.info("\n" + "=" * 80)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total papers: {summary['total']}")
        logger.info(f"Successful: {summary['successful']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Success rate: {summary['success_rate']:.1%}")
        logger.info(f"\nResults saved to: {results_path}")

        if self.results["failed"]:
            logger.warning("\nFailed downloads:")
            for failure in self.results["failed"]:
                logger.warning(f"  - {failure['id']} ({failure['arxiv_id']})")
                for error in failure["errors"]:
                    logger.warning(f"    • {error}")


def main() -> None:
    """Main entry point."""
    # Paths (relative to script location)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    targets_path = project_root / "corpus" / "academic" / "arxiv_targets.yaml"
    output_dir = project_root / "corpus" / "academic" / "arxiv"

    # Verify targets file exists
    if not targets_path.exists():
        logger.error(f"Targets file not found: {targets_path}")
        sys.exit(1)

    # Create downloader and run
    downloader = ArxivCorpusDownloader(
        targets_path=targets_path,
        output_dir=output_dir,
        rate_limit=1.0,  # 1 request/second (polite)
    )

    try:
        downloader.download_all()
    except KeyboardInterrupt:
        logger.warning("\nDownload interrupted by user")
        downloader._save_results()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Download failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
