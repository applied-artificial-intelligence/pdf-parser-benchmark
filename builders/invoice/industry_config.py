"""Industry-specific configuration for realistic invoice generation.

This module defines 15 industry types with authentic characteristics including:
- Realistic company name patterns
- Industry-specific products/services
- Appropriate pricing ranges
- Payment terms typical for each industry
- Line item structures
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class IndustryConfig:
    """Configuration for an industry type."""

    name: str
    company_suffixes: List[str]
    company_prefixes: List[str]
    products_services: List[Dict[str, Any]]  # {name, unit, price_range}
    payment_terms: List[str]
    typical_line_items: tuple[int, int]  # (min, max)
    notes_templates: List[str]


# SaaS / Cloud Services
SAAS_CONFIG = IndustryConfig(
    name="SaaS",
    company_suffixes=["Technologies", "Software", "Cloud", "Labs", "Digital", "Solutions"],
    company_prefixes=["Cloud", "Data", "Sync", "Stream", "Connect", "Flow", "Smart", "Nexus"],
    products_services=[
        {"name": "Enterprise Plan - Annual", "unit": "subscription", "price_range": (24000, 120000)},
        {"name": "Professional Plan - Monthly", "unit": "subscription", "price_range": (499, 2499)},
        {"name": "API Usage", "unit": "per 1000 calls", "price_range": (0.50, 5.00)},
        {"name": "Additional Storage", "unit": "TB/month", "price_range": (50, 200)},
        {"name": "Premium Support", "unit": "month", "price_range": (500, 5000)},
        {"name": "Implementation Services", "unit": "hour", "price_range": (150, 350)},
    ],
    payment_terms=["Net 30", "Due on Receipt", "Annual Prepayment", "Net 60"],
    typical_line_items=(1, 8),
    notes_templates=[
        "Thank you for your business. Support available 24/7 at support@{company}.com",
        "Auto-renews annually unless cancelled 30 days prior to renewal date.",
        "Questions? Contact your account manager or billing@{company}.com",
    ]
)

# Manufacturing / Industrial
MANUFACTURING_CONFIG = IndustryConfig(
    name="Manufacturing",
    company_suffixes=["Manufacturing", "Industries", "Inc", "Corp", "Industrial", "Fabrication"],
    company_prefixes=["Precision", "Advanced", "Titan", "Global", "United", "Standard"],
    products_services=[
        {"name": "Steel Plate - 1/4 inch", "unit": "sq ft", "price_range": (3.50, 8.00)},
        {"name": "CNC Machining", "unit": "hour", "price_range": (85, 150)},
        {"name": "Aluminum Extrusion", "unit": "linear ft", "price_range": (12, 35)},
        {"name": "Powder Coating", "unit": "sq ft", "price_range": (2.50, 6.00)},
        {"name": "Assembly Labor", "unit": "hour", "price_range": (45, 95)},
        {"name": "Quality Inspection", "unit": "hour", "price_range": (75, 125)},
        {"name": "Custom Tooling", "unit": "each", "price_range": (500, 5000)},
    ],
    payment_terms=["Net 30", "Net 45", "2% 10 Net 30", "Net 60"],
    typical_line_items=(3, 15),
    notes_templates=[
        "Purchase Order #{po_number} - Rush charges may apply for expedited orders.",
        "All materials conform to ASTM standards. Certifications available upon request.",
        "Standard lead time 4-6 weeks. Contact production@{company}.com for rush orders.",
    ]
)

# Legal Services
LEGAL_CONFIG = IndustryConfig(
    name="Legal",
    company_suffixes=["LLP", "P.C.", "Law Offices", "Legal Group", "Attorneys at Law"],
    company_prefixes=["Wilson", "Johnson", "Anderson", "Thompson", "Roberts", "Morgan"],
    products_services=[
        {"name": "Partner Legal Services", "unit": "hour", "price_range": (450, 850)},
        {"name": "Associate Legal Services", "unit": "hour", "price_range": (250, 450)},
        {"name": "Paralegal Services", "unit": "hour", "price_range": (125, 200)},
        {"name": "Legal Research", "unit": "hour", "price_range": (150, 275)},
        {"name": "Document Review", "unit": "hour", "price_range": (175, 325)},
        {"name": "Court Filing Fees", "unit": "filing", "price_range": (50, 500)},
        {"name": "Expert Witness Consultation", "unit": "hour", "price_range": (300, 600)},
    ],
    payment_terms=["Due on Receipt", "Net 15", "Retainer Applied", "Net 30"],
    typical_line_items=(2, 12),
    notes_templates=[
        "Matter: {matter_number}. Retain this invoice for your records.",
        "Detailed time entries available upon request. Questions? Contact billing@{company}.com",
        "Payment by wire transfer, check, or credit card accepted.",
    ]
)

# Freight / Logistics
FREIGHT_CONFIG = IndustryConfig(
    name="Freight",
    company_suffixes=["Logistics", "Freight", "Transport", "Shipping", "Express"],
    company_prefixes=["Global", "Express", "Swift", "Continental", "Premier", "Rapid"],
    products_services=[
        {"name": "LTL Freight - Class 50", "unit": "cwt", "price_range": (15, 45)},
        {"name": "LTL Freight - Class 85", "unit": "cwt", "price_range": (25, 65)},
        {"name": "Fuel Surcharge", "unit": "% of base", "price_range": (12, 28)},
        {"name": "Liftgate Service", "unit": "per stop", "price_range": (75, 150)},
        {"name": "Inside Delivery", "unit": "per stop", "price_range": (50, 125)},
        {"name": "Residential Delivery", "unit": "per stop", "price_range": (40, 95)},
        {"name": "Pallet Exchange", "unit": "pallet", "price_range": (15, 30)},
    ],
    payment_terms=["Net 15", "Quick Pay - 1% 5 Days", "Net 30", "Prepaid"],
    typical_line_items=(2, 8),
    notes_templates=[
        "BOL #{bol_number} - Shipment delivered on {date}. POD available online.",
        "Fuel surcharge updated weekly based on DOE index. Current rate: {rate}%",
        "Questions about this shipment? Call 1-800-{company} or email freight@{company}.com",
    ]
)

# Construction
CONSTRUCTION_CONFIG = IndustryConfig(
    name="Construction",
    company_suffixes=["Construction", "Builders", "Contractors", "Development", "Inc"],
    company_prefixes=["Summit", "Apex", "Foundation", "Elite", "Premier", "Cornerstone"],
    products_services=[
        {"name": "General Labor", "unit": "hour", "price_range": (35, 65)},
        {"name": "Skilled Carpentry", "unit": "hour", "price_range": (55, 95)},
        {"name": "Electrical Work", "unit": "hour", "price_range": (75, 135)},
        {"name": "Plumbing", "unit": "hour", "price_range": (80, 140)},
        {"name": "Materials - Lumber", "unit": "board ft", "price_range": (2.50, 8.00)},
        {"name": "Materials - Concrete", "unit": "cu yd", "price_range": (120, 180)},
        {"name": "Equipment Rental", "unit": "day", "price_range": (150, 800)},
        {"name": "Permits and Fees", "unit": "lump sum", "price_range": (500, 5000)},
    ],
    payment_terms=["Net 30", "Progress Payment", "Upon Completion", "Net 45"],
    typical_line_items=(4, 20),
    notes_templates=[
        "Project: {project_name} - Invoice #{invoice_number} for work period {period}",
        "Retain 10% until final completion and inspection. License #: {license_number}",
        "Change orders require written approval. Contact PM@{company}.com",
    ]
)

# Marketing / Advertising Agency
MARKETING_CONFIG = IndustryConfig(
    name="Marketing",
    company_suffixes=["Agency", "Marketing", "Media", "Creative", "Group", "Studios"],
    company_prefixes=["Bright", "Spark", "Vision", "Zenith", "Catalyst", "Elevate"],
    products_services=[
        {"name": "Creative Direction", "unit": "hour", "price_range": (150, 300)},
        {"name": "Copywriting", "unit": "hour", "price_range": (100, 200)},
        {"name": "Graphic Design", "unit": "hour", "price_range": (85, 175)},
        {"name": "Social Media Management", "unit": "month", "price_range": (2000, 8000)},
        {"name": "Video Production", "unit": "day", "price_range": (1500, 5000)},
        {"name": "Media Buy - Digital", "unit": "campaign", "price_range": (5000, 50000)},
        {"name": "Analytics & Reporting", "unit": "month", "price_range": (500, 2000)},
    ],
    payment_terms=["50% Deposit, 50% on Completion", "Net 30", "Net 15", "Due on Receipt"],
    typical_line_items=(3, 10),
    notes_templates=[
        "Campaign: {campaign_name} - Deliverables due {date}",
        "Media buy is net of agency commission. Detailed reporting available in client portal.",
        "Questions? Contact your account executive at {email}",
    ]
)

# IT Services / Consulting
IT_CONSULTING_CONFIG = IndustryConfig(
    name="IT Consulting",
    company_suffixes=["Consulting", "IT Solutions", "Systems", "Technology Group", "Services"],
    company_prefixes=["Tech", "Digital", "Vertex", "Quantum", "Synergy", "Pinnacle"],
    products_services=[
        {"name": "Senior Consultant", "unit": "hour", "price_range": (175, 325)},
        {"name": "Systems Analyst", "unit": "hour", "price_range": (125, 225)},
        {"name": "Network Engineer", "unit": "hour", "price_range": (150, 250)},
        {"name": "Project Management", "unit": "hour", "price_range": (140, 240)},
        {"name": "After-Hours Support", "unit": "hour", "price_range": (200, 400)},
        {"name": "Cloud Migration Services", "unit": "project", "price_range": (10000, 100000)},
        {"name": "Security Assessment", "unit": "assessment", "price_range": (5000, 25000)},
    ],
    payment_terms=["Net 30", "Net 45", "Net 60", "Monthly Retainer"],
    typical_line_items=(2, 12),
    notes_templates=[
        "Project #{project_number} - Hours for period ending {date}",
        "Detailed time logs attached. All work performed remotely unless noted.",
        "Questions? Contact your project manager at pm@{company}.com",
    ]
)

# Medical / Healthcare Services
MEDICAL_CONFIG = IndustryConfig(
    name="Medical",
    company_suffixes=["Medical Group", "Healthcare", "Clinic", "Associates", "P.C."],
    company_prefixes=["Premier", "Advanced", "Optimal", "Complete", "Integrated", "Summit"],
    products_services=[
        {"name": "Medical Consultation", "unit": "visit", "price_range": (150, 350)},
        {"name": "Diagnostic Imaging", "unit": "procedure", "price_range": (300, 2000)},
        {"name": "Laboratory Services", "unit": "panel", "price_range": (50, 500)},
        {"name": "Physical Therapy", "unit": "session", "price_range": (100, 200)},
        {"name": "Specialized Procedure", "unit": "procedure", "price_range": (500, 5000)},
        {"name": "Medical Supplies", "unit": "item", "price_range": (10, 200)},
    ],
    payment_terms=["Due on Receipt", "Net 30", "Payment Plan Available"],
    typical_line_items=(1, 8),
    notes_templates=[
        "Patient: {patient_id} - Date of Service: {date} - Insurance pending",
        "This is not a bill. Your insurance carrier may pay all or part of this amount.",
        "Questions about billing? Call (555) 123-4567 or visit our billing portal.",
    ]
)

# Retail / E-commerce
RETAIL_CONFIG = IndustryConfig(
    name="Retail",
    company_suffixes=["Supply", "Distributors", "Wholesale", "Direct", "Outlet"],
    company_prefixes=["Metro", "National", "Direct", "Quality", "Value", "Wholesale"],
    products_services=[
        {"name": "Office Supplies - Bulk", "unit": "case", "price_range": (25, 150)},
        {"name": "Electronics - Various", "unit": "each", "price_range": (50, 2000)},
        {"name": "Furniture - Office", "unit": "each", "price_range": (200, 3000)},
        {"name": "Cleaning Supplies", "unit": "case", "price_range": (30, 120)},
        {"name": "Break Room Supplies", "unit": "case", "price_range": (40, 180)},
        {"name": "Shipping & Handling", "unit": "order", "price_range": (15, 250)},
    ],
    payment_terms=["Net 30", "2% 10 Net 30", "Credit Card", "Net 45"],
    typical_line_items=(3, 25),
    notes_templates=[
        "Order #{order_number} - Shipped via {carrier} on {date}",
        "Volume discounts available. Contact sales@{company}.com for quote.",
        "Returns accepted within 30 days with original packaging.",
    ]
)

# Architecture / Engineering
ARCHITECTURE_CONFIG = IndustryConfig(
    name="Architecture",
    company_suffixes=["Architects", "Design Group", "AIA", "Studio", "Associates"],
    company_prefixes=["Studio", "Design", "Modern", "Landmark", "Urban", "Visionary"],
    products_services=[
        {"name": "Schematic Design", "unit": "% of project", "price_range": (15, 25)},
        {"name": "Design Development", "unit": "% of project", "price_range": (20, 35)},
        {"name": "Construction Documents", "unit": "% of project", "price_range": (40, 50)},
        {"name": "Principal Architect", "unit": "hour", "price_range": (200, 400)},
        {"name": "Project Architect", "unit": "hour", "price_range": (125, 225)},
        {"name": "CAD Technician", "unit": "hour", "price_range": (75, 135)},
        {"name": "Site Visits", "unit": "visit", "price_range": (250, 1000)},
    ],
    payment_terms=["Net 30", "Progress Payments", "Net 45", "Retainer"],
    typical_line_items=(3, 10),
    notes_templates=[
        "Project: {project_name} - Phase: {phase} - Invoice #{invoice_number}",
        "Architectural services per AIA B101 agreement dated {date}",
        "Questions? Contact project lead at design@{company}.com",
    ]
)

# Accounting / Financial Services
ACCOUNTING_CONFIG = IndustryConfig(
    name="Accounting",
    company_suffixes=["CPA", "Accounting", "Financial Services", "Tax Group", "LLP"],
    company_prefixes=["Premier", "Trusted", "Precision", "Summit", "Alliance", "Liberty"],
    products_services=[
        {"name": "Tax Preparation - Individual", "unit": "return", "price_range": (250, 1500)},
        {"name": "Tax Preparation - Corporate", "unit": "return", "price_range": (1500, 15000)},
        {"name": "Bookkeeping Services", "unit": "month", "price_range": (300, 2000)},
        {"name": "Audit Services", "unit": "hour", "price_range": (150, 350)},
        {"name": "Payroll Processing", "unit": "month", "price_range": (100, 1000)},
        {"name": "Financial Planning", "unit": "hour", "price_range": (200, 400)},
    ],
    payment_terms=["Due on Receipt", "Net 15", "50% Deposit", "Net 30"],
    typical_line_items=(1, 8),
    notes_templates=[
        "Tax Year {year} - Client: {client_number} - Prepared by {preparer}",
        "All work performed in accordance with GAAP and AICPA standards.",
        "Questions? Contact your accountant at {email} or call {phone}",
    ]
)

# Catering / Food Service
CATERING_CONFIG = IndustryConfig(
    name="Catering",
    company_suffixes=["Catering", "Events", "Hospitality", "Culinary", "Services"],
    company_prefixes=["Gourmet", "Elite", "Premier", "Savory", "Exquisite", "Tasteful"],
    products_services=[
        {"name": "Breakfast Buffet", "unit": "per person", "price_range": (12, 30)},
        {"name": "Lunch Service", "unit": "per person", "price_range": (15, 45)},
        {"name": "Dinner Service - Plated", "unit": "per person", "price_range": (35, 120)},
        {"name": "Appetizers - Passed", "unit": "dozen", "price_range": (25, 75)},
        {"name": "Bar Service", "unit": "hour", "price_range": (150, 400)},
        {"name": "Service Staff", "unit": "hour", "price_range": (25, 50)},
        {"name": "Equipment Rental", "unit": "event", "price_range": (200, 2000)},
        {"name": "Delivery & Setup", "unit": "event", "price_range": (100, 500)},
    ],
    payment_terms=["50% Deposit, Balance Due Day of Event", "Net 15", "Due on Receipt"],
    typical_line_items=(4, 15),
    notes_templates=[
        "Event: {event_name} on {date} - Guest count: {count}",
        "Gratuity (18%) and service charge included. Sales tax additional.",
        "Final count due 72 hours prior to event. Contact events@{company}.com",
    ]
)

# Printing / Publishing
PRINTING_CONFIG = IndustryConfig(
    name="Printing",
    company_suffixes=["Printing", "Graphics", "Press", "Publishing", "Print Solutions"],
    company_prefixes=["Precision", "Quality", "Express", "Digital", "Professional", "Creative"],
    products_services=[
        {"name": "Business Cards - 4/4 Color", "unit": "per 1000", "price_range": (50, 200)},
        {"name": "Brochures - Tri-fold", "unit": "per 1000", "price_range": (200, 800)},
        {"name": "Letterhead - 1 Color", "unit": "per 1000", "price_range": (100, 400)},
        {"name": "Posters - Large Format", "unit": "sq ft", "price_range": (8, 25)},
        {"name": "Binding Services", "unit": "book", "price_range": (3, 15)},
        {"name": "Graphic Design", "unit": "hour", "price_range": (75, 150)},
        {"name": "Rush Production", "unit": "% surcharge", "price_range": (25, 50)},
    ],
    payment_terms=["50% Deposit, 50% on Completion", "Net 30", "Credit Card", "Net 15"],
    typical_line_items=(2, 10),
    notes_templates=[
        "Job #{job_number} - Proof approved {date} - Ship date: {ship_date}",
        "All work guaranteed. Reprints for errors at no charge.",
        "Questions? Contact production@{company}.com or call {phone}",
    ]
)

# Property Management / Real Estate
PROPERTY_MGMT_CONFIG = IndustryConfig(
    name="Property Management",
    company_suffixes=["Properties", "Realty", "Management", "Real Estate", "Group"],
    company_prefixes=["Prime", "Summit", "Keystone", "Landmark", "Elite", "Premier"],
    products_services=[
        {"name": "Property Management Fee", "unit": "% of rent", "price_range": (8, 12)},
        {"name": "Leasing Fee - New Tenant", "unit": "% of annual rent", "price_range": (50, 100)},
        {"name": "Maintenance Coordination", "unit": "hour", "price_range": (50, 100)},
        {"name": "Tenant Screening", "unit": "application", "price_range": (35, 75)},
        {"name": "Property Inspection", "unit": "inspection", "price_range": (75, 200)},
        {"name": "Eviction Processing", "unit": "case", "price_range": (500, 2000)},
        {"name": "Marketing & Advertising", "unit": "month", "price_range": (200, 1000)},
    ],
    payment_terms=["Net 15", "ACH Auto-Pay", "Net 30", "Due on Receipt"],
    typical_line_items=(2, 8),
    notes_templates=[
        "Property: {property_address} - Period: {period}",
        "Owner statement available in online portal. Login at portal.{company}.com",
        "Questions? Contact your property manager at {email}",
    ]
)

# Landscaping / Grounds Maintenance
LANDSCAPING_CONFIG = IndustryConfig(
    name="Landscaping",
    company_suffixes=["Landscaping", "Lawn Care", "Grounds Maintenance", "Services", "Inc"],
    company_prefixes=["Green", "Pro", "Elite", "Complete", "Premier", "Quality"],
    products_services=[
        {"name": "Weekly Mowing Service", "unit": "month", "price_range": (150, 500)},
        {"name": "Spring Cleanup", "unit": "service", "price_range": (200, 800)},
        {"name": "Fall Cleanup", "unit": "service", "price_range": (200, 800)},
        {"name": "Mulch Installation", "unit": "cu yd", "price_range": (50, 120)},
        {"name": "Tree Trimming", "unit": "hour", "price_range": (75, 150)},
        {"name": "Fertilization Treatment", "unit": "application", "price_range": (50, 200)},
        {"name": "Irrigation Maintenance", "unit": "visit", "price_range": (100, 300)},
        {"name": "Snow Removal", "unit": "push", "price_range": (75, 300)},
    ],
    payment_terms=["Net 15", "Due on Receipt", "Monthly Auto-Pay", "Net 30"],
    typical_line_items=(2, 10),
    notes_templates=[
        "Property: {property_address} - Service date: {date}",
        "Seasonal contracts available - save 15%. Call {phone} for details.",
        "Questions or service requests? Email service@{company}.com",
    ]
)


# Complete industry registry
INDUSTRIES = {
    "saas": SAAS_CONFIG,
    "manufacturing": MANUFACTURING_CONFIG,
    "legal": LEGAL_CONFIG,
    "freight": FREIGHT_CONFIG,
    "construction": CONSTRUCTION_CONFIG,
    "marketing": MARKETING_CONFIG,
    "it_consulting": IT_CONSULTING_CONFIG,
    "medical": MEDICAL_CONFIG,
    "retail": RETAIL_CONFIG,
    "architecture": ARCHITECTURE_CONFIG,
    "accounting": ACCOUNTING_CONFIG,
    "catering": CATERING_CONFIG,
    "printing": PRINTING_CONFIG,
    "property_mgmt": PROPERTY_MGMT_CONFIG,
    "landscaping": LANDSCAPING_CONFIG,
}
