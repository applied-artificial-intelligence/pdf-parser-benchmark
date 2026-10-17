# PDF-Bench source status

October 17, 2026. The current deliverable is the
[practical parser evaluation guide](../.workspace/work/2026-10-13-benchmark-rebuild/benchmark-design-guide.md).
The plan and issues now centre on interpreting public evidence and learning from
retained evaluation mistakes. All benchmark and GPU execution is paused;
full-population and sampled comparisons are deferred.

The guide recommends consulting published ParseBench results before repeating
experiments. ExtractBench and OmniDocBench supply other relevant task/reference
contracts. Our full ParseBench inventory accounts for 2,078 input paths and
2,553 group/input cases; visual observations cover 221 inputs. It establishes
neither a business-wide coverage percentage nor a consequential deficit that
justifies a replacement general-purpose corpus.

The retained invoice example shows how complete-document acceptance and record
F1 can prefer different configured pipelines. Selecting only one pipeline's
successful inputs reverses their record-F1 ordering. These are controlled
generated-template examples, not a real-vendor parser recommendation. The guide
also explains reference mismatch, output-contract loss and cold initialization.

The [guide evidence record](../.workspace/work/2026-10-13-benchmark-rebuild/guide-evidence.json)
identifies pinned sources, saved artifact hashes, recomputed arithmetic and
verification limits. No new parser, grader, model or GPU execution was used for
the guide. Historical test receipts are not new checks of this writing task.

Earlier invoice and public-subset runs retain fresh/relocated execution and
offline regrading evidence. Their generated report and claim export remain
identified by the work unit's `report-evidence/latest.json`. The immutable
registry preserves SEC, legal/HR, presentations, decks, academic papers and
commercial/frontier pilots in their evidence tiers. None becomes a current
leaderboard through citation in this guide.

[Project orientation](../PROJECT_ORIENTATION.md) names the authoritative artifacts
and boundaries. Draft [PR #9](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/pull/9)
is not approval to merge or publish. No paid calls, sibling implementation,
editorial/CMS changes, package release or public publication occurred.

The previous April status is preserved in
[the status archive](archive/benchmark-status-april-2026-retained.md).
