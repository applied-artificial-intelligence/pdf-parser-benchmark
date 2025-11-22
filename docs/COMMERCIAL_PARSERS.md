# Commercial PDF Parsers

PDF-Bench supports 5 commercial PDF parsing services, providing cost tracking, credential validation, and performance comparison against open-source alternatives.

## Overview

| Parser | Cost/1000 Pages | Best For | Setup Complexity |
|--------|----------------|----------|------------------|
| **AWS Textract** | $1.50 | General documents, forms, tables | Medium |
| **Azure Document Intelligence** | $1.50 | Structured documents, invoices, receipts | Medium |
| **Google Cloud Document AI** | $1.50 | High accuracy OCR, multi-language | Medium |
| **Databricks** | $3.00 | Enterprise lakehouse integration | High |
| **Landing AI** | $3.50 | Visual AI, complex layouts, forms | Low-Medium |

## Setup Instructions

### AWS Textract

**Prerequisites:**
- AWS account with Textract API access
- IAM credentials with `textract:DetectDocumentText` permission

**Environment Variables:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"  # Optional, defaults to us-east-1
```

**Python Usage:**
```python
from pdf_bench.systems import AWSTextractParser

parser = AWSTextractParser()
result = parser.parse(pdf_path, output_dir)
print(f"Cost: ${parser.last_parsing_cost:.4f}")
```

**Install Dependencies:**
```bash
uv pip install boto3
```

**Cost Details:**
- DetectDocumentText: $1.50 per 1,000 pages
- AnalyzeDocument (tables): $15 per 1,000 pages
- Free tier: 1,000 pages/month for first 3 months

**API Limits:**
- Max file size: 10 MB (synchronous)
- Max pages: 3,000 pages (synchronous)
- Rate limit: 300 pages/minute

---

### Azure Document Intelligence

**Prerequisites:**
- Azure subscription
- Document Intelligence resource created in Azure Portal
- API key from the resource

**Environment Variables:**
```bash
export AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="https://<resource-name>.cognitiveservices.azure.com/"
export AZURE_DOCUMENT_INTELLIGENCE_KEY="your-api-key"
```

**Python Usage:**
```python
from pdf_bench.systems import AzureDocumentIntelligenceParser

parser = AzureDocumentIntelligenceParser()
result = parser.parse(pdf_path, output_dir)
print(f"Cost: ${parser.last_parsing_cost:.4f}")
```

**Install Dependencies:**
```bash
uv pip install azure-ai-formrecognizer
```

**Cost Details:**
- Read model: $1.50 per 1,000 pages
- Layout model: $10 per 1,000 pages
- Prebuilt models (invoice, receipt): $10-$65 per 1,000 pages
- Free tier: 500 pages/month

**API Limits:**
- Max file size: 500 MB
- Rate limit: 15 requests/second (can be increased)

---

### Google Cloud Document AI

**Prerequisites:**
- Google Cloud Platform account
- Document AI API enabled
- Service account with Document AI User role
- Service account JSON key file downloaded

**Environment Variables:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us"  # Optional: us, eu, asia
export GOOGLE_DOCUMENT_AI_PROCESSOR_ID="processor-id"  # Optional: auto-creates if missing
```

**Python Usage:**
```python
from pdf_bench.systems import GoogleDocumentAIParser

parser = GoogleDocumentAIParser()
result = parser.parse(pdf_path, output_dir)
print(f"Cost: ${parser.last_parsing_cost:.4f}")
```

**Install Dependencies:**
```bash
uv pip install google-cloud-documentai
```

**Setup Steps:**
1. Create GCP project: `gcloud projects create pdf-bench`
2. Enable Document AI API: `gcloud services enable documentai.googleapis.com`
3. Create service account: `gcloud iam service-accounts create pdf-bench-sa`
4. Grant permissions: `gcloud projects add-iam-policy-binding PROJECT_ID --member="serviceAccount:pdf-bench-sa@PROJECT_ID.iam.gserviceaccount.com" --role="roles/documentai.apiUser"`
5. Download key: `gcloud iam service-accounts keys create key.json --iam-account=pdf-bench-sa@PROJECT_ID.iam.gserviceaccount.com`

