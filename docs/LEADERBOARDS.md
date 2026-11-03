# Historical benchmark cohorts

Documentation correction: November 3, 2026. This is a guide to retained November 2025 reports, not a new experiment or a current model leaderboard.

| Retained report | Reported scope | Interpretation |
| --- | --- | --- |
| Frontier-model section | 28 documents | Historical scores within that reported sample. |
| Budget-model section | 30 documents | A different sample; do not subtract its average from the frontier average as a matched effect. |
| Open-source summary | 353 documents across six listed corpora | Coverage, failed outputs, reference identity and normalization still need to agree before comparing averages. |
| Commercial results | Counts vary by service; overall table lists 200, 64, 200, 62 and 3 | Per-service scores do not establish equal coverage. Overall counts do not identify the invoice subset. |
| Detailed invoice section | 100 documents per listed invoice row | Reports 90.6% for Azure and 77.1% for PyMuPDF4LLM, with regenerated text references; conflicts with the older 49.9% summary. |

The original [leaderboard proposals](archive/leaderboards-before-2026-11-03.md) and [results report](archive/results-before-2026-11-03.md) remain unchanged. They contain inconsistent summaries and unsupported recommendations. The dated [update notice](UPDATE_NOTICE_2025-11-30.md) is also historical, not release approval or current advice.

The quoted $0.05 and $0.003 per-page values imply a ratio of approximately 16.7. Neither that ratio nor a cross-sample score difference establishes the cost of a correctly completed document workflow.

For a selection decision, first freeze the common document set, parser and dependency revisions, settings, reference generation, metric normalization and failure treatment. Report the matched results and coverage together. This correction does not supply a new matched ranking or require spending on another run.
