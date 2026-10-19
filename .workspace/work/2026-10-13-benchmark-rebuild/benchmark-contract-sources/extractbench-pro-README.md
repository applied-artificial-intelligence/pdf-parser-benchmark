---
license: apache-2.0
configs:
- config_name: extract-bench-pro
  features:
  - name: id
    dtype: string
  - name: category
    dtype: string
  - name: pdf
    dtype: string
  - name: data_schema
    dtype: string
  - name: expected_output
    dtype: string
  - name: field_rules
    dtype: string
  - name: repeated_structure
    dtype: string
  - name: tags
    sequence: string
  data_files:
  - split: document_conventions
    path: document_conventions.jsonl
  - split: house_vocabulary
    path: house_vocabulary.jsonl
  - split: house_counting_rules
    path: house_counting_rules.jsonl
  - split: drawn_relations
    path: drawn_relations.jsonl
  - split: charts_inside_documents
    path: charts_inside_documents.jsonl
  - split: long_chart_sheets
    path: long_chart_sheets.jsonl
language:
- en
pretty_name: ExtractBench Pro
size_categories:
- n<1K
tags:
- document-extraction
- structured-extraction
- information-extraction
- pdf
- benchmark
- evaluation
- json-schema
- visual-grounding
- synthetic
---

# ExtractBench Pro