**Cost Details:**
- Document OCR: $1.50 per 1,000 pages (first 1M pages/month)
- Form Parser: $45 per 1,000 pages
- Specialized parsers: $30-$65 per 1,000 pages
- Free tier: None (pay-as-you-go from page 1)

**API Limits:**
- Max file size: 20 MB (synchronous)
- Max pages: 15 pages (sync), unlimited (async)
- Rate limit: 600 pages/minute

---

### Databricks

**Prerequisites:**
- Databricks workspace (AWS, Azure, or GCP)
- Personal access token from workspace
- Optional: Running cluster for processing

**Environment Variables:**
```bash
export DATABRICKS_HOST="https://<workspace-id>.cloud.databricks.com"
export DATABRICKS_TOKEN="your-personal-access-token"
export DATABRICKS_CLUSTER_ID="cluster-id"  # Optional
```

**Python Usage:**
```python
from pdf_bench.systems import DatabricksParser

parser = DatabricksParser()
result = parser.parse(pdf_path, output_dir)
print(f"Cost: ${parser.last_parsing_cost:.4f}")
```

**Install Dependencies:**
```bash
uv pip install requests
```

**Setup Steps:**
1. Create Databricks workspace in your cloud provider
2. Generate personal access token: User Settings → Access Tokens → Generate New Token
3. (Optional) Create cluster for document processing
4. Configure environment variables

**Cost Details:**
- Estimated $3.00 per 1,000 pages
- Based on DBU (Databricks Unit) consumption: ~0.15 DBU per 100 pages
- DBU cost varies by workspace tier:
  - Standard: ~$0.40/DBU
  - Premium: ~$0.55/DBU
  - Enterprise: ~$0.65/DBU
- Actual cost depends on cluster configuration

**API Limits:**
- Max file size: 100 MB
- Rate limit: Depends on cluster configuration
- Batch processing recommended for large volumes

**Notes:**
- This is a placeholder implementation
- Production use requires setting up document processing pipeline
- Consider using Databricks ML models or Mosaic AI Document Intelligence

---

### Landing AI

