#!/usr/bin/env python3
"""
Seed intern jobs from Tiger Global Management portfolio companies.

Tiger Global Management is a major investment firm focused on internet, software,
consumer, and financial technology companies. This script seeds US-based intern
positions from confirmed Tiger Global portfolio companies.

Companies included (8): Stripe, Brex, Coinbase, Toast, Databricks, Zip, Confluent, GitLab
Total jobs: 12

Run with: cd apps/api && python -m scripts.seed_tigerglobal_jobs
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.employer import (
    Employer, Job, Organization, OrganizationMember,
    Vertical, RoleType, OrganizationRole,
)
from app.utils.auth import get_password_hash
from app.config import settings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRM_NAME = "Tiger Global Management"
SCRIPT_ID = "tigerglobal"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Stripe ──
    {
        "company_name": "Stripe",
        "email": "careers@stripe.com",
        "name": "Patrick Collison",
        "industry": "Financial Technology / Payments",
        "company_size": "startup",
        "website": "https://stripe.com",
        "slug": "stripe",
        "description": (
            "Stripe builds economic infrastructure for the internet. Millions of "
            "businesses—from startups to Fortune 500s—use Stripe to accept payments, "
            "send payouts, and manage their businesses online. Stripe processes "
            "hundreds of billions of dollars annually.\n\n"
            "Fund: Tiger Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Patrick Collison", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/patrickc"},
            {"name": "John Collison", "title": "President & Co-Founder", "linkedin": "https://linkedin.com/in/johncollison"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 9500,
                "salary_max": 10800,
                "requirements": [
                    "Experience from previous internships or multi-person projects including open source",
                    "At least 2 years of university education or equivalent work experience",
                    "Ability to learn unfamiliar systems and navigate new codebases with multiple languages",
                    "Strong fundamentals in computer science and software engineering",
                ],
                "description": (
                    "Software Engineer Intern at Stripe (Summer 2026)\n\n"
                    "Tackle important projects to increase global commerce. Write production code "
                    "with meaningful impact, participate in code reviews and design discussions, "
                    "and collaborate with engineers and cross-functional stakeholders. Recent intern "
                    "projects include rebuilding statistics aggregation services, building new service "
                    "discovery systems, and user-facing projects like improving error messages on "
                    "Stripe Checkout. 12 or 16 week program with housing ($6,900), transportation "
                    "($1,600), and wellness ($250) stipends.\n\n"
                    "Source: https://stripe.com/jobs/listing/software-engineer-intern-summer-and-winter/7210115"
                ),
            },
        ],
    },

    # ── 2. Brex ──
    {
        "company_name": "Brex",
        "email": "careers@brex.com",
        "name": "Pedro Franceschi",
        "industry": "Financial Technology / Corporate Finance",
        "company_size": "startup",
        "website": "https://brex.com",
        "slug": "brex",
        "description": (
            "Brex is the AI-powered spend platform that helps companies spend with confidence. "
            "From corporate cards and expense management to bill pay and travel, Brex provides "
            "an all-in-one finance solution for startups and enterprises. Valued at $12.3 billion.\n\n"
            "Fund: Tiger Global (Led Series D, $425M) | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Pedro Franceschi", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/pfranceschi"},
            {"name": "Henrique Dubugras", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/henriquedubugras"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8000,
                "salary_max": 9500,
                "requirements": [
                    "Strong CS fundamentals and experience in backend programming languages",
                    "Experience with Java, Kotlin, Python, or SQL databases",
                    "Passion for AI and financial technology",
                    "Currently pursuing a degree in Computer Science or related field",
                ],
                "description": (
                    "Software Engineer Intern at Brex (Summer 2026)\n\n"
                    "Join Brex's inaugural AI-centric internship cohort in NYC. Collaborate with "
                    "a mentor and team to develop impactful products, services, and infrastructure "
                    "that accelerate the adoption of AI-first tools and workflows across Brex. "
                    "Hybrid work arrangement with at least 2 days per week in the office "
                    "(Wednesdays and Thursdays).\n\n"
                    "Source: https://www.brex.com/careers"
                ),
            },
            {
                "title": "Operations Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.BUSINESS_ANALYST,
                "location": "New York, NY",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Currently pursuing a bachelor's degree with graduation between Dec 2026 - Dec 2027",
                    "Demonstrated experience using AI tools and effective prompting skills",
                    "Strong problem-solving abilities and comfort working through ambiguity",
                    "Familiarity with Retool, Salesforce, Hex, or Looker preferred",
                ],
                "description": (
                    "Operations Intern at Brex (Summer 2026)\n\n"
                    "Join one of Brex's Operations teams in a 1-2 year program. Learn about risk "
                    "management, operations, and data analysis while contributing to critical process "
                    "improvements with a focus on leveraging AI to streamline workflows. Complete a "
                    "core project focused on key data insights, process implementation, or process "
                    "improvement and share findings with Brex executives.\n\n"
                    "Source: https://www.brex.com/careers/8172520002"
                ),
            },
        ],
    },

    # ── 3. Coinbase ──
    {
        "company_name": "Coinbase",
        "email": "careers@coinbase.com",
        "name": "Brian Armstrong",
        "industry": "Cryptocurrency / Financial Technology",
        "company_size": "startup",
        "website": "https://coinbase.com",
        "slug": "coinbase",
        "description": (
            "Coinbase is the leading cryptocurrency exchange in the United States, building "
            "the next generation of crypto-forward products and financial infrastructure. "
            "The platform serves as a trusted gateway for millions of users to access "
            "the cryptoeconomy.\n\n"
            "Fund: Tiger Global (Led Series E, $300M) | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Brian Armstrong", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/barmstrong"},
            {"name": "Fred Ehrsam", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/fredehrsam"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10400,
                "requirements": [
                    "Programming experience in any language (systems written in Golang, JavaScript, Ruby)",
                    "Currently enrolled in a Bachelor's or Master's program in CS or related field",
                    "Strong problem-solving and analytical skills",
                    "Interest in cryptocurrency and blockchain technology",
                ],
                "description": (
                    "Software Engineer Intern at Coinbase (Summer 2026)\n\n"
                    "12-week internship building next-generation crypto-forward products and features. "
                    "Write high-quality, well-tested code and work on projects with engineers, "
                    "designers, product managers, and senior leadership. Teams include Base (Layer 2) "
                    "and core exchange infrastructure. Eligible for housing stipend and benefits.\n\n"
                    "Source: https://www.coinbase.com/careers/positions/7268895"
                ),
            },
            {
                "title": "Machine Learning Engineer Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10400,
                "requirements": [
                    "Experience with machine learning frameworks (PyTorch, TensorFlow, scikit-learn)",
                    "Strong programming skills in Python",
                    "Understanding of ML fundamentals: supervised/unsupervised learning, NLP, or computer vision",
                    "Currently pursuing a degree in CS, ML, Statistics, or related field",
                ],
                "description": (
                    "Machine Learning Engineer Intern at Coinbase (Summer 2026)\n\n"
                    "Work on ML-powered features across the Coinbase platform. Apply machine learning "
                    "to problems in fraud detection, recommendation systems, market analysis, and "
                    "user experience personalization. Collaborate with data scientists and engineers "
                    "to build production ML models. Hybrid role in San Francisco.\n\n"
                    "Source: https://www.coinbase.com/careers/positions/7294075"
                ),
            },
        ],
    },

    # ── 4. Toast ──
    {
        "company_name": "Toast",
        "email": "careers@toasttab.com",
        "name": "Aman Narang",
        "industry": "Restaurant Technology / SaaS",
        "company_size": "startup",
        "website": "https://toasttab.com",
        "slug": "toast-pos",
        "description": (
            "Toast provides an all-in-one restaurant management platform integrating "
            "point-of-sale, payments, operations, and analytics. The platform runs on a "
            "stack including Android tablets, web applications, and backend microservices "
            "serving restaurants of all sizes.\n\n"
            "Fund: Tiger Global | HQ: Boston, MA"
        ),
        "founders": [
            {"name": "Aman Narang", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/amannarang"},
            {"name": "Steve Fredette", "title": "President & Co-Founder", "linkedin": "https://linkedin.com/in/stevefredette"},
            {"name": "Jonathan Grimm", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/jonathangrimm"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Boston, MA",
                "salary_min": 5500,
                "salary_max": 6500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science, Software Engineering, or related field",
                    "Experience with Java, Kotlin, React, or Python",
                    "At least one semester of school remaining after internship",
                    "Interest in restaurant technology, POS systems, or fintech",
                ],
                "description": (
                    "Software Engineering Intern at Toast (Summer 2026)\n\n"
                    "Work across Toast's diverse tech stack: Android POS (Java/Kotlin), "
                    "containerized RESTful and gRPC backend services, Apache Camel integrations, "
                    "React front-end applications, and GraphQL data access layers. Areas include "
                    "Android/iOS development, web frontend, backend infrastructure, AI/ML models, "
                    "and cybersecurity. Full-time 40-hour/week role for approximately 10 weeks.\n\n"
                    "Source: https://careers.toasttab.com/early-career"
                ),
            },
        ],
    },

    # ── 5. Databricks ──
    {
        "company_name": "Databricks",
        "email": "careers@databricks.com",
        "name": "Ali Ghodsi",
        "industry": "Data & AI / Infrastructure",
        "company_size": "startup",
        "website": "https://databricks.com",
        "slug": "databricks",
        "description": (
            "Databricks is the Data + AI company, providing a unified analytics platform for "
            "data engineering, data science, and machine learning. Built on Apache Spark, the "
            "platform is used by thousands of organizations worldwide. Valued at $134 billion.\n\n"
            "Fund: Tiger Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Ali Ghodsi", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/alighodsi"},
            {"name": "Ion Stoica", "title": "Co-Founder & Executive Chairman", "linkedin": ""},
            {"name": "Matei Zaharia", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/mateizaharia"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10400,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with a degree in CS, Engineering, or related field",
                    "Implementation skills in Python, Java, or C++",
                    "Strong knowledge of algorithms, data structures, and OOP principles",
                    "Interest in distributed systems, databases, or cloud infrastructure",
                ],
                "description": (
                    "Software Engineering Intern at Databricks (Summer 2026)\n\n"
                    "Join a team of engineers to build features that contribute directly to the "
                    "Databricks platform. Work across full stack, backend, infrastructure, systems, "
                    "tools, cloud, databases, and customer-facing products. Choose between 12-week "
                    "summer internship or 16-week co-op. Receive a dedicated mentor and join the "
                    "2026 intern cohort connecting with engineers and leaders.\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/software-engineering-intern-2026-6866531002"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10400,
                "requirements": [
                    "Pursuing a degree in Data Science, Statistics, CS, or related quantitative field",
                    "Experience with data science methodologies (causal inference, recommender systems)",
                    "Proficiency in Python and SQL",
                    "Strong statistical analysis and data visualization skills",
                ],
                "description": (
                    "Data Science Intern at Databricks (Summer 2026)\n\n"
                    "Work with the Data team and internal stakeholders to use data to solve problems. "
                    "Apply expertise in data science methodologies such as causal inference modeling "
                    "and recommender systems. Contribute to data-driven decision making across the "
                    "organization. Dedicated mentor and intern cohort experience included.\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/data-science-intern-2026-start-6866538002"
                ),
            },
            {
                "title": "Product Management Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "San Francisco, CA",
                "salary_min": 8000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a degree in CS, Business, Engineering, or related field",
                    "Strong analytical and problem-solving skills",
                    "Excellent communication and stakeholder management abilities",
                    "Interest in data platforms, AI/ML, or enterprise software",
                ],
                "description": (
                    "Product Management Intern at Databricks (Summer 2026)\n\n"
                    "Work with product teams to define product strategy and roadmap for the "
                    "Databricks platform. Conduct user research, analyze market trends, and "
                    "collaborate with engineering and design to ship product features. Gain "
                    "hands-on experience in enterprise product management at one of the "
                    "fastest-growing data companies.\n\n"
                    "Source: https://www.databricks.com/company/careers/product/product-management-intern-summer-2026-6883068002"
                ),
            },
        ],
    },

    # ── 6. Zip ──
    {
        "company_name": "Zip",
        "email": "careers@ziphq.com",
        "name": "Rujul Zaparde",
        "industry": "Enterprise Software / Procurement",
        "company_size": "startup",
        "website": "https://ziphq.com",
        "slug": "zip-procurement",
        "description": (
            "Zip is the AI-powered procurement orchestration platform used by companies like "
            "OpenAI, Snowflake, Anthropic, and Coinbase to manage billions of dollars in spend. "
            "Founded in 2020 by former Airbnb product leaders, Zip has created a new category "
            "in the $50B+ procurement TAM space. Valued at $2.2 billion.\n\n"
            "Fund: Tiger Global, Y Combinator | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Rujul Zaparde", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/rujulzaparde"},
            {"name": "Lu Cheng", "title": "CTO & Co-Founder", "linkedin": "https://linkedin.com/in/lucheng"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing BS or MS in Computer Science or related technical field (graduation Dec 2026 - Jun 2027)",
                    "Experience with web applications and API development",
                    "Familiarity with Python, JavaScript/TypeScript, React, or GraphQL",
                    "Strong problem-solving skills and interest in enterprise software",
                ],
                "description": (
                    "Software Engineer Intern at Zip (Summer 2026)\n\n"
                    "Build core products and features on Zip's procurement orchestration platform. "
                    "Collaborate with a team to solve technical challenges while receiving mentorship "
                    "and guidance. Stack includes Python, JavaScript/TypeScript, React, and GraphQL. "
                    "Previous interns built an internal AI bot using generative AI, Devbox (a "
                    "development environment in AWS cloud), and Virtual Card Auto Lock features. "
                    "Hybrid role in San Francisco.\n\n"
                    "Source: https://jobs.ashbyhq.com/zip/2bad03a8-4e98-480e-b8cb-bc65d36e429f"
                ),
            },
        ],
    },

    # ── 7. Confluent ──
    {
        "company_name": "Confluent",
        "email": "careers@confluent.io",
        "name": "Jay Kreps",
        "industry": "Data Infrastructure / Streaming",
        "company_size": "startup",
        "website": "https://confluent.io",
        "slug": "confluent",
        "description": (
            "Confluent provides a cloud-native data streaming platform built on Apache Kafka, "
            "enabling organizations to harness real-time data at scale. Founded by the creators "
            "of Apache Kafka at LinkedIn, Confluent powers data-in-motion for thousands of "
            "enterprises worldwide.\n\n"
            "Fund: Tiger Global | HQ: Mountain View, CA"
        ),
        "founders": [
            {"name": "Jay Kreps", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/jaykreps"},
            {"name": "Neha Narkhede", "title": "Co-Founder & Former CTO", "linkedin": ""},
            {"name": "Jun Rao", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/junrao"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 7200,
                "salary_max": 9800,
                "requirements": [
                    "Pursuing Bachelor's or Master's in CS, Math, or related technical field (graduation Dec 2026 - Aug 2027)",
                    "Strong knowledge of data structures and algorithms",
                    "Proficiency in Java/Scala, C, C++, or Go",
                    "Interest in distributed systems, data infrastructure, or streaming platforms",
                ],
                "description": (
                    "Software Engineering Intern at Confluent (Summer 2026)\n\n"
                    "Join a team focused on solving complex distributed systems and infrastructure "
                    "problems. Work on the Confluent data streaming platform built on Apache Kafka. "
                    "12-week internship starting in May/June with hybrid work model (3 days/week "
                    "in office). Includes $4,000 housing stipend and travel reimbursement.\n\n"
                    "Source: https://jobs.ashbyhq.com/confluent/d9ebd50b-967e-4f35-8ebd-f0ce2705136a"
                ),
            },
        ],
    },

    # ── 8. GitLab ──
    {
        "company_name": "GitLab",
        "email": "careers@gitlab.com",
        "name": "Sid Sijbrandij",
        "industry": "Developer Tools / DevOps",
        "company_size": "startup",
        "website": "https://gitlab.com",
        "slug": "gitlab",
        "description": (
            "GitLab provides a complete DevOps platform delivered as a single application for "
            "the entire software development lifecycle. From planning to monitoring, GitLab "
            "enables teams to collaborate on code, CI/CD, and security in one unified platform. "
            "GitLab is an all-remote company with team members in 65+ countries.\n\n"
            "Fund: Tiger Global (Series E) | HQ: All-Remote (San Francisco)"
        ),
        "founders": [
            {"name": "Sid Sijbrandij", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/sijbrandij"},
            {"name": "Dmitriy Zaporozhets", "title": "Co-Founder & Engineering Fellow", "linkedin": "https://linkedin.com/in/dzaporozhets"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, US",
                "salary_min": 7000,
                "salary_max": 9000,
                "requirements": [
                    "Experience coding with Ruby on Rails or JavaScript framework (Vue.js or similar)",
                    "Proficiency in English for remote async work environment",
                    "Ability to understand complex technical and architectural problems",
                    "Currently pursuing a degree in CS, Software Engineering, or related field",
                ],
                "description": (
                    "Software Engineer Intern at GitLab (Summer 2026)\n\n"
                    "Work on the GitLab product including open source and enterprise editions. "
                    "Join either a Frontend or Backend team on a mature stage product. Craft code "
                    "that meets internal standards for style, maintainability, and best practices "
                    "for a high-scale web environment. Ship small features and improvements with "
                    "guidance from mentors and managers. Fully remote position.\n\n"
                    "Source: https://handbook.gitlab.com/job-families/engineering/software-engineer-intern/"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DB OPERATIONS — Do not modify below this line
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def seed_new_company(session, company_data):
    """
    Create a new company with employer, organization, membership, and jobs.
    Skips entirely if company_name already exists.
    Returns number of jobs added.
    """
    company_name = company_data["company_name"]

    existing = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()
    if existing:
        print(f"  SKIP (already exists): {company_name}")
        return 0

    slug = company_data.get("slug", company_name.lower().replace(" ", "-"))
    employer_id = generate_cuid("e_")
    org_id = generate_cuid("o_")
    member_id = generate_cuid("tm_")

    # Create employer
    employer = Employer(
        id=employer_id,
        name=company_data["name"],
        company_name=company_name,
        email=company_data["email"],
        password=get_password_hash(f"{slug}Seed!2026"),
        industry=company_data.get("industry"),
        company_size=company_data.get("company_size", "startup"),
        is_verified=True,
    )
    session.add(employer)

    # Create organization
    organization = Organization(
        id=org_id,
        name=company_name,
        slug=slug,
        website=company_data.get("website"),
        industry=company_data.get("industry"),
        company_size=company_data.get("company_size", "startup"),
        description=company_data.get("description"),
        settings={"founders": company_data.get("founders", [])},
    )
    session.add(organization)

    # Link employer to organization
    membership = OrganizationMember(
        id=member_id,
        organization_id=org_id,
        employer_id=employer_id,
        role=OrganizationRole.OWNER,
    )
    session.add(membership)

    # Create jobs
    job_count = 0
    for job_data in company_data.get("jobs", []):
        job = Job(
            id=generate_cuid("j_"),
            title=job_data["title"],
            description=job_data["description"],
            vertical=job_data.get("vertical"),
            role_type=job_data.get("role_type"),
            requirements=job_data.get("requirements", []),
            location=job_data.get("location"),
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            employer_id=employer_id,
            is_active=True,
        )
        session.add(job)
        job_count += 1
        sal = f"${job_data.get('salary_min', 0):,}-${job_data.get('salary_max', 0):,}/mo"
        print(f"    + {job.title} | {job.location} | {sal}")

    return job_count


def add_jobs_to_existing(session, entry):
    """
    Add new jobs to a company that already exists in the DB.
    Deduplicates by job title. Returns number of jobs added.
    """
    company_name = entry["company_name"]
    employer = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()

    if not employer:
        print(f"  SKIP (not found in DB): {company_name}")
        return 0

    existing_titles = {
        j.title
        for j in session.query(Job).filter(Job.employer_id == employer.id).all()
    }

    job_count = 0
    for job_data in entry.get("jobs", []):
        if job_data["title"] in existing_titles:
            print(f"    SKIP (duplicate): {job_data['title']}")
            continue

        job = Job(
            id=generate_cuid("j_"),
            title=job_data["title"],
            description=job_data["description"],
            vertical=job_data.get("vertical"),
            role_type=job_data.get("role_type"),
            requirements=job_data.get("requirements", []),
            location=job_data.get("location"),
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            employer_id=employer.id,
            is_active=True,
        )
        session.add(job)
        job_count += 1
        sal = f"${job_data.get('salary_min', 0):,}-${job_data.get('salary_max', 0):,}/mo"
        print(f"    + NEW {job.title} | {job.location} | {sal}")

    return job_count


def main():
    if not COMPANIES and not ADDITIONAL_JOBS:
        print("ERROR: No companies or jobs defined. Fill in the COMPANIES list.")
        sys.exit(1)

    print("=" * 60)
    print(f"Seeding Intern Jobs — {FIRM_NAME}")
    print("=" * 60)

    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)

    total_companies = 0
    total_jobs = 0
    errors = []

    # Phase 1: New companies (one transaction per company for isolation)
    if COMPANIES:
        print(f"\n--- Phase 1: {len(COMPANIES)} New Companies ---")
        for company_data in COMPANIES:
            company_name = company_data["company_name"]
            session = Session()
            try:
                print(f"\n[{company_name}]")
                jobs_added = seed_new_company(session, company_data)
                session.commit()
                if jobs_added > 0:
                    total_companies += 1
                    total_jobs += jobs_added
                    print(f"  OK: {jobs_added} job(s)")
            except Exception as e:
                session.rollback()
                error_msg = f"{company_name}: {e}"
                errors.append(error_msg)
                print(f"  ERROR: {e}")
            finally:
                session.close()

    # Phase 2: Additional jobs for existing companies
    if ADDITIONAL_JOBS:
        print(f"\n--- Phase 2: Additional Jobs for {len(ADDITIONAL_JOBS)} Existing Companies ---")
        for entry in ADDITIONAL_JOBS:
            company_name = entry["company_name"]
            session = Session()
            try:
                print(f"\n[{company_name}]")
                jobs_added = add_jobs_to_existing(session, entry)
                session.commit()
                total_jobs += jobs_added
                if jobs_added:
                    print(f"  OK: {jobs_added} new job(s)")
                else:
                    print(f"  No new jobs needed")
            except Exception as e:
                session.rollback()
                error_msg = f"{company_name} (additional): {e}"
                errors.append(error_msg)
                print(f"  ERROR: {e}")
            finally:
                session.close()

    # Summary
    session = Session()
    db_employers = session.query(Employer).count()
    db_jobs = session.query(Job).count()
    session.close()

    print(f"\n{'=' * 60}")
    print(f"{FIRM_NAME} seed complete:")
    print(f"  New companies: {total_companies}")
    print(f"  New jobs:      {total_jobs}")
    if errors:
        print(f"  Errors:        {len(errors)}")
        for e in errors:
            print(f"    - {e}")
    print(f"\nDB totals: {db_employers} employers, {db_jobs} jobs")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
