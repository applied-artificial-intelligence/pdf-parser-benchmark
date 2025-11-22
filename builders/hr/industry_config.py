"""Industry-specific configuration for realistic resume and job application generation.

This module defines 5 industry types with authentic characteristics including:
- Realistic job titles by experience level (Entry/Mid/Senior/Executive)
- Industry-specific skills and technologies
- Relevant certifications and credentials
- Typical responsibilities and achievements
- Salary ranges for validation
"""

from dataclasses import dataclass


@dataclass
class HRIndustryConfig:
    """Configuration for an HR industry type."""

    name: str
    company_suffixes: list[str]
    company_prefixes: list[str]
    job_titles: dict[str, list[str]]  # experience_level -> titles
    skills: list[str]
    certifications: list[str]
    responsibilities: dict[str, list[str]]  # experience_level -> responsibilities
    achievements_templates: list[str]
    salary_ranges: dict[str, tuple[int, int]]  # experience_level -> (min, max)


# Technology / Software Development
TECHNOLOGY_CONFIG = HRIndustryConfig(
    name="Technology",
    company_suffixes=["Technologies", "Software", "Systems", "Labs", "Digital", "Inc"],
    company_prefixes=["Cloud", "Data", "Tech", "Digital", "Quantum", "Neural", "Apex"],
    job_titles={
        "entry": [
            "Junior Software Engineer",
            "Software Developer I",
            "Associate Developer",
            "QA Engineer I",
            "IT Support Specialist",
            "Junior Data Analyst",
            "Technical Support Engineer",
        ],
        "mid": [
            "Software Engineer",
            "Senior Software Developer",
            "DevOps Engineer",
            "Data Scientist",
            "Product Manager",
            "Solutions Architect",
            "Site Reliability Engineer",
            "Full Stack Developer",
        ],
        "senior": [
            "Senior Software Engineer",
            "Lead Developer",
            "Principal Engineer",
            "Engineering Manager",
            "Senior DevOps Architect",
            "Data Science Manager",
            "Director of Engineering",
        ],
        "executive": [
            "VP of Engineering",
            "Chief Technology Officer",
            "VP of Product Development",
            "Chief Architect",
            "SVP of Technology",
        ],
    },
    skills=[
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "AWS",
        "Azure",
        "GCP",
        "Docker",
        "Kubernetes",
        "CI/CD",
        "PostgreSQL",
        "MongoDB",
        "Redis",
        "Git",
        "Agile/Scrum",
        "Machine Learning",
        "TensorFlow",
        "PyTorch",
        "REST APIs",
        "Microservices",
        "System Design",
        "Linux",
        "Terraform",
    ],
    certifications=[
        "AWS Certified Solutions Architect",
        "Google Cloud Professional",
        "Certified Kubernetes Administrator (CKA)",
        "Microsoft Azure Developer",
        "Certified ScrumMaster (CSM)",
        "Oracle Certified Professional",
    ],
    responsibilities={
        "entry": [
            "Write clean, maintainable code following team standards",
            "Participate in code reviews and testing",
            "Debug and fix software defects",
            "Collaborate with team members on feature development",
            "Document technical processes and procedures",
        ],
        "mid": [
            "Design and implement scalable software solutions",
            "Lead technical initiatives and feature development",
            "Mentor junior engineers and conduct code reviews",
            "Optimize application performance and reliability",
            "Collaborate with product and design teams",
            "Participate in technical architecture decisions",
        ],
        "senior": [
            "Define technical architecture and technology strategy",
            "Lead cross-functional engineering teams (5-15 people)",
            "Drive adoption of best practices and engineering standards",
            "Own critical system components and infrastructure",
            "Evaluate and integrate new technologies",
            "Resolve complex technical challenges at scale",
        ],
        "executive": [
            "Set engineering vision and technical strategy",
            "Build and scale engineering organization (50-500+ people)",
            "Drive innovation and R&D initiatives",
            "Partner with C-suite on business objectives",
            "Oversee technology budgets ($5M-$50M+)",
        ],
    },
    achievements_templates=[
        "Reduced deployment time by {percent}% through CI/CD automation",
        "Improved application performance by {percent}%, reducing latency from {old}ms to {new}ms",
        "Led migration to microservices, improving scalability by {factor}x",
        "Designed and implemented feature serving {num} million users daily",
        "Reduced AWS costs by ${amount} annually through infrastructure optimization",
        "Increased test coverage from {old}% to {new}%, reducing production bugs by {percent}%",
        "Mentored {num} junior engineers, {count} promoted to senior roles",
    ],
    salary_ranges={
        "entry": (60000, 90000),
        "mid": (90000, 160000),
        "senior": (140000, 250000),
        "executive": (200000, 500000),
    },
)


