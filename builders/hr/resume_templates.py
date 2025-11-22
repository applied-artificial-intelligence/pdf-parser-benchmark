"""DOCX resume template generation.

This module creates three professional resume templates:
1. Chronological Resume - Traditional format with work history first
2. Functional Resume - Skills-based with de-emphasized work history
3. Hybrid Resume - Combination of chronological and functional
"""

from pathlib import Path
from datetime import datetime
from typing import List

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from builders.hr.data_generators import (
    CandidateInfo,
    Education,
    WorkExperience,
    Skill,
    Certification,
)


class ChronologicalResumeTemplate:
    """Traditional chronological resume template.

    Format:
    - Header (name, contact)
    - Professional Summary
    - Work Experience (reverse chronological)
    - Education
    - Skills
    - Certifications (if any)
    """

    def __init__(self):
        self.doc = Document()
        # Set narrow margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

    def create_resume(
        self,
        candidate: CandidateInfo,
        professional_summary: str,
        work_experience: List[WorkExperience],
        education: List[Education],
        skills: List[Skill],
        certifications: List[Certification] = None,
    ) -> Document:
        """Generate chronological resume."""

        # Header - Name
        name_para = self.doc.add_paragraph()
        name_run = name_para.add_run(candidate.name)
        name_run.font.size = Pt(20)
        name_run.font.bold = True
        name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Contact Information
        contact_para = self.doc.add_paragraph()
        contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_text = f"{candidate.city}, {candidate.state_province}  •  {candidate.phone}  •  {candidate.email}"
        if candidate.linkedin:
            contact_text += f"  •  {candidate.linkedin}"
        contact_para.add_run(contact_text).font.size = Pt(10)

        self.doc.add_paragraph()  # Spacing

        # Professional Summary
        self._add_section_header("PROFESSIONAL SUMMARY")
        summary_para = self.doc.add_paragraph(professional_summary)
        summary_para.paragraph_format.space_after = Pt(12)

        # Work Experience
        self._add_section_header("WORK EXPERIENCE")
        for exp in work_experience:
            # Company and Title
            exp_para = self.doc.add_paragraph()
            title_run = exp_para.add_run(exp.title)
            title_run.font.bold = True
            title_run.font.size = Pt(11)

            exp_para.add_run(f" — {exp.company}")

            # Location and Dates
            dates_para = self.doc.add_paragraph()
            dates_para.add_run(f"{exp.city}, {exp.state}").font.italic = True
            dates_para.add_run(f"  •  {exp.start_date} – {exp.end_date}").font.italic = True
            dates_para.paragraph_format.space_after = Pt(6)

            # Responsibilities and achievements
            for responsibility in exp.responsibilities:
                bullet_para = self.doc.add_paragraph(responsibility, style='List Bullet')
                bullet_para.paragraph_format.left_indent = Inches(0.25)
                bullet_para.paragraph_format.space_after = Pt(2)

            for achievement in exp.achievements:
                bullet_para = self.doc.add_paragraph(achievement, style='List Bullet')
                bullet_para.paragraph_format.left_indent = Inches(0.25)
                bullet_para.paragraph_format.space_after = Pt(2)

            self.doc.add_paragraph()  # Spacing between jobs

        # Education
        self._add_section_header("EDUCATION")
        for edu in education:
            edu_para = self.doc.add_paragraph()
            degree_run = edu_para.add_run(f"{edu.degree}, {edu.major}")
            degree_run.font.bold = True
            degree_run.font.size = Pt(11)

            edu_para_2 = self.doc.add_paragraph()
            edu_para_2.add_run(f"{edu.institution}, {edu.city}, {edu.state}")

            if edu.gpa:
                edu_para_2.add_run(f"  •  GPA: {edu.gpa}").font.italic = True

            edu_para_2.add_run(f"  •  Graduated: {edu.graduation_year}").font.italic = True
            edu_para_2.paragraph_format.space_after = Pt(6)

        # Skills
        self._add_section_header("SKILLS")
        skills_para = self.doc.add_paragraph()
        skill_names = [skill.name for skill in skills]
        skills_para.add_run(", ".join(skill_names))
        skills_para.paragraph_format.space_after = Pt(12)

        # Certifications (if any)
        if certifications:
            self._add_section_header("CERTIFICATIONS")
            for cert in certifications:
                cert_para = self.doc.add_paragraph()
                cert_run = cert_para.add_run(cert.name)
                cert_run.font.bold = True
                cert_para.add_run(f" — {cert.issuer}, {cert.year}")
                cert_para.paragraph_format.space_after = Pt(4)

        return self.doc

    def _add_section_header(self, text: str):
        """Add a section header with consistent styling."""
        header_para = self.doc.add_paragraph()
        header_run = header_para.add_run(text)
        header_run.font.size = Pt(12)
        header_run.font.bold = True
        header_run.font.color.rgb = RGBColor(0, 51, 102)  # Dark blue

        # Add bottom border
        pPr = header_para._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '003366')
        pBdr.append(bottom)
        pPr.append(pBdr)

        header_para.paragraph_format.space_before = Pt(12)
        header_para.paragraph_format.space_after = Pt(6)


