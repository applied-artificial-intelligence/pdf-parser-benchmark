"""Generate synthetic DOCX corpus using templates.

This script creates 3 synthetic documents from DOCX templates:
1. 06_docx_simple - Simple business report
2. 07_docx_tables - Table-heavy financial document
3. 08_docx_multicolumn - Multi-column research article

Each document is:
- Rendered from template with realistic test data
- Converted to PDF via LibreOffice
- Ground truth extracted from DOCX structure
- Metadata created with hashes
"""

from pathlib import Path

from build_docx import DocxBuilder  # type: ignore[import-not-found]


def create_simple_report_context() -> dict:
    """Create context data for simple report template."""
    return {
        "title": "Annual Performance Review 2025",
        "author": "Jane Smith, Chief Operations Officer",
        "date": "November 14, 2025",
        "report_id": "APR-2025-001",
        "executive_summary": (
            "This report presents a comprehensive analysis of organizational "
            "performance for fiscal year 2025. Key metrics show sustained growth "
            "across all departments, with revenue increasing by 23% and customer "
            "satisfaction reaching an all-time high of 94%. Strategic initiatives "
            "launched in Q2 have yielded measurable improvements in operational "
            "efficiency and market positioning."
        ),
        "introduction": (
            "The 2025 fiscal year marked a period of significant transformation "
            "for our organization. Building on the foundation established in "
            "previous years, we implemented targeted strategies to enhance "
            "productivity, streamline operations, and expand our market presence. "
            "This report evaluates performance against established benchmarks "
            "and provides insights into areas of achievement and opportunity."
        ),
        "background": (
            "Our organization entered 2025 with ambitious goals: achieve double-digit "
            "revenue growth, improve operational efficiency by 15%, and enhance "
            "customer satisfaction scores. These objectives were developed through "
            "extensive stakeholder consultation and market analysis. The competitive "
            "landscape required agility and innovation to maintain our market "
            "leadership position."
        ),
        "methodology": (
            "This evaluation employs a multi-dimensional approach combining "
            "quantitative metrics and qualitative assessments. Data sources include "
            "financial statements, customer surveys, employee feedback, and "
            "operational dashboards. We analyzed quarterly performance trends, "
            "conducted comparative benchmarking against industry standards, and "
            "reviewed strategic initiative outcomes. All findings were validated "
            "through cross-departmental review processes."
        ),
        "findings": (
            "Analysis reveals several notable achievements. Revenue growth exceeded "
            "targets at 23%, driven primarily by new product launches and market "
            "expansion. Operational efficiency improvements resulted in a 17% "
            "reduction in processing time. Customer satisfaction scores increased "
            "from 87% to 94%, reflecting enhanced service delivery. Employee "
            "engagement metrics showed positive trends, with retention rates "
            "improving by 8 percentage points."
        ),
        "observations": [
            "Revenue growth concentrated in emerging markets (65% of total increase)",
            "Digital transformation initiatives exceeded adoption projections by 40%",
            "Supply chain optimization reduced costs by $2.3M annually",
            "Customer retention improved across all market segments",
            "Employee productivity increased 12% following training programs",
        ],
        "results": (
            "The organization achieved or exceeded 87% of established objectives. "
            "Financial performance was robust, with EBITDA margins expanding to 28%. "
            "Market share increased by 3.2 percentage points, solidifying our "
            "position as industry leader. Innovation metrics demonstrate sustained "
            "investment in R&D, with 5 new products launched successfully. "
            "Operational KPIs show consistent improvement across quality, "
            "efficiency, and customer satisfaction dimensions."
        ),
        "conclusion": (
            "The 2025 fiscal year represents a milestone in organizational evolution. "
            "Strategic priorities were successfully executed, yielding tangible "
            "improvements across all performance dimensions. While challenges remain, "
            "particularly in talent acquisition and technology infrastructure, the "
            "foundation for continued success is firmly established. The organization "
            "is well-positioned to capitalize on emerging opportunities and navigate "
            "evolving market dynamics."
        ),
        "recommendations": [
            "Accelerate digital transformation with $5M investment in cloud infrastructure",
            "Expand operations into Asia-Pacific markets within 18 months",
            "Implement advanced analytics platform for predictive insights",
            "Enhance talent development programs to address skills gaps",
            "Strengthen sustainability initiatives to meet ESG commitments",
        ],
        "references": (
            "Internal financial statements (2023-2025), Industry benchmark reports "
            "(Gartner, McKinsey), Customer satisfaction surveys (Q1-Q4 2025), "
            "Employee engagement data (Quarterly pulse surveys), Operational KPI "
            "dashboards (Real-time metrics), Strategic planning documents (Board "
            "approved initiatives)."
        ),
    }