# Healthcare / Medical
HEALTHCARE_CONFIG = HRIndustryConfig(
    name="Healthcare",
    company_suffixes=["Medical Center", "Hospital", "Healthcare", "Health Systems", "Clinic"],
    company_prefixes=["Regional", "University", "Memorial", "General", "Community", "Advanced"],
    job_titles={
        "entry": [
            "Registered Nurse",
            "Medical Assistant",
            "Clinical Coordinator",
            "Patient Care Technician",
            "Medical Records Specialist",
            "Healthcare Administrator I",
        ],
        "mid": [
            "Nurse Practitioner",
            "Physician Assistant",
            "Clinical Manager",
            "Healthcare Analyst",
            "Nursing Supervisor",
            "Quality Assurance Coordinator",
            "Medical Office Manager",
        ],
        "senior": [
            "Director of Nursing",
            "Clinical Director",
            "Senior Healthcare Administrator",
            "Chief Nursing Officer",
            "Director of Patient Services",
            "Director of Clinical Operations",
        ],
        "executive": [
            "Chief Medical Officer",
            "VP of Clinical Operations",
            "Chief Nursing Officer",
            "VP of Patient Care Services",
            "Chief Operating Officer",
        ],
    },
    skills=[
        "Patient Care",
        "Electronic Health Records (EHR)",
        "Epic",
        "Cerner",
        "Medical Terminology",
        "HIPAA Compliance",
        "Clinical Documentation",
        "Patient Assessment",
        "Care Coordination",
        "Medical Billing",
        "Quality Improvement",
        "Healthcare Analytics",
        "Regulatory Compliance",
        "Infection Control",
        "Emergency Response",
        "Care Planning",
    ],
    certifications=[
        "Registered Nurse (RN)",
        "Board Certified Family Nurse Practitioner (FNP-BC)",
        "Certified Medical Assistant (CMA)",
        "Healthcare Administrator Certification (FACHE)",
        "Certified Professional in Healthcare Quality (CPHQ)",
        "Epic Certification",
        "BLS/ACLS Certification",
    ],
    responsibilities={
        "entry": [
            "Provide direct patient care and monitoring",
            "Administer medications and treatments per physician orders",
            "Document patient information in EHR system",
            "Assist with patient assessments and care planning",
            "Communicate with patients and families about care",
        ],
        "mid": [
            "Diagnose and treat acute and chronic conditions",
            "Develop and implement patient care plans",
            "Supervise nursing staff and coordinate care",
            "Ensure compliance with healthcare regulations",
            "Participate in quality improvement initiatives",
            "Manage department operations and workflows",
        ],
        "senior": [
            "Direct clinical operations and nursing services",
            "Lead quality improvement and patient safety programs",
            "Manage department budget and resource allocation",
            "Develop and implement clinical policies and protocols",
            "Oversee staff recruitment, training, and development",
            "Ensure regulatory compliance and accreditation standards",
        ],
        "executive": [
            "Set strategic vision for clinical operations",
            "Lead organization-wide quality and safety initiatives",
            "Partner with medical staff and C-suite leadership",
            "Oversee multi-department operations and budgets ($20M-$100M+)",
            "Drive patient experience and satisfaction improvements",
        ],
    },
    achievements_templates=[
        "Improved patient satisfaction scores from {old}% to {new}% over {months} months",
        "Reduced hospital readmission rate by {percent}% through care coordination",
        "Led implementation of new EHR system across {num} departments",
        "Achieved {percent}% compliance on regulatory audits for {years} consecutive years",
        "Managed team of {num} clinical staff providing care to {count} patients daily",
        "Reduced medication errors by {percent}% through protocol improvements",
        "Saved ${amount} annually through operational efficiency initiatives",
    ],
    salary_ranges={
        "entry": (45000, 75000),
        "mid": (75000, 120000),
        "senior": (100000, 180000),
        "executive": (180000, 400000),
    },
)