**Prerequisites:**
- Landing AI account (https://landing.ai)
- API key from Landing AI platform
- Optional: Custom project ID for specialized models

**Environment Variables:**
```bash
export LANDING_AI_API_KEY="your-api-key"
export LANDING_AI_ENDPOINT="https://api.landing.ai/v1"  # Optional: defaults to production
export LANDING_AI_PROJECT_ID="project-id"  # Optional: for custom models
```

**Python Usage:**
```python
from pdf_bench.systems import LandingAIParser

parser = LandingAIParser()
result = parser.parse(pdf_path, output_dir)
print(f"Cost: ${parser.last_parsing_cost:.4f}")
```

**Install Dependencies:**
```bash
uv pip install requests pymupdf
```

**Setup Steps:**
1. Sign up at https://landing.ai/platform
2. Create new project (or use default)
3. Generate API key from Settings → API Keys
4. Set environment variable

**Cost Details:**
- Estimated $3.50 per 1,000 pages
- Pricing varies by plan (Starter, Professional, Enterprise)
- Custom models may have additional training costs
- Free tier: Limited pages for evaluation

**API Limits:**
- Max file size: 25 MB
- Rate limit: Varies by plan (typically 100-1000 requests/minute)
- Batch processing available

---

## Cost Estimation

Use the built-in cost estimator before parsing:

```python
from pathlib import Path
from pdf_bench.utils.cost_tracking import CostEstimator

# Estimate cost before parsing
estimator = CostEstimator()
pdfs = list(Path("corpus").glob("*.pdf"))
estimate = estimator.estimate_cost(pdfs, "aws_textract")

print(f"Total pages: {estimate.total_pages}")
print(f"Total cost: ${estimate.total_cost:.2f}")
print(f"PDF count: {estimate.pdf_count}")

# Per-PDF breakdown
for pdf_name, info in estimate.breakdown.items():
    print(f"{pdf_name}: {info['pages']} pages, ${info['cost']:.4f}")
```

## Cost Reporting

Track costs after parsing:

```python
from pdf_bench.utils.cost_tracking import CostReport

# Create report
report = CostReport()

# Add parsing results
report.add_parse_result("aws_textract", "doc1.pdf", pages=10, cost=0.015)
report.add_parse_result("azure_document_intelligence", "doc2.pdf", pages=5, cost=0.0075)

# Print summary
print(report.summary())

# Get cost by parser
for parser_name, cost in report.get_cost_by_parser().items():
    print(f"{parser_name}: ${cost:.4f}")
```

## Credential Validation

Validate credentials before running benchmarks:

```python
from pdf_bench.systems import (
    AWSTextractParser,
    AzureDocumentIntelligenceParser,
    GoogleDocumentAIParser,
    DatabricksParser,
    LandingAIParser,
)

parsers = {
    "AWS Textract": AWSTextractParser,
    "Azure": AzureDocumentIntelligenceParser,
    "Google Cloud": GoogleDocumentAIParser,
    "Databricks": DatabricksParser,
    "Landing AI": LandingAIParser,
}

for name, parser_class in parsers.items():
    is_valid, message = parser_class.validate_credentials()
    status = "✅" if is_valid else "❌"
    print(f"{status} {name}: {message}")
```

## Best Practices

### Cost Management

1. **Estimate before parsing**: Always run cost estimation for large corpora
2. **Set budget limits**: Use `--max-cost` flag to prevent overruns
3. **Test with samples**: Use `--test` mode with small subset first
4. **Monitor spending**: Track costs with `CostReport` throughout benchmarks

### Performance Optimization

1. **Batch processing**: Use async APIs for large volumes
2. **Parallel execution**: Some APIs support concurrent requests
3. **Local caching**: Cache results to avoid re-parsing
4. **Rate limiting**: Respect API rate limits to avoid throttling

### Security

1. **Rotate credentials**: Regularly rotate API keys and tokens
2. **Use IAM roles**: Prefer IAM roles over long-lived credentials (AWS)
3. **Least privilege**: Grant minimum required permissions
4. **Secret management**: Store credentials in secret managers, not code

## Troubleshooting

### Common Issues

**"Credentials not found" error:**
- Verify environment variables are set correctly
- Check file paths for service account JSON files
- Ensure credentials haven't expired

**"Rate limit exceeded" error:**
- Add delays between requests
- Reduce parallelism
- Request quota increase from provider

**"File too large" error:**
- Check API limits for each parser
- Split large documents into smaller chunks
- Use async APIs for large files

**High costs:**
- Review estimated costs before parsing
- Use cheaper APIs (OCR vs specialized parsers)
- Consider open-source alternatives for non-critical use

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Comparison Matrix

| Feature | AWS | Azure | Google | Databricks | Landing AI |
|---------|-----|-------|--------|------------|------------|
| **Cost/1000 pages** | $1.50 | $1.50 | $1.50 | $3.00 | $3.50 |
| **Accuracy (OCR)** | 99%+ | 99%+ | 99%+ | Varies | 98%+ |
| **Table extraction** | ✅ Good | ✅ Excellent | ✅ Good | ⚠️ Custom | ✅ Good |
| **Form detection** | ✅ Excellent | ✅ Excellent | ✅ Good | ⚠️ Custom | ✅ Excellent |
| **Multi-language** | 🟡 Limited | ✅ 100+ | ✅ 100+ | ⚠️ Depends | ✅ Good |
| **Handwriting** | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Custom | ✅ Yes |
| **Async processing** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Custom models** | 🟡 Limited | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Free tier** | ✅ 1000 pages/mo | ✅ 500 pages/mo | ❌ No | ❌ No | ✅ Limited |

## Support

For issues with:
- **PDF-Bench integration**: Open issue at https://github.com/pdf-bench/pdf-bench
- **AWS Textract**: AWS Support or AWS forums
- **Azure**: Azure Support or Microsoft Q&A
- **Google Cloud**: Google Cloud Support or Stack Overflow
- **Databricks**: Databricks Support or Community
- **Landing AI**: Landing AI Support at support@landing.ai

## License

Commercial parsers are subject to their respective terms of service. PDF-Bench integration is MIT licensed.