def create_table_heavy_context() -> dict:
    """Create context data for table-heavy template."""
    return {
        "title": "Global Financial Performance Report Q1-Q4 2025",
        "author": "David Chen, Chief Financial Officer",
        "date": "November 14, 2025",
        "introduction": (
            "This comprehensive financial report presents detailed performance "
            "metrics across all business units and geographic regions for fiscal "
            "year 2025. Analysis includes quarterly trends, regional comparisons, "
            "and product-level profitability assessments."
        ),
        "regional_intro": (
            "Regional performance analysis reveals diverse growth patterns, with "
            "emerging markets leading expansion efforts while mature markets "
            "demonstrate stable, predictable returns."
        ),
        "summary": (
            "Consolidated results show strong financial health with balanced growth "
            "across geographies and product lines. Strategic investments in high-"
            "margin segments have improved overall profitability while maintaining "
            "market competitiveness."
        ),
        # TABLE-01: Basic metrics
        "metric_1_name": "Annual Revenue",
        "metric_1_value": "$487.3M",
        "metric_1_unit": "USD",
        "metric_2_name": "EBITDA Margin",
        "metric_2_value": "28.4%",
        "metric_2_unit": "Percent",
        "metric_3_name": "Net Income",
        "metric_3_value": "$92.1M",
        "metric_3_unit": "USD",
        # TABLE-02: Quarterly financials
        "q1_revenue": "$115.2M",
        "q1_expenses": "$82.7M",
        "q1_net_income": "$32.5M",
        "q1_margin": "28.2%",
        "q2_revenue": "$118.9M",
        "q2_expenses": "$84.1M",
        "q2_net_income": "$34.8M",
        "q2_margin": "29.3%",
        "q3_revenue": "$121.7M",
        "q3_expenses": "$87.2M",
        "q3_net_income": "$34.5M",
        "q3_margin": "28.3%",
        "q4_revenue": "$131.5M",
        "q4_expenses": "$91.3M",
        "q4_net_income": "$40.2M",
        "q4_margin": "30.6%",
        # TABLE-03: Regional performance
        "north_america_sales": "$198.4M",
        "north_america_growth": "+12.3%",
        "north_america_share": "40.7%",
        "europe_sales": "$156.2M",
        "europe_growth": "+8.7%",
        "europe_share": "32.1%",
        "asia_pacific_sales": "$98.5M",
        "asia_pacific_growth": "+45.2%",
        "asia_pacific_share": "20.2%",
        "latin_america_sales": "$24.1M",
        "latin_america_growth": "+18.9%",
        "latin_america_share": "4.9%",
        "africa_sales": "$10.1M",
        "africa_growth": "+31.4%",
        "africa_share": "2.1%",
        # TABLE-04: Product metrics
        "product_1_name": "Cloud Platform",
        "product_1_units": "12,450",
        "product_1_price": "$2,400",
        "product_1_revenue": "$29.9M",
        "product_1_cost": "$18.2M",
        "product_1_profit": "$11.7M",
        "product_1_roi": "64.3%",
        "product_2_name": "Analytics Suite",
        "product_2_units": "8,730",
        "product_2_price": "$1,850",
        "product_2_revenue": "$16.2M",
        "product_2_cost": "$9.8M",
        "product_2_profit": "$6.4M",
        "product_2_roi": "65.3%",
        "product_3_name": "Mobile App",
        "product_3_units": "45,200",
        "product_3_price": "$120",
        "product_3_revenue": "$5.4M",
        "product_3_cost": "$2.1M",
        "product_3_profit": "$3.3M",
        "product_3_roi": "157.1%",
        # TABLE-05: Team assignments
        "team_1_name": "Product Development",
        "team_1_lead": "Sarah Johnson",
        "team_1_focus": "Cloud infrastructure, API development, Platform scalability",
        "team_2_name": "Customer Success",
        "team_2_lead": "Michael Torres",
        "team_2_focus": "Onboarding, Training, Support operations, Retention programs",
        "team_3_name": "Market Expansion",
        "team_3_lead": "Emily Zhang",
        "team_3_focus": "APAC growth, Partnership development, Localization efforts",
    }


