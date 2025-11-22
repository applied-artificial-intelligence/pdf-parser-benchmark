# Business Document Types - Research-Backed Priority List

**Based on**: Web research Nov 2024, OCR market reports, enterprise automation trends

## Tier 1: HIGHEST VOLUME & BUSINESS VALUE

### **Accounts Payable / Finance** (BFSI = 21.3% of OCR market)
**Processing volume**: Millions per day across enterprises

1. **Invoices** ⭐⭐⭐⭐⭐
   - #1 most processed document type globally
   - Highly structured (vendor, date, line items, totals)
   - Clear success metric (data extraction accuracy)
   - Generation: Easy (standard AP invoice format)

2. **Receipts** ⭐⭐⭐⭐⭐
   - Massive volume (expense reporting)
   - Variable formats (retail, restaurant, gas, hotel)
   - OCR platforms have pre-trained models
   - Generation: Easy (receipt templates)

3. **Purchase Orders** ⭐⭐⭐⭐
   - Structured form (PO number, vendor, line items)
   - Paired with invoices (3-way matching)
   - Generation: Easy (standard PO format)

4. **Bank Statements** ⭐⭐⭐⭐
   - Structured tabular data
   - Account numbers, transactions, balances
   - Generation: Moderate (need realistic transaction data)

### **HR / Recruiting** (99% of Fortune 500 use ATS)
**Processing volume**: Millions of resumes annually

5. **Resumes/CVs** ⭐⭐⭐⭐⭐
   - ATS parsing = 95% accuracy target
   - Variable formats (chronological, functional, hybrid)
   - Clear extraction targets (name, email, skills, experience)
   - Generation: Easy (many templates available)

6. **Job Applications** ⭐⭐⭐⭐
   - Form-based data extraction
   - Paired with resumes
   - Generation: Easy (standard application forms)

### **Identity Verification / KYC** (65M docs in 2024, +41% YoY)
**Processing volume**: Massive (banking, healthcare, government)

7. **Passports** ⭐⭐⭐⭐⭐
   - Highly standardized (MRZ = Machine Readable Zone)
   - Critical for KYC/AML compliance
   - Generation: Moderate (need MRZ format)

8. **Driver's Licenses** ⭐⭐⭐⭐⭐
   - Standardized by state/country
   - Common KYC document
   - Generation: Moderate (state-specific formats)

9. **Utility Bills** ⭐⭐⭐⭐
   - Address verification for KYC
   - Structured (account number, address, amount)
   - Generation: Easy (standard utility bill format)

### **Legal Documents**
**Processing volume**: High in law firms, corporate legal

10. **Contracts** ⭐⭐⭐⭐⭐
    - SaaS agreements, employment contracts, NDAs
    - Highly structured (numbered clauses)
    - Automation tools widely used
    - Generation: Easy (standard contract templates)

11. **Court Filings** ⭐⭐⭐⭐
    - Pleadings, motions, briefs
    - Structured format (case number, parties, etc.)
    - Generation: Moderate (legal formatting required)

---

## Tier 2: HIGH VOLUME IN SPECIFIC INDUSTRIES

### **Healthcare** ($4.3B in AML penalties in 2024)

12. **Medical Claims (CMS-1500)** ⭐⭐⭐⭐⭐
    - Physician/professional claims
    - Highly standardized (81 fields)
    - Pre-configured extraction templates exist
    - Generation: Moderate (need to follow CMS format)

13. **Medical Claims (UB-04/CMS-1450)** ⭐⭐⭐⭐⭐
    - Hospital/institutional claims
    - Highly standardized
    - Generation: Moderate (CMS format)

14. **Prescriptions** ⭐⭐⭐⭐
    - High volume (pharmacy processing)
    - Structured fields (patient, drug, dosage)
    - Generation: Easy (Rx pad format)

### **Banking / Lending** (Mortgage = up to 20 forms per application)

15. **Loan Applications** ⭐⭐⭐⭐⭐
    - Massive volume (mortgages, auto, personal)
    - Structured forms (income, employment, assets)
    - Generation: Easy (standard loan application)

16. **Tax Forms** ⭐⭐⭐⭐⭐
    - W-2, 1099, 1040, etc.
    - IRS standardized formats
    - Generation: Moderate (need IRS format compliance)

17. **Pay Stubs** ⭐⭐⭐⭐
    - Income verification for loans
    - Semi-structured (employer, pay period, YTD)
    - Generation: Easy (payroll stub template)

### **Logistics / Supply Chain**

18. **Bill of Lading** ⭐⭐⭐⭐⭐
    - Critical shipping document
    - Structured fields (shipper, carrier, consignee)
    - 85% automation rate achieved by some companies
    - Generation: Easy (standard BOL format)

