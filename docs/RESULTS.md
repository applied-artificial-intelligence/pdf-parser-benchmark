# Retained result reports: scope and inconsistencies

Documentation correction: November 3, 2026. No result files or frozen runs were changed.

The complete [November 2025 results report](archive/results-before-2026-11-03.md) is retained unchanged. It contains internally inconsistent aggregate summaries, including:

- A corpus summary calls 49.9% the best invoice score. The detailed invoice section reports 90.6% edit similarity for Azure and 77.1% for PyMuPDF4LLM, each labelled 100 documents. It describes regenerated ground truth from extracted PDF text rather than DOCX tables. The older summary cannot support a claim that every parser scores below 50%.
- The README and results report give different open-source aggregate scores. Their reference preparation and normalization must be identified before choosing one as a current headline.
- Commercial coverage varies by service. The overall table lists 200 Azure results, 64 Databricks, 200 AWS, 62 Google and 3 Landing AI. Later invoice rows and coverage summaries cannot be assumed to describe the same successful-run population.
- Frontier and budget samples contain 28 and 30 documents respectively. Their score difference is not an estimate of improvement on a common sample.

These are observations about the retained reports, not an independent rerun or validation of every listed result. They withdraw the unsupported combined rankings and universal parser recommendations. They do not replace historical numbers with a new performance claim.

Use the [cohort guide](LEADERBOARDS.md) to locate the reported populations. A reproducible comparison requires the run's exact document identities, reference revision, parser/dependency revision, settings, metric treatment, successful outputs and failures. Missing provenance remains unresolved; the current library must not silently substitute for the dependency code used in a frozen run.