class FunctionalResumeTemplate:
    """Skills-based functional resume template.

    Format:
    - Header (name, contact)
    - Professional Summary
    - Core Competencies / Skills (prominently featured)
    - Professional Experience (brief, de-emphasized)
    - Education
    - Certifications (if any)
    """

    def __init__(self):
        self.doc = Document()
        # Set narrow margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

    def create_resume(
        self,
        candidate: CandidateInfo,
        professional_summary: str,
        work_experience: List[WorkExperience],
        education: List[Education],
        skills: List[Skill],
        certifications: List[Certification] = None,
    ) -> Document:
        """Generate functional resume."""

        # Header - Name (centered, prominent)
        name_para = self.doc.add_paragraph()
        name_run = name_para.add_run(candidate.name)
        name_run.font.size = Pt(22)
        name_run.font.bold = True
        name_run.font.color.rgb = RGBColor(0, 51, 102)
        name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Contact Information
        contact_para = self.doc.add_paragraph()
        contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_line1 = f"{candidate.phone}  •  {candidate.email}"
        contact_para.add_run(contact_line1).font.size = Pt(10)

        contact_para2 = self.doc.add_paragraph()
        contact_para2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_line2 = f"{candidate.city}, {candidate.state_province}"
        if candidate.linkedin:
            contact_line2 += f"  •  {candidate.linkedin}"
        contact_para2.add_run(contact_line2).font.size = Pt(10)

        self.doc.add_paragraph()  # Spacing

        # Professional Summary
        self._add_section_header("PROFESSIONAL SUMMARY")
        summary_para = self.doc.add_paragraph(professional_summary)
        summary_para.paragraph_format.space_after = Pt(12)

        # Core Competencies (Skills prominently featured)
        self._add_section_header("CORE COMPETENCIES")

        # Group skills into categories or columns
        skills_per_row = 3
        skill_names = [skill.name for skill in skills]

        # Create table for multi-column skills layout
        num_rows = (len(skill_names) + skills_per_row - 1) // skills_per_row
        skills_table = self.doc.add_table(rows=num_rows, cols=skills_per_row)

        for i, skill_name in enumerate(skill_names):
            row_idx = i // skills_per_row
            col_idx = i % skills_per_row
            cell = skills_table.rows[row_idx].cells[col_idx]
            cell_para = cell.paragraphs[0]
            cell_para.add_run(f"• {skill_name}").font.size = Pt(10)

        self.doc.add_paragraph()  # Spacing

        # Professional Achievements (extracted from work experience)
        self._add_section_header("KEY ACHIEVEMENTS")

        # Collect all achievements from work experience
        all_achievements = []
        for exp in work_experience:
            all_achievements.extend(exp.achievements)

        # Show top 6-8 achievements
        for achievement in all_achievements[:8]:
            bullet_para = self.doc.add_paragraph(achievement, style='List Bullet')
            bullet_para.paragraph_format.left_indent = Inches(0.25)
            bullet_para.paragraph_format.space_after = Pt(4)

        self.doc.add_paragraph()  # Spacing

        # Professional Experience (abbreviated - just company, title, dates)
        self._add_section_header("PROFESSIONAL EXPERIENCE")
        for exp in work_experience:
            exp_para = self.doc.add_paragraph()
            title_run = exp_para.add_run(f"{exp.title}, {exp.company}")
            title_run.font.bold = True
            title_run.font.size = Pt(10)
            exp_para.add_run(f"  •  {exp.start_date} – {exp.end_date}").font.italic = True
            exp_para.paragraph_format.space_after = Pt(4)

        # Education
        self._add_section_header("EDUCATION")
        for edu in education:
            edu_para = self.doc.add_paragraph()
            degree_run = edu_para.add_run(f"{edu.degree}, {edu.major}")
            degree_run.font.bold = True
            degree_run.font.size = Pt(11)

            edu_para_2 = self.doc.add_paragraph()
            edu_para_2.add_run(f"{edu.institution}")
            if edu.gpa:
                edu_para_2.add_run(f"  •  GPA: {edu.gpa}").font.italic = True
            edu_para_2.add_run(f"  •  {edu.graduation_year}").font.italic = True
            edu_para_2.paragraph_format.space_after = Pt(6)

        # Certifications (if any)
        if certifications:
            self._add_section_header("CERTIFICATIONS")
            for cert in certifications:
                cert_para = self.doc.add_paragraph()
                cert_run = cert_para.add_run(cert.name)
                cert_run.font.bold = True
                cert_para.add_run(f" — {cert.issuer}, {cert.year}")
                cert_para.paragraph_format.space_after = Pt(4)

        return self.doc

    def _add_section_header(self, text: str):
        """Add a section header with consistent styling."""
        header_para = self.doc.add_paragraph()
        header_run = header_para.add_run(text)
        header_run.font.size = Pt(12)
        header_run.font.bold = True
        header_run.font.color.rgb = RGBColor(51, 51, 51)  # Dark gray
        header_run.font.all_caps = True

        header_para.paragraph_format.space_before = Pt(12)
        header_para.paragraph_format.space_after = Pt(6)