19. **Packing Slips** ⭐⭐⭐⭐
    - Paired with BOL
    - Line items, quantities, tracking
    - Generation: Easy (packing slip template)

20. **Commercial Invoice** ⭐⭐⭐⭐
    - International shipping
    - Customs compliance
    - Generation: Moderate (INCOTERMS, HS codes)

### **Insurance**

21. **Insurance Claims** ⭐⭐⭐⭐⭐
    - Auto, property, health
    - VIN extraction, damage codes
    - 35% faster claim approval with OCR
    - Generation: Moderate (claim form standards)

22. **Policy Documents** ⭐⭐⭐⭐
    - Insurance policies (auto, home, life)
    - Structured sections
    - Generation: Moderate (legal language)

---

## Tier 3: SPECIALIZED BUT IMPORTANT

### **Real Estate**

23. **Lease Agreements** ⭐⭐⭐⭐
    - Residential and commercial
    - State-specific standardized forms
    - Generation: Easy (state lease templates)

24. **Title Documents** ⭐⭐⭐
    - Property deeds, title insurance
    - Legal format
    - Generation: Difficult (legal complexity)

### **Government / Compliance**

25. **Tax Returns** ⭐⭐⭐⭐
    - Corporate and personal
    - IRS/state standardized
    - Generation: Moderate (tax forms)

26. **Regulatory Filings** ⭐⭐⭐
    - SEC, FDA, EPA submissions
    - Highly structured
    - Generation: Difficult (compliance requirements)

---

## Document Type Priorities for PDF-Bench

### **Phase 1: MVP (Choose 3-4 personas, ~12-15 docs)**

**Recommended:**

1. **Finance/AP** (5 docs):
   - Invoice (vendor, product, service) - 3 variations
   - Receipt (retail, restaurant) - 2 variations

2. **HR** (5 docs):
   - Resume (chronological, functional, technical) - 3 variations
   - Job application - 2 variations

3. **Legal** (5 docs):
   - SaaS contract - 2 variations
   - Employment agreement - 2 variations
   - NDA - 1 variation

**Rationale:**
- ✅ Covers 3 major use cases (Finance, HR, Legal)
- ✅ All are high-volume, high-value
- ✅ Easy to generate with templates
- ✅ Clear extraction targets (structured data)
- ✅ Diverse enough to show parser strengths/weaknesses

### **Phase 2: Expand Coverage (Add 2-3 more, ~10-12 docs)**

4. **Banking/KYC** (5 docs):
   - Loan application - 2 variations
   - Pay stub - 2 variations
   - Utility bill - 1 variation

5. **Logistics** (5 docs):
   - Bill of Lading - 3 variations
   - Packing slip - 2 variations

### **Phase 3: Specialized Industries (If demand exists)**

6. **Healthcare** (only if healthcare-focused users):
   - CMS-1500 claim
   - UB-04 claim
   - Prescription

7. **Insurance**:
   - Auto claim form
   - Property claim form

---

## Generation Feasibility Matrix

| Document Type | Template Availability | Data Generation | Legal/Compliance | Difficulty |
|---------------|----------------------|-----------------|------------------|-----------|
| Invoice | ⭐⭐⭐⭐⭐ Abundant | ⭐⭐⭐⭐⭐ Easy | ✅ None | **Easy** |
| Receipt | ⭐⭐⭐⭐⭐ Abundant | ⭐⭐⭐⭐⭐ Easy | ✅ None | **Easy** |
| Resume | ⭐⭐⭐⭐⭐ Abundant | ⭐⭐⭐⭐⭐ Easy (LLM) | ✅ None | **Easy** |
| Contract | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐ Good (LLM) | ⚠️  Legal review | **Moderate** |
| Loan App | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐ Easy | ⚠️  Compliance | **Moderate** |
| Tax Form | ⭐⭐⭐⭐ IRS templates | ⭐⭐⭐ Moderate | ⚠️⚠️ IRS format | **Moderate** |
| CMS-1500 | ⭐⭐⭐ CMS standard | ⭐⭐ Complex | ⚠️⚠️ HIPAA | **Hard** |
| Passport | ⭐⭐ MRZ format | ⭐⭐ Complex | ⚠️⚠️⚠️ Security | **Hard** |

---

## Key Insights from Research

1. **BFSI dominates**: 21.3% of OCR market = Finance, banking, insurance
2. **ATS near-universal**: 99% of Fortune 500 use resume parsing
3. **KYC growing fast**: 65M identity docs in 2024, +41% YoY
4. **Claims automation**: 35% faster processing with OCR
5. **Logistics impact**: 95% error reduction in Bill of Lading processing

**Bottom line**: Focus on **Invoices, Resumes, and Contracts** for maximum user relevance.

---

**Generated**: 2025-11-18
**Sources**: OCR market reports, enterprise automation vendors, industry surveys
