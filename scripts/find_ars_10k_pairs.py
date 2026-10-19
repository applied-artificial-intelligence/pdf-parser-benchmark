#!/usr/bin/env python3
"""
Find ARS (Annual Report to Stockholders) PDF filings on SEC EDGAR
and pair them with 10-K HTML filings for the same company and fiscal year.

Since the 2023 proxy season, the SEC requires companies to furnish their
"glossy" Annual Report electronically on EDGAR as a PDF submission.
The corresponding 10-K is filed as HTML/iXBRL, creating natural pairs.
"""

import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

HEADERS = {"User-Agent": "pdf-bench research@example.com"}
RATE_LIMIT_SLEEP = 0.15


def fetch_json(url: str, retries: int = 3) -> dict | None:
    """Fetch JSON from a URL with retries and rate limiting."""
    for attempt in range(retries):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            time.sleep(RATE_LIMIT_SLEEP)
            return data
        except HTTPError as e:
            if e.code == 429:
                wait = 2 ** attempt
                print(f"  Rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
            elif e.code == 404:
                return None
            else:
                print(f"  HTTP {e.code} for {url}", file=sys.stderr)
                if attempt < retries - 1:
                    time.sleep(1)
        except (URLError, TimeoutError) as e:
            print(f"  Error fetching {url}: {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(1)
    return None


def search_ars_filings(start_dt: str = "2023-01-01", end_dt: str = "2026-12-31", size: int = 100, start: int = 0) -> dict | None:
    """Search EDGAR EFTS for ARS filings."""
    url = (
        f"https://efts.sec.gov/LATEST/search-index?forms=ARS"
        f"&_source=adsh,ciks,display_names,file_date,sics,period_ending"
        f"&size={size}&from={start}"
        f"&dateRange=custom&startdt={start_dt}&enddt={end_dt}"
    )
    return fetch_json(url)


def get_filing_index(cik: str, accession: str) -> dict | None:
    """Get the filing index to find individual documents."""
    # accession without dashes
    acc_nodash = accession.replace("-", "")
    cik_num = cik.lstrip("0")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc_nodash}/index.json"
    return fetch_json(url)


def get_company_submissions(cik: str) -> dict | None:
    """Get company submissions to find 10-K filings."""
    cik_padded = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    return fetch_json(url)


def find_pdf_in_filing(index_data: dict, cik: str, accession: str) -> dict | None:
    """Find PDF document(s) in a filing index."""
    if not index_data or "directory" not in index_data:
        return None

    acc_nodash = accession.replace("-", "")
    cik_num = cik.lstrip("0")
    base_url = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc_nodash}"

    pdfs = []
    for item in index_data["directory"].get("item", []):
        name = item.get("name", "")
        if name.lower().endswith(".pdf"):
            pdfs.append({
                "filename": name,
                "url": f"{base_url}/{name}",
                "size": item.get("size", "unknown"),
                "last_modified": item.get("last-modified", ""),
            })

    if not pdfs:
        return None

    # Return the largest PDF (usually the main ARS document)
    if len(pdfs) == 1:
        return pdfs[0]

    # Try to pick the main one by size (largest)
    def parse_size(s):
        """Parse size string like '2.5 MB' to bytes."""
        if isinstance(s, (int, float)):
            return s
        s = str(s).strip()
        if not s or s == "unknown":
            return 0
        multipliers = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
        for unit, mult in multipliers.items():
            if unit in s.upper():
                try:
                    return float(s.upper().replace(unit, "").strip()) * mult
                except ValueError:
                    return 0
        try:
            return float(s)
        except ValueError:
            return 0

    pdfs.sort(key=lambda p: parse_size(p["size"]), reverse=True)
    return pdfs[0]


