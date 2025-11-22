# Corpus Attribution and Licensing

This directory contains ground truth data and metadata for PDF-to-Markdown benchmark evaluation.

## Corpus Overview

| Corpus | Documents | Source | License |
|--------|-----------|--------|---------|
| CUAD | 75 | Cornell Law School | CC-BY-4.0 |
| OmniDocBench | 193 | OpenDataLab | CC-BY-4.0 |
| Synthetic | 32 | Generated | MIT |
| Invoices | 20 | Generated | MIT |
| HR | 20 | Generated | MIT |
| Legal | 20 | Generated | MIT |

## Attribution

### CUAD (Contract Understanding Atticus Dataset)

**Source**: https://www.atticusprojectai.org/cuad
**Paper**: Hendrycks et al., "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review" (2021)
**License**: CC-BY-4.0
**Original Data**: https://huggingface.co/datasets/cuad

The CUAD dataset contains real contracts from SEC EDGAR filings. SEC filings are public domain (not subject to copyright). The CUAD annotations and dataset structure are licensed under CC-BY-4.0.

```bibtex
@article{hendrycks2021cuad,
  title={CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review},
  author={Hendrycks, Dan and Burns, Collin and Chen, Anya and Ball, Spencer},
  journal={arXiv preprint arXiv:2103.06268},
  year={2021}
}
```

### OmniDocBench

**Source**: https://huggingface.co/datasets/opendatalab/OmniDocBench
**Paper**: OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations (2024)
**License**: CC-BY-4.0

OmniDocBench provides diverse document types including academic papers, presentations, exam papers, books, and newspapers with comprehensive layout annotations.

```bibtex
@misc{ouyang2024omnidocbench,
  title={OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations},
  author={Ouyang, Linke and others},
  year={2024},
  publisher={OpenDataLab}
}
```

### Synthetic and Generated Corpora

The synthetic, invoices, HR, and legal corpora are generated programmatically for testing purposes and are released under the MIT license as part of this project.

## Directory Structure

```
corpus/
├── academic/
│   ├── omnidocbench/      # OmniDocBench documents (CC-BY-4.0)
│   └── sample/            # Sample academic papers
├── business/
│   ├── cuad/              # CUAD legal contracts (CC-BY-4.0)
│   ├── invoices/          # Generated invoices (MIT)
│   ├── hr/                # Generated HR documents (MIT)
│   └── legal/             # Generated legal templates (MIT)
└── synthetic/             # Generated test documents (MIT)
```

## PDF Files

PDF files are not included in the repository (gitignored). To obtain PDFs:

1. **CUAD**: Download from HuggingFace and convert HTML to PDF
2. **OmniDocBench**: Download from HuggingFace, convert images to PDF
3. **Synthetic**: Generate using `builders/generate_systematic_corpus.py`

## What's Included

- `ground_truth/` - Markdown reference text for evaluation
- `metadata/` - Document metadata (source URLs, features, difficulty)
- `corpus_metadata.yaml` - Corpus-level configuration

## License Summary

- **CUAD ground truth**: CC-BY-4.0 (requires attribution)
- **OmniDocBench ground truth**: CC-BY-4.0 (requires attribution)
- **Generated content**: MIT (part of pdf-bench)
- **This benchmark suite**: MIT
