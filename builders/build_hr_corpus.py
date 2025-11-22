"""Generate comprehensive 100-document HR corpus for PDF-Bench.

This script generates 50 resumes + 50 job applications distributed across:
- 5 industries (Technology, Healthcare, Finance, Manufacturing, Education)
- 4 experience levels (Entry, Mid, Senior, Executive)
- 3 resume formats (Chronological, Functional, Hybrid)

Output:
- DOCX source files for ground truth extraction
- PDF files for parser testing (normalized for parser compatibility)
- Markdown ground truth
- YAML metadata
"""

import argparse
import json
import logging
import random
import subprocess
from datetime import datetime
from pathlib import Path

import yaml
from docx import Document

from builders.hr.data_generators import ResumeDataGenerator
from builders.hr.industry_config import INDUSTRIES
from builders.hr.job_app_templates import (
    JobApplicationTemplate,
    generate_cover_letter,
)
from builders.hr.resume_templates import (
    ChronologicalResumeTemplate,
    FunctionalResumeTemplate,
    HybridResumeTemplate,
)
from builders.pdf_utils import normalize_pdf

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Distribution matrix: 100 documents (50 resumes + 50 job applications)
DISTRIBUTION: dict[str, dict[str, int | list[str]]] = {
    "technology": {
        "count": 20,  # 10 resumes + 10 job apps
        "levels": ["entry", "mid", "senior", "executive"],
    },
    "healthcare": {
        "count": 20,
        "levels": ["entry", "mid", "senior", "executive"],
    },
    "finance": {
        "count": 20,
        "levels": ["entry", "mid", "senior", "executive"],
    },
    "manufacturing": {
        "count": 20,
        "levels": ["entry", "mid", "senior", "executive"],
    },
    "education": {
        "count": 20,
        "levels": ["entry", "mid", "senior", "executive"],
    },
}


# Resume formats
RESUME_FORMATS = ["chronological", "functional", "hybrid"]