def find_10k_for_company(submissions: dict, target_period: str) -> dict | None:
    """Find the 10-K filing matching a given fiscal period from company submissions."""
    if not submissions:
        return None

    recent = submissions.get("filings", {}).get("recent", {})
    if not recent:
        return None

    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    primary_docs = recent.get("primaryDocument", [])
    primary_doc_descs = recent.get("primaryDocDescription", [])
    report_dates = recent.get("reportDate", [])

    # Look for 10-K or 10-K/A matching the period
    target_year = target_period[:4] if target_period else None

    candidates = []
    for i, form in enumerate(forms):
        if form in ("10-K", "10-K/A"):
            rd = report_dates[i] if i < len(report_dates) else ""
            # Check if the report date matches the target period
            if target_period and rd:
                # Match by period ending (exact or same year)
                if rd == target_period or (target_year and rd.startswith(target_year)):
                    candidates.append(i)
            elif target_year and dates[i].startswith(target_year):
                candidates.append(i)

    # Also try year +1 for filing date (10-K for FY2024 is typically filed in early 2025)
    if not candidates and target_year:
        next_year = str(int(target_year) + 1)
        for i, form in enumerate(forms):
            if form in ("10-K", "10-K/A"):
                rd = report_dates[i] if i < len(report_dates) else ""
                if rd and rd.startswith(target_year):
                    candidates.append(i)

    if not candidates:
        return None

    # Prefer 10-K over 10-K/A
    best = None
    for idx in candidates:
        if forms[idx] == "10-K":
            best = idx
            break
    if best is None:
        best = candidates[0]

    i = best
    cik = str(submissions.get("cik", "")).zfill(10)
    cik_num = str(submissions.get("cik", ""))
    acc = accessions[i]
    acc_nodash = acc.replace("-", "")
    primary_doc = primary_docs[i] if i < len(primary_docs) else ""

    return {
        "form": forms[i],
        "accession": acc,
        "filing_date": dates[i],
        "report_date": report_dates[i] if i < len(report_dates) else "",
        "primary_document": primary_doc,
        "primary_doc_url": f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc_nodash}/{primary_doc}",
        "primary_doc_description": primary_doc_descs[i] if i < len(primary_doc_descs) else "",
    }


def find_html_in_10k(index_data: dict, cik: str, accession: str) -> dict | None:
    """Find the primary HTML document in a 10-K filing."""
    if not index_data or "directory" not in index_data:
        return None

    acc_nodash = accession.replace("-", "")
    cik_num = cik.lstrip("0")
    base_url = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc_nodash}"

    html_docs = []
    for item in index_data["directory"].get("item", []):
        name = item.get("name", "")
        if name.lower().endswith((".htm", ".html")) and not name.startswith("R"):
            html_docs.append({
                "filename": name,
                "url": f"{base_url}/{name}",
                "size": item.get("size", "unknown"),
            })

    if not html_docs:
        return None

    # Return the largest HTML file (usually the main 10-K document)
    def parse_size(s):
        if isinstance(s, (int, float)):
            return s
        s = str(s).strip()
        if not s or s == "unknown":
            return 0
        multipliers = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
        for unit, mult in multipliers.items():
            if unit in s.upper():
                try:
                    return float(s.upper().replace(unit, "").strip()) * mult
                except ValueError:
                    return 0
        try:
            return float(s)
        except ValueError:
            return 0

    html_docs.sort(key=lambda h: parse_size(h["size"]), reverse=True)
    return html_docs[0]


