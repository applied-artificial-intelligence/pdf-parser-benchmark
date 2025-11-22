"""Data generators for realistic legal contract content.

Generates authentic-looking contract data including:
- Party information (companies, individuals, addresses)
- Contract dates and terms
- Monetary values (fees, salaries, rates)
- Contract-specific data (services, job titles, etc.)
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from faker import Faker

from .contract_config import (
    SAAS_CONFIG, EMPLOYMENT_CONFIG, NDA_CONFIG,
    CONSULTING_CONFIG, SERVICE_CONFIG, ContractConfig
)


@dataclass
class Party:
    """Represents a party to a contract."""
    name: str
    type: str  # "Company", "Individual", "Provider", etc.
    address: str
    city: str
    state: str
    zip: str

    @property
    def full_address(self) -> str:
        """Get formatted full address."""
        return f"{self.address}, {self.city}, {self.state} {self.zip}"


class LegalDataGenerator:
    """Generates realistic legal contract data."""

    def __init__(self, seed: int = None):
        """Initialize generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)

    def generate_company_party(self, party_type: str = "Company") -> Party:
        """Generate a company party.

        Args:
            party_type: Party type label (e.g., "Provider", "Client", "Company")

        Returns:
            Party instance for a company
        """
        # Generate company name with common structures
        company_types = [
            lambda: f"{self.fake.company()} Inc.",
            lambda: f"{self.fake.company()} LLC",
            lambda: f"{self.fake.company()} Corporation",
            lambda: f"{self.fake.company()} Ltd.",
            lambda: f"{self.fake.last_name()} {random.choice(['Technologies', 'Solutions', 'Systems', 'Enterprises'])}",
        ]

        company_name = random.choice(company_types)()

        return Party(
            name=company_name,
            type=party_type,
            address=self.fake.street_address(),
            city=self.fake.city(),
            state=self.fake.state_abbr(),
            zip=self.fake.zipcode(),
        )

    def generate_individual_party(self, party_type: str = "Individual") -> Party:
        """Generate an individual party.

        Args:
            party_type: Party type label (e.g., "Employee", "Consultant")

        Returns:
            Party instance for an individual
        """
        name = self.fake.name()

        return Party(
            name=name,
            type=party_type,
            address=self.fake.street_address(),
            city=self.fake.city(),
            state=self.fake.state_abbr(),
            zip=self.fake.zipcode(),
        )

    def generate_contract_date(self, past_days: int = 365) -> str:
        """Generate a contract effective date.

        Args:
            past_days: Maximum days in the past

        Returns:
            Formatted date string (e.g., "January 15, 2024")
        """
        days_ago = random.randint(0, past_days)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%B %d, %Y")

    def generate_jurisdiction(self) -> str:
        """Generate a governing law jurisdiction.

        Returns:
            State name for jurisdiction
        """
        common_jurisdictions = [
            "Delaware", "California", "New York", "Texas",
            "Illinois", "Massachusetts", "Washington", "Florida"
        ]
        return random.choice(common_jurisdictions)

    def generate_monetary_value(self, min_amount: int, max_amount: int) -> int:
        """Generate a monetary value within a range.

        Args:
            min_amount: Minimum amount
            max_amount: Maximum amount

        Returns:
            Random amount (rounded to reasonable increments)
        """
        amount = random.randint(min_amount, max_amount)

        # Round to reasonable increments based on magnitude
        if amount < 1000:
            return (amount // 100) * 100
        elif amount < 10000:
            return (amount // 500) * 500
        elif amount < 100000:
            return (amount // 1000) * 1000
        else:
            return (amount // 5000) * 5000

    def generate_term_months(self, min_months: int, max_months: int) -> int:
        """Generate contract term in months.

        Args:
            min_months: Minimum term
            max_months: Maximum term

        Returns:
            Term in months
        """
        return random.randint(min_months, max_months)

    # ============================================================
    # SAAS-SPECIFIC GENERATORS
    # ============================================================

    def generate_saas_variables(self) -> Dict[str, any]:
        """Generate variables for SaaS Agreement.

        Returns:
            Dictionary of variables for template substitution
        """
        provider = self.generate_company_party("Provider")
        customer = self.generate_company_party("Customer")

        # Platform/service names
        platform_adjectives = ["Cloud", "Smart", "Enterprise", "Pro", "Digital", "Adaptive", "Integrated"]
        platform_types = ["Platform", "Suite", "Hub", "Workspace", "Portal", "Engine"]
        platform_name = f"{random.choice(platform_adjectives)} {random.choice(platform_types)}"

        # Service purposes
        purposes = [
            "streamline business operations and improve productivity",
            "manage customer relationships and sales processes",
            "facilitate project management and team collaboration",
            "automate workflow and business processes",
            "analyze data and generate business intelligence",
        ]

        # Pricing
        monthly_fee = self.generate_monetary_value(*SAAS_CONFIG.typical_value_range)
        annual_fee = monthly_fee  # Stored as annual in config, but we'll use monthly

        # Service levels
        uptime_options = ["99.5", "99.9", "99.95"]

        # Plan tiers
        plan_tiers = ["Basic", "Professional", "Enterprise", "Premium"]

        return {
            "provider": provider.name,
            "customer": customer.name,
            "provider_address": provider.full_address,
            "customer_address": customer.full_address,
            "effective_date": self.generate_contract_date(),
            "platform_name": platform_name,
            "service_purpose": random.choice(purposes),
            "uptime_pct": random.choice(uptime_options),
            "notice_hours": random.choice([24, 48, 72]),
            "business_hours": random.choice(["9am-5pm EST", "8am-6pm PST", "Monday-Friday 9am-5pm"]),
            "critical_response_hrs": random.choice([1, 2, 4]),
            "high_response_hrs": random.choice([8, 12, 24]),
            "normal_response_hrs": random.choice([24, 48, 72]),
            "plan_tier": random.choice(plan_tiers),
            "monthly_fee": monthly_fee // 12,  # Convert annual to monthly
            "max_users": random.choice([5, 10, 25, 50, 100]),
            "storage_gb": random.choice([10, 50, 100, 250, 500]),
            "per_user_fee": random.choice([10, 15, 20, 25, 30]),
            "payment_days": random.choice([15, 30, 45]),
            "interest_rate": random.choice([1.0, 1.5, 2.0]),
            "jurisdiction": self.generate_jurisdiction(),
            "initial_term_months": self.generate_term_months(*SAAS_CONFIG.typical_duration),
            "renewal_term_months": random.choice([12, 24, 36]),
            "notice_days": random.choice([30, 60, 90]),
            "start_date": self.generate_contract_date(),
            "billing_frequency": random.choice(["monthly", "quarterly", "annually"]),
            "suspension_days": random.choice([15, 30, 45]),
            "liability_period": random.choice([6, 12, 24]),
        }

    # ============================================================
    # EMPLOYMENT-SPECIFIC GENERATORS
    # ============================================================

    def generate_employment_variables(self) -> Dict[str, any]:
        """Generate variables for Employment Agreement.

        Returns:
            Dictionary of variables for template substitution
        """
        company = self.generate_company_party("Company")
        employee = self.generate_individual_party("Employee")

        # Job titles by level
        job_titles = {
            "entry": ["Software Engineer", "Marketing Associate", "Sales Representative", "Data Analyst"],
            "mid": ["Senior Software Engineer", "Marketing Manager", "Account Manager", "Product Manager"],
            "senior": ["Engineering Manager", "Director of Marketing", "Sales Director", "VP of Operations"],
            "executive": ["VP of Engineering", "Chief Marketing Officer", "Chief Revenue Officer", "Chief Technology Officer"],
        }

        level = random.choice(["entry", "mid", "senior", "executive"])
        position_title = random.choice(job_titles[level])

        # Reports to
        reports_to_titles = {
            "entry": ["Senior Manager", "Director", "Team Lead"],
            "mid": ["Director", "VP", "Senior Director"],
            "senior": ["VP", "C-Suite Executive", "CEO"],
            "executive": ["CEO", "Board of Directors", "President"],
        }
        reports_to = random.choice(reports_to_titles[level])

        # Salary based on level
        annual_salary = self.generate_monetary_value(*EMPLOYMENT_CONFIG.typical_value_range)

        # Bonus percentage
        bonus_pct = random.choice([10, 15, 20, 25, 30])

        # Severance weeks
        severance_weeks = random.choice([4, 8, 12, 16, 26])

        # Non-compete/non-solicitation terms
        noncompete_months = random.choice([6, 12, 18, 24])
        nonsolicitation_months = random.choice([12, 18, 24])
        noncompete_radius = random.choice([25, 50, 100])
        lookback_months = random.choice([12, 18, 24])

        return {
            "company": company.name,
            "employee": employee.name,
            "position_title": position_title,
            "reports_to": reports_to,
            "annual_salary": f"{annual_salary:,}",
            "bonus_pct": bonus_pct,
            "severance_weeks": severance_weeks,
            "noncompete_months": noncompete_months,
            "nonsolicitation_months": nonsolicitation_months,
            "noncompete_radius": noncompete_radius,
            "lookback_months": lookback_months,
            "effective_date": self.generate_contract_date(),
            "jurisdiction": self.generate_jurisdiction(),
        }

    # ============================================================
    # NDA-SPECIFIC GENERATORS
    # ============================================================

    def generate_nda_variables(self) -> Dict[str, any]:
        """Generate variables for NDA.

        Returns:
            Dictionary of variables for template substitution
        """
        disclosing_party = self.generate_company_party("Disclosing Party")
        receiving_party = self.generate_company_party("Receiving Party")

        # Purposes
        purposes = [
            "evaluating a potential business relationship",
            "discussing a potential merger or acquisition",
            "exploring a strategic partnership",
            "evaluating investment opportunities",
            "discussing technology licensing opportunities",
        ]

        return {
            "disclosing_party": disclosing_party.name,
            "receiving_party": receiving_party.name,
            "purpose": random.choice(purposes),
            "effective_date": self.generate_contract_date(),
            "jurisdiction": self.generate_jurisdiction(),
        }

    # ============================================================
    # CONSULTING-SPECIFIC GENERATORS
    # ============================================================

    def generate_consulting_variables(self) -> Dict[str, any]:
        """Generate variables for Consulting Agreement.

        Returns:
            Dictionary of variables for template substitution
        """
        client = self.generate_company_party("Client")

        # Consultant can be individual or company
        if random.random() < 0.7:  # 70% individual consultants
            consultant = self.generate_individual_party("Consultant")
        else:
            consultant = self.generate_company_party("Consultant")

        # Hourly rate based on typical value range
        total_value = self.generate_monetary_value(*CONSULTING_CONFIG.typical_value_range)
        estimated_hours = random.randint(100, 1000)
        hourly_rate = (total_value // estimated_hours // 5) * 5  # Round to $5

        # Payment terms
        payment_days = random.choice([15, 30, 45])
        review_days = random.choice([3, 5, 7, 10])

        return {
            "client": client.name,
            "consultant": consultant.name,
            "hourly_rate": hourly_rate,
            "payment_days": payment_days,
            "review_days": review_days,
            "effective_date": self.generate_contract_date(),
            "jurisdiction": self.generate_jurisdiction(),
        }

    # ============================================================
    # SERVICE AGREEMENT-SPECIFIC GENERATORS
    # ============================================================

    def generate_service_variables(self) -> Dict[str, any]:
        """Generate variables for Service Agreement.

        Returns:
            Dictionary of variables for template substitution
        """
        service_provider = self.generate_company_party("Service Provider")
        customer = self.generate_company_party("Customer")

        # Service descriptions
        service_types = [
            "IT infrastructure management and support services",
            "facility maintenance and janitorial services",
            "security and monitoring services",
            "marketing and advertising services",
            "accounting and bookkeeping services",
        ]

        # Billing
        billing_frequencies = ["monthly", "quarterly", "annually"]

        # Fees
        annual_fee = self.generate_monetary_value(*SERVICE_CONFIG.typical_value_range)

        # Insurance coverage
        gl_coverage = random.choice([1000000, 2000000, 3000000])  # General liability
        pl_coverage = random.choice([1000000, 2000000, 3000000])  # Professional liability

        return {
            "service_provider": service_provider.name,
            "customer": customer.name,
            "service_description": random.choice(service_types),
            "start_date": self.generate_contract_date(),
            "effective_date": self.generate_contract_date(),
            "billing_frequency": random.choice(billing_frequencies),
            "payment_days": random.choice([15, 30, 45]),
            "suspension_days": random.choice([15, 30, 45]),
            "initial_term_months": self.generate_term_months(*SERVICE_CONFIG.typical_duration),
            "renewal_term_months": random.choice([12, 24, 36]),
            "notice_days": random.choice([30, 60, 90]),
            "jurisdiction": self.generate_jurisdiction(),
            "liability_period": random.choice([6, 12, 24]),
            "gl_coverage": f"{gl_coverage:,}",
            "pl_coverage": f"{pl_coverage:,}",
        }

    # ============================================================
    # GENERIC GENERATOR
    # ============================================================

    def generate_contract_variables(self, contract_type: str) -> Dict[str, any]:
        """Generate variables for any contract type.

        Args:
            contract_type: Contract type (saas, employment, nda, consulting, service)

        Returns:
            Dictionary of variables for template substitution

        Raises:
            ValueError: If contract type is invalid
        """
        generators = {
            "saas": self.generate_saas_variables,
            "employment": self.generate_employment_variables,
            "nda": self.generate_nda_variables,
            "consulting": self.generate_consulting_variables,
            "service": self.generate_service_variables,
        }

        generator = generators.get(contract_type)
        if not generator:
            raise ValueError(f"Unknown contract type: {contract_type}")

        return generator()


# Example usage
if __name__ == "__main__":
    generator = LegalDataGenerator(seed=42)

    print("=== SaaS Agreement Variables ===")
    saas_vars = generator.generate_saas_variables()
    for key, value in saas_vars.items():
        print(f"{key}: {value}")

    print("\n=== Employment Agreement Variables ===")
    emp_vars = generator.generate_employment_variables()
    for key, value in emp_vars.items():
        print(f"{key}: {value}")

    print("\n=== NDA Variables ===")
    nda_vars = generator.generate_nda_variables()
    for key, value in emp_vars.items():
        print(f"{key}: {value}")
