"""Regional tax calculation logic for invoice generation.

This module provides authentic tax calculation for 5 geographic regions:
- United States (state sales tax + local)
- European Union (VAT)
- United Kingdom (VAT)
- Canada (GST/HST + PST)
- Asia-Pacific (GST/VAT varies by country)
"""

from dataclasses import dataclass
from typing import Optional, Dict
from decimal import Decimal


@dataclass
class TaxResult:
    """Result of tax calculation."""
    subtotal: Decimal
    tax_amount: Decimal
    tax_rate: Decimal
    tax_label: str
    total: Decimal
    tax_number: Optional[str] = None  # VAT number, GST registration, etc.


class TaxCalculator:
    """Base class for regional tax calculators."""

    def calculate(self, subtotal: Decimal, **kwargs) -> TaxResult:
        """Calculate tax for a given subtotal."""
        raise NotImplementedError


class USTaxCalculator(TaxCalculator):
    """United States state sales tax calculator."""

    # Simplified state tax rates (combined state + average local)
    STATE_RATES = {
        "CA": Decimal("0.0875"),  # California
        "TX": Decimal("0.0820"),  # Texas
        "FL": Decimal("0.0700"),  # Florida
        "NY": Decimal("0.0852"),  # New York
        "IL": Decimal("0.0882"),  # Illinois
        "PA": Decimal("0.0634"),  # Pennsylvania
        "OH": Decimal("0.0723"),  # Ohio
        "GA": Decimal("0.0729"),  # Georgia
        "NC": Decimal("0.0698"),  # North Carolina
        "WA": Decimal("0.0929"),  # Washington
        "OR": Decimal("0.0000"),  # Oregon (no sales tax)
        "NH": Decimal("0.0000"),  # New Hampshire (no sales tax)
    }

    def calculate(self, subtotal: Decimal, state: str = "CA", **kwargs) -> TaxResult:
        """Calculate US state sales tax.

        Args:
            subtotal: Subtotal amount before tax
            state: Two-letter state code (default: CA)
        """
        rate = self.STATE_RATES.get(state, Decimal("0.0750"))  # Default 7.5%
        tax_amount = (subtotal * rate).quantize(Decimal("0.01"))
        total = subtotal + tax_amount

        return TaxResult(
            subtotal=subtotal,
            tax_amount=tax_amount,
            tax_rate=rate,
            tax_label=f"{state} Sales Tax ({rate * 100:.2f}%)",
            total=total,
        )


class EUTaxCalculator(TaxCalculator):
    """European Union VAT calculator."""

    # Standard VAT rates by country
    VAT_RATES = {
        "DE": Decimal("0.19"),   # Germany
        "FR": Decimal("0.20"),   # France
        "IT": Decimal("0.22"),   # Italy
        "ES": Decimal("0.21"),   # Spain
        "NL": Decimal("0.21"),   # Netherlands
        "BE": Decimal("0.21"),   # Belgium
        "AT": Decimal("0.20"),   # Austria
        "SE": Decimal("0.25"),   # Sweden
        "DK": Decimal("0.25"),   # Denmark
        "FI": Decimal("0.24"),   # Finland
        "PL": Decimal("0.23"),   # Poland
        "IE": Decimal("0.23"),   # Ireland
    }

    def calculate(self, subtotal: Decimal, country: str = "DE", **kwargs) -> TaxResult:
        """Calculate EU VAT.

        Args:
            subtotal: Subtotal amount before VAT
            country: Two-letter country code (default: DE)
        """
        rate = self.VAT_RATES.get(country, Decimal("0.20"))  # Default 20%
        tax_amount = (subtotal * rate).quantize(Decimal("0.01"))
        total = subtotal + tax_amount

        # Generate realistic VAT number
        vat_number = self._generate_vat_number(country)

        return TaxResult(
            subtotal=subtotal,
            tax_amount=tax_amount,
            tax_rate=rate,
            tax_label=f"VAT ({rate * 100:.0f}%)",
            total=total,
            tax_number=vat_number,
        )

    def _generate_vat_number(self, country: str) -> str:
        """Generate a realistic-looking VAT number."""
        import random
        if country == "DE":
            return f"DE{random.randint(100000000, 999999999)}"
        elif country == "FR":
            return f"FR{random.randint(10000000000, 99999999999)}"
        elif country == "IT":
            return f"IT{random.randint(10000000000, 99999999999)}"
        elif country == "ES":
            return f"ES{random.choice('ABCDEFGHJKLMNPQRSUVW')}{random.randint(10000000, 99999999)}"
        elif country == "NL":
            return f"NL{random.randint(100000000, 999999999)}B{random.randint(10, 99)}"
        else:
            return f"{country}{random.randint(100000000, 999999999)}"


