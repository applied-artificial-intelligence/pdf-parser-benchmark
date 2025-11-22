"""Realistic data generators for resume and job application content.

This module generates authentic HR data including:
- Candidate names and contact information
- Work experience with realistic progression
- Education history
- Skills and certifications
- Achievements and responsibilities
"""

import random
from dataclasses import dataclass
from datetime import datetime

from faker import Faker


@dataclass
class CandidateInfo:
    """Candidate personal information."""

    name: str
    address: str
    city: str
    state_province: str
    postal_code: str
    country: str
    phone: str
    email: str
    linkedin: str = ""


@dataclass
class Education:
    """Educational background entry."""

    degree: str
    major: str
    institution: str
    city: str
    state: str
    graduation_year: int
    gpa: str = ""  # Optional


@dataclass
class WorkExperience:
    """Work experience entry."""

    company: str
    title: str
    city: str
    state: str
    start_date: str  # e.g., "January 2020"
    end_date: str  # e.g., "Present" or "June 2023"
    responsibilities: list[str]
    achievements: list[str]


@dataclass
class Skill:
    """Technical or professional skill."""

    name: str
    category: str = ""  # e.g., "Programming Languages", "Tools"


@dataclass
class Certification:
    """Professional certification."""

    name: str
    issuer: str
    year: int


