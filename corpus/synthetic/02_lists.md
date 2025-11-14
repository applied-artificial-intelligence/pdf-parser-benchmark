# Working with Lists in Markdown

Lists are fundamental structures in technical documentation. This document tests parser handling of various list types.

## Ordered Lists

Here are the steps to evaluate a PDF parser:

1. Select a test corpus
2. Configure the parser
3. Run the extraction
4. Compare output to ground truth
5. Calculate metrics

## Unordered Lists

PDF parsing systems can be categorized by approach:

- **Rule-based parsers**: Use heuristics for text extraction
- **Layout analysis parsers**: Detect document structure first
- **Machine learning parsers**: Train models on labeled data
- **Commercial APIs**: Cloud-based services with high accuracy

## Nested Lists

Project organization:

1. **Phase 1: Foundation**
   - Set up development environment
   - Create base parser interface
   - Implement caching system
   - Add basic metrics
2. **Phase 2: Synthetic Corpus**
   - Author test documents
   - Generate PDFs from Markdown
   - Validate ground truth
   - Document limitations
3. **Phase 3: Advanced Metrics**
   - Implement AST-based metrics
   - Add table-specific metrics
   - Create math evaluation
   - Benchmark on synthetic corpus

## Mixed Lists

Considerations for parser selection:

- **Open-source options**:
  1. PyMuPDF: Fast, simple text extraction
  2. Marker: Vision-based with layout analysis
  3. Nougat: Optimized for academic papers
- **Commercial options**:
  1. AWS Textract: Enterprise-grade, pay-per-page
  2. Azure Document Intelligence: Good for forms
  3. Google Document AI: Strong OCR capabilities

## Task Lists

Development checklist:

- [x] Create directory structure
- [x] Implement BaseParser
- [x] Add caching system
- [ ] Create synthetic corpus
- [ ] Implement advanced metrics
- [ ] Build real-world corpora
- [ ] Run full benchmark

## Conclusion

This document exercises nested lists, mixed ordered/unordered lists, and task lists to test structural preservation in PDF conversion.