class UKTaxCalculator(TaxCalculator):
    """United Kingdom VAT calculator."""

    STANDARD_RATE = Decimal("0.20")  # 20% standard rate
    REDUCED_RATE = Decimal("0.05")   # 5% reduced rate
    ZERO_RATE = Decimal("0.00")      # 0% zero rate

    def calculate(self, subtotal: Decimal, rate_type: str = "standard", **kwargs) -> TaxResult:
        """Calculate UK VAT.

        Args:
            subtotal: Subtotal amount before VAT
            rate_type: "standard", "reduced", or "zero" (default: standard)
        """
        if rate_type == "reduced":
            rate = self.REDUCED_RATE
        elif rate_type == "zero":
            rate = self.ZERO_RATE
        else:
            rate = self.STANDARD_RATE

        tax_amount = (subtotal * rate).quantize(Decimal("0.01"))
        total = subtotal + tax_amount

        # Generate realistic UK VAT number
        import random
        vat_number = f"GB{random.randint(100000000, 999999999)}"

        return TaxResult(
            subtotal=subtotal,
            tax_amount=tax_amount,
            tax_rate=rate,
            tax_label=f"VAT ({rate * 100:.0f}%)",
            total=total,
            tax_number=vat_number,
        )


class CanadaTaxCalculator(TaxCalculator):
    """Canada GST/HST + PST calculator."""

    # Tax rates by province
    PROVINCE_TAXES = {
        # HST provinces (harmonized - single rate)
        "ON": {"type": "HST", "rate": Decimal("0.13")},  # Ontario
        "NS": {"type": "HST", "rate": Decimal("0.15")},  # Nova Scotia
        "NB": {"type": "HST", "rate": Decimal("0.15")},  # New Brunswick
        "NL": {"type": "HST", "rate": Decimal("0.15")},  # Newfoundland
        "PE": {"type": "HST", "rate": Decimal("0.15")},  # Prince Edward Island

        # GST + PST provinces (separate)
        "BC": {"type": "GST+PST", "gst": Decimal("0.05"), "pst": Decimal("0.07")},  # British Columbia
        "SK": {"type": "GST+PST", "gst": Decimal("0.05"), "pst": Decimal("0.06")},  # Saskatchewan
        "MB": {"type": "GST+PST", "gst": Decimal("0.05"), "pst": Decimal("0.07")},  # Manitoba
        "QC": {"type": "GST+QST", "gst": Decimal("0.05"), "qst": Decimal("0.09975")},  # Quebec

        # GST only provinces
        "AB": {"type": "GST", "rate": Decimal("0.05")},  # Alberta
        "NT": {"type": "GST", "rate": Decimal("0.05")},  # Northwest Territories
        "NU": {"type": "GST", "rate": Decimal("0.05")},  # Nunavut
        "YT": {"type": "GST", "rate": Decimal("0.05")},  # Yukon
    }

    def calculate(self, subtotal: Decimal, province: str = "ON", **kwargs) -> TaxResult:
        """Calculate Canada GST/HST + PST.

        Args:
            subtotal: Subtotal amount before tax
            province: Two-letter province code (default: ON)
        """
        tax_config = self.PROVINCE_TAXES.get(province, {"type": "HST", "rate": Decimal("0.13")})

        if tax_config["type"] == "HST":
            # Single harmonized tax
            rate = tax_config["rate"]
            tax_amount = (subtotal * rate).quantize(Decimal("0.01"))
            tax_label = f"HST ({rate * 100:.0f}%)"
        elif tax_config["type"] in ["GST+PST", "GST+QST"]:
            # Separate GST and PST
            gst = tax_config["gst"]
            pst = tax_config.get("pst") or tax_config.get("qst")
            rate = gst + pst
            tax_amount = (subtotal * rate).quantize(Decimal("0.01"))
            if "qst" in tax_config:
                tax_label = f"GST ({gst * 100:.0f}%) + QST ({pst * 100:.2f}%)"
            else:
                tax_label = f"GST ({gst * 100:.0f}%) + PST ({pst * 100:.0f}%)"
        else:
            # GST only
            rate = tax_config["rate"]
            tax_amount = (subtotal * rate).quantize(Decimal("0.01"))
            tax_label = f"GST ({rate * 100:.0f}%)"

        total = subtotal + tax_amount

        # Generate realistic GST number
        import random
        gst_number = f"{random.randint(100000000, 999999999)}RT0001"

        return TaxResult(
            subtotal=subtotal,
            tax_amount=tax_amount,
            tax_rate=rate,
            tax_label=tax_label,
            total=total,
            tax_number=f"GST/HST: {gst_number}",
        )