class HybridResumeTemplate:
    """Hybrid resume combining chronological and functional elements.

    Format:
    - Header (name, contact)
    - Professional Summary
    - Skills & Competencies (featured but not dominant)
    - Work Experience (detailed, chronological)
    - Education
    - Certifications (if any)
    """

    def __init__(self):
        self.doc = Document()
        # Set narrow margins
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

    def create_resume(
        self,
        candidate: CandidateInfo,
        professional_summary: str,
        work_experience: List[WorkExperience],
        education: List[Education],
        skills: List[Skill],
        certifications: List[Certification] = None,
    ) -> Document:
        """Generate hybrid resume."""

        # Header - Name
        name_para = self.doc.add_paragraph()
        name_run = name_para.add_run(candidate.name)
        name_run.font.size = Pt(18)
        name_run.font.bold = True
        name_para.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Contact Information (two-column layout)
        contact_para = self.doc.add_paragraph()
        contact_para.add_run(f"{candidate.phone}  •  {candidate.email}").font.size = Pt(9)

        contact_para2 = self.doc.add_paragraph()
        contact_text = f"{candidate.city}, {candidate.state_province}"
        if candidate.linkedin:
            contact_text += f"  •  {candidate.linkedin}"
        contact_para2.add_run(contact_text).font.size = Pt(9)

        # Horizontal line separator
        self._add_horizontal_line()

        # Professional Summary
        self._add_section_header("PROFESSIONAL SUMMARY")
        summary_para = self.doc.add_paragraph(professional_summary)
        summary_para.paragraph_format.space_after = Pt(12)

        # Technical Skills / Core Competencies
        self._add_section_header("TECHNICAL SKILLS")

        # Categorize skills if possible, or list in compact format
        skill_names = [skill.name for skill in skills]

        # Group in rows of skills
        chunk_size = 6
        for i in range(0, len(skill_names), chunk_size):
            chunk = skill_names[i:i + chunk_size]
            skills_para = self.doc.add_paragraph()
            skills_para.add_run("• ").font.bold = True
            skills_para.add_run(", ".join(chunk))
            skills_para.paragraph_format.left_indent = Inches(0.15)
            skills_para.paragraph_format.space_after = Pt(4)

        self.doc.add_paragraph()  # Spacing

        # Work Experience (detailed)
        self._add_section_header("PROFESSIONAL EXPERIENCE")
        for exp in work_experience:
            # Company and dates on first line
            exp_header_para = self.doc.add_paragraph()
            company_run = exp_header_para.add_run(exp.company)
            company_run.font.bold = True
            company_run.font.size = Pt(11)
            exp_header_para.add_run(f"  •  {exp.city}, {exp.state}")

            # Title and dates on second line
            title_para = self.doc.add_paragraph()
            title_run = title_para.add_run(exp.title)
            title_run.font.italic = True
            title_para.add_run(f"  •  {exp.start_date} – {exp.end_date}").font.italic = True
            title_para.paragraph_format.space_after = Pt(4)

            # Responsibilities
            for responsibility in exp.responsibilities[:3]:  # Limit to 3 for hybrid
                bullet_para = self.doc.add_paragraph(responsibility, style='List Bullet')
                bullet_para.paragraph_format.left_indent = Inches(0.25)
                bullet_para.paragraph_format.space_after = Pt(2)

            # Achievements (highlighted)
            if exp.achievements:
                achievements_para = self.doc.add_paragraph()
                achievements_run = achievements_para.add_run("Key Achievements:")
                achievements_run.font.bold = True
                achievements_run.font.size = Pt(9)
                achievements_para.paragraph_format.left_indent = Inches(0.25)
                achievements_para.paragraph_format.space_after = Pt(2)

                for achievement in exp.achievements:
                    bullet_para = self.doc.add_paragraph(achievement, style='List Bullet')
                    bullet_para.paragraph_format.left_indent = Inches(0.5)
                    bullet_para.paragraph_format.space_after = Pt(2)

            self.doc.add_paragraph()  # Spacing between jobs

        # Education
        self._add_section_header("EDUCATION")
        for edu in education:
            edu_para = self.doc.add_paragraph()
            degree_run = edu_para.add_run(f"{edu.degree}, {edu.major}")
            degree_run.font.bold = True
            degree_run.font.size = Pt(11)

            edu_para_2 = self.doc.add_paragraph()
            edu_para_2.add_run(f"{edu.institution}, {edu.city}, {edu.state}")

            if edu.gpa:
                edu_para_2.add_run(f"  •  GPA: {edu.gpa}").font.italic = True

            edu_para_2.add_run(f"  •  {edu.graduation_year}").font.italic = True
            edu_para_2.paragraph_format.space_after = Pt(6)

        # Certifications (if any)
        if certifications:
            self._add_section_header("CERTIFICATIONS")
            for cert in certifications:
                cert_para = self.doc.add_paragraph()
                cert_run = cert_para.add_run(cert.name)
                cert_run.font.bold = True
                cert_para.add_run(f" — {cert.issuer}, {cert.year}")
                cert_para.paragraph_format.space_after = Pt(4)

        return self.doc

    def _add_section_header(self, text: str):
        """Add a section header with consistent styling."""
        header_para = self.doc.add_paragraph()
        header_run = header_para.add_run(text)
        header_run.font.size = Pt(11)
        header_run.font.bold = True
        header_run.font.color.rgb = RGBColor(0, 0, 0)
        header_run.font.all_caps = True

        header_para.paragraph_format.space_before = Pt(10)
        header_para.paragraph_format.space_after = Pt(4)

    def _add_horizontal_line(self):
        """Add a horizontal line separator."""
        line_para = self.doc.add_paragraph()
        pPr = line_para._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '12')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '000000')
        pBdr.append(bottom)
        pPr.append(pBdr)
        line_para.paragraph_format.space_after = Pt(12)
