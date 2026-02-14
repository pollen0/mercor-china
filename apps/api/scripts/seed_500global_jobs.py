#!/usr/bin/env python3
"""
Seed intern jobs from 500 Global (formerly 500 Startups) portfolio companies.

JOB BOARD: https://500.co/portfolio (no centralized job board)
FIRM: 500 Global
SCRIPT ID: 500global

Sources:
- https://500.co/portfolio (portfolio list)
- Individual company career pages (Greenhouse, Lever, Ashby)
- Levels.fyi, Glassdoor, ZipRecruiter for salary data
- Failory.com for 500 Global unicorn list

Note: 500 Global has 2900+ portfolio companies across 80+ countries.
This script focuses on notable US-based unicorn/late-stage portfolio companies
with confirmed internship programs.
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
FIRM_NAME = "500 Global"
SCRIPT_ID = "500global"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Talkdesk ──
    {
        "company_name": "Talkdesk",
        "email": "careers@talkdesk.com",
        "name": "Tiago Paiva",
        "industry": "AI / Customer Service",
        "company_size": "startup",
        "website": "https://www.talkdesk.com",
        "slug": "talkdesk",
        "description": (
            "Talkdesk is an AI-powered cloud contact center platform that helps "
            "enterprises deliver modern customer service. Valued at $10B, Talkdesk "
            "serves 1,800+ customers globally including IBM, Acxiom, and Trivago.\n\n"
            "Fund: 500 Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Tiago Paiva", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/tiagopaiva"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Python, Java, or JavaScript",
                    "Interest in cloud platforms and AI/ML applications",
                    "Strong problem-solving skills",
                ],
                "description": (
                    "Software Engineering Intern at Talkdesk. Work on the AI-powered "
                    "cloud contact center platform used by 1,800+ enterprise customers. "
                    "Build features for real-time voice AI, customer analytics, and "
                    "workflow automation.\n\n"
                    "Source: https://www.talkdesk.com/careers/"
                ),
            },
        ],
    },
    # ── Udemy ──
    {
        "company_name": "Udemy",
        "email": "careers@udemy.com",
        "name": "Eren Bali",
        "industry": "EdTech / Online Learning",
        "company_size": "startup",
        "website": "https://www.udemy.com",
        "slug": "udemy",
        "description": (
            "Udemy is the world's largest online learning marketplace with 75M+ "
            "learners and 220K+ courses. The platform connects students and "
            "professionals with expert instructors across technology, business, "
            "and creative skills.\n\n"
            "Fund: 500 Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Eren Bali", "title": "Co-Founder", "linkedin": ""},
            {"name": "Gagan Biyani", "title": "Co-Founder", "linkedin": ""},
            {"name": "Oktay Caglar", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8500,
                "salary_max": 9500,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Proficiency in Python, JavaScript/TypeScript, or Go",
                    "Experience with web frameworks (React, Django, or similar)",
                    "Available for hybrid work in San Francisco",
                ],
                "description": (
                    "Software Engineering Intern at Udemy. Build features for the "
                    "world's largest online learning marketplace serving 75M+ learners. "
                    "Work on personalization, search, content delivery, or platform "
                    "infrastructure. Hybrid role in San Francisco.\n\n"
                    "Source: https://about.udemy.com/careers/"
                ),
            },
        ],
    },
    # ── Credit Karma ──
    {
        "company_name": "Credit Karma",
        "email": "careers@creditkarma.com",
        "name": "Kenneth Lin",
        "industry": "Fintech / Personal Finance",
        "company_size": "startup",
        "website": "https://www.creditkarma.com",
        "slug": "credit-karma",
        "description": (
            "Credit Karma is a personal finance platform that provides free credit "
            "scores, reports, and insights to 130M+ members. Acquired by Intuit in "
            "2020, it continues operating as an independent brand helping consumers "
            "make smarter financial decisions.\n\n"
            "Fund: 500 Global | HQ: Charlotte, NC"
        ),
        "founders": [
            {"name": "Kenneth Lin", "title": "Founder & CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Charlotte, NC",
                "salary_min": 5400,
                "salary_max": 9700,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Strong programming skills in Java, Python, or Kotlin",
                    "Interest in fintech and personal finance products",
                    "Must be onsite minimum 3 days per week",
                    "Available for 12-week summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Credit Karma. Join the 12-week "
                    "summer internship program working on real-time financial data "
                    "systems, recommendation engines, and distributed systems serving "
                    "130M+ members. Includes housing stipend.\n\n"
                    "Source: https://www.creditkarma.com/careers/university"
                ),
            },
        ],
    },
    # ── LaunchDarkly ──
    {
        "company_name": "LaunchDarkly",
        "email": "careers@launchdarkly.com",
        "name": "Edith Harbaugh",
        "industry": "Developer Tools / Feature Management",
        "company_size": "startup",
        "website": "https://launchdarkly.com",
        "slug": "launchdarkly",
        "description": (
            "LaunchDarkly is the leading feature management platform used by teams "
            "at IBM, Microsoft, and Atlassian to safely deploy and manage features "
            "at scale. Valued at $3B, it processes trillions of feature flags daily.\n\n"
            "Fund: 500 Global | HQ: Oakland, CA"
        ),
        "founders": [
            {"name": "Edith Harbaugh", "title": "Co-Founder & CEO", "linkedin": ""},
            {"name": "John Kodumal", "title": "Co-Founder & CTO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Fullstack Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Oakland, CA",
                "salary_min": 7500,
                "salary_max": 8500,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with React, TypeScript, or Go",
                    "Interest in developer tools and feature management",
                    "Strong foundation in data structures and algorithms",
                ],
                "description": (
                    "Fullstack Software Engineering Intern at LaunchDarkly. Work on "
                    "the feature management platform trusted by thousands of engineering "
                    "teams worldwide. Build full-stack features using React, TypeScript, "
                    "and Go. Based in Oakland, CA.\n\n"
                    "Source: https://launchdarkly.com/careers/"
                ),
            },
        ],
    },
    # ── Aircall ──
    {
        "company_name": "Aircall",
        "email": "careers@aircall.io",
        "name": "Olivier Pailhes",
        "industry": "Communications / SaaS",
        "company_size": "startup",
        "website": "https://aircall.io",
        "slug": "aircall",
        "description": (
            "Aircall is a cloud-based phone and communication platform for modern "
            "businesses. With 100+ integrations including Salesforce and HubSpot, "
            "Aircall serves 19,000+ customers. Valued at $1B+.\n\n"
            "Fund: 500 Global | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Olivier Pailhes", "title": "Co-Founder & CEO", "linkedin": ""},
            {"name": "Jonathan Anguelov", "title": "Co-Founder & COO", "linkedin": ""},
            {"name": "Xavier Durand", "title": "Co-Founder", "linkedin": ""},
            {"name": "Pierre-Baptiste Bechu", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Proficiency in Python, JavaScript, or Ruby",
                    "Interest in telecommunications and SaaS platforms",
                    "Available for summer 2026 internship in NYC",
                ],
                "description": (
                    "Software Engineering Intern at Aircall. Build features for the "
                    "cloud phone platform used by 19,000+ businesses. Work on real-time "
                    "voice systems, CRM integrations, and AI-powered call analytics.\n\n"
                    "Source: https://aircall.io/careers/"
                ),
            },
        ],
    },
    # ── Algolia ──
    {
        "company_name": "Algolia",
        "email": "careers@algolia.com",
        "name": "Nicolas Dessaigne",
        "industry": "Search / AI / Developer Tools",
        "company_size": "startup",
        "website": "https://www.algolia.com",
        "slug": "algolia",
        "description": (
            "Algolia is the AI-powered search and discovery platform used by 17,000+ "
            "customers including Stripe, Twitch, and Lacoste. Processes 1.7 trillion "
            "searches per year with sub-100ms response times. Valued at $2.25B.\n\n"
            "Fund: 500 Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Nicolas Dessaigne", "title": "Co-Founder", "linkedin": ""},
            {"name": "Julien Lemoine", "title": "Co-Founder & CTO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5500,
                "salary_max": 8000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with C++, Go, Python, or JavaScript",
                    "Interest in search algorithms and distributed systems",
                    "Strong CS fundamentals",
                ],
                "description": (
                    "Software Engineering Intern at Algolia. Work on the search and "
                    "discovery platform processing 1.7T+ searches/year. Contribute to "
                    "search indexing, ranking algorithms, or developer SDKs.\n\n"
                    "Source: https://www.algolia.com/careers/"
                ),
            },
        ],
    },
    # ── Intercom ──
    {
        "company_name": "Intercom",
        "email": "careers@intercom.com",
        "name": "Eoghan McCabe",
        "industry": "AI / Customer Communications",
        "company_size": "startup",
        "website": "https://www.intercom.com",
        "slug": "intercom",
        "description": (
            "Intercom is the AI-first customer service platform trusted by 25,000+ "
            "businesses including Amazon, Meta, and Microsoft. Its AI agent Fin "
            "resolves 50%+ of support conversations instantly. Valued at $1.28B.\n\n"
            "Fund: 500 Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Eoghan McCabe", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/eoghanmccabe"},
            {"name": "Des Traynor", "title": "Co-Founder & Chief Strategy Officer", "linkedin": ""},
            {"name": "Ciaran Lee", "title": "Co-Founder", "linkedin": ""},
            {"name": "David Barrett", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Ruby, Python, or JavaScript/TypeScript",
                    "Interest in AI, NLP, or customer communication platforms",
                    "Strong problem-solving and communication skills",
                ],
                "description": (
                    "Software Engineering Intern at Intercom. Build features for the "
                    "AI-first customer service platform used by 25,000+ businesses. "
                    "Work on AI agent capabilities, messaging infrastructure, or "
                    "product analytics.\n\n"
                    "Source: https://www.intercom.com/careers"
                ),
            },
        ],
    },
    # ── The RealReal ──
    {
        "company_name": "The RealReal",
        "email": "careers@therealreal.com",
        "name": "Julie Wainwright",
        "industry": "Luxury Resale / E-commerce",
        "company_size": "startup",
        "website": "https://www.therealreal.com",
        "slug": "the-realreal",
        "description": (
            "The RealReal is the world's largest online marketplace for authenticated "
            "luxury consignment. Publicly traded (NASDAQ: REAL), it offers 20+ "
            "luxury categories including fashion, fine jewelry, watches, and art.\n\n"
            "Fund: 500 Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Julie Wainwright", "title": "Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Analytics Engineering Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 3600,
                "salary_max": 4300,
                "requirements": [
                    "Pursuing a BS/MS in Data Science, Statistics, or related field",
                    "Experience with SQL and Python",
                    "Interest in data pipelines and analytics engineering",
                    "Available for 10-week summer internship",
                ],
                "description": (
                    "Analytics Engineering Intern at The RealReal. Join the 10-week "
                    "paid summer internship (June-August). Work on data pipelines, "
                    "analytics dashboards, and ML models for the world's largest "
                    "authenticated luxury resale marketplace.\n\n"
                    "Source: https://careers.therealreal.com/"
                ),
            },
            {
                "title": "Product Analytics Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_ANALYST,
                "location": "San Francisco, CA",
                "salary_min": 3600,
                "salary_max": 4300,
                "requirements": [
                    "Pursuing a BS/MS in Business Analytics, Statistics, or related field",
                    "Strong SQL skills and experience with data visualization tools",
                    "Interest in e-commerce and marketplace analytics",
                    "Available for 10-week summer internship",
                ],
                "description": (
                    "Product Analytics Intern at The RealReal. Analyze user behavior, "
                    "marketplace trends, and product performance for the luxury "
                    "consignment platform. Present findings to senior executives.\n\n"
                    "Source: https://careers.therealreal.com/"
                ),
            },
        ],
    },
    # ── Lucid Software ──
    {
        "company_name": "Lucid Software",
        "email": "careers@lucid.co",
        "name": "Karl Sun",
        "industry": "Visual Collaboration / SaaS",
        "company_size": "startup",
        "website": "https://lucid.co",
        "slug": "lucid-software",
        "description": (
            "Lucid Software builds visual collaboration tools including Lucidchart "
            "and Lucidspark, used by 99% of Fortune 500 companies. The platform "
            "helps teams brainstorm, design, and build the future together.\n\n"
            "Fund: 500 Global | HQ: Salt Lake City, UT"
        ),
        "founders": [
            {"name": "Karl Sun", "title": "Co-Founder & CEO", "linkedin": ""},
            {"name": "Ben Dilts", "title": "Co-Founder & CTO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Salt Lake City, UT",
                "salary_min": 5000,
                "salary_max": 5500,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Java, TypeScript, or Kotlin",
                    "Interest in building web applications at scale",
                    "Available for summer internship in Salt Lake City",
                ],
                "description": (
                    "Software Engineering Intern at Lucid Software. Build world-class "
                    "web applications for Lucidchart and Lucidspark used by Fortune 500 "
                    "companies. Includes workshops, hackathons, and executive lectures. "
                    "$30/hour in Salt Lake City.\n\n"
                    "Source: https://lucid.co/careers/internships"
                ),
            },
        ],
    },
    # ── Nextdoor ──
    {
        "company_name": "Nextdoor",
        "email": "careers@nextdoor.com",
        "name": "Nirav Tolia",
        "industry": "Social Networking / Local Community",
        "company_size": "startup",
        "website": "https://nextdoor.com",
        "slug": "nextdoor",
        "description": (
            "Nextdoor is the neighborhood network connecting neighbors and local "
            "businesses across 335,000+ neighborhoods globally. Publicly traded "
            "(NYSE: KIND), it's the platform where communities connect and share.\n\n"
            "Fund: 500 Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Nirav Tolia", "title": "Co-Founder & CEO", "linkedin": ""},
            {"name": "Sarah Leary", "title": "Co-Founder", "linkedin": ""},
            {"name": "Prakash Janakiraman", "title": "Co-Founder", "linkedin": ""},
            {"name": "David Wiesen", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Python, Java, or JavaScript",
                    "Graduation between Fall 2026 and Summer 2027",
                    "Available for 12-week hybrid internship in San Francisco",
                ],
                "description": (
                    "Software Engineering Intern at Nextdoor. Join the 12-week program "
                    "building features for the neighborhood network connecting 335K+ "
                    "communities. Hybrid work, $48.75/hour + $1,000 housing stipend.\n\n"
                    "Source: https://about.nextdoor.com/careers/"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "San Francisco, CA",
                "salary_min": 8000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a BS/MS in Data Science, Statistics, or related field",
                    "Strong Python and SQL skills",
                    "Experience with statistical modeling or machine learning",
                    "Graduation between Fall 2026 and Summer 2027",
                ],
                "description": (
                    "Data Science Intern at Nextdoor. Analyze community engagement "
                    "patterns, build recommendation models, and derive insights for "
                    "the neighborhood network. $48.75/hour + housing stipend.\n\n"
                    "Source: https://about.nextdoor.com/careers/"
                ),
            },
        ],
    },
    # ── Twilio ──
    {
        "company_name": "Twilio",
        "email": "careers@twilio.com",
        "name": "Jeff Lawson",
        "industry": "Communications Platform / CPaaS",
        "company_size": "startup",
        "website": "https://www.twilio.com",
        "slug": "twilio",
        "description": (
            "Twilio is the cloud communications platform powering voice, messaging, "
            "and video for millions of developers and businesses. Publicly traded "
            "(NYSE: TWLO), Twilio's APIs are used by companies like Airbnb, Uber, "
            "and Instacart.\n\n"
            "Fund: 500 Global | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Jeff Lawson", "title": "Co-Founder", "linkedin": ""},
            {"name": "Evan Cooke", "title": "Co-Founder", "linkedin": ""},
            {"name": "John Wolthuis", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7300,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Java, Python, C++, or Go",
                    "Interest in distributed systems and real-time communications",
                    "Available for 8-week summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Twilio. Join the 8-week program "
                    "designing, developing, and operating software for the leading "
                    "cloud communications platform. Work on distributed systems "
                    "solving resiliency, latency, and quality challenges.\n\n"
                    "Source: https://www.twilio.com/en-us/company/careers"
                ),
            },
        ],
    },
    # ── GitLab ──
    {
        "company_name": "GitLab",
        "email": "careers@gitlab.com",
        "name": "Sid Sijbrandij",
        "industry": "DevOps / Developer Platform",
        "company_size": "startup",
        "website": "https://about.gitlab.com",
        "slug": "gitlab",
        "description": (
            "GitLab is the most comprehensive AI-powered DevSecOps platform, used "
            "by 30M+ registered users. Publicly traded (NASDAQ: GTLB), GitLab "
            "provides a single application for the entire software development "
            "lifecycle.\n\n"
            "Fund: 500 Global | HQ: San Francisco, CA (all-remote)"
        ),
        "founders": [
            {"name": "Sid Sijbrandij", "title": "Co-Founder", "linkedin": ""},
            {"name": "Dmitriy Zaporozhets", "title": "Co-Founder & Engineering Fellow", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, US",
                "salary_min": 7000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Ruby, Go, or JavaScript/TypeScript",
                    "Familiarity with Git and CI/CD concepts",
                    "Comfortable working in an all-remote environment",
                ],
                "description": (
                    "Software Engineering Intern at GitLab. Contribute to the open-source "
                    "DevSecOps platform used by 30M+ developers. Work on GitLab's product "
                    "features, CI/CD pipelines, or AI-powered development tools. Fully "
                    "remote position.\n\n"
                    "Source: https://about.gitlab.com/jobs/"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    # Mercury is a 500 Global portfolio company already in the DB
]


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
