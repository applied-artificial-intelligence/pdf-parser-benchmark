# pdf-bench

PDF-to-Markdown benchmarking suite with 17 parsers and 353+ documents.

## Project Understanding
@.claude/PROJECT_MAP.md

## Quick Commands

```bash
# Run full benchmark
uv run python -m pdf_bench.runner benchmarks/full_corpus_353docs.yaml

# Run specific benchmark with parsers
uv run python -m pdf_bench.runner benchmarks/cuad_75docs.yaml --parsers docling marker

# Check results
ls -la results/
```

## Environment

API keys in `.env`:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` - Textract
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS` - Document AI
