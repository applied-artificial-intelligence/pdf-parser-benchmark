"""Invoice corpus generation module.

This module provides tools for generating realistic business invoices across:
- 5 geographic regions (US, EU, UK, CA, APAC)
- 15 industry types
- Multiple complexity and quality levels
"""

from builders.invoice.data_generators import InvoiceDataGenerator
from builders.invoice.industry_config import INDUSTRIES
from builders.invoice.tax_calculators import get_tax_calculator
from builders.invoice.templates import get_template

__all__ = [
    "INDUSTRIES",
    "InvoiceDataGenerator",
    "get_tax_calculator",
    "get_template",
]
