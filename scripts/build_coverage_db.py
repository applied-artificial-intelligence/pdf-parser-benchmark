#!/usr/bin/env python3
"""
Build a SQLite database showing parser-document coverage.

This creates a single source of truth for:
- Which documents exist in our corpus
- Which parsers have been tested on which documents
- Success/failure status and key metrics

Usage:
    python scripts/build_coverage_db.py

Output:
    data_exports/coverage.db
"""

import csv
import sqlite3
from pathlib import Path
from collections import defaultdict

# Paths
RESULTS_CSV = Path("data_exports/detailed_results.csv")
OUTPUT_DB = Path("data_exports/coverage.db")


def main():
    # Remove existing DB
    if OUTPUT_DB.exists():
        OUTPUT_DB.unlink()

    conn = sqlite3.connect(OUTPUT_DB)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE documents (
            document_id TEXT PRIMARY KEY,
            domain TEXT NOT NULL,
            requires_ocr TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE parsers (
            parser TEXT PRIMARY KEY,
            parser_type TEXT NOT NULL,
            has_ocr TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE coverage (
            document_id TEXT NOT NULL,
            parser TEXT NOT NULL,
            success INTEGER NOT NULL,
            edit_similarity REAL,
            tree_similarity REAL,
            parse_time_ms REAL,
            PRIMARY KEY (document_id, parser),
            FOREIGN KEY (document_id) REFERENCES documents(document_id),
            FOREIGN KEY (parser) REFERENCES parsers(parser)
        )
    """)

    # Read data
    documents = {}
    parsers = {}
    coverage = []

    with open(RESULTS_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_id = row['document_id']
            parser = row['parser']

            # Track documents
            if doc_id not in documents:
                documents[doc_id] = {
                    'domain': row['domain'],
                    'requires_ocr': row['requires_ocr']
                }

            # Track parsers
            if parser not in parsers:
                parsers[parser] = {
                    'parser_type': row['parser_type'],
                    'has_ocr': row['parser_has_ocr']
                }

            # Track coverage
            success = 1 if row['success'] == '1' else 0
            edit_sim = float(row['edit_similarity']) if row['edit_similarity'] else None
            tree_sim = float(row['tree_similarity']) if row['tree_similarity'] else None
            parse_time = float(row['parse_time_ms']) if row['parse_time_ms'] else None

            coverage.append((doc_id, parser, success, edit_sim, tree_sim, parse_time))

    # Insert data
    for doc_id, meta in documents.items():
        cur.execute("INSERT INTO documents VALUES (?, ?, ?)",
                   (doc_id, meta['domain'], meta['requires_ocr']))

    for parser, meta in parsers.items():
        cur.execute("INSERT INTO parsers VALUES (?, ?, ?)",
                   (parser, meta['parser_type'], meta['has_ocr']))

    for row in coverage:
        cur.execute("INSERT INTO coverage VALUES (?, ?, ?, ?, ?, ?)", row)

    # Create useful views
    cur.execute("""
        CREATE VIEW document_parser_count AS
        SELECT
            d.document_id,
            d.domain,
            d.requires_ocr,
            COUNT(c.parser) as parsers_tested,
            SUM(c.success) as parsers_succeeded
        FROM documents d
        LEFT JOIN coverage c ON d.document_id = c.document_id
        GROUP BY d.document_id
    """)

    cur.execute("""
        CREATE VIEW parser_document_count AS
        SELECT
            p.parser,
            p.parser_type,
            COUNT(c.document_id) as docs_tested,
            SUM(c.success) as docs_succeeded
        FROM parsers p
        LEFT JOIN coverage c ON p.parser = c.parser
        GROUP BY p.parser
    """)

    cur.execute("""
        CREATE VIEW parser_domain_coverage AS
        SELECT
            p.parser,
            p.parser_type,
            d.domain,
            COUNT(c.document_id) as docs_tested,
            SUM(c.success) as docs_succeeded,
            AVG(CASE WHEN c.success=1 THEN c.edit_similarity END) as avg_edit_similarity
        FROM parsers p
        CROSS JOIN (SELECT DISTINCT domain FROM documents) domains
        LEFT JOIN documents d ON d.domain = domains.domain
        LEFT JOIN coverage c ON c.parser = p.parser AND c.document_id = d.document_id
        GROUP BY p.parser, d.domain
    """)

    conn.commit()

    # Print summary
    print(f"Database created: {OUTPUT_DB}")
    print(f"\nDocuments: {len(documents)}")
    print(f"Parsers: {len(parsers)}")
    print(f"Coverage records: {len(coverage)}")

    # Show domain breakdown
    print("\n=== Documents by Domain ===")
    cur.execute("""
        SELECT domain, COUNT(*) as count, requires_ocr
        FROM documents
        GROUP BY domain, requires_ocr
        ORDER BY count DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} docs (OCR: {row[2]})")

    # Show parser coverage
    print("\n=== Parser Coverage (docs tested) ===")
    cur.execute("""
        SELECT parser, parser_type, docs_tested, docs_succeeded
        FROM parser_document_count
        ORDER BY docs_tested DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[2]} docs ({row[3]} succeeded) [{row[1]}]")

    # Find documents tested by ALL parsers
    total_parsers = len(parsers)
    cur.execute(f"""
        SELECT document_id, domain, parsers_tested
        FROM document_parser_count
        WHERE parsers_tested = {total_parsers}
    """)
    full_coverage_docs = cur.fetchall()
    print(f"\n=== Documents tested by ALL {total_parsers} parsers: {len(full_coverage_docs)} ===")
    for row in full_coverage_docs:
        print(f"  {row[0]} ({row[1]})")

    # Find frontier LLMs arxiv coverage
    print("\n=== Frontier LLMs on arxiv ===")
    cur.execute("""
        SELECT p.parser, COUNT(c.document_id) as docs
        FROM parsers p
        LEFT JOIN coverage c ON c.parser = p.parser
        LEFT JOIN documents d ON d.document_id = c.document_id AND d.domain = 'arxiv'
        WHERE p.parser_type = 'frontier_llm'
        GROUP BY p.parser
        ORDER BY docs DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} arxiv docs")

    conn.close()


if __name__ == "__main__":
    main()