def extract_ground_truth_from_docx(docx_path: Path) -> str:
    """Extract plain text ground truth from DOCX resume/application.

    Args:
        docx_path: Path to DOCX file

    Returns:
        Markdown-formatted ground truth text
    """
    doc = Document(str(docx_path))

    # Extract text from all paragraphs
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            # Detect headings by font size or bold or all caps
            is_heading = False
            if para.runs:
                first_run = para.runs[0]
                # Check for heading characteristics
                if first_run.bold:
                    if first_run.font.size and first_run.font.size.pt >= 11:
                        is_heading = True
                    elif text.isupper() and len(text) < 50:
                        is_heading = True

            if is_heading:
                paragraphs.append(f"\n## {text}\n")
            else:
                paragraphs.append(text)

    # Extract text from tables
    for table in doc.tables:
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            # Filter out empty rows
            if any(cells):
                rows.append(" | ".join(cells))

        if rows:
            paragraphs.append("\n")
            # All rows as plain text (HR docs don't need header formatting)
            for row in rows:
                paragraphs.append(row)
            paragraphs.append("")

    return "\n".join(paragraphs)


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> None:
    """Convert DOCX to PDF using LibreOffice headless.

    Args:
        docx_path: Path to input DOCX file
        pdf_path: Path for output PDF file
    """
    output_dir = pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run LibreOffice conversion
    result = subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(docx_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        logger.error(f"PDF conversion failed: {result.stderr}")
        raise RuntimeError(f"Failed to convert {docx_path} to PDF")

    # LibreOffice creates PDF with same name as DOCX
    generated_pdf = output_dir / f"{docx_path.stem}.pdf"
    if generated_pdf != pdf_path and generated_pdf.exists():
        generated_pdf.rename(pdf_path)

    # Normalize PDF for parser compatibility
    normalize_pdf(pdf_path)


def generate_resume(
    resume_id: int,
    industry_key: str,
    experience_level: str,
    resume_format: str,
    output_dirs: dict[str, Path],
    generator: ResumeDataGenerator,
    current_year: int,
) -> dict:
    """Generate a single resume with all output files.

    Args:
        resume_id: Resume identifier (1-50)
        industry_key: Industry key (e.g., "technology")
        experience_level: One of "entry", "mid", "senior", "executive"
        resume_format: One of "chronological", "functional", "hybrid"
        output_dirs: Dictionary of output directory paths
        generator: ResumeDataGenerator instance
        current_year: Current year for date calculations

    Returns:
        Metadata dictionary
    """
    doc_id = f"resume_{resume_id:03d}"
    industry_config = INDUSTRIES[industry_key]

    logger.info(f"Generating {doc_id}: {industry_key}/{experience_level}/{resume_format}")

    # Generate candidate data
    candidate = generator.generate_candidate_info()
    work_experience, graduation_year = generator.generate_work_history(
        industry_config, experience_level, current_year
    )
    education = generator.generate_education(experience_level, graduation_year)
    skills = generator.generate_skills(industry_config, experience_level)
    certifications = generator.generate_certifications(
        industry_config, experience_level, current_year
    )

    # Calculate total years of experience
    total_years = current_year - graduation_year - 22

    # Generate professional summary
    professional_summary = generator.generate_professional_summary(
        industry_config, experience_level, total_years
    )

    # Select template based on format
    template: ChronologicalResumeTemplate | FunctionalResumeTemplate | HybridResumeTemplate
    if resume_format == "chronological":
        template = ChronologicalResumeTemplate()
    elif resume_format == "functional":
        template = FunctionalResumeTemplate()
    else:  # hybrid
        template = HybridResumeTemplate()

    # Create resume document
    doc = template.create_resume(
        candidate=candidate,
        professional_summary=professional_summary,
        work_experience=work_experience,
        education=education,
        skills=skills,
        certifications=certifications if certifications else [],
    )
    if doc is None:
        raise RuntimeError(f"Failed to create resume for {doc_id}")

    # Save DOCX
    docx_path = output_dirs["docx"] / f"{doc_id}.docx"
    doc.save(str(docx_path))
    logger.debug(f"Saved DOCX: {docx_path}")

    # Convert to PDF
    pdf_path = output_dirs["pdfs"] / f"{doc_id}.pdf"
    convert_docx_to_pdf(docx_path, pdf_path)
    logger.debug(f"Saved PDF: {pdf_path}")

    # Extract ground truth
    ground_truth = extract_ground_truth_from_docx(docx_path)
    gt_path = output_dirs["ground_truth"] / f"{doc_id}.md"
    gt_path.write_text(ground_truth, encoding="utf-8")
    logger.debug(f"Saved ground truth: {gt_path}")

    # Generate metadata
    metadata = {
        "document_id": doc_id,
        "document_type": "resume",
        "industry": industry_key,
        "experience_level": experience_level,
        "resume_format": resume_format,
        "years_experience": total_years,
        "candidate_name": candidate.name,
        "num_jobs": len(work_experience),
        "num_education": len(education),
        "num_skills": len(skills),
        "num_certifications": len(certifications),
        "generated_at": datetime.now().isoformat(),
    }

    metadata_path = output_dirs["metadata"] / f"{doc_id}.yaml"
    with open(metadata_path, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
    logger.debug(f"Saved metadata: {metadata_path}")

    return metadata


def generate_job_application(
    app_id: int,
    resume_id: int,
    industry_key: str,
    experience_level: str,
    output_dirs: dict[str, Path],
    generator: ResumeDataGenerator,
    current_year: int,
) -> dict:
    """Generate a single job application with all output files.

    Args:
        app_id: Application identifier (1-50)
        resume_id: Corresponding resume ID for alignment
        industry_key: Industry key
        experience_level: Experience level
        output_dirs: Dictionary of output directory paths
        generator: ResumeDataGenerator instance
        current_year: Current year for date calculations

    Returns:
        Metadata dictionary
    """
    doc_id = f"job_app_{app_id:03d}"
    industry_config = INDUSTRIES[industry_key]

    logger.info(f"Generating {doc_id}: {industry_key}/{experience_level}")

    # Generate candidate data (aligned with resume)
    candidate = generator.generate_candidate_info()
    work_experience, graduation_year = generator.generate_work_history(
        industry_config, experience_level, current_year
    )

    # Get position title from industry config
    position_title = random.choice(industry_config.job_titles[experience_level])

    # Generate company name (employer)
    company_prefix = random.choice(industry_config.company_prefixes)
    company_suffix = random.choice(industry_config.company_suffixes)
    company_name = f"{company_prefix} {company_suffix}"

    # Generate cover letter
    cover_letter = generate_cover_letter(
        candidate.name,
        position_title,
        company_name,
        experience_level,
        industry_config,
    )

    # Create job application document
    template = JobApplicationTemplate()
    doc = template.create_application(
        candidate=candidate,
        position_title=position_title,
        company_name=company_name,
        cover_letter=cover_letter,
        work_experience=work_experience,
        application_date=datetime.now(),
    )
    if doc is None:
        raise RuntimeError(f"Failed to create job application for {doc_id}")

    # Save DOCX
    docx_path = output_dirs["docx"] / f"{doc_id}.docx"
    doc.save(str(docx_path))
    logger.debug(f"Saved DOCX: {docx_path}")

    # Convert to PDF
    pdf_path = output_dirs["pdfs"] / f"{doc_id}.pdf"
    convert_docx_to_pdf(docx_path, pdf_path)
    logger.debug(f"Saved PDF: {pdf_path}")

    # Extract ground truth
    ground_truth = extract_ground_truth_from_docx(docx_path)
    gt_path = output_dirs["ground_truth"] / f"{doc_id}.md"
    gt_path.write_text(ground_truth, encoding="utf-8")
    logger.debug(f"Saved ground truth: {gt_path}")

    # Generate metadata
    total_years = current_year - graduation_year - 22
    metadata = {
        "document_id": doc_id,
        "document_type": "job_application",
        "industry": industry_key,
        "experience_level": experience_level,
        "position_title": position_title,
        "company_name": company_name,
        "years_experience": total_years,
        "candidate_name": candidate.name,
        "related_resume": f"resume_{resume_id:03d}",
        "generated_at": datetime.now().isoformat(),
    }

    metadata_path = output_dirs["metadata"] / f"{doc_id}.yaml"
    with open(metadata_path, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
    logger.debug(f"Saved metadata: {metadata_path}")

    return metadata


def generate_corpus(output_base: Path, count: int = 100, seed: int = 42) -> None:
    """Generate complete HR corpus.

    Args:
        output_base: Base output directory (e.g., corpus/business/hr)
        count: Total number of documents to generate (100 = 50 resumes + 50 apps)
        seed: Random seed for reproducibility
    """
    random.seed(seed)

    # Create output directories
    output_dirs = {
        "docx": output_base / "docx",
        "pdfs": output_base / "pdfs",
        "ground_truth": output_base / "ground_truth",
        "metadata": output_base / "metadata",
    }

    for dir_path in output_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    current_year = datetime.now().year

    # Generate resumes (50 total: 10 per industry)
    resume_id = 1
    resume_metadata_list = []

    for industry_key, config in DISTRIBUTION.items():
        count_val = config["count"]
        count = count_val if isinstance(count_val, int) else 0
        levels_val = config["levels"]
        levels = levels_val if isinstance(levels_val, list) else []
        docs_per_industry = count // 2  # Half for resumes

        for i in range(docs_per_industry):
            # Cycle through experience levels
            experience_level = str(levels[i % len(levels)])

            # Cycle through resume formats
            resume_format = RESUME_FORMATS[i % len(RESUME_FORMATS)]

            # Create generator with unique seed
            generator = ResumeDataGenerator(seed=seed + resume_id)

            # Generate resume
            metadata = generate_resume(
                resume_id=resume_id,
                industry_key=industry_key,
                experience_level=experience_level,
                resume_format=resume_format,
                output_dirs=output_dirs,
                generator=generator,
                current_year=current_year,
            )
            resume_metadata_list.append(metadata)
            resume_id += 1

    logger.info(f"Generated {len(resume_metadata_list)} resumes")

    # Generate job applications (50 total: 10 per industry)
    app_id = 1
    app_metadata_list = []

    for industry_key, config in DISTRIBUTION.items():
        count_val = config["count"]
        count = count_val if isinstance(count_val, int) else 0
        levels_val = config["levels"]
        levels = levels_val if isinstance(levels_val, list) else []
        docs_per_industry = count // 2  # Half for job apps

        for i in range(docs_per_industry):
            # Cycle through experience levels
            experience_level = str(levels[i % len(levels)])

            # Calculate corresponding resume ID for alignment
            # Each industry has 10 resumes and 10 apps, so app aligns with resume
            base_resume_id = (list(DISTRIBUTION.keys()).index(industry_key)) * 10 + 1
            related_resume_id = base_resume_id + i

            # Create generator with unique seed
            generator = ResumeDataGenerator(seed=seed + 100 + app_id)

            # Generate job application
            metadata = generate_job_application(
                app_id=app_id,
                resume_id=related_resume_id,
                industry_key=industry_key,
                experience_level=experience_level,
                output_dirs=output_dirs,
                generator=generator,
                current_year=current_year,
            )
            app_metadata_list.append(metadata)
            app_id += 1

    logger.info(f"Generated {len(app_metadata_list)} job applications")

    # Generate corpus summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_documents": len(resume_metadata_list) + len(app_metadata_list),
        "total_resumes": len(resume_metadata_list),
        "total_job_applications": len(app_metadata_list),
        "distribution": {
            "by_industry": {
                industry: {
                    "resumes": len([r for r in resume_metadata_list if r["industry"] == industry]),
                    "job_applications": len(
                        [a for a in app_metadata_list if a["industry"] == industry]
                    ),
                    "total": len([r for r in resume_metadata_list if r["industry"] == industry])
                    + len([a for a in app_metadata_list if a["industry"] == industry]),
                }
                for industry in DISTRIBUTION.keys()
            },
            "by_experience_level": {
                level: {
                    "resumes": len(
                        [r for r in resume_metadata_list if r["experience_level"] == level]
                    ),
                    "job_applications": len(
                        [a for a in app_metadata_list if a["experience_level"] == level]
                    ),
                    "total": len(
                        [r for r in resume_metadata_list if r["experience_level"] == level]
                    )
                    + len([a for a in app_metadata_list if a["experience_level"] == level]),
                }
                for level in ["entry", "mid", "senior", "executive"]
            },
            "by_resume_format": {
                fmt: len([r for r in resume_metadata_list if r["resume_format"] == fmt])
                for fmt in RESUME_FORMATS
            },
        },
    }

    summary_path = output_base / "corpus_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Saved corpus summary: {summary_path}")
    logger.info("=" * 60)
    logger.info("CORPUS GENERATION COMPLETE")
    logger.info(f"Total Documents: {summary['total_documents']}")
    logger.info(f"  Resumes: {summary['total_resumes']}")
    logger.info(f"  Job Applications: {summary['total_job_applications']}")
    logger.info("=" * 60)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate HR corpus for PDF-Bench")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("corpus/business/hr"),
        help="Output base directory (default: corpus/business/hr)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Total number of documents to generate (default: 100)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: generate only 10 documents (5 resumes + 5 apps)",
    )

    args = parser.parse_args()

    if args.test:
        logger.info("TEST MODE: Generating 10 documents")
        args.count = 10

    generate_corpus(args.output, args.count, args.seed)


if __name__ == "__main__":
    main()
