"""DOCX job application template generation.

This module creates professional job application documents including:
- Applicant information
- Position applied for
- Cover letter
- References
"""

from datetime import datetime

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

from builders.hr.data_generators import CandidateInfo, WorkExperience


class JobApplicationTemplate:
    """Standard job application template.

    Format:
    - Header with "Employment Application"
    - Applicant Information
    - Position Information
    - Cover Letter
    - Professional References
    """

    def __init__(self):
        self.doc = Document()
        # Set standard margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

    def create_application(
        self,
        candidate: CandidateInfo,
        position_title: str,
        company_name: str,
        cover_letter: str,
        work_experience: list[WorkExperience],
        application_date: datetime = None,
    ) -> Document:
        """Generate job application document.

        Args:
            candidate: Candidate personal information
            position_title: Position being applied for
            company_name: Company name
            cover_letter: Cover letter text (2-3 paragraphs)
            work_experience: Work history (for references)
            application_date: Date of application (defaults to today)

        Returns:
            Document instance
        """
        if application_date is None:
            application_date = datetime.now()

        # Header - "Employment Application"
        title_para = self.doc.add_paragraph()
        title_run = title_para.add_run("EMPLOYMENT APPLICATION")
        title_run.font.size = Pt(16)
        title_run.font.bold = True
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_para.paragraph_format.space_after = Pt(12)

        # Application Date
        date_para = self.doc.add_paragraph()
        date_para.add_run(f"Date: {application_date.strftime('%B %d, %Y')}")
        date_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        date_para.paragraph_format.space_after = Pt(20)

        # Applicant Information Section
        self._add_section_header("APPLICANT INFORMATION")

        info_table = self.doc.add_table(rows=5, cols=2)
        info_table.autofit = False

        # Name
        info_table.rows[0].cells[0].text = "Name:"
        info_table.rows[0].cells[0].paragraphs[0].runs[0].font.bold = True
        info_table.rows[0].cells[1].text = candidate.name

        # Address
        info_table.rows[1].cells[0].text = "Address:"
        info_table.rows[1].cells[0].paragraphs[0].runs[0].font.bold = True
        address_cell = info_table.rows[1].cells[1]
        address_cell.text = f"{candidate.address}, {candidate.city}, {candidate.state_province} {candidate.postal_code}"

        # Phone
        info_table.rows[2].cells[0].text = "Phone:"
        info_table.rows[2].cells[0].paragraphs[0].runs[0].font.bold = True
        info_table.rows[2].cells[1].text = candidate.phone

        # Email
        info_table.rows[3].cells[0].text = "Email:"
        info_table.rows[3].cells[0].paragraphs[0].runs[0].font.bold = True
        info_table.rows[3].cells[1].text = candidate.email

        # LinkedIn (optional)
        if candidate.linkedin:
            info_table.rows[4].cells[0].text = "LinkedIn:"
            info_table.rows[4].cells[0].paragraphs[0].runs[0].font.bold = True
            info_table.rows[4].cells[1].text = candidate.linkedin

        self.doc.add_paragraph()  # Spacing

        # Position Information
        self._add_section_header("POSITION APPLIED FOR")

        position_table = self.doc.add_table(rows=2, cols=2)
        position_table.autofit = False

        # Position Title
        position_table.rows[0].cells[0].text = "Position:"
        position_table.rows[0].cells[0].paragraphs[0].runs[0].font.bold = True
        position_table.rows[0].cells[1].text = position_title

        # Company
        position_table.rows[1].cells[0].text = "Company:"
        position_table.rows[1].cells[0].paragraphs[0].runs[0].font.bold = True
        position_table.rows[1].cells[1].text = company_name

        self.doc.add_paragraph()  # Spacing

        # Cover Letter
        self._add_section_header("COVER LETTER")

        # Split cover letter into paragraphs (if not already split)
        paragraphs = cover_letter.split("\n\n") if "\n\n" in cover_letter else [cover_letter]

        for para_text in paragraphs:
            para = self.doc.add_paragraph(para_text)
            para.paragraph_format.space_after = Pt(12)
            para.paragraph_format.first_line_indent = Inches(0.5)

        # Closing
        closing_para = self.doc.add_paragraph("Sincerely,")
        closing_para.paragraph_format.space_after = Pt(36)

        signature_para = self.doc.add_paragraph(candidate.name)
        signature_para.paragraph_format.space_after = Pt(20)

        # Professional References
        self._add_section_header("PROFESSIONAL REFERENCES")

        # Generate 3 references from work experience
        references = self._generate_references(work_experience)

        for i, ref in enumerate(references, 1):
            ref_para = self.doc.add_paragraph()
            ref_num_run = ref_para.add_run(f"Reference {i}")
            ref_num_run.font.bold = True
            ref_num_run.font.size = Pt(11)
            ref_para.paragraph_format.space_before = Pt(8)
            ref_para.paragraph_format.space_after = Pt(4)

            ref_table = self.doc.add_table(rows=4, cols=2)

            ref_table.rows[0].cells[0].text = "Name:"
            ref_table.rows[0].cells[0].paragraphs[0].runs[0].font.bold = True
            ref_table.rows[0].cells[1].text = ref["name"]

            ref_table.rows[1].cells[0].text = "Title:"
            ref_table.rows[1].cells[0].paragraphs[0].runs[0].font.bold = True
            ref_table.rows[1].cells[1].text = ref["title"]

            ref_table.rows[2].cells[0].text = "Company:"
            ref_table.rows[2].cells[0].paragraphs[0].runs[0].font.bold = True
            ref_table.rows[2].cells[1].text = ref["company"]

            ref_table.rows[3].cells[0].text = "Phone:"
            ref_table.rows[3].cells[0].paragraphs[0].runs[0].font.bold = True
            ref_table.rows[3].cells[1].text = ref["phone"]

        # Disclaimer
        self.doc.add_paragraph()
        disclaimer_para = self.doc.add_paragraph()
        disclaimer_run = disclaimer_para.add_run(
            "I certify that the information provided in this application is true and complete. "
            "I understand that false information may be grounds for not hiring me or for immediate "
            "termination of employment at any point in the future."
        )
        disclaimer_run.font.italic = True
        disclaimer_run.font.size = Pt(9)
        disclaimer_para.paragraph_format.space_before = Pt(20)

        # Signature line
        self.doc.add_paragraph()
        sig_line_para = self.doc.add_paragraph()
        sig_line_para.add_run("_" * 50)
        sig_line_para.paragraph_format.space_after = Pt(4)

        sig_label_para = self.doc.add_paragraph(
            "Signature                                                        Date"
        )
        sig_label_para.paragraph_format.left_indent = Inches(0.5)

        return self.doc

    def _add_section_header(self, text: str):
        """Add a section header with consistent styling."""
        header_para = self.doc.add_paragraph()
        header_run = header_para.add_run(text)
        header_run.font.size = Pt(12)
        header_run.font.bold = True
        header_run.font.color.rgb = RGBColor(0, 51, 102)  # Dark blue

        header_para.paragraph_format.space_before = Pt(16)
        header_para.paragraph_format.space_after = Pt(8)

    def _generate_references(self, work_experience: list[WorkExperience]) -> list[dict]:
        """Generate professional references from work experience.

        Args:
            work_experience: List of work experiences

        Returns:
            List of 3 reference dictionaries
        """
        import random

        from faker import Faker

        fake = Faker()
        references = []

        # Use past employers as references (not current if "Present")
        past_experiences = [exp for exp in work_experience if exp.end_date != "Present"]

        # If not enough past experiences, use all
        if len(past_experiences) < 3:
            reference_pool = work_experience[:3]
        else:
            reference_pool = past_experiences[:3]

        for exp in reference_pool:
            # Generate a fictitious manager/supervisor name
            ref_name = fake.name()

            # Manager title based on the employee's title
            manager_titles = [
                "Manager",
                "Senior Manager",
                "Director",
                "Vice President",
                "Team Lead",
            ]
            manager_title = random.choice(manager_titles)

            # Generate phone number
            phone = fake.phone_number()

            ref = {
                "name": ref_name,
                "title": manager_title,
                "company": exp.company,
                "phone": phone,
            }
            references.append(ref)

        # Ensure we have exactly 3 references
        while len(references) < 3:
            ref_name = fake.name()
            manager_title = random.choice(["Manager", "Director", "Supervisor"])
            company = fake.company()
            phone = fake.phone_number()

            references.append(
                {
                    "name": ref_name,
                    "title": manager_title,
                    "company": company,
                    "phone": phone,
                }
            )

        return references[:3]