class APACTaxCalculator(TaxCalculator):
    """Asia-Pacific GST/VAT calculator."""

    # Tax rates by country
    TAX_RATES = {
        "AU": {"type": "GST", "rate": Decimal("0.10")},   # Australia
        "NZ": {"type": "GST", "rate": Decimal("0.15")},   # New Zealand
        "SG": {"type": "GST", "rate": Decimal("0.09")},   # Singapore (9% as of 2024)
        "JP": {"type": "Consumption Tax", "rate": Decimal("0.10")},  # Japan
        "IN": {"type": "GST", "rate": Decimal("0.18")},   # India (standard rate)
        "MY": {"type": "SST", "rate": Decimal("0.10")},   # Malaysia (Sales & Service Tax)
    }

    def calculate(self, subtotal: Decimal, country: str = "AU", **kwargs) -> TaxResult:
        """Calculate APAC GST/VAT.

        Args:
            subtotal: Subtotal amount before tax
            country: Two-letter country code (default: AU)
        """
        tax_config = self.TAX_RATES.get(country, {"type": "GST", "rate": Decimal("0.10")})

        rate = tax_config["rate"]
        tax_type = tax_config["type"]
        tax_amount = (subtotal * rate).quantize(Decimal("0.01"))
        total = subtotal + tax_amount

        # Generate realistic tax number
        tax_number = self._generate_tax_number(country)

        return TaxResult(
            subtotal=subtotal,
            tax_amount=tax_amount,
            tax_rate=rate,
            tax_label=f"{tax_type} ({rate * 100:.0f}%)",
            total=total,
            tax_number=tax_number,
        )

    def _generate_tax_number(self, country: str) -> str:
        """Generate a realistic-looking tax registration number."""
        import random
        if country == "AU":
            # Australian ABN (Australian Business Number)
            return f"ABN {random.randint(10000000000, 99999999999)}"
        elif country == "NZ":
            # New Zealand GST number
            return f"GST {random.randint(100000000, 999999999)}"
        elif country == "SG":
            # Singapore GST registration
            return f"{random.randint(10000000, 99999999)}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
        elif country == "JP":
            # Japan Corporate Number
            return f"{random.randint(1000000000000, 9999999999999)}"
        elif country == "IN":
            # India GSTIN
            state_code = random.randint(10, 35)
            return f"{state_code}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.randint(1000, 9999)}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.randint(1, 9)}{random.choice('Z')}{random.randint(0, 9)}"
        else:
            return f"{country}{random.randint(100000000, 999999999)}"


# Regional calculator factory
def get_tax_calculator(region: str) -> TaxCalculator:
    """Get appropriate tax calculator for a region.

    Args:
        region: One of "US", "EU", "UK", "CA", "APAC"

    Returns:
        TaxCalculator instance for the region
    """
    calculators = {
        "US": USTaxCalculator(),
        "EU": EUTaxCalculator(),
        "UK": UKTaxCalculator(),
        "CA": CanadaTaxCalculator(),
        "APAC": APACTaxCalculator(),
    }
    return calculators.get(region, USTaxCalculator())
