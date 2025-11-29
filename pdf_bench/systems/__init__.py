"""PDF parser system adapters.

SPDX-License-Identifier: MIT
Copyright (c) 2025 PDF-Bench Contributors
"""

from pdf_bench.systems.anthropic_parser import AnthropicParser
from pdf_bench.systems.aws_textract import AWSTextractParser
from pdf_bench.systems.azure_document_intelligence import (
    AzureDocumentIntelligenceParser,
)
from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.systems.databricks_parser import DatabricksParser
from pdf_bench.systems.docling_parser import DoclingParser
from pdf_bench.systems.extractous_parser import ExtractousParser
from pdf_bench.systems.gemini_parser import GeminiParser
from pdf_bench.systems.google_document_ai import GoogleDocumentAIParser
from pdf_bench.systems.kreuzberg_parser import KreuzbergParser
from pdf_bench.systems.landing_ai_parser import LandingAIParser
from pdf_bench.systems.llamaparse_parser import LlamaParseParser
from pdf_bench.systems.marker import MarkerParser
from pdf_bench.systems.marker_ollama import MarkerOllamaParser
from pdf_bench.systems.openai_parser import OpenAIParser
from pdf_bench.systems.pdfminer_parser import PDFMinerParser
from pdf_bench.systems.pdfplumber_parser import PdfPlumberParser
from pdf_bench.systems.pymupdf import PyMuPDFParser
from pdf_bench.systems.pymupdf4llm_parser import PyMuPDF4LLMParser
from pdf_bench.systems.pypdf2_parser import PyPDF2Parser
from pdf_bench.systems.pypdf_parser import PyPDFParser
from pdf_bench.systems.pypdfium2_parser import PyPDFium2Parser
from pdf_bench.systems.tika_parser import TikaParser
from pdf_bench.systems.unstructured_parser import UnstructuredParser

__all__ = [
    "AnthropicParser",
    "AWSTextractParser",
    "AzureDocumentIntelligenceParser",
    "BaseParser",
    "DatabricksParser",
    "DoclingParser",
    "ExtractousParser",
    "GeminiParser",
    "GoogleDocumentAIParser",
    "OpenAIParser",
    "KreuzbergParser",
    "LandingAIParser",
    "LlamaParseParser",
    "MarkerParser",
    "MarkerOllamaParser",
    "PDFMinerParser",
    "PdfPlumberParser",
    "PyPDF2Parser",
    "PyPDFParser",
    "PyPDFium2Parser",
    "PyMuPDFParser",
    "PyMuPDF4LLMParser",
    "TikaParser",
    "UnstructuredParser",
]
