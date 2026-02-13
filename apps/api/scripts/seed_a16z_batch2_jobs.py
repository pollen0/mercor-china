#!/usr/bin/env python3
"""
Seed intern jobs from a16z (Andreessen Horowitz) portfolio companies — Batch 2.

Batch 1 (seed_a16z_jobs.py) covered 17 companies with 20 jobs.
This batch adds companies discovered from deeper search of jobs.a16z.com.

Usage:
    cd apps/api
    python -m scripts.seed_a16z_batch2_jobs

Source: jobs.a16z.com, individual company career pages (Feb 2026)
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


FIRM_NAME = "a16z (Batch 2)"
SCRIPT_ID = "a16z_batch2"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Airbnb ──
    {
        "company_name": "Airbnb",
        "email": "careers@airbnb.com",
        "name": "Brian Chesky",
        "industry": "Travel / Hospitality / Marketplace",
        "company_size": "startup",
        "website": "https://airbnb.com",
        "slug": "airbnb",
        "description": (
            "Airbnb is a global online marketplace for lodging, primarily homestays for "
            "vacation rentals, and tourism activities. The platform connects millions of "
            "hosts with travelers worldwide.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Brian Chesky", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/brianchesky"},
            {"name": "Joe Gebbia", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/joegebbia"},
            {"name": "Nathan Blecharczyk", "title": "Co-Founder & CSO", "linkedin": "https://linkedin.com/in/blecharczyk"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8500,
                "salary_max": 8500,
                "requirements": [
                    "Enrolled in Bachelor's or Doctorate program with at least one semester remaining",
                    "Strong CS fundamentals: data structures, algorithms",
                    "Proficiency in Java, Scala, Ruby, C++, SQL, JavaScript, or Swift",
                    "US work authorization required (CPT/OPT accepted)",
                ],
                "description": (
                    "Software Engineering Intern at Airbnb. 12-week program with potential "
                    "Employee Travel Credits. Work on real product features used by millions.\n\n"
                    "Source: https://careers.airbnb.com/positions/7453837/"
                ),
            },
        ],
    },
    # ── Tanium ──
    {
        "company_name": "Tanium",
        "email": "careers@tanium.com",
        "name": "Orion Hindawi",
        "industry": "Cybersecurity / Endpoint Management",
        "company_size": "startup",
        "website": "https://tanium.com",
        "slug": "tanium",
        "description": (
            "Tanium provides endpoint management and security platform that gives "
            "enterprises real-time visibility and control over all endpoints. Serves "
            "the world's largest organizations including half of the Fortune 100.\n\n"
            "Fund: a16z | HQ: Kirkland, WA"
        ),
        "founders": [
            {"name": "Orion Hindawi", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/orionhindawi"},
            {"name": "David Hindawi", "title": "Executive Chairman & Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Emeryville, CA",
                "salary_min": 9500,
                "salary_max": 10400,
                "requirements": [
                    "Graduating Spring 2027 or Fall 2026",
                    "Experience with backend or frontend development",
                    "Strong communication skills",
                    "US work authorization required",
                ],
                "description": (
                    "Software Engineering Intern at Tanium. June 8 - August 14, 2026. "
                    "Includes housing stipend, 401k matching, and communications allowance. "
                    "Also available in Addison TX, Morrisville NC, Durham NC.\n\n"
                    "Source: https://builtin.com/job/software-engineering-intern/3201224"
                ),
            },
            {
                "title": "AI Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Durham, NC",
                "salary_min": 9500,
                "salary_max": 10400,
                "requirements": [
                    "Currently enrolled Master's/PhD in Statistics, ML, or related field",
                    "3.5+ GPA",
                    "Proficiency in Python and ML frameworks (PyTorch, scikit-learn, TensorFlow)",
                    "Experience with large datasets",
                    "US work authorization required",
                ],
                "description": (
                    "AI Research Intern at Tanium. Work on ML research for endpoint security. "
                    "Also available in Emeryville, CA. Includes housing stipend + 401k matching.\n\n"
                    "Source: https://www.glassdoor.com/job-listing/ai-research-intern-tanium-JV_IC1138697_KO0,18_KE19,25.htm"
                ),
            },
            {
                "title": "Product Management Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "Addison, TX",
                "salary_min": 7800,
                "salary_max": 11300,
                "requirements": [
                    "Currently enrolled in graduate degree (MBA or similar)",
                    "Background in CS or related technical field",
                    "US work authorization required",
                ],
                "description": (
                    "Product Management Intern at Tanium. June 8 - August 14, 2026. "
                    "Also available in Durham NC and Emeryville CA. Includes housing stipend.\n\n"
                    "Source: https://prosple.com/graduate-employers/tanium-usa/jobs-internships/product-management-intern-addison-tx"
                ),
            },
        ],
    },
    # ── Nuro ──
    {
        "company_name": "Nuro",
        "email": "careers@nuro.ai",
        "name": "Jiajun Zhu",
        "industry": "Autonomous Vehicles / Robotics / Delivery",
        "company_size": "startup",
        "website": "https://nuro.ai",
        "slug": "nuro",
        "description": (
            "Nuro builds autonomous delivery vehicles for local commerce. Their "
            "custom-designed robots deliver groceries, prescriptions, and other goods "
            "without a human driver. Backed by SoftBank, a16z, and others.\n\n"
            "Fund: a16z | HQ: Mountain View, CA"
        ),
        "founders": [
            {"name": "Jiajun Zhu", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/jiajunzhu"},
            {"name": "Dave Ferguson", "title": "Co-Founder & President", "linkedin": "https://linkedin.com/in/dave-ferguson-a4a83b2"},
        ],
        "jobs": [
            {
                "title": "Embedded Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Mountain View, CA",
                "salary_min": 9000,
                "salary_max": 11000,
                "requirements": [
                    "Current BS or MS candidate in CS, EE, Robotics, or related field",
                    "Graduating in or before December 2026",
                    "Experience with embedded systems and real-time software",
                ],
                "description": (
                    "Embedded Software Engineer Intern at Nuro. Design and develop critical "
                    "code for Nuro's autonomous robot software — sensing and movement systems.\n\n"
                    "Source: https://builtin.com/job/embedded-software-engineer-intern/4217601"
                ),
            },
            {
                "title": "Software Engineer, AI Platform Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Mountain View, CA",
                "salary_min": 10000,
                "salary_max": 11500,
                "requirements": [
                    "Current BS or MS in CS, EE, Robotics, or related field",
                    "Graduating December 2026 or later",
                    "Interest in ML infrastructure and autonomous driving",
                ],
                "description": (
                    "AI Platform Intern at Nuro. Work on ML infrastructure, data platforms, "
                    "and simulation for autonomous driving. 12-16 week internship.\n\n"
                    "Source: https://climatebase.org/job/66128594/software-engineer-ai-platform---intern"
                ),
            },
        ],
    },
    # ── Applied Intuition ──
    {
        "company_name": "Applied Intuition",
        "email": "careers@appliedintuition.com",
        "name": "Qasar Younis",
        "industry": "Autonomous Vehicles / Simulation / Software",
        "company_size": "startup",
        "website": "https://appliedintuition.com",
        "slug": "applied-intuition",
        "description": (
            "Applied Intuition provides simulation and infrastructure software for "
            "autonomous vehicle development. Their tools help teams create thousands of "
            "scenarios in minutes, run simulations at scale, and validate algorithms.\n\n"
            "Fund: a16z | HQ: Mountain View, CA"
        ),
        "founders": [
            {"name": "Qasar Younis", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/qasaryounis"},
            {"name": "Peter Ludwig", "title": "CTO & Co-Founder", "linkedin": "https://linkedin.com/in/peter-ludwig-61283533"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Mountain View, CA",
                "salary_min": 9000,
                "salary_max": 12000,
                "requirements": [
                    "Strong engineering skills — designing elegant solutions to difficult problems",
                    "Experience with full-stack, infrastructure, robotics, or graphics",
                    "Interest in autonomy and simulation",
                ],
                "description": (
                    "Software Engineer Summer Intern at Applied Intuition. Work across the "
                    "suite of products tackling full-stack, infrastructure, robotics, and "
                    "graphics challenges for autonomous vehicle simulation.\n\n"
                    "Source: https://startup.jobs/software-engineer-summer-intern-applied-intuition-3805871"
                ),
            },
        ],
    },
    # ── Relativity Space ──
    {
        "company_name": "Relativity Space",
        "email": "careers@relativityspace.com",
        "name": "Tim Ellis",
        "industry": "Aerospace / 3D Printing / Rockets",
        "company_size": "startup",
        "website": "https://relativityspace.com",
        "slug": "relativity-space",
        "description": (
            "Relativity Space is building the world's first 3D-printed rockets. Their "
            "Stargate factory uses autonomous robotics and AI to 3D-print entire rocket "
            "structures, dramatically reducing parts count and lead times.\n\n"
            "Fund: a16z | HQ: Long Beach, CA"
        ),
        "founders": [
            {"name": "Tim Ellis", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/timothyellis"},
            {"name": "Jordan Noone", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/jordannoone"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Long Beach, CA",
                "salary_min": 5400,
                "salary_max": 6600,
                "requirements": [
                    "Currently pursuing BS/MS in Computer Science or related field",
                    "Strong programming fundamentals",
                    "Interest in aerospace and manufacturing automation",
                ],
                "description": (
                    "Software Engineer Intern at Relativity Space. Work on software for "
                    "3D-printed rockets including propulsion, avionics, and manufacturing. "
                    "Competitive salary + equity.\n\n"
                    "Source: https://www.relativityspace.com/internship-positions"
                ),
            },
        ],
    },
    # ── Ironclad ──
    {
        "company_name": "Ironclad",
        "email": "careers@ironcladapp.com",
        "name": "Jason Boehmig",
        "industry": "Legal Tech / Contract Management / AI",
        "company_size": "startup",
        "website": "https://ironcladapp.com",
        "slug": "ironclad",
        "description": (
            "Ironclad is a digital contracting platform that helps legal teams manage "
            "contracts end-to-end with AI-powered workflows. Used by companies like "
            "Mastercard, L'Oreal, and OpenAI.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Jason Boehmig", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/jasonboehmig"},
            {"name": "Cai GoGwilt", "title": "CTO & Co-Founder", "linkedin": "https://linkedin.com/in/caigogwilt"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7500,
                "salary_max": 10000,
                "requirements": [
                    "Demonstrated experience shipping code through projects, internships, or open-source",
                    "Strong problem-solving skills and bias toward action",
                    "Proficiency in TypeScript, Java, and/or Python preferred",
                    "Willingness to learn about contracts, legal workflows, and AI",
                ],
                "description": (
                    "Software Engineer Intern at Ironclad. ~12 weeks, full-time, hybrid "
                    "(in-office 2x/week). Also available in NYC. Work on AI-powered contract "
                    "management tools.\n\n"
                    "Source: https://jobs.ashbyhq.com/ironcladhq/95ae3b0a-a061-4323-926a-7fa308b59387"
                ),
            },
        ],
    },
    # ── Circle ──
    {
        "company_name": "Circle",
        "email": "careers@circle.com",
        "name": "Jeremy Allaire",
        "industry": "Fintech / Crypto / Payments",
        "company_size": "startup",
        "website": "https://circle.com",
        "slug": "circle",
        "description": (
            "Circle is the issuer of USDC, one of the world's largest stablecoins. "
            "The company builds infrastructure for digital currency payments and "
            "financial applications used globally.\n\n"
            "Fund: a16z | HQ: Boston / Remote"
        ),
        "founders": [
            {"name": "Jeremy Allaire", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/jeremyallaire"},
            {"name": "Sean Neville", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/seanneville"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 7800,
                "salary_max": 7800,
                "requirements": [
                    "Pursuing BS/MS in CS, Software Engineering, or related field (graduation 2026-2027)",
                    "Experience with object-oriented programming (Java, Go, Python)",
                    "Familiarity with RESTful APIs and backend development",
                    "Interest in blockchain, distributed systems, or fintech",
                ],
                "description": (
                    "Software Engineer Intern at Circle. 12 weeks, May 26 - August 14, 2026. "
                    "Remote-first with 3 required in-person experiences including Final Showcase "
                    "Week at NYC HQ (One World Trade Center).\n\n"
                    "Source: https://careers.circle.com/us/en/job/CIICIRUSJR100188EGEXTERNALENUS/Software-Engineer-Intern-Summer-2026"
                ),
            },
        ],
    },
    # ── Samsara (not in DB from batch 1) ──
    # Note: Samsara IS already in DB — moved to ADDITIONAL_JOBS

    # ── Snyk ──
    {
        "company_name": "Snyk",
        "email": "careers@snyk.io",
        "name": "Guy Podjarny",
        "industry": "Developer Security / DevSecOps",
        "company_size": "startup",
        "website": "https://snyk.io",
        "slug": "snyk",
        "description": (
            "Snyk is a developer-first security platform that helps developers find and "
            "fix vulnerabilities in code, dependencies, containers, and infrastructure as "
            "code. Used by millions of developers worldwide.\n\n"
            "Fund: a16z | HQ: Boston, MA"
        ),
        "founders": [
            {"name": "Guy Podjarny", "title": "Founder & President", "linkedin": "https://linkedin.com/in/guypod"},
            {"name": "Assaf Hefetz", "title": "Co-Founder", "linkedin": ""},
            {"name": "Danny Grander", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Security Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Boston, MA",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Currently pursuing a degree in CS or related field",
                    "Interest in cybersecurity",
                    "Strong problem-solving skills",
                ],
                "description": (
                    "Security Engineer Intern at Snyk. Work on vulnerability assessments, "
                    "threat modeling, incident response, security tooling, and automation "
                    "script development. Hybrid in Boston.\n\n"
                    "Source: https://boards.greenhouse.io/snyk/jobs/7715204002"
                ),
            },
        ],
    },
    # ── Substack ──
    {
        "company_name": "Substack",
        "email": "careers@substack.com",
        "name": "Chris Best",
        "industry": "Media / Publishing / Newsletter Platform",
        "company_size": "startup",
        "website": "https://substack.com",
        "slug": "substack",
        "description": (
            "Substack is a platform that lets independent writers and podcasters publish "
            "directly to their audience and get paid through subscriptions. Hosts thousands "
            "of publications across news, culture, tech, and more.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Chris Best", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/hamishm"},
            {"name": "Hamish McKenzie", "title": "Co-Founder", "linkedin": ""},
            {"name": "Jairaj Sethi", "title": "Co-Founder & CTO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Research Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Interest in product research and user experience",
                    "Ability to synthesize qualitative feedback",
                    "Strong communication skills",
                ],
                "description": (
                    "Research Intern at Substack. 12 weeks, June-August 2026. Support the "
                    "Product Researcher on the design team. Collect pre/post-launch feedback, "
                    "set up beta groups, conduct user interviews, and help prioritize product "
                    "improvements.\n\n"
                    "Source: https://startup.jobs/research-intern-substack-2-3198555"
                ),
            },
        ],
    },
    # ── Greenlight ──
    {
        "company_name": "Greenlight",
        "email": "careers@greenlight.com",
        "name": "Timothy Sheehan",
        "industry": "Fintech / Family Finance / Banking",
        "company_size": "startup",
        "website": "https://greenlight.com",
        "slug": "greenlight",
        "description": (
            "Greenlight is a family fintech company offering a debit card for kids, "
            "investing for families, and financial literacy tools. Serves millions of "
            "parents and kids across the US.\n\n"
            "Fund: a16z | HQ: Atlanta, GA"
        ),
        "founders": [
            {"name": "Timothy Sheehan", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/timsheehan"},
            {"name": "Johnson Cook", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/johnsoncook"},
        ],
        "jobs": [
            {
                "title": "Product Management Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "Atlanta, GA",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Currently enrolled college student",
                    "Interest in product management and fintech",
                    "Strong analytical and communication skills",
                ],
                "description": (
                    "Product Management Intern at Greenlight. Cross-functional work with "
                    "designers, engineers, data scientists. End-to-end product feature delivery "
                    "and user research exposure.\n\n"
                    "Source: https://jobs.lever.co/greenlight/ffa2e907-11af-4ba3-baa4-0118dc0bb3ed"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — For companies already in the DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    # ── Roblox (has 1 SWE intern) — add PM + Data Science ──
    {
        "company_name": "Roblox",
        "jobs": [
            {
                "title": "Product Management Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "San Mateo, CA",
                "salary_min": 10700,
                "salary_max": 10700,
                "requirements": [
                    "Interest in gaming, social platforms, or virtual worlds",
                    "Strong analytical and communication skills",
                    "Ability to conduct product research and define requirements",
                ],
                "description": (
                    "Product Management Intern at Roblox. Assist with product development by "
                    "conducting research, defining projects, writing requirements, analyzing "
                    "metrics, and collaborating with cross-functional teams.\n\n"
                    "Source: https://www.builtinsf.com/job/summer-2026-product-management-intern/7027450"
                ),
            },
            {
                "title": "Data Scientist PhD Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "San Mateo, CA",
                "salary_min": 10700,
                "salary_max": 10700,
                "requirements": [
                    "PhD candidate in Statistics, Economics, CS, or related quantitative field",
                    "1+ year experience in causal inference, ML, or experiment design",
                    "Proficiency in SQL, Python, or R",
                ],
                "description": (
                    "Data Scientist PhD Intern at Roblox. Work on causal inference and ML "
                    "to drive product decisions across the Roblox platform serving 70M+ daily users.\n\n"
                    "Source: https://careers.roblox.com/jobs/7299325"
                ),
            },
        ],
    },
    # ── Scale AI (has 1 SWE intern) — add ML Research ──
    {
        "company_name": "Scale AI",
        "jobs": [
            {
                "title": "ML Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8000,
                "salary_max": 11000,
                "requirements": [
                    "Enrolled in BS/MS/PhD with focus on ML, Deep Learning, NLP, or Computer Vision",
                    "Graduation date Fall 2026 or Spring 2027",
                    "Track record of research publications on LLMs, NLP, agents, safety, or evaluation",
                ],
                "description": (
                    "ML Research Intern at Scale AI. Work on frontier model post-training, "
                    "scalable oversight, synthetic data pipelines, red teaming, and evaluation. "
                    "Push the boundaries of what's possible with AI systems.\n\n"
                    "Source: https://scale.com/careers/4606060005"
                ),
            },
        ],
    },
    # ── Notion (has SWE + AI intern) — add Mobile + Data Science ──
    {
        "company_name": "Notion",
        "jobs": [
            {
                "title": "Software Engineer, Mobile Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9900,
                "salary_max": 10600,
                "requirements": [
                    "Pursuing BS/MS in CS, Engineering, or related field",
                    "Graduating before July 2027",
                    "Experience with mobile development (iOS or Android)",
                ],
                "description": (
                    "Mobile Software Engineer Intern at Notion. 12-week internship, paired "
                    "with a mentor. Work on Notion's mobile apps used by millions.\n\n"
                    "Source: https://jobs.ashbyhq.com/notion/1bda6206-2258-4c1f-a585-ef31ee56f1d4"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "New York, NY",
                "salary_min": 9900,
                "salary_max": 10600,
                "requirements": [
                    "Pursuing degree in Data Science, Statistics, CS, or related field",
                    "Experience with Python and SQL",
                    "Strong analytical and quantitative skills",
                ],
                "description": (
                    "Data Science Intern at Notion. Work on data-driven insights for one of "
                    "the fastest-growing productivity platforms.\n\n"
                    "Source: https://www.builtinnyc.com/job/data-science-intern-winter-or-summer-2026/7054740"
                ),
            },
        ],
    },
    # ── Stripe (has 2 SWE interns) — add PhD ML + Data Analyst ──
    {
        "company_name": "Stripe",
        "jobs": [
            {
                "title": "PhD Machine Learning Engineer Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10300,
                "salary_max": 10300,
                "requirements": [
                    "PhD candidate in Machine Learning, Statistics, or related field",
                    "Experience with foundation models, NLP, or applied ML",
                    "Strong Python skills",
                ],
                "description": (
                    "PhD ML Engineer Intern at Stripe. Work on foundation models and ML systems "
                    "that enhance Stripe's products across payments, risk, and data science.\n\n"
                    "Source: https://stripe.com/jobs/listing/phd-machine-learning-engineer-intern/7216664"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DB OPERATIONS — Do not modify below this line
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def seed_new_company(session, company_data):
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

    membership = OrganizationMember(
        id=member_id,
        organization_id=org_id,
        employer_id=employer_id,
        role=OrganizationRole.OWNER,
    )
    session.add(membership)

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