# Finance / Banking
FINANCE_CONFIG = HRIndustryConfig(
    name="Finance",
    company_suffixes=["Capital", "Financial", "Advisors", "Group", "Partners", "Bank"],
    company_prefixes=["Summit", "Capital", "Strategic", "Global", "Premier", "Wealth"],
    job_titles={
        "entry": [
            "Financial Analyst",
            "Junior Accountant",
            "Tax Associate",
            "Investment Analyst",
            "Credit Analyst",
            "Accounting Assistant",
        ],
        "mid": [
            "Senior Financial Analyst",
            "Accountant",
            "Senior Tax Associate",
            "Portfolio Manager",
            "Financial Planning & Analysis Manager",
            "Senior Auditor",
            "Treasury Analyst",
        ],
        "senior": [
            "Finance Manager",
            "Accounting Manager",
            "Director of FP&A",
            "Senior Portfolio Manager",
            "Controller",
            "Director of Finance",
            "Tax Director",
        ],
        "executive": [
            "Chief Financial Officer",
            "VP of Finance",
            "Treasurer",
            "Chief Accounting Officer",
            "VP of Financial Planning & Analysis",
        ],
    },
    skills=[
        "Financial Modeling",
        "Excel (Advanced)",
        "Financial Reporting",
        "GAAP",
        "IFRS",
        "SAP",
        "Oracle Financials",
        "QuickBooks",
        "Budgeting & Forecasting",
        "Variance Analysis",
        "Financial Analysis",
        "Tableau",
        "Power BI",
        "SQL",
        "VBA",
        "Python",
        "M&A Analysis",
        "Valuation",
        "Risk Management",
    ],
    certifications=[
        "CPA (Certified Public Accountant)",
        "CFA (Chartered Financial Analyst)",
        "CMA (Certified Management Accountant)",
        "CFP (Certified Financial Planner)",
        "FRM (Financial Risk Manager)",
        "CIA (Certified Internal Auditor)",
    ],
    responsibilities={
        "entry": [
            "Prepare financial reports and analysis",
            "Assist with month-end and year-end close processes",
            "Reconcile accounts and investigate variances",
            "Support budgeting and forecasting activities",
            "Maintain accurate financial records and documentation",
        ],
        "mid": [
            "Develop financial models and business cases",
            "Lead budgeting and forecasting processes",
            "Analyze financial performance and identify trends",
            "Prepare presentations for senior management",
            "Manage financial reporting and compliance",
            "Collaborate with business units on financial planning",
        ],
        "senior": [
            "Lead financial planning and analysis function",
            "Manage team of {num} finance professionals",
            "Drive strategic financial initiatives and cost optimization",
            "Own financial close process and ensure GAAP compliance",
            "Partner with business leaders on financial strategy",
            "Present financial results to board and executives",
        ],
        "executive": [
            "Set financial strategy and oversee all financial operations",
            "Lead investor relations and board reporting",
            "Manage treasury, tax, accounting, and FP&A functions",
            "Drive M&A activities and capital allocation strategy",
            "Oversee financial systems and controls",
        ],
    },
    achievements_templates=[
        "Identified cost savings of ${amount} through financial analysis",
        "Improved forecast accuracy from {old}% to {new}%",
        "Led implementation of new ERP system (SAP/Oracle) across organization",
        "Reduced month-end close time from {old} days to {new} days",
        "Successfully completed {num} M&A transactions totaling ${amount}M",
        "Achieved clean audit for {years} consecutive years with zero material weaknesses",
        "Managed annual budget of ${amount}M with {percent}% variance accuracy",
    ],
    salary_ranges={
        "entry": (55000, 80000),
        "mid": (80000, 140000),
        "senior": (120000, 220000),
        "executive": (200000, 500000),
    },
)