def create_multicolumn_context() -> dict:
    """Create context data for multi-column template."""
    return {
        "title": "Advances in Machine Learning for Natural Language Processing",
        "subtitle": "A Comprehensive Review of Transformer Architectures",
        "author": "Dr. Alex Martinez, MIT Computer Science",
        "date": "November 2025",
        "abstract": (
            "This paper presents a comprehensive analysis of transformer-based "
            "architectures in natural language processing, examining recent "
            "developments in attention mechanisms, model scaling, and efficiency "
            "optimization. We evaluate performance across benchmark datasets and "
            "propose novel approaches to reduce computational requirements while "
            "maintaining accuracy. Our findings demonstrate that architectural "
            "innovations can achieve state-of-the-art results with 40% fewer "
            "parameters through strategic layer design and attention pattern "
            "optimization."
        ),
        "keywords": (
            "transformers, attention mechanisms, NLP, language models, efficiency, "
            "BERT, GPT, model compression"
        ),
        "intro_paragraph": (
            "The field of natural language processing has undergone revolutionary "
            "change with the introduction of transformer architectures. Traditional "
            "sequential models have been largely superseded by parallel attention-"
            "based approaches that capture long-range dependencies more effectively."
        ),
        "section_1_title": "Background and Motivation",
        "section_1_content": (
            "Transformer models, introduced by Vaswani et al. in 2017, revolutionized "
            "sequence-to-sequence learning through self-attention mechanisms. Unlike "
            "recurrent architectures, transformers process entire sequences in parallel, "
            "enabling efficient training on modern GPU hardware. The self-attention "
            "mechanism computes representations by attending to all positions in the "
            "input, capturing dependencies regardless of distance. This fundamental "
            "shift enabled models to scale to billions of parameters, achieving "
            "unprecedented performance on language understanding tasks."
        ),
        "section_2_title": "Architectural Components",
        "section_2_content": (
            "Core transformer components include multi-head self-attention layers, "
            "position-wise feed-forward networks, and layer normalization. The multi-"
            "head mechanism allows the model to attend to information from different "
            "representation subspaces. Residual connections facilitate gradient flow "
            "through deep networks. Positional encodings inject sequence order "
            "information, compensating for the permutation-invariant nature of "
            "attention operations. Recent variants explore different normalization "
            "schemes, activation functions, and attention patterns to improve "
            "efficiency and performance."
        ),
        "section_3_title": "Scaling Considerations",
        "section_3_content": (
            "Model scaling has been a primary driver of performance improvements. "
            "Empirical studies demonstrate log-linear relationships between model "
            "size, dataset size, and performance. However, computational costs scale "
            "quadratically with sequence length due to attention operations. This "
            "limitation motivates research into efficient attention mechanisms, "
            "sparse patterns, and linear approximations. Techniques such as gradient "
            "checkpointing, mixed precision training, and model parallelism enable "
            "training of models with hundreds of billions of parameters across "
            "distributed hardware."
        ),
        "section_4_title": "Efficiency Optimization",
        "section_4_content": (
            "Recent work focuses on reducing computational requirements through "
            "architectural innovations and training optimizations. Sparse attention "
            "patterns reduce complexity from O(n²) to O(n√n) or O(n log n). Knowledge "
            "distillation transfers capabilities from large models to smaller variants. "
            "Quantization reduces numerical precision, enabling efficient inference. "
            "Our experiments show that combining these techniques yields 40% parameter "
            "reduction with less than 2% performance degradation on GLUE benchmarks. "
            "These advances make large language models more accessible for deployment "
            "in resource-constrained environments."
        ),
        "approach_a_performance": "Standard transformer: 89.2% accuracy, 355M parameters",
        "approach_a_cost": "$12,000 training cost, 40ms latency",
        "approach_a_scalability": "Linear scaling to 1024 sequence length",
        "approach_b_performance": "Optimized variant: 87.4% accuracy, 213M parameters",
        "approach_b_cost": "$4,200 training cost, 18ms latency",
        "approach_b_scalability": "Efficient scaling to 4096 sequence length",
        "key_point_1": (
            "Transformer architectures achieve superior performance through parallel "
            "self-attention mechanisms that capture long-range dependencies effectively."
        ),
        "key_point_2": (
            "Computational efficiency can be significantly improved through sparse "
            "attention patterns, layer optimization, and precision reduction techniques."
        ),
        "key_point_3": (
            "Our proposed architecture achieves comparable accuracy to standard models "
            "while reducing parameters by 40% and inference latency by 55%."
        ),
        "conclusion": (
            "This work demonstrates that strategic architectural modifications and "
            "training optimizations can substantially reduce computational requirements "
            "of transformer-based language models while maintaining competitive "
            "performance. Our findings suggest that the field is moving beyond simple "
            "scaling toward more efficient and sustainable model designs. Future work "
            "should explore adaptive computation, mixture-of-experts architectures, "
            "and continual learning to further enhance efficiency and capability."
        ),
        "future_work": [
            "Investigate adaptive attention mechanisms that allocate computation dynamically",
            "Explore mixture-of-experts architectures for conditional computation",
            "Develop continual learning approaches to update models without full retraining",
            "Study cross-lingual transfer and multilingual model efficiency",
            "Examine environmental impact and sustainable training practices",
        ],
    }