def main():
    print("=" * 80)
    print("SEC EDGAR ARS + 10-K Pair Finder")
    print("=" * 80)

    # Step 1: Collect ARS filings
    print("\n[Step 1] Searching for ARS filings (2023-2026)...")
    all_ars = []

    for start in range(0, 500, 100):
        result = search_ars_filings(size=100, start=start)
        if not result or "hits" not in result:
            break
        hits = result["hits"].get("hits", [])
        if not hits:
            break

        for hit in hits:
            src = hit.get("_source", {})
            doc_id = hit.get("_id", "")
            # Check if it's a PDF from the doc ID
            is_pdf = doc_id.lower().endswith(".pdf")

            ciks = src.get("ciks", [])
            names = src.get("display_names", [])

            if ciks:
                all_ars.append({
                    "doc_id": doc_id,
                    "accession": src.get("adsh", ""),
                    "cik": ciks[0],
                    "company_name": names[0] if names else "Unknown",
                    "file_date": src.get("file_date", ""),
                    "period_ending": src.get("period_ending", ""),
                    "sic": (src.get("sics") or [""])[0] if src.get("sics") else "",
                    "is_pdf_from_id": is_pdf,
                })

        total = result["hits"]["total"]["value"]
        print(f"  Fetched {len(all_ars)} / {total} ARS filings...")
        if len(all_ars) >= total or len(hits) < 100:
            break

    print(f"\n  Total ARS filings found: {len(all_ars)}")
    pdf_ars = [a for a in all_ars if a["is_pdf_from_id"]]
    print(f"  ARS filings with PDF (from doc ID): {len(pdf_ars)}")

    # Step 2: For each ARS, verify PDF and find matching 10-K
    print(f"\n[Step 2] Processing ARS filings to find 10-K pairs...")

    # Deduplicate by CIK + period to avoid processing same company twice
    seen = set()
    unique_ars = []
    for a in pdf_ars:
        key = (a["cik"], a["period_ending"])
        if key not in seen:
            seen.add(key)
            unique_ars.append(a)

    print(f"  Unique company/period combinations: {len(unique_ars)}")

    pairs = []
    processed = 0
    errors = 0

    for ars in unique_ars:
        processed += 1
        if processed % 10 == 0:
            print(f"  Processing {processed}/{len(unique_ars)}... ({len(pairs)} pairs found)")

        cik = ars["cik"]
        accession = ars["accession"]

        # Get ARS filing index to verify PDF
        ars_index = get_filing_index(cik, accession)
        if not ars_index:
            errors += 1
            continue

        pdf_info = find_pdf_in_filing(ars_index, cik, accession)
        if not pdf_info:
            continue

        # Get company submissions to find 10-K
        submissions = get_company_submissions(cik)
        if not submissions:
            errors += 1
            continue

        tenk = find_10k_for_company(submissions, ars["period_ending"])
        if not tenk:
            continue

        # Get 10-K filing index to find HTML document
        tenk_index = get_filing_index(cik, tenk["accession"])
        if tenk_index:
            html_info = find_html_in_10k(tenk_index, cik, tenk["accession"])
        else:
            html_info = None

        # Use primary doc from submissions if we couldn't get index
        if not html_info and tenk.get("primary_document"):
            html_info = {
                "filename": tenk["primary_document"],
                "url": tenk["primary_doc_url"],
                "size": "unknown",
            }

        if not html_info:
            continue

        pair = {
            "company_name": ars["company_name"],
            "cik": cik,
            "sic": ars.get("sic", ""),
            "fiscal_period_ending": ars["period_ending"],
            "ars": {
                "accession": accession,
                "filing_date": ars["file_date"],
                "pdf_filename": pdf_info["filename"],
                "pdf_url": pdf_info["url"],
                "pdf_size": pdf_info["size"],
            },
            "tenk": {
                "form": tenk["form"],
                "accession": tenk["accession"],
                "filing_date": tenk["filing_date"],
                "report_date": tenk["report_date"],
                "html_filename": html_info["filename"],
                "html_url": html_info["url"],
                "html_size": html_info.get("size", "unknown"),
            },
        }
        pairs.append(pair)

        # Stop if we have enough
        if len(pairs) >= 50:
            print(f"\n  Reached 50 pairs, stopping early.")
            break

    # Step 3: Output results
    print(f"\n{'=' * 80}")
    print(f"RESULTS: Found {len(pairs)} confirmed ARS+10-K pairs")
    print(f"{'=' * 80}")

    for i, pair in enumerate(pairs, 1):
        print(f"\n--- Pair {i} ---")
        print(f"  Company: {pair['company_name']}")
        print(f"  CIK: {pair['cik']}")
        print(f"  Fiscal Period Ending: {pair['fiscal_period_ending']}")
        print(f"  ARS:")
        print(f"    Accession: {pair['ars']['accession']}")
        print(f"    PDF: {pair['ars']['pdf_url']}")
        print(f"    PDF Size: {pair['ars']['pdf_size']}")
        print(f"    Filed: {pair['ars']['filing_date']}")
        print(f"  10-K:")
        print(f"    Form: {pair['tenk']['form']}")
        print(f"    Accession: {pair['tenk']['accession']}")
        print(f"    HTML: {pair['tenk']['html_url']}")
        print(f"    HTML Size: {pair['tenk']['html_size']}")
        print(f"    Filed: {pair['tenk']['filing_date']}")
        print(f"    Report Date: {pair['tenk']['report_date']}")

    # Save to JSON
    output_path = "ars_10k_pairs.json"
    with open(output_path, "w") as f:
        json.dump({
            "description": "ARS PDF + 10-K HTML pairs from SEC EDGAR",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_pairs": len(pairs),
            "pairs": pairs,
        }, f, indent=2)
    print(f"\n  Results saved to {output_path}")

    # Summary stats
    print(f"\n  Processing stats:")
    print(f"    ARS filings examined: {processed}")
    print(f"    Confirmed pairs: {len(pairs)}")
    print(f"    Errors/404s: {errors}")


if __name__ == "__main__":
    main()