# Manufacturing / Industrial
MANUFACTURING_CONFIG = HRIndustryConfig(
    name="Manufacturing",
    company_suffixes=["Manufacturing", "Industries", "Corp", "Industrial", "Inc", "Group"],
    company_prefixes=["Precision", "Advanced", "Global", "Industrial", "Quality", "Premier"],
    job_titles={
        "entry": [
            "Production Associate",
            "Quality Control Technician",
            "Manufacturing Engineer I",
            "Maintenance Technician",
            "Process Technician",
            "Assembly Technician",
        ],
        "mid": [
            "Manufacturing Engineer",
            "Production Supervisor",
            "Quality Engineer",
            "Process Engineer",
            "Maintenance Manager",
            "Production Planner",
            "Industrial Engineer",
        ],
        "senior": [
            "Senior Manufacturing Engineer",
            "Plant Manager",
            "Director of Manufacturing",
            "Director of Quality",
            "Senior Operations Manager",
            "Director of Supply Chain",
        ],
        "executive": [
            "VP of Operations",
            "Chief Operations Officer",
            "VP of Manufacturing",
            "VP of Supply Chain",
            "General Manager",
        ],
    },
    skills=[
        "Lean Manufacturing",
        "Six Sigma",
        "Continuous Improvement",
        "Production Planning",
        "Quality Control",
        "ISO 9001",
        "Safety Management",
        "OSHA Compliance",
        "Root Cause Analysis",
        "CAD/CAM",
        "PLC Programming",
        "Equipment Maintenance",
        "Inventory Management",
        "ERP Systems",
        "Process Optimization",
        "Statistical Process Control",
        "GD&T",
        "5S Implementation",
    ],
    certifications=[
        "Six Sigma Black Belt",
        "Six Sigma Green Belt",
        "Lean Manufacturing Certification",
        "Certified Quality Engineer (CQE)",
        "PMP (Project Management Professional)",
        "OSHA Safety Certification",
        "Certified Production Technician (CPT)",
    ],
    responsibilities={
        "entry": [
            "Operate production equipment and machinery",
            "Perform quality inspections and testing",
            "Maintain production records and documentation",
            "Follow safety protocols and procedures",
            "Assist with equipment maintenance and troubleshooting",
        ],
        "mid": [
            "Optimize manufacturing processes and workflows",
            "Supervise production teams (10-30 people)",
            "Implement lean manufacturing and continuous improvement",
            "Ensure quality standards and compliance",
            "Manage production schedules and capacity planning",
            "Troubleshoot equipment and process issues",
        ],
        "senior": [
            "Lead plant operations and manufacturing strategy",
            "Manage multi-shift production operations",
            "Drive operational excellence and efficiency improvements",
            "Oversee quality, safety, and regulatory compliance",
            "Manage facility budget and capital expenditures ($5M-$20M)",
            "Lead cross-functional teams on improvement projects",
        ],
        "executive": [
            "Set strategic vision for manufacturing operations",
            "Oversee multiple facilities and production sites",
            "Drive operational efficiency and cost reduction initiatives",
            "Partner with supply chain, engineering, and quality teams",
            "Manage operations budget ($50M-$500M+)",
        ],
    },
    achievements_templates=[
        "Reduced manufacturing defects by {percent}% through process improvements",
        "Increased production output by {percent}% while maintaining quality standards",
        "Implemented lean manufacturing, reducing waste by ${amount} annually",
        "Achieved {months} months of zero safety incidents across {num} employees",
        "Reduced production costs by {percent}% through automation and optimization",
        "Led implementation of new production line, increasing capacity by {percent}%",
        "Improved on-time delivery from {old}% to {new}% over {months} months",
    ],
    salary_ranges={
        "entry": (40000, 65000),
        "mid": (65000, 110000),
        "senior": (100000, 170000),
        "executive": (150000, 350000),
    },
)