def main() -> None:
    """Generate all synthetic DOCX documents."""
    print("=" * 80)
    print("DOCX Synthetic Corpus Generation")
    print("=" * 80)
    print()

    templates_dir = Path("corpus/synthetic/templates")
    output_dir = Path("corpus/synthetic")

    builder = DocxBuilder(templates_dir, output_dir)

    documents = [
        {
            "template": "01_simple_report.docx",
            "output": "06_docx_simple",
            "title": "Annual Performance Review 2025",
            "context": create_simple_report_context(),
        },
        {
            "template": "02_table_heavy.docx",
            "output": "07_docx_tables",
            "title": "Global Financial Performance Report Q1-Q4 2025",
            "context": create_table_heavy_context(),
        },
        {
            "template": "03_multicolumn.docx",
            "output": "08_docx_multicolumn",
            "title": "Advances in Machine Learning for NLP",
            "context": create_multicolumn_context(),
        },
    ]

    results = []
    for i, doc in enumerate(documents, 1):
        print(f"[{i}/3] {doc['output']}")
        print("-" * 80)

        try:
            result = builder.build_document(
                template_name=doc["template"],
                output_name=doc["output"],
                title=doc["title"],
                context=doc["context"],
            )
            results.append(result)
            print()
        except Exception as e:
            print(f"ERROR: Failed to build {doc['output']}: {e}")
            raise

    print("=" * 80)
    print("✓ Generation Complete!")
    print("=" * 80)
    print()
    print(f"Generated {len(results)} documents:")
    for i, doc in enumerate(documents, 1):
        output_name = str(doc["output"])
        print(f"  {i}. {output_name}")
        print(f"     - DOCX: {output_dir / output_name}.docx")
        print(f"     - PDF:  {output_dir / output_name}.pdf")
        print(f"     - GT:   {output_dir / output_name}.md")
        print(f"     - META: {output_dir / output_name}.yaml")
        print()

    print("Summary:")
    print(f"  Total documents: {len(results)}")
    print(f"  Total files:     {len(results) * 4}")
    print(f"  Output location: {output_dir}")
    print()
    print("Next: Visual inspection and validation (TASK-016 completion)")


if __name__ == "__main__":
    main()
