"""PDF parser system adapters.

Most parsers are now provided via pdfsmith backends through PdfsmithAdapter.
Only native parsers (not available in pdfsmith) are directly implemented here.

SPDX-License-Identifier: MIT
Copyright (c) 2025 PDF-Bench Contributors
"""

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.systems.landing_ai_parser import LandingAIParser
from pdf_bench.systems.marker_ollama import MarkerOllamaParser
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter
from pdf_bench.systems.tika_parser import TikaParser

__all__ = [
    "BaseParser",
    "LandingAIParser",
    "MarkerOllamaParser",
    "PdfsmithAdapter",
    "TikaParser",
]