# Education / Academic
EDUCATION_CONFIG = HRIndustryConfig(
    name="Education",
    company_suffixes=["School District", "University", "College", "Academy", "Learning Center"],
    company_prefixes=["Regional", "Community", "State", "Central", "Metropolitan", "City"],
    job_titles={
        "entry": [
            "Teacher",
            "Teaching Assistant",
            "Curriculum Coordinator",
            "Academic Advisor",
            "Instructional Designer",
            "School Counselor",
        ],
        "mid": [
            "Lead Teacher",
            "Department Chair",
            "Curriculum Director",
            "Instructional Coach",
            "Student Services Coordinator",
            "Dean of Students",
            "Assessment Coordinator",
        ],
        "senior": [
            "Assistant Principal",
            "Principal",
            "Director of Curriculum & Instruction",
            "Director of Special Education",
            "Director of Student Services",
            "Academic Dean",
        ],
        "executive": [
            "Superintendent",
            "Assistant Superintendent",
            "VP of Academic Affairs",
            "Chief Academic Officer",
            "Provost",
        ],
    },
    skills=[
        "Curriculum Development",
        "Lesson Planning",
        "Classroom Management",
        "Educational Technology",
        "Learning Management Systems (LMS)",
        "Student Assessment",
        "Data-Driven Instruction",
        "Differentiated Instruction",
        "Google Classroom",
        "Canvas",
        "Blackboard",
        "Educational Standards",
        "Student Support Services",
        "Parent Communication",
        "Professional Development",
    ],
    certifications=[
        "State Teaching License",
        "National Board Certification",
        "Master's Degree in Education",
        "Educational Leadership Certification",
        "Special Education Certification",
        "ESL Certification",
        "Administrator Certification",
    ],
    responsibilities={
        "entry": [
            "Plan and deliver standards-aligned instruction",
            "Assess student learning and provide feedback",
            "Manage classroom environment and student behavior",
            "Communicate with parents about student progress",
            "Participate in professional development and collaboration",
        ],
        "mid": [
            "Lead curriculum development and instructional planning",
            "Mentor and support new teachers",
            "Analyze student data and drive improvement strategies",
            "Coordinate department activities and initiatives",
            "Facilitate professional learning communities",
            "Manage student services programs",
        ],
        "senior": [
            "Lead school operations and instructional programs",
            "Supervise and evaluate teachers and staff",
            "Manage school budget and resource allocation",
            "Ensure compliance with state and federal regulations",
            "Partner with community and stakeholder groups",
            "Drive school improvement and student achievement",
        ],
        "executive": [
            "Set district/institutional vision and strategic priorities",
            "Oversee all academic programs and operations",
            "Lead district budget ($50M-$500M+) and resource planning",
            "Partner with school board and community stakeholders",
            "Drive educational policy and reform initiatives",
        ],
    },
    achievements_templates=[
        "Improved student proficiency rates from {old}% to {new}% in {subject}",
        "Developed curriculum adopted across {num} schools serving {count} students",
        "Led school to achieve {rating} rating on state accountability system",
        "Increased graduation rate from {old}% to {new}% over {years} years",
        "Secured ${amount} in grants for educational programs and technology",
        "Reduced achievement gap by {percent} percentage points over {years} years",
        "Implemented new instructional model improving student growth by {percent}%",
    ],
    salary_ranges={
        "entry": (40000, 65000),
        "mid": (60000, 95000),
        "senior": (80000, 140000),
        "executive": (120000, 300000),
    },
)


# Complete industry registry
INDUSTRIES = {
    "technology": TECHNOLOGY_CONFIG,
    "healthcare": HEALTHCARE_CONFIG,
    "finance": FINANCE_CONFIG,
    "manufacturing": MANUFACTURING_CONFIG,
    "education": EDUCATION_CONFIG,
}


# Experience level definitions
EXPERIENCE_LEVELS = {
    "entry": {"name": "Entry Level", "years_min": 0, "years_max": 2},
    "mid": {"name": "Mid Level", "years_min": 3, "years_max": 7},
    "senior": {"name": "Senior Level", "years_min": 8, "years_max": 15},
    "executive": {"name": "Executive Level", "years_min": 15, "years_max": 35},
}
