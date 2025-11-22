"""Contract-specific configuration for realistic legal document generation.

This module defines 5 contract types with authentic characteristics including:
- Required and optional sections
- Defined terms that should be capitalized
- Typical clause patterns
- Contract-specific boilerplate language
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ContractSection:
    """Configuration for a contract section."""
    name: str
    required: bool
    subsections: List[str] = None


@dataclass
class ContractConfig:
    """Configuration for a contract type."""
    name: str
    sections: List[ContractSection]
    defined_terms: List[str]  # Terms that should be capitalized after definition
    recitals: List[str]  # WHEREAS clauses
    party_types: List[str]  # e.g., ["Provider", "Client"] or ["Company", "Employee"]
    typical_duration: tuple[int, int]  # (min_months, max_months)
    typical_value_range: tuple[int, int]  # (min_amount, max_amount) in USD
    governing_law_jurisdictions: List[str]


# SaaS Agreement Configuration
SAAS_CONFIG = ContractConfig(
    name="SaaS Agreement",
    sections=[
        ContractSection("Definitions", required=True),
        ContractSection("Services", required=True, subsections=[
            "Service Description",
            "Service Level Agreement",
            "Support Services",
        ]),
        ContractSection("Subscription and Fees", required=True, subsections=[
            "Subscription Plans",
            "Payment Terms",
            "Invoicing",
        ]),
        ContractSection("Data and Privacy", required=True, subsections=[
            "Data Ownership",
            "Data Security",
            "Privacy Compliance",
        ]),
        ContractSection("Intellectual Property", required=True),
        ContractSection("Term and Termination", required=True, subsections=[
            "Initial Term",
            "Renewal",
            "Termination for Cause",
            "Effect of Termination",
        ]),
        ContractSection("Warranties and Disclaimers", required=True),
        ContractSection("Limitation of Liability", required=True),
        ContractSection("Indemnification", required=False),
        ContractSection("General Provisions", required=True, subsections=[
            "Governing Law",
            "Dispute Resolution",
            "Notices",
            "Entire Agreement",
        ]),
    ],
    defined_terms=[
        "Service", "Services", "Platform", "Subscription", "Subscriber",
        "Customer Data", "Confidential Information", "Documentation",
        "Service Level Agreement", "SLA", "Uptime", "Support Services",
    ],
    recitals=[
        "Provider offers a cloud-based software platform",
        "Customer desires to subscribe to and use the Services",
        "Parties wish to establish terms governing such use",
    ],
    party_types=["Provider", "Customer"],
    typical_duration=(12, 36),  # 1-3 years
    typical_value_range=(10000, 500000),  # $10K - $500K annually
    governing_law_jurisdictions=["Delaware", "California", "New York"],
)


# Employment Agreement Configuration
EMPLOYMENT_CONFIG = ContractConfig(
    name="Employment Agreement",
    sections=[
        ContractSection("Position and Duties", required=True),
        ContractSection("Compensation", required=True, subsections=[
            "Base Salary",
            "Bonus and Incentives",
            "Benefits",
        ]),
        ContractSection("Term of Employment", required=True),
        ContractSection("Termination", required=True, subsections=[
            "Termination by Company",
            "Termination by Employee",
            "Severance",
        ]),
        ContractSection("Confidentiality", required=True),
        ContractSection("Intellectual Property Assignment", required=True),
        ContractSection("Non-Compete and Non-Solicitation", required=False),
        ContractSection("At-Will Employment", required=True),
        ContractSection("General Provisions", required=True, subsections=[
            "Governing Law",
            "Entire Agreement",
            "Amendments",
        ]),
    ],
    defined_terms=[
        "Employee", "Company", "Position", "Base Salary", "Bonus",
        "Confidential Information", "Intellectual Property", "Work Product",
        "Termination Date", "Severance", "Benefits",
    ],
    recitals=[
        "Company desires to employ Employee in the specified position",
        "Employee wishes to accept such employment",
        "Parties desire to set forth terms of employment relationship",
    ],
    party_types=["Company", "Employee"],
    typical_duration=(0, 36),  # 0 = at-will, or fixed term up to 3 years
    typical_value_range=(60000, 300000),  # $60K - $300K annual salary
    governing_law_jurisdictions=["California", "New York", "Texas", "Delaware"],
)


# Non-Disclosure Agreement (NDA) Configuration
NDA_CONFIG = ContractConfig(
    name="Non-Disclosure Agreement",
    sections=[
        ContractSection("Definitions", required=True),
        ContractSection("Confidential Information", required=True, subsections=[
            "Definition of Confidential Information",
            "Exclusions from Confidential Information",
        ]),
        ContractSection("Obligations", required=True, subsections=[
            "Non-Disclosure",
            "Non-Use",
            "Protection Measures",
        ]),
        ContractSection("Permitted Disclosures", required=True),
        ContractSection("Return of Materials", required=True),
        ContractSection("Term and Termination", required=True),
        ContractSection("Remedies", required=True),
        ContractSection("General Provisions", required=True, subsections=[
            "Governing Law",
            "Entire Agreement",
            "Severability",
        ]),
    ],
    defined_terms=[
        "Confidential Information", "Disclosing Party", "Receiving Party",
        "Purpose", "Representatives", "Effective Date", "Term",
    ],
    recitals=[
        "Parties contemplate entering into business discussions",
        "Disclosures of Confidential Information may be necessary",
        "Parties desire to protect confidentiality of such information",
    ],
    party_types=["Disclosing Party", "Receiving Party"],
    typical_duration=(12, 60),  # 1-5 years
    typical_value_range=(0, 0),  # NDAs typically have no monetary value specified
    governing_law_jurisdictions=["Delaware", "California", "New York"],
)


# Consulting Agreement Configuration
CONSULTING_CONFIG = ContractConfig(
    name="Consulting Agreement",
    sections=[
        ContractSection("Services", required=True, subsections=[
            "Scope of Services",
            "Deliverables",
            "Timeline",
        ]),
        ContractSection("Compensation", required=True, subsections=[
            "Fees",
            "Expenses",
            "Payment Terms",
        ]),
        ContractSection("Term and Termination", required=True),
        ContractSection("Independent Contractor Relationship", required=True),
        ContractSection("Intellectual Property", required=True, subsections=[
            "Work Product Ownership",
            "Pre-Existing IP",
            "License Grants",
        ]),
        ContractSection("Confidentiality", required=True),
        ContractSection("Representations and Warranties", required=True),
        ContractSection("Indemnification", required=False),
        ContractSection("Limitation of Liability", required=False),
        ContractSection("General Provisions", required=True, subsections=[
            "Governing Law",
            "Dispute Resolution",
            "Entire Agreement",
        ]),
    ],
    defined_terms=[
        "Consultant", "Client", "Services", "Deliverables", "Work Product",
        "Fees", "Confidential Information", "Effective Date",
        "Pre-Existing IP", "Statement of Work",
    ],
    recitals=[
        "Client desires to engage Consultant to provide certain services",
        "Consultant has expertise and is willing to provide such services",
        "Parties wish to establish terms governing engagement",
    ],
    party_types=["Client", "Consultant"],
    typical_duration=(3, 12),  # 3 months - 1 year
    typical_value_range=(15000, 250000),  # $15K - $250K total
    governing_law_jurisdictions=["California", "New York", "Delaware"],
)


# Service Agreement Configuration
SERVICE_CONFIG = ContractConfig(
    name="Service Agreement",
    sections=[
        ContractSection("Services", required=True, subsections=[
            "Service Description",
            "Service Standards",
            "Service Locations",
        ]),
        ContractSection("Fees and Payment", required=True, subsections=[
            "Service Fees",
            "Payment Schedule",
            "Late Payments",
        ]),
        ContractSection("Term and Renewal", required=True),
        ContractSection("Responsibilities of Parties", required=True, subsections=[
            "Service Provider Obligations",
            "Customer Obligations",
        ]),
        ContractSection("Changes to Services", required=True),
        ContractSection("Termination", required=True, subsections=[
            "Termination for Convenience",
            "Termination for Cause",
            "Effect of Termination",
        ]),
        ContractSection("Warranties", required=True),
        ContractSection("Limitation of Liability", required=True),
        ContractSection("Insurance", required=False),
        ContractSection("General Provisions", required=True, subsections=[
            "Governing Law",
            "Notices",
            "Entire Agreement",
        ]),
    ],
    defined_terms=[
        "Service Provider", "Customer", "Services", "Service Fees",
        "Service Standards", "Term", "Effective Date", "Service Locations",
        "Change Order", "Force Majeure",
    ],
    recitals=[
        "Customer requires certain services to be provided",
        "Service Provider is in the business of providing such services",
        "Parties desire to enter into agreement for provision of services",
    ],
    party_types=["Service Provider", "Customer"],
    typical_duration=(12, 36),  # 1-3 years
    typical_value_range=(25000, 1000000),  # $25K - $1M annually
    governing_law_jurisdictions=["Delaware", "California", "New York", "Texas"],
)


# Complete contract type registry
CONTRACTS = {
    "saas": SAAS_CONFIG,
    "employment": EMPLOYMENT_CONFIG,
    "nda": NDA_CONFIG,
    "consulting": CONSULTING_CONFIG,
    "service": SERVICE_CONFIG,
}
