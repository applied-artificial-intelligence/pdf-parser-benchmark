"""Realistic data generators for invoice content.

This module generates authentic invoice data including:
- Company names and addresses
- Contact information
- Product/service descriptions with pricing
- Invoice numbers and dates
- Payment information
"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from faker import Faker


@dataclass
class CompanyInfo:
    """Company information for invoice."""

    name: str
    address: str
    city: str
    state_province: str
    postal_code: str
    country: str
    phone: str
    email: str
    website: str
    tax_id: str = ""


@dataclass
class LineItem:
    """Single line item on invoice."""

    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    amount: Decimal


class InvoiceDataGenerator:
    """Generator for realistic invoice data."""

    def __init__(self, region: str = "US", seed: int = None):
        """Initialize generator with region and optional seed.

        Args:
            region: One of "US", "EU", "UK", "CA", "APAC"
            seed: Random seed for reproducibility
        """
        self.region = region
        if seed:
            random.seed(seed)
            Faker.seed(seed)

        # Initialize Faker with appropriate locale
        locale_map = {
            "US": "en_US",
            "EU": "de_DE",  # Default to Germany for EU
            "UK": "en_GB",
            "CA": "en_CA",
            "APAC": "en_AU",  # Default to Australia for APAC
        }
        self.fake = Faker(locale_map.get(region, "en_US"))

    def generate_company(self, industry_config, is_vendor: bool = True) -> CompanyInfo:
        """Generate realistic company information.

        Args:
            industry_config: IndustryConfig instance
            is_vendor: True for vendor company, False for customer company

        Returns:
            CompanyInfo instance
        """
        # Generate company name from industry patterns
        if is_vendor:
            prefix = random.choice(industry_config.company_prefixes)
            suffix = random.choice(industry_config.company_suffixes)
            name = f"{prefix} {suffix}"
        else:
            # Customer can be any generic company
            name = self.fake.company()

        # Generate address based on region
        if self.region == "US":
            address = self.fake.street_address()
            city = self.fake.city()
            state = self.fake.state_abbr()
            postal = self.fake.zipcode()
            country = "USA"
            phone = self.fake.phone_number()
            tax_id = f"EIN: {random.randint(10, 99)}-{random.randint(1000000, 9999999)}"

        elif self.region == "EU":
            address = self.fake.street_address()
            city = self.fake.city()
            state = ""  # Not used in EU
            postal = self.fake.postcode()
            country = random.choice(["Germany", "France", "Italy", "Spain", "Netherlands"])
            phone = self.fake.phone_number()
            tax_id = ""  # Will be set via VAT number

        elif self.region == "UK":
            address = self.fake.street_address()
            city = self.fake.city()
            state = ""  # Not used in UK
            postal = self.fake.postcode()
            country = "United Kingdom"
            phone = self.fake.phone_number()
            tax_id = f"Company No. {random.randint(1000000, 9999999)}"

        elif self.region == "CA":
            address = self.fake.street_address()
            city = self.fake.city()
            state = random.choice(["ON", "BC", "AB", "QC", "NS", "MB", "SK"])
            postal = self.fake.postalcode()
            country = "Canada"
            phone = self.fake.phone_number()
            tax_id = f"BN: {random.randint(100000000, 999999999)}RT0001"

        else:  # APAC
            address = self.fake.street_address()
            city = self.fake.city()
            state = random.choice(["NSW", "VIC", "QLD", "WA", "SA", "TAS"])
            postal = self.fake.postcode()
            country = random.choice(["Australia", "New Zealand", "Singapore"])
            phone = self.fake.phone_number()
            tax_id = f"ABN: {random.randint(10000000000, 99999999999)}"

        # Generate email and website
        company_slug = name.lower().replace(" ", "").replace(",", "")[:20]
        email = f"billing@{company_slug}.com"
        website = f"www.{company_slug}.com"

        return CompanyInfo(
            name=name,
            address=address,
            city=city,
            state_province=state,
            postal_code=postal,
            country=country,
            phone=phone,
            email=email,
            website=website,
            tax_id=tax_id,
        )

    def generate_invoice_number(self, style: str = "standard") -> str:
        """Generate realistic invoice number.

        Args:
            style: One of "standard", "dated", "prefixed", "sequential"

        Returns:
            Invoice number string
        """
        if style == "dated":
            # Format: INV-YYYYMMDD-NNN
            date_str = datetime.now().strftime("%Y%m%d")
            seq = random.randint(1, 999)
            return f"INV-{date_str}-{seq:03d}"

        elif style == "prefixed":
            # Format: PREFIX-NNNNN
            prefix = random.choice(["INV", "SI", "BILL", "SO"])
            seq = random.randint(10000, 99999)
            return f"{prefix}-{seq}"

        elif style == "sequential":
            # Format: NNNNNN
            return str(random.randint(100000, 999999))

        else:  # standard
            # Format: INV-NNNNN
            seq = random.randint(10000, 99999)
            return f"INV-{seq}"

    def generate_invoice_date(self, days_ago_range: tuple[int, int] = (0, 90)) -> datetime:
        """Generate invoice date within specified range.

        Args:
            days_ago_range: Tuple of (min_days_ago, max_days_ago)

        Returns:
            datetime object
        """
        days_ago = random.randint(*days_ago_range)
        return datetime.now() - timedelta(days=days_ago)

    def generate_due_date(self, invoice_date: datetime, payment_terms: str) -> datetime:
        """Calculate due date based on payment terms.

        Args:
            invoice_date: Invoice date
            payment_terms: Payment terms string (e.g., "Net 30")

        Returns:
            datetime object
        """
        # Parse common payment terms
        if "Net" in payment_terms:
            # Extract number of days
            days = int(payment_terms.split()[-1])
            return invoice_date + timedelta(days=days)
        elif "Due on Receipt" in payment_terms:
            return invoice_date
        elif "Annual" in payment_terms or "Prepayment" in payment_terms:
            return invoice_date + timedelta(days=365)
        else:
            # Default to Net 30
            return invoice_date + timedelta(days=30)

    def generate_line_items(
        self, industry_config, count_range: tuple[int, int] = None, complexity: str = "medium"
    ) -> list[LineItem]:
        """Generate realistic line items for invoice.

        Args:
            industry_config: IndustryConfig instance
            count_range: Tuple of (min_items, max_items), defaults to industry typical
            complexity: "simple" (1-3 items), "medium" (4-10), "complex" (11-50)

        Returns:
            List of LineItem instances
        """
        # Determine item count based on complexity
        if complexity == "simple":
            count_range = (1, 3)
        elif complexity == "medium":
            count_range = (4, 10)
        elif complexity == "complex":
            count_range = (11, 50)
        elif count_range is None:
            count_range = industry_config.typical_line_items

        item_count = random.randint(*count_range)

        items = []
        for _ in range(item_count):
            # Select random product/service from industry config
            product = random.choice(industry_config.products_services)

            # Generate quantity
            quantity = Decimal(str(random.uniform(1, 100))).quantize(Decimal("0.01"))

            # Generate unit price within industry range
            min_price, max_price = product["price_range"]
            unit_price = Decimal(str(random.uniform(min_price, max_price))).quantize(
                Decimal("0.01")
            )

            # Calculate amount
            amount = (quantity * unit_price).quantize(Decimal("0.01"))

            items.append(
                LineItem(
                    description=product["name"],
                    quantity=quantity,
                    unit=product["unit"],
                    unit_price=unit_price,
                    amount=amount,
                )
            )

        return items

    def generate_po_number(self) -> str:
        """Generate realistic purchase order number.

        Returns:
            PO number string
        """
        prefix = random.choice(["PO", "P.O.", "Purchase Order"])
        if prefix == "Purchase Order":
            return f"{prefix} #{random.randint(100000, 999999)}"
        else:
            return f"{prefix}-{random.randint(100000, 999999)}"

    def generate_notes(self, industry_config, **kwargs) -> str:
        """Generate invoice notes/terms.

        Args:
            industry_config: IndustryConfig instance
            **kwargs: Variables to fill in template placeholders

        Returns:
            Notes text
        """
        template = random.choice(industry_config.notes_templates)

        # Fill in common placeholders
        company = kwargs.get("company", "example")
        date = kwargs.get("date", datetime.now().strftime("%Y-%m-%d"))
        po_number = kwargs.get("po_number", self.generate_po_number())
        invoice_number = kwargs.get("invoice_number", "INV-12345")

        notes = template.format(
            company=company,
            date=date,
            po_number=po_number,
            invoice_number=invoice_number,
            matter_number=kwargs.get("matter_number", f"M-{random.randint(1000, 9999)}"),
            project_name=kwargs.get("project_name", "Project Alpha"),
            period=kwargs.get("period", date),
            license_number=kwargs.get("license_number", f"LIC-{random.randint(100000, 999999)}"),
            campaign_name=kwargs.get("campaign_name", "Q4 Campaign"),
            project_number=kwargs.get("project_number", f"PRJ-{random.randint(1000, 9999)}"),
            email=kwargs.get("email", f"contact@{company}.com"),
            phone=kwargs.get("phone", "(555) 123-4567"),
            patient_id=kwargs.get("patient_id", f"PAT-{random.randint(10000, 99999)}"),
            order_number=kwargs.get("order_number", f"ORD-{random.randint(100000, 999999)}"),
            carrier=kwargs.get("carrier", "FedEx"),
            bol_number=kwargs.get("bol_number", f"BOL-{random.randint(100000, 999999)}"),
            rate=kwargs.get("rate", "15.5"),
            year=kwargs.get("year", str(datetime.now().year)),
            client_number=kwargs.get("client_number", f"CLI-{random.randint(1000, 9999)}"),
            preparer=kwargs.get("preparer", self.fake.name()),
            event_name=kwargs.get("event_name", "Annual Meeting"),
            count=kwargs.get("count", "50"),
            job_number=kwargs.get("job_number", f"JOB-{random.randint(10000, 99999)}"),
            ship_date=kwargs.get("ship_date", date),
            property_address=kwargs.get("property_address", self.fake.address().split("\n")[0]),
            phase=kwargs.get("phase", "Design Development"),
        )

        return notes

    def add_variation(self, items: list[LineItem], variation_type: str) -> list[LineItem]:
        """Add realistic variations to line items.

        Args:
            items: List of LineItem instances
            variation_type: "discount", "rush_fee", "shipping", "tax_exempt"

        Returns:
            Modified list of LineItem instances
        """
        if variation_type == "discount":
            # Add percentage discount
            subtotal = sum(item.amount for item in items)
            discount_pct = random.choice([Decimal("0.05"), Decimal("0.10"), Decimal("0.15")])
            discount_amount = -(subtotal * discount_pct).quantize(Decimal("0.01"))

            items.append(
                LineItem(
                    description=f"Volume Discount ({discount_pct * 100:.0f}%)",
                    quantity=Decimal("1"),
                    unit="discount",
                    unit_price=discount_amount,
                    amount=discount_amount,
                )
            )

        elif variation_type == "rush_fee":
            # Add rush processing fee
            rush_fee = random.choice([Decimal("50.00"), Decimal("100.00"), Decimal("250.00")])
            items.append(
                LineItem(
                    description="Rush Processing Fee",
                    quantity=Decimal("1"),
                    unit="fee",
                    unit_price=rush_fee,
                    amount=rush_fee,
                )
            )

        elif variation_type == "shipping":
            # Add shipping charge
            shipping = Decimal(str(random.uniform(15, 250))).quantize(Decimal("0.01"))
            items.append(
                LineItem(
                    description="Shipping & Handling",
                    quantity=Decimal("1"),
                    unit="shipment",
                    unit_price=shipping,
                    amount=shipping,
                )
            )

        return items
