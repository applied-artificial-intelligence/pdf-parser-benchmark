# Source-linked result appendix

| Pipeline | Complete invoices | Correct fields | Matched / expected / predicted records | Record F1 |
| --- | ---: | ---: | ---: | ---: |
| pypdf | 84/100 | 500/500 | 668 / 696 / 698 | 0.958393 |
| pdfplumber | 55/100 | 468/500 | 677 / 696 / 691 | 0.976208 |

| Source cell | Inputs | pypdf complete | pdfplumber complete |
| --- | ---: | ---: | ---: |
| enterprise/simple | 19 | 11 | 10 |
| small_business/simple | 19 | 14 | 16 |
| economy/medium | 17 | 17 | 0 |
| enterprise/medium | 15 | 15 | 15 |
| small_business/medium | 15 | 12 | 14 |
| economy/complex | 15 | 15 | 0 |

| Pipeline | Native content faithfulness | Native table composite |
| --- | ---: | ---: |
| pypdf | 0.599212 (30/30) | 0.000000 (20/20) |
| pdfplumber | 0.570951 (30/30) | 0.106763 (20/20) |

| Retained family | Tier | Supported interpretation |
| --- | --- | --- |
| academic_arxiv | directional | Technical-paper text metrics; exact source-to-PDF and equation correspondence require qualification. |
| investor_decks_prototype | prototype | Synthetic PPTX/PDF prototype, limited templates and realism; no corporate-deck population claim. |
| frontier_premium_pilot | historical | Historical paid pilot; metric subsets and configuration identities must be inspected before interpreting differences. |
| frontier_budget_unified | historical | Historical paid model pilot; current provider/model/configuration and cost comparability are unverified. |
| invoices_source_first | historical | Retained DOCX extraction matches backups, not current references. The original scored reference bytes are not established; source-first independence is unverified for this run. |
| legacy_presentations | directional | Retained presentation evidence with uneven reference/source correspondence; not a full-deck task comparison. |
| sec_filings_real_business | directional | Current selection config uses pypdfium2 >= 0.90; ARS PDFs and 10-K HTML may differ. Similarity to that reference is diagnostic, not independent task correctness. |
| sec_commercial_pilot | historical | Observed rows contradict declared failure count. Preserve paid-run diagnostics and separate counters; no current paid-parser winner. |
| sec_screening_full | directional | One-parser screen over observed rows. Title All 89 conflicts with 320 observed document IDs; no parser ranking or impartial sample follows. |

Each exported claim carries its source SHA256 and JSON pointer in claims.json. Native dimensions and complete-invoice scores measure different tasks.