class ResumeDataGenerator:
    """Generator for realistic resume and job application data."""

    def __init__(self, seed: int = None):
        """Initialize generator with optional seed.

        Args:
            seed: Random seed for reproducibility
        """
        if seed:
            random.seed(seed)
            Faker.seed(seed)

        # Default to US locale for resumes
        self.fake = Faker("en_US")

    def generate_candidate_info(self) -> CandidateInfo:
        """Generate realistic candidate personal information.

        Returns:
            CandidateInfo instance
        """
        name = self.fake.name()
        address = self.fake.street_address()
        city = self.fake.city()
        state = self.fake.state_abbr()
        postal = self.fake.zipcode()
        country = "USA"
        phone = self.fake.phone_number()

        # Generate professional email
        first = name.split()[0].lower()
        last = name.split()[-1].lower()
        email_formats = [
            f"{first}.{last}@gmail.com",
            f"{first}{last}@yahoo.com",
            f"{first[0]}{last}@outlook.com",
            f"{first}.{last}@{self.fake.free_email_domain()}",
        ]
        email = random.choice(email_formats)

        # Generate LinkedIn profile
        linkedin = f"linkedin.com/in/{first}-{last}-{random.randint(100, 999)}"

        return CandidateInfo(
            name=name,
            address=address,
            city=city,
            state_province=state,
            postal_code=postal,
            country=country,
            phone=phone,
            email=email,
            linkedin=linkedin,
        )

    def generate_education(
        self, experience_level: str, graduation_year_base: int
    ) -> list[Education]:
        """Generate realistic education history.

        Args:
            experience_level: One of "entry", "mid", "senior", "executive"
            graduation_year_base: Base graduation year (typically calculated from work start)

        Returns:
            List of Education instances
        """
        education = []
        current_year = datetime.now().year

        # All levels have bachelor's degree
        bachelor_majors = {
            "technology": [
                "Computer Science",
                "Software Engineering",
                "Information Systems",
                "Computer Engineering",
            ],
            "healthcare": [
                "Nursing",
                "Health Administration",
                "Biology",
                "Public Health",
            ],
            "finance": [
                "Finance",
                "Accounting",
                "Economics",
                "Business Administration",
            ],
            "manufacturing": [
                "Industrial Engineering",
                "Mechanical Engineering",
                "Manufacturing Engineering",
                "Business Management",
            ],
            "education": [
                "Education",
                "Elementary Education",
                "Secondary Education",
                "Liberal Arts",
            ],
        }

        # Choose random subject area
        subject_areas = list(bachelor_majors.keys())
        subject = random.choice(subject_areas)

        # Bachelor's degree
        universities = [
            ("University of {}", "State"),
            ("{} State University", "State"),
            ("{} University", "City"),
            ("{} College", "City"),
        ]
        univ_template, location_type = random.choice(universities)
        if location_type == "State":
            location = self.fake.state()
        else:
            location = self.fake.city()

        univ_name = univ_template.format(location)

        bachelor_year = graduation_year_base
        gpa_value = random.uniform(3.0, 4.0)
        gpa = f"{gpa_value:.2f}" if random.random() > 0.3 else ""  # 70% include GPA

        bachelor = Education(
            degree="Bachelor of Science" if subject != "education" else "Bachelor of Arts",
            major=random.choice(bachelor_majors[subject]),
            institution=univ_name,
            city=self.fake.city(),
            state=self.fake.state_abbr(),
            graduation_year=bachelor_year,
            gpa=gpa,
        )
        education.append(bachelor)

        # Mid-level and above may have master's (60% chance)
        if experience_level in ["mid", "senior", "executive"] and random.random() > 0.4:
            masters_majors = {
                "technology": [
                    "Computer Science",
                    "Data Science",
                    "Software Engineering",
                    "MBA",
                ],
                "healthcare": [
                    "Nursing",
                    "Healthcare Administration",
                    "Public Health",
                    "MBA",
                ],
                "finance": ["MBA", "Finance", "Accounting"],
                "manufacturing": [
                    "Engineering Management",
                    "Industrial Engineering",
                    "MBA",
                ],
                "education": [
                    "Education",
                    "Educational Leadership",
                    "Curriculum & Instruction",
                ],
            }

            masters_year = bachelor_year + random.randint(2, 8)
            masters_gpa = random.uniform(3.3, 4.0)
            masters_gpa_str = f"{masters_gpa:.2f}" if random.random() > 0.5 else ""

            masters = Education(
                degree="Master of Business Administration"
                if "MBA" in random.choice(masters_majors[subject])
                else "Master of Science",
                major=random.choice(masters_majors[subject]),
                institution=random.choice(
                    [
                        f"{self.fake.state()} State University",
                        f"University of {self.fake.state()}",
                        f"{self.fake.city()} University",
                    ]
                ),
                city=self.fake.city(),
                state=self.fake.state_abbr(),
                graduation_year=masters_year,
                gpa=masters_gpa_str,
            )
            education.append(masters)

        # Senior/Executive may have additional certifications shown as education (30% chance)
        if experience_level in ["senior", "executive"] and random.random() > 0.7:
            exec_programs = [
                "Executive Leadership Program",
                "Strategic Management Certificate",
                "Executive MBA",
            ]
            cert_year = current_year - random.randint(1, 5)

            exec_ed = Education(
                degree="Certificate",
                major=random.choice(exec_programs),
                institution=random.choice(
                    [
                        "Harvard Business School",
                        "Stanford Graduate School of Business",
                        "Wharton School",
                        "MIT Sloan",
                    ]
                ),
                city=self.fake.city(),
                state=self.fake.state_abbr(),
                graduation_year=cert_year,
                gpa="",
            )
            education.append(exec_ed)

        return education

    def generate_work_history(
        self,
        industry_config,
        experience_level: str,
        current_year: int,
    ) -> tuple[list[WorkExperience], int]:
        """Generate realistic work history based on experience level.

        Args:
            industry_config: HRIndustryConfig instance
            experience_level: One of "entry", "mid", "senior", "executive"
            current_year: Current year for date calculations

        Returns:
            Tuple of (list of WorkExperience instances, graduation_year)
        """
        experiences = []

        # Determine years of experience
        experience_years = {
            "entry": random.randint(0, 2),
            "mid": random.randint(3, 7),
            "senior": random.randint(8, 15),
            "executive": random.randint(15, 30),
        }
        total_years = experience_years[experience_level]

        # Calculate graduation year (assume graduated at 22)
        graduation_year = current_year - total_years - 22

        # Determine number of jobs (people change jobs every 2-5 years on average)
        if total_years == 0:
            num_jobs = 1
        elif total_years <= 2:
            num_jobs = 1
        elif total_years <= 5:
            num_jobs = random.choice([1, 2])
        elif total_years <= 10:
            num_jobs = random.randint(2, 4)
        else:
            num_jobs = random.randint(3, 6)

        # Generate jobs in reverse chronological order (most recent first)
        years_remaining = total_years
        for job_idx in range(num_jobs):
            if job_idx == 0:
                # Current job
                years_in_role = random.randint(1, max(1, min(4, years_remaining)))
                end_date = "Present"
                start_year = current_year - years_in_role

                # Current job uses higher-level title
                if experience_level == "entry":
                    title = random.choice(industry_config.job_titles["entry"])
                elif experience_level == "mid":
                    title = random.choice(industry_config.job_titles["mid"])
                elif experience_level == "senior":
                    title = random.choice(industry_config.job_titles["senior"])
                else:  # executive
                    title = random.choice(industry_config.job_titles["executive"])

            else:
                # Previous jobs
                years_in_role = random.randint(1, max(1, min(5, years_remaining)))
                end_year = start_year
                start_year = end_year - years_in_role
                end_date = f"{self._month_name(random.randint(1, 12))} {end_year}"

                # Previous jobs use progressively lower titles
                if job_idx == 1 and experience_level in ["senior", "executive"]:
                    # One level down
                    if experience_level == "senior":
                        title = random.choice(industry_config.job_titles["mid"])
                    else:
                        title = random.choice(industry_config.job_titles["senior"])
                elif job_idx <= 2 and experience_level == "executive":
                    title = random.choice(industry_config.job_titles["mid"])
                else:
                    # Entry or earlier career roles
                    title = random.choice(industry_config.job_titles["entry"])

            start_date = f"{self._month_name(random.randint(1, 12))} {start_year}"

            # Generate company name
            prefix = random.choice(industry_config.company_prefixes)
            suffix = random.choice(industry_config.company_suffixes)
            company = f"{prefix} {suffix}"

            # Get responsibilities and achievements for this level
            level_key = self._title_to_level(title, industry_config)
            responsibilities = random.sample(
                industry_config.responsibilities[level_key],
                k=min(random.randint(3, 5), len(industry_config.responsibilities[level_key])),
            )

            # Generate achievements from templates
            achievements = self._generate_achievements(
                industry_config, level_key, num_achievements=random.randint(2, 4)
            )

            experience = WorkExperience(
                company=company,
                title=title,
                city=self.fake.city(),
                state=self.fake.state_abbr(),
                start_date=start_date,
                end_date=end_date,
                responsibilities=responsibilities,
                achievements=achievements,
            )
            experiences.append(experience)

            years_remaining -= years_in_role
            if years_remaining <= 0:
                break

        return experiences, graduation_year

    def _title_to_level(self, title: str, industry_config) -> str:
        """Determine experience level from job title.

        Args:
            title: Job title
            industry_config: HRIndustryConfig instance

        Returns:
            Experience level key ("entry", "mid", "senior", "executive")
        """
        for level, titles in industry_config.job_titles.items():
            if title in titles:
                return level
        return "mid"  # Default

    def _generate_achievements(
        self, industry_config, level_key: str, num_achievements: int = 3
    ) -> list[str]:
        """Generate realistic achievements from templates.

        Args:
            industry_config: HRIndustryConfig instance
            level_key: Experience level ("entry", "mid", "senior", "executive")
            num_achievements: Number of achievements to generate

        Returns:
            List of achievement strings
        """
        achievements = []
        templates = industry_config.achievements_templates

        for _ in range(num_achievements):
            template = random.choice(templates)

            # Fill in template variables with realistic values
            filled = template.format(
                percent=random.randint(15, 85),
                old=random.randint(30, 70),
                new=random.randint(75, 99),
                oldms=random.randint(500, 2000),
                newms=random.randint(50, 400),
                factor=random.randint(2, 10),
                num=random.randint(5, 500),
                count=random.randint(10, 1000),
                amount=f"{random.randint(50, 500)}K",
                months=random.randint(6, 24),
                years=random.randint(2, 5),
                subject=random.choice(["Math", "Reading", "Science", "Overall"]),
                rating=random.choice(["A", "Excellent", "Outstanding"]),
                old_var=random.randint(50, 200),
                new_var=random.randint(10, 40),
            )
            achievements.append(filled)

        return achievements

    def generate_skills(
        self, industry_config, experience_level: str, num_skills: int = None
    ) -> list[Skill]:
        """Generate realistic skills list.

        Args:
            industry_config: HRIndustryConfig instance
            experience_level: One of "entry", "mid", "senior", "executive"
            num_skills: Number of skills (auto-determined if None)

        Returns:
            List of Skill instances
        """
        if num_skills is None:
            # More experienced = more skills
            num_skills_range = {
                "entry": (5, 10),
                "mid": (10, 18),
                "senior": (15, 25),
                "executive": (15, 20),
            }
            num_skills = random.randint(*num_skills_range[experience_level])

        # Sample from industry skills
        selected_skills = random.sample(
            industry_config.skills, k=min(num_skills, len(industry_config.skills))
        )

        skills = [Skill(name=skill) for skill in selected_skills]
        return skills

    def generate_certifications(
        self, industry_config, experience_level: str, current_year: int
    ) -> list[Certification]:
        """Generate realistic certifications.

        Args:
            industry_config: HRIndustryConfig instance
            experience_level: One of "entry", "mid", "senior", "executive"
            current_year: Current year for date calculations

        Returns:
            List of Certification instances
        """
        certifications = []

        # Probability of having certifications increases with experience
        cert_probability = {
            "entry": 0.3,
            "mid": 0.6,
            "senior": 0.8,
            "executive": 0.7,
        }

        if random.random() > cert_probability[experience_level]:
            return []

        # Number of certifications
        num_certs_range = {
            "entry": (1, 2),
            "mid": (1, 3),
            "senior": (2, 4),
            "executive": (1, 3),
        }
        num_certs = random.randint(*num_certs_range[experience_level])

        # Sample from industry certifications
        selected_certs = random.sample(
            industry_config.certifications,
            k=min(num_certs, len(industry_config.certifications)),
        )

        for cert_name in selected_certs:
            # Certifications earned within last 5-10 years
            cert_year = current_year - random.randint(1, 10)

            # Extract issuer from cert name (simple heuristic)
            if "AWS" in cert_name:
                issuer = "Amazon Web Services"
            elif "Google" in cert_name or "GCP" in cert_name:
                issuer = "Google Cloud"
            elif "Microsoft" in cert_name or "Azure" in cert_name:
                issuer = "Microsoft"
            elif "Oracle" in cert_name:
                issuer = "Oracle"
            elif "CPA" in cert_name:
                issuer = "State Board of Accountancy"
            elif "CFA" in cert_name:
                issuer = "CFA Institute"
            elif "Six Sigma" in cert_name:
                issuer = "International Association for Six Sigma Certification"
            elif "PMP" in cert_name:
                issuer = "Project Management Institute"
            else:
                issuer = "Professional Certification Board"

            cert = Certification(name=cert_name, issuer=issuer, year=cert_year)
            certifications.append(cert)

        return certifications

    def generate_professional_summary(
        self, industry_config, experience_level: str, total_years: int
    ) -> str:
        """Generate professional summary paragraph.

        Args:
            industry_config: HRIndustryConfig instance
            experience_level: One of "entry", "mid", "senior", "executive"
            total_years: Total years of experience

        Returns:
            Professional summary string
        """
        summaries = {
            "entry": [
                f"Recent graduate with {total_years} year{'s' if total_years != 1 else ''} of experience in {industry_config.name.lower()}. "
                f"Eager to contribute technical skills and fresh perspectives to a dynamic team.",
                f"Motivated {industry_config.name.lower()} professional with {total_years} year{'s' if total_years != 1 else ''} of hands-on experience. "
                f"Strong foundation in core technologies and commitment to continuous learning.",
            ],
            "mid": [
                f"Results-driven {industry_config.name.lower()} professional with {total_years} years of progressive experience. "
                f"Proven track record of delivering high-quality solutions and driving process improvements.",
                f"Experienced {industry_config.name.lower()} specialist with {total_years} years leading technical initiatives. "
                f"Strong problem-solving skills and ability to collaborate across teams.",
            ],
            "senior": [
                f"Senior {industry_config.name.lower()} leader with {total_years}+ years of experience driving strategic initiatives. "
                f"Expertise in building high-performing teams and delivering business-critical solutions at scale.",
                f"Accomplished {industry_config.name.lower()} professional with {total_years}+ years of expertise. "
                f"Track record of leading complex projects and mentoring engineering teams.",
            ],
            "executive": [
                f"Executive-level {industry_config.name.lower()} leader with {total_years}+ years of experience. "
                f"Proven ability to set technical vision, build world-class teams, and drive business transformation.",
                f"Strategic {industry_config.name.lower()} executive with {total_years}+ years leading organizations. "
                f"Expertise in scaling operations, driving innovation, and delivering measurable business results.",
            ],
        }

        return random.choice(summaries[experience_level])

    @staticmethod
    def _month_name(month: int) -> str:
        """Convert month number to name.

        Args:
            month: Month number (1-12)

        Returns:
            Month name
        """
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        return months[month - 1]