def generate_cover_letter(
    candidate_name: str,
    position_title: str,
    company_name: str,
    experience_level: str,
    industry_config,
) -> str:
    """Generate a realistic cover letter.

    Args:
        candidate_name: Applicant's name
        position_title: Position being applied for
        company_name: Company name
        experience_level: One of "entry", "mid", "senior", "executive"
        industry_config: HRIndustryConfig instance

    Returns:
        Cover letter text (2-3 paragraphs)
    """
    import random

    # Opening paragraphs by experience level
    openings = {
        "entry": [
            f"I am writing to express my strong interest in the {position_title} position at {company_name}. "
            f"As a recent graduate with a passion for {industry_config.name.lower()}, I am excited about the "
            f"opportunity to contribute my skills and enthusiasm to your team.",
            f"I am pleased to submit my application for the {position_title} role at {company_name}. "
            f"With my educational background and growing experience in {industry_config.name.lower()}, "
            f"I am eager to bring fresh perspectives and dedication to your organization.",
        ],
        "mid": [
            f"I am writing to apply for the {position_title} position at {company_name}. "
            f"With several years of progressive experience in {industry_config.name.lower()}, I have developed "
            f"a strong track record of delivering results and driving continuous improvement.",
            f"I am excited to submit my application for the {position_title} role at {company_name}. "
            f"My background in {industry_config.name.lower()} has equipped me with the technical expertise "
            f"and problem-solving skills necessary to excel in this position.",
        ],
        "senior": [
            f"I am writing to express my interest in the {position_title} position at {company_name}. "
            f"Throughout my career in {industry_config.name.lower()}, I have consistently led high-performing "
            f"teams and delivered strategic initiatives that drive business value.",
            f"I am pleased to apply for the {position_title} role at {company_name}. "
            f"With extensive experience leading {industry_config.name.lower()} operations, I bring a proven "
            f"ability to scale organizations and execute complex projects successfully.",
        ],
        "executive": [
            f"I am writing to express my interest in the {position_title} position at {company_name}. "
            f"As an executive leader with deep expertise in {industry_config.name.lower()}, I have a demonstrated "
            f"track record of building world-class teams and driving transformational change.",
            f"I am excited to apply for the {position_title} role at {company_name}. "
            f"Throughout my career, I have led {industry_config.name.lower()} organizations through periods of "
            f"significant growth and innovation, consistently delivering measurable business results.",
        ],
    }

    # Middle paragraphs highlighting relevant skills
    middle_paras = {
        "entry": [
            f"During my studies and internships, I gained hands-on experience with {', '.join(industry_config.skills[:3])}. "
            f"I am particularly drawn to {company_name}'s commitment to innovation and excellence in the field. "
            f"I am confident that my technical skills, combined with my eagerness to learn, will allow me to make "
            f"meaningful contributions to your team.",
        ],
        "mid": [
            f"In my current role, I have successfully {random.choice(['led cross-functional projects', 'optimized critical systems', 'implemented new processes'])} "
            f"that resulted in significant improvements in quality and efficiency. My expertise includes {', '.join(industry_config.skills[:4])}, "
            f"and I excel at collaborating with stakeholders to deliver innovative solutions that meet business objectives.",
        ],
        "senior": [
            f"In my most recent position, I managed teams of up to {random.choice(['15', '25', '40'])} professionals "
            f"while overseeing {random.choice(['critical infrastructure', 'strategic initiatives', 'operational excellence'])}. "
            f"I have a proven track record of implementing best practices, mentoring emerging leaders, and driving "
            f"organizational change. My deep expertise in {', '.join(industry_config.skills[:5])} positions me "
            f"to make an immediate impact at {company_name}.",
        ],
        "executive": [
            f"In my current executive role, I have successfully built and scaled organizations, managed budgets "
            f"exceeding {random.choice(['$20M', '$50M', '$100M'])}, and partnered with C-suite leadership to align "
            f"technology strategy with business goals. I bring extensive experience in {', '.join(industry_config.skills[:4])}, "
            f"combined with a strategic vision for leveraging innovation to drive competitive advantage.",
        ],
    }

    # Closing paragraphs
    closings = [
        f"I would welcome the opportunity to discuss how my background and skills align with the needs of {company_name}. "
        f"Thank you for considering my application. I look forward to the possibility of contributing to your team's success.",
        f"I am enthusiastic about the opportunity to bring my expertise to {company_name} and contribute to your continued success. "
        f"Thank you for your time and consideration. I look forward to discussing this opportunity with you further.",
        f"I believe my experience and passion for {industry_config.name.lower()} make me an excellent fit for this role. "
        f"Thank you for considering my application. I would be delighted to discuss how I can contribute to {company_name}'s goals.",
    ]

    # Assemble cover letter
    opening = random.choice(openings[experience_level])
    middle = random.choice(middle_paras[experience_level])
    closing = random.choice(closings)

    cover_letter = f"{opening}\n\n{middle}\n\n{closing}"

    return cover_letter
