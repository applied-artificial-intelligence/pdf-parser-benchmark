"""Legal clause library with authentic legal language and variable substitution.

This module provides 50+ standard legal clauses organized by section type,
with support for:
- Variable substitution (parties, dates, amounts, jurisdictions)
- Clause variants (strict, standard, permissive)
- Defined terms tracking and auto-capitalization
- Multiple contract types (SaaS, Employment, NDA, Consulting, Service)
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum


class ClauseVariant(Enum):
    """Clause strictness variants."""
    STRICT = "strict"  # More protective/restrictive language
    STANDARD = "standard"  # Balanced language
    PERMISSIVE = "permissive"  # More flexible/lenient language


@dataclass
class LegalClause:
    """A legal clause with metadata."""
    section: str
    text: str
    defined_terms: List[str] = field(default_factory=list)
    variant: ClauseVariant = ClauseVariant.STANDARD
    contract_types: List[str] = field(default_factory=list)  # Empty = all types


class DefinedTermsTracker:
    """Tracks defined terms and ensures consistent capitalization.

    Legal contracts define key terms (e.g., "Service", "Platform") that must
    be consistently capitalized throughout the document after first use.
    """

    def __init__(self):
        self.terms: Set[str] = set()
        self.first_use: Dict[str, str] = {}  # term -> full definition

    def add_term(self, term: str, definition: Optional[str] = None):
        """Add a defined term to track.

        Args:
            term: The term to track (e.g., "Service")
            definition: Optional full definition text
        """
        self.terms.add(term)
        if definition:
            self.first_use[term] = definition

    def add_terms(self, terms: List[str]):
        """Add multiple defined terms."""
        for term in terms:
            self.add_term(term)

    def capitalize_in_text(self, text: str) -> str:
        """Capitalize defined terms in text.

        Args:
            text: Text to process

        Returns:
            Text with defined terms properly capitalized
        """
        result = text
        for term in sorted(self.terms, key=lambda x: len(x), reverse=True):
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term.lower()) + r'\b'
            result = re.sub(pattern, term, result, flags=re.IGNORECASE)
        return result

    def get_definitions_section(self) -> str:
        """Generate a Definitions section from tracked terms.

        Returns:
            Formatted definitions section text
        """
        if not self.first_use:
            return ""

        lines = ["The following terms shall have the meanings set forth below:\n"]
        for term in sorted(self.first_use.keys()):
            definition = self.first_use[term]
            lines.append(f'"{term}" means {definition}.')

        return "\n".join(lines)


class ClauseLibrary:
    """Library of standard legal clauses with variable substitution."""

    def __init__(self):
        self.clauses: List[LegalClause] = []
        self._initialize_clauses()

    def _initialize_clauses(self):
        """Initialize the clause library with 50+ standard clauses."""

        # ============================================================
        # GENERAL PROVISIONS (used across all contract types)
        # ============================================================

        # Governing Law variants
        self.clauses.append(LegalClause(
            section="Governing Law",
            text="This Agreement shall be governed by and construed in accordance with the laws of the State of {jurisdiction}, without regard to its conflict of law principles.",
            variant=ClauseVariant.STANDARD,
        ))

        self.clauses.append(LegalClause(
            section="Governing Law",
            text="This Agreement and any disputes arising out of or related to this Agreement shall be governed exclusively by the internal laws of the State of {jurisdiction}, without regard to its conflicts of law rules. The parties expressly exclude the application of the United Nations Convention on Contracts for the International Sale of Goods.",
            variant=ClauseVariant.STRICT,
        ))

        # Entire Agreement
        self.clauses.append(LegalClause(
            section="Entire Agreement",
            text="This Agreement constitutes the entire agreement between the parties concerning the subject matter hereof and supersedes all prior or contemporaneous agreements, understandings, negotiations, and discussions, whether oral or written, between the parties.",
        ))

        # Amendments
        self.clauses.append(LegalClause(
            section="Amendments",
            text="No amendment, modification, or waiver of any provision of this Agreement shall be effective unless in writing and signed by both parties.",
            variant=ClauseVariant.STANDARD,
        ))

        self.clauses.append(LegalClause(
            section="Amendments",
            text="This Agreement may be amended only by a written instrument signed by authorized representatives of both parties.",
            variant=ClauseVariant.STRICT,
        ))

        # Severability
        self.clauses.append(LegalClause(
            section="Severability",
            text="If any provision of this Agreement is held to be invalid, illegal, or unenforceable, the remaining provisions shall continue in full force and effect. The parties shall negotiate in good faith to replace any invalid provision with a valid provision that most closely approximates the intent and economic effect of the invalid provision.",
        ))

        # Notices
        self.clauses.append(LegalClause(
            section="Notices",
            text="All notices, requests, demands, and other communications under this Agreement shall be in writing and shall be deemed to have been duly given: (a) on the date of delivery if delivered personally; (b) on the first business day following the date of dispatch if delivered by a nationally recognized next-day courier service; or (c) on the third business day following the date of mailing if delivered by registered or certified mail, return receipt requested, postage prepaid.",
        ))

        # Force Majeure
        self.clauses.append(LegalClause(
            section="Force Majeure",
            text="Neither party shall be liable for any failure or delay in performance under this Agreement (except for payment obligations) to the extent such failure or delay is caused by circumstances beyond its reasonable control, including acts of God, natural disasters, war, terrorism, riots, labor disputes, governmental actions, or failures of the Internet or telecommunications infrastructure, provided that the affected party gives prompt written notice to the other party and uses reasonable efforts to resume performance.",
            defined_terms=["Force Majeure"],
        ))

        # Dispute Resolution - Litigation
        self.clauses.append(LegalClause(
            section="Dispute Resolution",
            text="Any dispute arising out of or relating to this Agreement shall be resolved exclusively in the state or federal courts located in {jurisdiction}, and each party hereby consents to the exclusive jurisdiction and venue of such courts.",
            variant=ClauseVariant.STANDARD,
        ))

        # Dispute Resolution - Arbitration
        self.clauses.append(LegalClause(
            section="Dispute Resolution",
            text="Any dispute, controversy, or claim arising out of or relating to this Agreement, or the breach, termination, or invalidity thereof, shall be finally settled by binding arbitration administered by the American Arbitration Association in accordance with its Commercial Arbitration Rules. The arbitration shall be conducted in {jurisdiction}, and judgment on the award rendered by the arbitrator(s) may be entered in any court having jurisdiction thereof. Each party shall bear its own costs and attorneys' fees, and the parties shall equally share the arbitrator's fees and administrative costs.",
            variant=ClauseVariant.PERMISSIVE,
        ))

        # Assignment
        self.clauses.append(LegalClause(
            section="Assignment",
            text="Neither party may assign this Agreement without the prior written consent of the other party, except that either party may assign this Agreement without consent to a successor in connection with a merger, acquisition, or sale of all or substantially all of its assets. Any attempted assignment in violation of this section shall be void.",
        ))

        # Waiver
        self.clauses.append(LegalClause(
            section="Waiver",
            text="No waiver of any provision of this Agreement shall be deemed or shall constitute a waiver of any other provision, nor shall any waiver constitute a continuing waiver unless otherwise expressly provided in writing.",
        ))

        # Counterparts
        self.clauses.append(LegalClause(
            section="Counterparts",
            text="This Agreement may be executed in one or more counterparts, each of which shall be deemed an original and all of which together shall constitute one and the same instrument. Execution by electronic signature or facsimile shall have the same force and effect as execution by original signature.",
        ))

        # ============================================================
        # SAAS AGREEMENT CLAUSES
        # ============================================================

        self.clauses.append(LegalClause(
            section="Service Description",
            text="{provider} shall provide {customer} with access to the {platform_name} platform (the \"Service\"), a cloud-based software solution designed to {service_purpose}. The Service shall be made available via the Internet in accordance with the service level agreement set forth in this Agreement.",
            defined_terms=["Service", "Platform"],
            contract_types=["saas"],
        ))

        self.clauses.append(LegalClause(
            section="Service Level Agreement",
            text="{provider} shall use commercially reasonable efforts to make the Service available {uptime_pct}% of the time, measured monthly, excluding scheduled maintenance and downtime caused by factors beyond {provider}'s reasonable control. Scheduled maintenance shall be performed during off-peak hours with at least {notice_hours} hours' advance notice to {customer}.",
            defined_terms=["Service Level Agreement", "SLA", "Uptime"],
            contract_types=["saas"],
        ))

        self.clauses.append(LegalClause(
            section="Support Services",
            text="{provider} shall provide {customer} with technical support services via email during normal business hours ({business_hours}). Response times shall be: (a) {critical_response_hrs} hours for critical issues affecting core functionality; (b) {high_response_hrs} hours for high-priority issues; and (c) {normal_response_hrs} hours for normal priority requests.",
            defined_terms=["Support Services"],
            contract_types=["saas"],
        ))

        self.clauses.append(LegalClause(
            section="Subscription Plans",
            text="{customer} shall subscribe to the {plan_tier} plan at a monthly subscription fee of ${monthly_fee}. The subscription includes {max_users} user accounts and {storage_gb} GB of data storage. Additional users may be added at ${per_user_fee} per user per month.",
            defined_terms=["Subscription", "Subscriber"],
            contract_types=["saas"],
        ))

        self.clauses.append(LegalClause(
            section="Payment Terms",
            text="All fees are due and payable in advance on a monthly basis. {provider} shall invoice {customer} on or about the first day of each month, and payment shall be due within {payment_days} days of the invoice date. Late payments shall accrue interest at the rate of {interest_rate}% per month or the maximum rate permitted by law, whichever is less.",
            contract_types=["saas"],
        ))

        self.clauses.append(LegalClause(
            section="Data Ownership",
            text="{customer} retains all right, title, and interest in and to all data, content, and materials provided by {customer} or its users to the Service (\"Customer Data\"). {provider} shall not access, use, or disclose Customer Data except as necessary to provide the Service or as required by law.",
            defined_terms=["Customer Data"],
            contract_types=["saas"],
        ))

        self.clauses.append(LegalClause(
            section="Data Security",
            text="{provider} shall implement and maintain administrative, physical, and technical safeguards designed to protect Customer Data against unauthorized access, use, or disclosure. Such safeguards shall include, at a minimum: (a) data encryption in transit and at rest; (b) regular security assessments and penetration testing; (c) employee background checks and security training; and (d) incident response procedures.",
            contract_types=["saas"],
        ))

        self.clauses.append(LegalClause(
            section="Privacy Compliance",
            text="{provider} shall comply with all applicable privacy and data protection laws and regulations, including but not limited to the California Consumer Privacy Act (CCPA) and, to the extent applicable, the General Data Protection Regulation (GDPR). {provider} shall maintain a written privacy policy describing its data practices.",
            contract_types=["saas"],
        ))

        # ============================================================
        # EMPLOYMENT AGREEMENT CLAUSES
        # ============================================================

        self.clauses.append(LegalClause(
            section="Position and Duties",
            text="{company} hereby employs {employee} in the position of {position_title}. {employee} shall perform such duties and responsibilities as are customarily associated with such position and such other duties as may be assigned by {company} from time to time. {employee} shall report to {reports_to}.",
            defined_terms=["Employee", "Company", "Position"],
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="Base Salary",
            text="{company} shall pay {employee} an annual base salary of ${annual_salary}, payable in accordance with {company}'s standard payroll practices, currently semi-monthly. This salary shall be subject to applicable withholdings and deductions.",
            defined_terms=["Base Salary"],
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="Bonus and Incentives",
            text="{employee} shall be eligible to participate in {company}'s annual bonus program, with a target bonus of {bonus_pct}% of Base Salary based on achievement of performance objectives to be mutually agreed upon. Any bonus payment shall be subject to {employee}'s continued employment through the payment date and shall be paid in the discretion of {company}.",
            defined_terms=["Bonus"],
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="Benefits",
            text="{employee} shall be eligible to participate in {company}'s employee benefit plans, including health insurance, retirement plans, and paid time off, in accordance with the terms of such plans as may be in effect from time to time.",
            defined_terms=["Benefits"],
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="At-Will Employment",
            text="Employee's employment with Company is at-will, meaning that either Employee or Company may terminate the employment relationship at any time, with or without cause and with or without notice. No provision of this Agreement shall be construed to create an employment contract for any specific term.",
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="Termination by Company",
            text="{company} may terminate {employee}'s employment at any time for Cause or without Cause. \"Cause\" means: (a) {employee}'s conviction of, or plea of guilty or nolo contendere to, any felony or crime involving moral turpitude; (b) {employee}'s gross negligence or willful misconduct in the performance of duties; (c) {employee}'s material breach of this Agreement; or (d) {employee}'s violation of {company}'s written policies after notice and opportunity to cure.",
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="Severance",
            text="If {company} terminates {employee}'s employment without Cause, {company} shall pay {employee} severance equal to {severance_weeks} weeks of Base Salary, payable in accordance with {company}'s standard payroll practices, provided that {employee} executes and does not revoke a general release of claims in a form satisfactory to {company}.",
            defined_terms=["Severance"],
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="Confidentiality",
            text="{employee} acknowledges that during employment, {employee} will have access to Confidential Information of {company}. \"Confidential Information\" means all non-public information relating to {company}'s business, including trade secrets, customer lists, financial information, business plans, product specifications, and marketing strategies. {employee} agrees to hold all Confidential Information in strict confidence and not to disclose or use such information except as necessary to perform duties for {company}.",
            defined_terms=["Confidential Information"],
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="Intellectual Property Assignment",
            text="{employee} hereby assigns to {company} all right, title, and interest in and to any inventions, discoveries, works of authorship, and other intellectual property created by {employee}, alone or with others, during the term of employment that: (a) relate to {company}'s actual or anticipated business; (b) result from work performed for {company}; or (c) are created using {company}'s equipment, supplies, facilities, or Confidential Information (collectively, \"Work Product\"). {employee} agrees to execute any documents necessary to perfect {company}'s rights in Work Product.",
            defined_terms=["Intellectual Property", "Work Product"],
            contract_types=["employment"],
        ))

        self.clauses.append(LegalClause(
            section="Non-Compete",
            text="During employment and for a period of {noncompete_months} months following termination for any reason, {employee} shall not, directly or indirectly, engage in any business that competes with {company}'s business within a {noncompete_radius} mile radius of {company}'s principal place of business. \"Compete\" means providing services or products that are the same as or substantially similar to those provided by {company}.",
            contract_types=["employment"],
            variant=ClauseVariant.STRICT,
        ))

        self.clauses.append(LegalClause(
            section="Non-Solicitation",
            text="During employment and for {nonsolicitation_months} months following termination, {employee} shall not: (a) solicit or encourage any employee of {company} to leave employment with {company}; or (b) solicit business from any customer or client of {company} with whom {employee} had material contact during the last {lookback_months} months of employment for purposes of providing products or services that compete with {company}'s business.",
            contract_types=["employment"],
        ))

        # ============================================================
        # NON-DISCLOSURE AGREEMENT CLAUSES
        # ============================================================

        self.clauses.append(LegalClause(
            section="Definition of Confidential Information",
            text="\"Confidential Information\" means any and all information disclosed by {disclosing_party} (the \"Disclosing Party\") to {receiving_party} (the \"Receiving Party\"), whether orally, in writing, or in any other form, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure. Confidential Information includes, without limitation, business plans, financial information, customer lists, technical data, trade secrets, know-how, research, product plans, products, services, suppliers, customer information, and software.",
            defined_terms=["Confidential Information", "Disclosing Party", "Receiving Party"],
            contract_types=["nda"],
        ))

        self.clauses.append(LegalClause(
            section="Exclusions from Confidential Information",
            text="Confidential Information does not include information that: (a) is or becomes publicly available through no breach of this Agreement by Receiving Party; (b) was rightfully in Receiving Party's possession prior to disclosure by Disclosing Party; (c) is rightfully received by Receiving Party from a third party without breach of any confidentiality obligation; or (d) is independently developed by Receiving Party without use of or reference to Disclosing Party's Confidential Information.",
            contract_types=["nda"],
        ))

        self.clauses.append(LegalClause(
            section="Non-Disclosure",
            text="Receiving Party shall: (a) hold Confidential Information in strict confidence; (b) not disclose Confidential Information to any third party; and (c) not use Confidential Information for any purpose other than {purpose} (the \"Purpose\").",
            defined_terms=["Purpose"],
            contract_types=["nda"],
        ))

        self.clauses.append(LegalClause(
            section="Protection Measures",
            text="Receiving Party shall protect Confidential Information using the same degree of care it uses to protect its own confidential information of a similar nature, but in no event less than reasonable care. Receiving Party shall limit access to Confidential Information to those of its employees, contractors, and advisors who need access for the Purpose and who have been informed of the confidential nature of such information.",
            contract_types=["nda"],
        ))

        self.clauses.append(LegalClause(
            section="Permitted Disclosures",
            text="Receiving Party may disclose Confidential Information to the extent required by law or court order, provided that Receiving Party provides Disclosing Party with prompt written notice of such requirement (to the extent legally permitted) and cooperates with Disclosing Party's efforts to seek a protective order or other appropriate protection.",
            contract_types=["nda"],
        ))

        self.clauses.append(LegalClause(
            section="Return of Materials",
            text="Upon Disclosing Party's request or upon termination of this Agreement, Receiving Party shall promptly: (a) return to Disclosing Party all documents, materials, and other tangible items containing or representing Confidential Information; and (b) permanently delete or destroy all electronic copies of Confidential Information in Receiving Party's possession or control. Upon request, Receiving Party shall certify in writing its compliance with this section.",
            contract_types=["nda"],
        ))

        self.clauses.append(LegalClause(
            section="Remedies",
            text="Receiving Party acknowledges that disclosure of Confidential Information would cause irreparable harm to Disclosing Party for which monetary damages would be an inadequate remedy. Accordingly, Disclosing Party shall be entitled to seek equitable relief, including injunction and specific performance, in addition to all other remedies available at law or in equity.",
            contract_types=["nda"],
        ))

        # ============================================================
        # CONSULTING AGREEMENT CLAUSES
        # ============================================================

        self.clauses.append(LegalClause(
            section="Scope of Services",
            text="{consultant} agrees to provide {client} with consulting services as described in one or more Statements of Work to be mutually agreed upon by the parties (the \"Services\"). Each Statement of Work shall specify the scope, deliverables, timeline, and fees for the Services to be performed.",
            defined_terms=["Consultant", "Client", "Services", "Statement of Work"],
            contract_types=["consulting"],
        ))

        self.clauses.append(LegalClause(
            section="Deliverables",
            text="{consultant} shall deliver to {client} the work product and deliverables described in the applicable Statement of Work (\"Deliverables\"). All Deliverables shall be delivered in the format and by the deadlines specified in the Statement of Work. {client} shall have {review_days} business days to review and approve each Deliverable.",
            defined_terms=["Deliverables"],
            contract_types=["consulting"],
        ))

        self.clauses.append(LegalClause(
            section="Fees",
            text="{client} shall pay {consultant} fees as specified in the applicable Statement of Work. Unless otherwise specified, fees shall be calculated at an hourly rate of ${hourly_rate} per hour. {consultant} shall submit monthly invoices detailing hours worked and expenses incurred, and {client} shall pay such invoices within {payment_days} days of receipt.",
            defined_terms=["Fees"],
            contract_types=["consulting"],
        ))

        self.clauses.append(LegalClause(
            section="Expenses",
            text="{consultant} shall be reimbursed for reasonable out-of-pocket expenses incurred in connection with performing the Services, provided that such expenses are pre-approved by {client} in writing and are supported by appropriate documentation. Travel expenses shall be reimbursed at coach class rates for air travel and standard rates for lodging and meals.",
            contract_types=["consulting"],
        ))

        self.clauses.append(LegalClause(
            section="Independent Contractor Relationship",
            text="{consultant} is an independent contractor and not an employee, partner, or joint venturer of {client}. {consultant} shall have sole control over the manner and means of performing the Services, subject to the specifications in the Statement of Work. {consultant} shall be responsible for all taxes, insurance, and benefits relating to {consultant}'s performance of Services. {consultant} shall not have authority to bind {client} or to make representations on behalf of {client}.",
            contract_types=["consulting"],
        ))

        self.clauses.append(LegalClause(
            section="Work Product Ownership",
            text="All Work Product created by {consultant} in connection with the Services shall be the sole and exclusive property of {client}. \"Work Product\" means all deliverables, documents, materials, inventions, discoveries, and other work product created or developed by {consultant} in performing the Services. {consultant} hereby assigns to {client} all right, title, and interest in and to the Work Product, including all intellectual property rights therein.",
            defined_terms=["Work Product"],
            contract_types=["consulting"],
        ))

        self.clauses.append(LegalClause(
            section="Pre-Existing IP",
            text="{consultant} retains all right, title, and interest in and to any intellectual property, materials, or tools that: (a) existed prior to this Agreement; (b) are developed by {consultant} independently of the Services; or (c) are not Work Product as defined in this Agreement (\"Pre-Existing IP\"). {consultant} hereby grants {client} a non-exclusive, worldwide, royalty-free license to use Pre-Existing IP solely to the extent incorporated into Work Product and solely for {client}'s internal business purposes.",
            defined_terms=["Pre-Existing IP"],
            contract_types=["consulting"],
        ))

        # ============================================================
        # SERVICE AGREEMENT CLAUSES
        # ============================================================

        self.clauses.append(LegalClause(
            section="Service Description",
            text="{service_provider} shall provide {customer} with {service_description} (the \"Services\") in accordance with the Service Standards set forth in this Agreement. The Services shall be performed at the locations specified in Exhibit A (the \"Service Locations\").",
            defined_terms=["Service Provider", "Customer", "Services", "Service Locations"],
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Service Standards",
            text="{service_provider} shall perform the Services in a professional and workmanlike manner in accordance with industry standards and best practices. {service_provider} warrants that all Services shall be performed by qualified personnel with appropriate skills, training, and experience.",
            defined_terms=["Service Standards"],
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Service Fees",
            text="{customer} shall pay {service_provider} the fees set forth in Exhibit B for the Services (the \"Service Fees\"). Service Fees are exclusive of all applicable taxes, which shall be the responsibility of {customer}.",
            defined_terms=["Service Fees"],
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Payment Schedule",
            text="Service Fees shall be invoiced {billing_frequency} and are due within {payment_days} days of the invoice date. {service_provider} may suspend Services if payment is more than {suspension_days} days overdue.",
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Term and Renewal",
            text="This Agreement shall commence on {start_date} (the \"Effective Date\") and shall continue for an initial term of {initial_term_months} months (the \"Initial Term\"). Thereafter, this Agreement shall automatically renew for successive {renewal_term_months}-month periods (each a \"Renewal Term\") unless either party provides written notice of non-renewal at least {notice_days} days prior to the end of the then-current term.",
            defined_terms=["Effective Date", "Term"],
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Change Orders",
            text="Either party may request changes to the Services by submitting a written change order request. No changes shall be effective unless agreed to in writing by both parties. Any changes that materially increase the scope of Services may result in additional fees to be mutually agreed upon.",
            defined_terms=["Change Order"],
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Service Provider Obligations",
            text="{service_provider} shall: (a) perform Services in a timely manner; (b) provide all equipment, materials, and supplies necessary to perform Services unless otherwise specified; (c) comply with all applicable laws and regulations; and (d) maintain appropriate insurance coverage as specified in this Agreement.",
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Customer Obligations",
            text="{customer} shall: (a) provide {service_provider} with reasonable access to Service Locations; (b) provide information and cooperation reasonably necessary for {service_provider} to perform Services; and (c) designate a primary contact for coordination of Services.",
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Warranties",
            text="{service_provider} warrants that: (a) it has the right and authority to enter into this Agreement; (b) the Services will be performed in a professional manner consistent with industry standards; and (c) the Services will conform to the Service Standards. EXCEPT AS EXPRESSLY SET FORTH IN THIS SECTION, SERVICE PROVIDER MAKES NO OTHER WARRANTIES, EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.",
            contract_types=["service"],
        ))

        self.clauses.append(LegalClause(
            section="Limitation of Liability",
            text="IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR RELATING TO THIS AGREEMENT, INCLUDING LOST PROFITS, LOST REVENUE, OR LOST DATA, EVEN IF SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. EXCEPT FOR LIABILITY ARISING FROM GROSS NEGLIGENCE OR WILLFUL MISCONDUCT, EACH PARTY'S TOTAL LIABILITY ARISING OUT OF OR RELATING TO THIS AGREEMENT SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE TO SERVICE PROVIDER IN THE {liability_period} MONTHS PRECEDING THE EVENT GIVING RISE TO LIABILITY.",
            contract_types=["service", "saas", "consulting"],
        ))

        self.clauses.append(LegalClause(
            section="Insurance",
            text="{service_provider} shall maintain at its own expense the following insurance coverage with insurers reasonably acceptable to {customer}: (a) commercial general liability insurance with limits of not less than ${gl_coverage} per occurrence; (b) professional liability insurance with limits of not less than ${pl_coverage} per claim; and (c) workers' compensation insurance as required by law. Upon request, {service_provider} shall provide {customer} with certificates of insurance evidencing such coverage.",
            contract_types=["service"],
        ))

    def get_clause(
        self,
        section: str,
        contract_type: Optional[str] = None,
        variant: ClauseVariant = ClauseVariant.STANDARD,
    ) -> Optional[LegalClause]:
        """Get a clause for a specific section.

        Args:
            section: Section name (e.g., "Governing Law")
            contract_type: Optional contract type filter (e.g., "saas")
            variant: Clause variant (strict, standard, permissive)

        Returns:
            Matching clause or None if not found
        """
        candidates = [
            c for c in self.clauses
            if c.section == section
            and (not contract_type or not c.contract_types or contract_type in c.contract_types)
            and c.variant == variant
        ]

        if not candidates:
            # Try to find any variant if exact match not found
            candidates = [
                c for c in self.clauses
                if c.section == section
                and (not contract_type or not c.contract_types or contract_type in c.contract_types)
            ]

        return candidates[0] if candidates else None

    def get_all_clauses_for_section(
        self,
        section: str,
        contract_type: Optional[str] = None,
    ) -> List[LegalClause]:
        """Get all clause variants for a section.

        Args:
            section: Section name
            contract_type: Optional contract type filter

        Returns:
            List of matching clauses
        """
        return [
            c for c in self.clauses
            if c.section == section
            and (not contract_type or not c.contract_types or contract_type in c.contract_types)
        ]

    def substitute_variables(self, text: str, variables: Dict[str, any]) -> str:
        """Substitute variables in clause text.

        Args:
            text: Clause text with {variable} placeholders
            variables: Dictionary of variable name -> value

        Returns:
            Text with variables substituted
        """
        result = text
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        return result

    def get_sections_by_contract_type(self, contract_type: str) -> List[str]:
        """Get all unique section names for a contract type.

        Args:
            contract_type: Contract type (e.g., "saas")

        Returns:
            Sorted list of unique section names
        """
        sections = set()
        for clause in self.clauses:
            if not clause.contract_types or contract_type in clause.contract_types:
                sections.add(clause.section)
        return sorted(sections)