**Quick links:** [\[🌐 Website\]](https://extractbenchpro.ai) [\[💻 Code\]](https://github.com/run-llama/ExtractBench) [\[📚 ExtractBench\]](https://huggingface.co/datasets/llamaindex/ExtractBench)

ExtractBench Pro is the hard companion to [ExtractBench](https://huggingface.co/datasets/llamaindex/ExtractBench). The task is the same: given a full document and a user-written schema, return a schema-valid JSON object with the correct, exhaustive values and evidence for each one. The difference is what makes a value hard. In ExtractBench Pro, many values cannot be copied from the page. They have to be read off a chart or a drawing, counted under the document’s own rules, or decoded with its own vocabulary. The documents are derived from real long-tail documents, and grouped into six challenges.

ExtractBench Pro contains 100 documents (2,622 pages, 1–83 pages each) across 86 document types, with 144,141 expected values. Every document is synthetic: its values are fictional and fixed before the page is rendered, so the expected output is exact by construction.

## Challenge subsets

Each document belongs to exactly one subset: the challenge a naive reader most often gets wrong in it. A document can also contain values of other challenges, and values that are read directly from the page.

| Subset | Challenge | Documents | Pages | Expected values |
|---|---|---:|---:|---:|
| `document_conventions` | **Document conventions.** One part of the document, such as a legend, rule or amendment, changes how the rest must be read | 22 | 875 | 121,287 |
| `house_vocabulary` | **House vocabulary.** The organization’s own definitions of its jargon decide the value | 14 | 606 | 15,242 |
| `house_counting_rules` | **House counting rules.** Counts and sums computed under definitions from the schema and the document | 12 | 225 | 409 |
| `drawn_relations` | **Drawn relations.** All or part of the value depends on a line in a diagram rather than a printed value | 20 | 352 | 2,349 |
| `charts_inside_documents` | **Charts inside documents.** Values read off charts, as the range between the tick marks the value falls in | 25 | 557 | 1,347 |
| `long_chart_sheets` | **Long chart sheets.** Hundreds of values on one extremely long, narrow chart sheet, such as a well log or a time-location chart | 7 | 7 | 3,507 |
| **Total** | | **100** | **2,622** | **144,141** |

<details>
  <summary>Document types per subset</summary>

- **Document conventions:** GL trial balances (2), loss runs (2), regulations (2), utility invoices (2), benefits census, clinical listing, customs entry (CBP 7501), grant award form, insurance schedule, investor report, mortgage application (URLA 1003), patient record, payment remittance, payroll audit packet, property bulletin, SEC 13F report, UB-04 claim form, UCC search form
- **House vocabulary:** care home census review, circulation audit, demand response settlement, export credit policy results, hotel room block review, import duty reconciliation, joint interest billing review, lab safety review, purchase contract review, school enrollment review, show entry check, spread betting account, subscription seat review, transit ridership review
- **House counting rules:** college cohort file, container demurrage claim, election canvass binder, engine utilisation return, franchise royalty report, landfill diversion return, library aid claim, mortgage servicing report, premium audit worksheet, travel expense binder, TV post-buy affidavit, vendor statement reconciliation
- **Drawn relations:** credit facility binders (2), fund structure files (2), HVAC balancing reports (2), insurance programme files (2), network change requests (2), one-line commissioning binders (2), water loss audits (2), audit findings report, capital call notice, fibre splice record, probate court file, procurement audit pack, tournament results pack
- **Charts inside documents:** agency staffing invoice, aggregate QC report, assessment billing run, capacity change pack, chemotherapy verification, claims triage bundle, contractor dispute binder, dam operations report, drilling report bundle, earthwork quantity packet, eligibility appeals file, Gantt schedule board, integrity filing annex, medical gas shutdown notice, parking variance hearing, pipeline inspection report, pump station calculation, QT audit bulletin, rezoning notice packet, right-of-way acquisition packet, site plan review, stock declaration file, titration packet, tower coverage credit, well completion filing
- **Long chart sheets:** wireline logs (3), time-location charts (2), borehole core log, track chart

</details>

## Capture conditions and length

Each document is also tagged by how most of its pages were captured, by length and by business domain. The axes are independent of the challenge subset.

| Perception | Documents | What most pages look like |
|---|---:|---|
| `digital` | 25 | Born-digital pages with a text layer |
| `image` | 8 | Clean page images without scanner noise |
| `scan` | 44 | Light or medium scan |
| `heavy_scan` | 16 | Heavy or extreme scan |
| `handwritten` | 7 | Hand-filled forms or handwritten values |

- **Length:** `short` (10 pages or fewer) 8 documents, `medium` (11–50 pages) 81 documents, `long` (more than 50 pages) 11 documents.
- **Domain:** `D1` finance (27), `D2` energy (19), `D3` government (16), `D5` supply chain (9), `D6` healthcare (13), `D7` legal (3), `D8` real estate (13), using the ExtractBench domain codes.

Seven of the eight short documents are single plotter sheets 13 to 17 feet long (well logs, a borehole core log, a track chart and time-location charts), scanned or photocopied, with no text layer; each asks for 390 to 715 values. The eighth is a two-page Gantt schedule board. Charts and drawings in other documents are often page images too, so their values cannot be read from a text layer. Some scanned documents carry a text layer that does not match the printed page. The printed page is authoritative. One document prints two pages on each sheet, turned sideways.

## Usage

Load a subset with `datasets`:

```python
from datasets import load_dataset
import json

ds = load_dataset("llamaindex/ExtractBenchPro", split="charts_inside_documents")
case = ds[0]
schema = json.loads(case["data_schema"])
expected = json.loads(case["expected_output"])
```

The rows use the same format as ExtractBench, so the [evaluation framework](https://github.com/run-llama/ExtractBench) scores them unchanged. To rebuild the `<stem>.pdf` + `<stem>.test.json` layout that the framework reads:

```python
import json, shutil
from pathlib import Path
from huggingface_hub import snapshot_download

root = Path(snapshot_download("llamaindex/ExtractBenchPro", repo_type="dataset"))
out = Path("data/extract_bench_pro")
for split in ["document_conventions", "house_vocabulary", "house_counting_rules", "drawn_relations", "charts_inside_documents", "long_chart_sheets"]:
    for line in (root / f"{split}.jsonl").read_text().splitlines():
        row = json.loads(line)
        stem = Path(row["pdf"]).stem
        (out / split).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / row["pdf"], out / split / f"{stem}.pdf")
        sidecar = {
            "tags": row["tags"],
            "data_schema": json.loads(row["data_schema"]),
            "expected_output": json.loads(row["expected_output"]),
            "_field_rules": json.loads(row["field_rules"]),
        }
        (out / split / f"{stem}.test.json").write_text(json.dumps(sidecar))
```

Scoring follows ExtractBench and is fully deterministic:

- **Unified value F1:** whether the extracted values match the expected output, under one definition for scalar fields and arrays of records.
- **Near-perfect value F1:** the share of documents with a unified value F1 of at least 99%.
- **Word-level grounding F1:** a field counts as grounded only when its value is correct and its predicted box overlaps an accepted box for that field at IoU 0.5.
- **Page-level grounding F1:** requires the correct source page rather than a box.

The evaluation dataset files are:

- [document_conventions.jsonl](document_conventions.jsonl): 22 test cases across 875 pages
- [house_vocabulary.jsonl](house_vocabulary.jsonl): 14 test cases across 606 pages
- [house_counting_rules.jsonl](house_counting_rules.jsonl): 12 test cases across 225 pages
- [drawn_relations.jsonl](drawn_relations.jsonl): 20 test cases across 352 pages
- [charts_inside_documents.jsonl](charts_inside_documents.jsonl): 25 test cases across 557 pages
- [long_chart_sheets.jsonl](long_chart_sheets.jsonl): 7 test cases across 7 pages
- [docs/](https://huggingface.co/datasets/llamaindex/ExtractBenchPro/tree/main/docs): source PDFs organized by subset

<details>
  <summary>Dataset Format</summary>

Each line in a JSONL file is one document-schema test case:

```json
{
    "id": "long_chart_sheets/wireline_log_01",      // Unique test-case id: <subset>/<stem>
    "category": "long_chart_sheets",                // Subset name
    "pdf": "docs/long_chart_sheets/wireline_log_01.pdf", // Relative path to the source document
    "data_schema": "{...}",         // JSON-encoded JSON Schema the output must validate against
    "expected_output": "{...}",     // JSON-encoded ground-truth extraction
    "field_rules": "{...}",         // JSON-encoded per-field scoring rules
    "repeated_structure": "{}",     // JSON-encoded record-identity config (empty: records are matched on their values)
    "tags": ["source:synthetic", "challenge:long_chart_sheets", "perception:scan", "length:short", "domain:D2"]
}
```

`data_schema`, `expected_output`, `field_rules` and `repeated_structure` are stored as JSON-encoded strings because schemas differ by document. Decode them with `json.loads`. The largest `field_rules` cell is about 6 MB, so the dataset viewer shows only a preview of each cell. The downloaded file contains the complete data.

**`field_rules`** maps each value path to a scoring rule:

- `evidence`: accepted readings and their source locations, stored as `{page, bbox, quote, value}`; any accepted reading counts as correct
- `source_policy`: whether the value must appear verbatim in the document
- `evidence_required` / `verified`: whether located evidence exists for the value
- `normalizers`: value normalization applied before comparison

</details>

## Data Display

<table>
  <tr>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/titration_packet_01.pdf"><img src="thumbnails/ecg_rhythm_strips.png" width="200" /></a><br><sub>ECG rhythm strips</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/claims_triage_bundle_01.pdf"><img src="thumbnails/decision_flowchart.png" width="200" /></a><br><sub>Decision flowchart</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/rezoning_notice_packet_01.pdf"><img src="thumbnails/zoning_atlas_map.png" width="200" /></a><br><sub>Zoning atlas map</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/capacity_change_pack_01.pdf"><img src="thumbnails/single_line_power_diagram.png" width="200" /></a><br><sub>Single-line power diagram</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/agency_staffing_invoice_01.pdf"><img src="thumbnails/colour_coded_shift_roster.png" width="200" /></a><br><sub>Colour-coded shift roster</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/drawn_relations/probate_court_file_01.pdf"><img src="thumbnails/probate_family_tree.png" width="200" /></a><br><sub>Probate family tree</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/drawn_relations/fund_structure_file_02.pdf"><img src="thumbnails/fund_structure_chart.png" width="200" /></a><br><sub>Fund structure chart</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/long_chart_sheets/wireline_log_01.pdf"><img src="thumbnails/wireline_well_log_tracks.png" width="200" /></a><br><sub>Wireline well-log tracks</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/chemo_verification_01.pdf"><img src="thumbnails/nomogram_with_straightedge.png" width="200" /></a><br><sub>Nomogram with straightedge</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/pipeline_inspection_report_01.pdf"><img src="thumbnails/pipeline_inspection_strip_log.png" width="200" /></a><br><sub>Pipeline inspection strip log</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/document_conventions/property_bulletin_01.pdf"><img src="thumbnails/bars_and_line_combo_chart.png" width="200" /></a><br><sub>Bars-and-line combo chart</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/stock_declaration_file_01.pdf"><img src="thumbnails/warehouse_slot_hatch_map.png" width="200" /></a><br><sub>Warehouse slot hatch map</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/site_plan_review_01.pdf"><img src="thumbnails/site_plan_with_review_marks.png" width="200" /></a><br><sub>Site plan with review marks</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/drawn_relations/insurance_programme_file_01.pdf"><img src="thumbnails/hand_drawn_ownership_network.png" width="200" /></a><br><sub>Hand-drawn ownership network</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/long_chart_sheets/time_location_chart_02.pdf"><img src="thumbnails/time_location_chart.png" width="200" /></a><br><sub>Time-location chart</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/document_conventions/investor_report_01.pdf"><img src="thumbnails/dark_theme_bar_panel.png" width="200" /></a><br><sub>Dark-theme bar panel</sub></td>
  </tr>
  <tr>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/assessment_billing_run_01.pdf"><img src="thumbnails/subdivision_plat.png" width="200" /></a><br><sub>Subdivision plat</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/aggregate_qc_report_01.pdf"><img src="thumbnails/sieve_grading_curves.png" width="200" /></a><br><sub>Sieve grading curves</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/drawn_relations/fibre_splice_record_01.pdf"><img src="thumbnails/fibre_splice_diagram.png" width="200" /></a><br><sub>Fibre splice diagram</sub></td>
    <td align="center"><a href="https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/main/docs/charts_inside_documents/dam_operations_report_01.pdf"><img src="thumbnails/reservoir_hydrograph_strips.png" width="200" /></a><br><sub>Reservoir hydrograph strips</sub></td>
  </tr>
</table>

## Copyright Statement

All documents are synthetic and contain fictional values. The dataset is released under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For questions, contact us through the [GitHub repository](https://github.com/run-llama/ExtractBench).

## Links

- **Code:** [run-llama/ExtractBench](https://github.com/run-llama/ExtractBench)
- **ExtractBench:** [llamaindex/ExtractBench](https://huggingface.co/datasets/llamaindex/ExtractBench), real-document extraction
- **ParseBench:** [llamaindex/ParseBench](https://huggingface.co/datasets/llamaindex/ParseBench), a companion benchmark for document parsing
