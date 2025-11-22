# Legal Contract Corpus

Complete corpus of 100 synthetic legal contracts for PDF parser evaluation.

## Overview

**Generated**: 2025-11-18
**Total Contracts**: 100
**Success Rate**: 100%
**Total Size**: ~14.5 MB (9.1 MB PDFs + 4.3 MB DOCX + 0.7 MB ground truth + 0.4 MB metadata)

## Distribution

| Contract Type | Count | ID Range |
|--------------|-------|----------|
| SaaS Agreement | 30 | legal_saas_001 - legal_saas_030 |
| Employment Agreement | 30 | legal_emp_031 - legal_emp_060 |
| Non-Disclosure Agreement | 20 | legal_nda_061 - legal_nda_080 |
| Consulting Agreement | 10 | legal_cons_081 - legal_cons_090 |
| Service Agreement | 10 | legal_svc_091 - legal_svc_100 |

## Files Per Contract

Each contract includes:
- **DOCX**: Source document (40-50 KB)
- **PDF**: Converted document (79-93 KB, multi-page)
- **Markdown**: Ground truth extraction
- **YAML**: Metadata with contract details and quality tags

## Quality Features

All contracts include:
- ✅ **Legal numbering** - 5-level hierarchy (1, 1.1, 1.1.1, (a), (i))
- ✅ **Recitals** - WHEREAS clauses
- ✅ **Defined terms** - Capitalized terms after definition
- ✅ **Signature blocks** - Professional signature pages
- ✅ **Multi-section structure** - Authentic legal organization
- ✅ **Professional formatting** - Times New Roman, proper spacing

## Sample Contract Characteristics

### SaaS Agreement (30 contracts)
- Platform names, service descriptions
- SLA terms (99.5%-99.95% uptime)
- Pricing ($10K-$500K annually)
- Data ownership and security clauses

### Employment Agreement (30 contracts)
- Job titles across 4 levels (entry to executive)
- Salaries ($60K-$300K)
- Bonus structures, severance terms
- Non-compete and IP assignment clauses

### Non-Disclosure Agreement (20 contracts)
- Mutual and unilateral NDAs
- Various disclosure purposes
- Confidential information definitions
- Return of materials provisions

### Consulting Agreement (10 contracts)
- Hourly rates ($50-$250/hr)
- Statement of Work frameworks
- Independent contractor language
- Work product ownership

### Service Agreement (10 contracts)
- Service descriptions and standards
- Payment schedules
- Insurance requirements
- Change order procedures

## Metadata Fields

Each YAML file contains:
- **Identity**: id, contract_type, generated_at
- **Classification**: source (synthetic), category (business), subcategory (legal)
- **Parties**: Varies by contract type (provider/customer, employer/employee, etc.)
- **Key Terms**: Contract-specific (salary, jurisdiction, rates, etc.)
- **Quality Tags**: legal_numbering, defined_terms, signature_blocks, recitals, multi_section
- **Complexity Indicators**: has_subsections, has_numbered_lists, has_legal_language, multi_page

## Use Cases

This corpus is designed to test PDF parsers on:
1. **Legal numbering extraction** - Multi-level hierarchical numbering
2. **Table of contents generation** - Section structure detection
3. **Defined terms tracking** - Capitalization consistency
4. **Multi-page layout** - Professional document formatting
5. **Signature block detection** - Contract execution sections
6. **Recitals parsing** - WHEREAS clause extraction

## Infrastructure

Built using:
- **Clause Library**: 60+ authentic legal clauses with variable substitution
- **Legal Numbering System**: 5-level hierarchical numbering
- **Contract Templates**: 5 templates using python-docx
- **Data Generators**: Realistic party names, dates, amounts using Faker
- **DOCX→PDF Conversion**: LibreOffice headless conversion

## Generation Statistics

- **Average generation time**: ~3-4 seconds per contract
- **Total generation time**: ~6-7 minutes for 100 contracts
- **PDF size range**: 79KB - 93KB
- **Ground truth size**: ~6-7KB markdown per contract
- **Metadata size**: ~4KB YAML per contract
