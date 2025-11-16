"""
Test ArxivClient on real arXiv papers.

This script tests the client with actual API calls to verify functionality.
"""

import logging
import sys
from pathlib import Path

from arxiv_client import ArxivClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_real_arxiv() -> None:
    """Test with real arXiv papers."""
    # Use a well-known, small paper for testing
    test_arxiv_id = "2303.18223"  # A Survey of Large Language Models

    logger.info(f"Testing ArxivClient with real paper: {test_arxiv_id}")
    logger.info("=" * 80)

    # Create client
    client = ArxivClient(rate_limit=1.0)

    # Create test output directory
    test_dir = Path(__file__).parent / "test_output"
    test_dir.mkdir(exist_ok=True)

    try:
        # 1. Test metadata fetching
        logger.info("\n1. Testing metadata fetching...")
        metadata = client.get_paper_metadata(test_arxiv_id)

        logger.info(f"   Title: {metadata['title']}")
        logger.info(f"   Authors: {', '.join(metadata['authors'][:3])}...")
        logger.info(f"   Categories: {', '.join(metadata['categories'])}")
        logger.info(f"   Published: {metadata['published']}")
        logger.info(f"   ✓ Metadata fetched successfully")

        # 2. Test PDF download (first 10 pages only to save bandwidth)
        logger.info("\n2. Testing PDF download...")
        pdf_path = test_dir / f"{test_arxiv_id}.pdf"
        if pdf_path.exists():
            logger.info(f"   PDF already exists ({pdf_path.stat().st_size} bytes)")
        else:
            client.download_pdf(test_arxiv_id, pdf_path)
            logger.info(f"   PDF downloaded: {pdf_path.stat().st_size} bytes")
            logger.info(f"   ✓ PDF download successful")

        # 3. Test source download
        logger.info("\n3. Testing source download...")
        source_path = test_dir / f"{test_arxiv_id}.tar.gz"
        if source_path.exists():
            logger.info(f"   Source already exists ({source_path.stat().st_size} bytes)")
        else:
            client.download_source(test_arxiv_id, source_path)
            logger.info(f"   Source downloaded: {source_path.stat().st_size} bytes")
            logger.info(f"   ✓ Source download successful")

        # 4. Test ar5iv HTML download
        logger.info("\n4. Testing ar5iv HTML5 download...")
        ar5iv_path = test_dir / f"{test_arxiv_id}.html"
        if ar5iv_path.exists():
            logger.info(f"   ar5iv HTML already exists ({ar5iv_path.stat().st_size} bytes)")
        else:
            client.download_ar5iv_html(test_arxiv_id, ar5iv_path)
            logger.info(f"   ar5iv HTML downloaded: {ar5iv_path.stat().st_size} bytes")
            logger.info(f"   ✓ ar5iv HTML download successful")

        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info(f"Test files saved to: {test_dir}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    test_real_arxiv()
