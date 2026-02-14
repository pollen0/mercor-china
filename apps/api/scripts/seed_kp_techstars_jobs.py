#!/usr/bin/env python3
"""
Seed intern jobs from Kleiner Perkins and Techstars portfolio companies.

Kleiner Perkins is a top-tier Silicon Valley VC firm with a dedicated Fellows program.
Techstars is the world's largest pre-seed investor and accelerator. Both have portfolio
companies large enough for formal intern programs.

SCRIPT ID: kp_techstars
RUN: cd apps/api && python -m scripts.seed_kp_techstars_jobs
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
FIRM_NAME = "Kleiner Perkins + Techstars"
SCRIPT_ID = "kp_techstars"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ─────────────────────────────────────────────
    # KLEINER PERKINS PORTFOLIO
    # ─────────────────────────────────────────────

    # ── 1. Duolingo (KP) ──
    {
        "company_name": "Duolingo",
        "email": "careers@duolingo.com",
        "name": "Luis von Ahn",
        "industry": "EdTech / Consumer",
        "company_size": "startup",
        "website": "https://duolingo.com",
        "slug": "duolingo",
        "description": (
            "Duolingo is the world's most popular language-learning platform with over 100 million "
            "monthly active users. Uses AI and gamification to make language education accessible "
            "and engaging. Public on NASDAQ (DUOL) with ~1,000 employees. KP Fellows partner.\n\n"
            "Source: Kleiner Perkins Portfolio | HQ: Pittsburgh, PA"
        ),
        "founders": [
            {"name": "Luis von Ahn", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/luis-von-ahn-duolingo"},
            {"name": "Severin Hacker", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/severinhacker"},
        ],
        "jobs": [
            {
                "title": "Software Engineer, Thrive Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Pittsburgh, PA",
                "salary_min": 8000,
                "salary_max": 10000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Python, Kotlin, Swift, or similar",
                    "Experience with mobile or web development",
                    "Interest in education technology and gamification",
                ],
                "description": (
                    "Software Engineer, Thrive Intern at Duolingo — Summer 2026\n\n"
                    "Join Duolingo's 10-week Thrive Internship program in Pittsburgh. Work on "
                    "features used by 100M+ monthly learners. Contribute to the platform that's "
                    "making language education free and accessible worldwide.\n\n"
                    "Source: Kleiner Perkins Fellows / Duolingo Careers"
                ),
            },
            {
                "title": "Data Scientist Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Pittsburgh, PA",
                "salary_min": 8000,
                "salary_max": 10400,
                "requirements": [
                    "Currently pursuing a degree in Data Science, Statistics, CS, or related field",
                    "Strong skills in Python, SQL, and statistical analysis",
                    "Experience with A/B testing, causal inference, or ML",
                    "Interest in education, language learning, or consumer products",
                ],
                "description": (
                    "Data Scientist Intern at Duolingo — Summer 2026\n\n"
                    "Apply data science to improve learning outcomes for 100M+ users. Run A/B tests, "
                    "build models, and uncover insights that shape the product experience. "
                    "$50-52/hr compensation.\n\n"
                    "Source: Kleiner Perkins Fellows / Duolingo Careers"
                ),
            },
            {
                "title": "Product Design, Thrive Intern (Summer 2026)",
                "vertical": Vertical.DESIGN,
                "role_type": RoleType.PRODUCT_DESIGNER,
                "location": "Pittsburgh, PA",
                "salary_min": 7500,
                "salary_max": 9500,
                "requirements": [
                    "Currently pursuing a degree in Design, HCI, or related field",
                    "Strong portfolio demonstrating product design skills",
                    "Proficiency with Figma or similar design tools",
                    "Interest in gamification, education, and consumer products",
                ],
                "description": (
                    "Product Design, Thrive Intern at Duolingo — Summer 2026\n\n"
                    "Design features for the world's most popular language-learning app. "
                    "10-week Thrive program in Pittsburgh working on product experience "
                    "used by millions of learners daily.\n\n"
                    "Source: Kleiner Perkins Fellows / Duolingo Careers"
                ),
            },
            {
                "title": "Associate Product Manager Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.ASSOCIATE_PM,
                "location": "Pittsburgh, PA",
                "salary_min": 7500,
                "salary_max": 9500,
                "requirements": [
                    "Currently pursuing a degree in Business, CS, or related field",
                    "Strong analytical and communication skills",
                    "Interest in consumer products, education, and gamification",
                    "Experience with data analysis or product analytics tools",
                ],
                "description": (
                    "Associate Product Manager Intern at Duolingo — Summer 2026\n\n"
                    "Help shape features used by 100M+ monthly learners. Work with engineering "
                    "and design teams to define, ship, and measure product improvements "
                    "for the world's leading language-learning platform.\n\n"
                    "Source: Kleiner Perkins Fellows / Duolingo Careers"
                ),
            },
        ],
    },

    # ── 2. Grammarly (KP) ──
    {
        "company_name": "Grammarly",
        "email": "careers@grammarly.com",
        "name": "Max Lytvyn",
        "industry": "AI / Productivity Software",
        "company_size": "startup",
        "website": "https://grammarly.com",
        "slug": "grammarly",
        "description": (
            "Grammarly is an AI-powered writing and productivity platform used by over 30 million "
            "daily active users. Provides real-time writing assistance across web, mobile, and "
            "desktop. Acquired KP-backed Coda in 2024. ~1,600 employees.\n\n"
            "Source: Kleiner Perkins Portfolio | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Max Lytvyn", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/max-lytvyn-61010b4"},
            {"name": "Alex Shevchenko", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/alex-shevchenko"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7500,
                "salary_max": 9500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Python, TypeScript, or Go",
                    "Interest in NLP, AI, or productivity tools",
                    "Experience building web applications is a plus",
                ],
                "description": (
                    "Software Engineering Intern at Grammarly — Summer 2026\n\n"
                    "Join Grammarly's 12-week internship program in San Francisco. Build AI-powered "
                    "features used by 30M+ daily users across writing, communication, and "
                    "productivity workflows.\n\n"
                    "Source: Kleiner Perkins Portfolio / Grammarly Careers"
                ),
            },
        ],
    },

    # ── 3. Imprint (KP) ──
    {
        "company_name": "Imprint",
        "email": "careers@imprint.co",
        "name": "Daragh Murphy",
        "industry": "FinTech / Credit Cards",
        "company_size": "startup",
        "website": "https://imprint.co",
        "slug": "imprint",
        "description": (
            "Imprint is a next-generation co-branded credit card and financial products platform, "
            "partnering with major consumer brands like H-E-B, Turkish Airlines, Brooks Brothers, "
            "and Eddie Bauer. Backed by KP, Thrive Capital, and Affirm. 100-250 employees.\n\n"
            "Source: Kleiner Perkins Portfolio | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Daragh Murphy", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/daraghjmurphy"},
            {"name": "Gaurav Ahuja", "title": "Co-Founder & Chairman", "linkedin": "https://linkedin.com/in/gauravahuja"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern, Full Stack (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8500,
                "salary_max": 10500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Experience with React, TypeScript, and Node.js",
                    "Interest in fintech and financial products",
                    "Ability to work hybrid (2-3 days/week in NYC office)",
                ],
                "description": (
                    "Software Engineer Intern, Full Stack at Imprint — Summer 2026\n\n"
                    "Build the next generation of co-branded credit card products. Work across "
                    "the stack on features powering partnerships with H-E-B, Turkish Airlines, "
                    "and other major consumer brands. Hybrid in NYC.\n\n"
                    "Source: Kleiner Perkins Portfolio / Imprint Careers"
                ),
            },
            {
                "title": "Software Engineer Intern, Backend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8500,
                "salary_max": 10500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong skills in Python, Go, or Java",
                    "Experience with databases and API design",
                    "Interest in financial systems and payments infrastructure",
                ],
                "description": (
                    "Software Engineer Intern, Backend at Imprint — Summer 2026\n\n"
                    "Build backend systems powering Imprint's co-branded credit card platform. "
                    "Work on payments infrastructure, credit decisioning, and card management "
                    "APIs. $54/hr compensation.\n\n"
                    "Source: Kleiner Perkins Portfolio / Imprint Careers"
                ),
            },
            {
                "title": "Product Designer Intern (Summer 2026)",
                "vertical": Vertical.DESIGN,
                "role_type": RoleType.PRODUCT_DESIGNER,
                "location": "New York, NY",
                "salary_min": 7500,
                "salary_max": 9500,
                "requirements": [
                    "Currently pursuing a degree in Design, HCI, or related field",
                    "Strong portfolio demonstrating product design skills",
                    "Proficiency with Figma",
                    "Interest in fintech, consumer products, and credit card design",
                ],
                "description": (
                    "Product Designer Intern at Imprint — Summer 2026\n\n"
                    "Design co-branded credit card experiences for major consumer brands. "
                    "Work on cardholder apps, partner dashboards, and card design at a "
                    "fast-growing fintech in NYC.\n\n"
                    "Source: Kleiner Perkins Portfolio / Imprint Careers"
                ),
            },
        ],
    },

    # ── 4. Garner Health (KP) ──
    {
        "company_name": "Garner Health",
        "email": "careers@getgarner.com",
        "name": "Nick Reber",
        "industry": "HealthTech",
        "company_size": "startup",
        "website": "https://getgarner.com",
        "slug": "garner-health",
        "description": (
            "Garner Health uses data science to help patients identify and access the highest-quality "
            "doctors, transforming how healthcare quality is measured. Serves 700+ clients including "
            "Kaiser and Volkswagen. KP's latest investment (Feb 2026). ~350 employees.\n\n"
            "Source: Kleiner Perkins Portfolio | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Nick Reber", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/nickreber"},
        ],
        "jobs": [
            {
                "title": "Full Stack Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 7000,
                "salary_max": 9000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Experience with React, Python, or similar web technologies",
                    "Interest in healthcare technology and data science",
                    "Ability to work in-office 3 days/week in NYC",
                ],
                "description": (
                    "Full Stack Engineering Intern at Garner Health — Summer 2026\n\n"
                    "Build technology that helps patients find the best doctors using data science. "
                    "Work on the platform serving 700+ enterprise clients. KP-backed, one of "
                    "NYC's fastest-growing healthtech companies.\n\n"
                    "Source: Kleiner Perkins Portfolio / Garner Health Careers"
                ),
            },
        ],
    },

    # ── 5. Ambiq (KP) ──
    {
        "company_name": "Ambiq",
        "email": "careers@ambiq.com",
        "name": "Scott Hanson",
        "industry": "Semiconductors / Edge AI",
        "company_size": "startup",
        "website": "https://ambiq.com",
        "slug": "ambiq",
        "description": (
            "Ambiq designs ultra-low-power microcontrollers and SoCs using patented Subthreshold "
            "Power Optimized Technology (SPOT) for edge AI, smartwatches, medical devices, and IoT. "
            "Public on NYSE (AMBQ) since July 2025. ~300 employees.\n\n"
            "Source: Kleiner Perkins Portfolio | HQ: Austin, TX"
        ),
        "founders": [
            {"name": "Scott Hanson", "title": "Founder & CTO", "linkedin": "https://linkedin.com/in/scott-hanson-82707b7"},
        ],
        "jobs": [
            {
                "title": "Embedded Firmware Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Computer Engineering, EE, or related field",
                    "Experience with embedded C/C++ programming",
                    "Understanding of microcontrollers, RTOS, and communication protocols",
                    "Interest in ultra-low-power design and edge AI",
                ],
                "description": (
                    "Embedded Firmware Engineering Intern at Ambiq — Summer 2026\n\n"
                    "Develop firmware for Ambiq's ultra-low-power microcontrollers used in "
                    "smartwatches, medical devices, and IoT sensors. Work with the team that "
                    "invented SPOT technology for edge AI computing.\n\n"
                    "Source: Kleiner Perkins Portfolio / Ambiq Careers"
                ),
            },
        ],
    },

    # ─────────────────────────────────────────────
    # TECHSTARS PORTFOLIO
    # ─────────────────────────────────────────────

    # ── 6. DigitalOcean (Techstars) ──
    {
        "company_name": "DigitalOcean",
        "email": "careers@digitalocean.com",
        "name": "Ben Uretsky",
        "industry": "Cloud Computing / Developer Tools",
        "company_size": "startup",
        "website": "https://digitalocean.com",
        "slug": "digitalocean",
        "description": (
            "DigitalOcean is a cloud infrastructure provider that simplifies cloud computing for "
            "developers and businesses. Publicly traded on NYSE (DOCN). Went through Techstars "
            "Boulder 2012. ~1,200-2,400 employees.\n\n"
            "Source: Techstars Portfolio | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Ben Uretsky", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/benuretsky"},
            {"name": "Moisey Uretsky", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/moisey"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 7000,
                "salary_max": 9000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Go, Python, or JavaScript",
                    "Interest in cloud infrastructure, distributed systems, or DevOps",
                    "Must be in a hub city: Austin, Boston, Denver, San Francisco, or Seattle",
                ],
                "description": (
                    "Software Engineer Intern at DigitalOcean — Summer 2026\n\n"
                    "Join DigitalOcean's 12-week internship program. Build cloud infrastructure "
                    "products used by millions of developers worldwide. Work on compute, storage, "
                    "networking, or Kubernetes services. NYSE-listed Techstars alum.\n\n"
                    "Source: Techstars Portfolio / DigitalOcean Careers"
                ),
            },
        ],
    },

    # ── 7. Chainalysis (Techstars) ──
    {
        "company_name": "Chainalysis",
        "email": "careers@chainalysis.com",
        "name": "Jonathan Levin",
        "industry": "Blockchain / Fintech / Cybersecurity",
        "company_size": "startup",
        "website": "https://chainalysis.com",
        "slug": "chainalysis",
        "description": (
            "Chainalysis is a blockchain analytics platform providing data, software, and research "
            "to government agencies, financial institutions, and crypto businesses. Valued at $8.6B. "
            "Techstars unicorn with ~400-500 employees.\n\n"
            "Source: Techstars Portfolio | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Jonathan Levin", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/jonylevin"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8000,
                "salary_max": 10000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Python, Java, or TypeScript",
                    "Interest in blockchain technology, cybersecurity, or fintech",
                    "Experience with data-intensive applications is a plus",
                ],
                "description": (
                    "Software Engineer Intern at Chainalysis — Summer 2026\n\n"
                    "Build blockchain analytics tools used by law enforcement and financial "
                    "institutions worldwide. Work on graph analysis, data pipelines, and "
                    "investigation tools at the $8.6B leader in crypto compliance. $50/hr.\n\n"
                    "Source: Techstars Portfolio / Chainalysis Careers"
                ),
            },
            {
                "title": "Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "New York, NY",
                "salary_min": 7500,
                "salary_max": 9500,
                "requirements": [
                    "Currently pursuing a degree in Data Science, Economics, CS, or related field",
                    "Strong analytical and research skills",
                    "Experience with data analysis tools (Python, R, SQL)",
                    "Interest in cryptocurrency, blockchain, and financial crime analysis",
                ],
                "description": (
                    "Research Intern at Chainalysis — Summer 2026\n\n"
                    "Conduct original research on blockchain ecosystems, cryptocurrency trends, "
                    "and illicit finance patterns. Your work may be published. Join the team "
                    "that produces industry-leading crypto crime reports.\n\n"
                    "Source: Techstars Portfolio / Chainalysis Careers"
                ),
            },
        ],
    },

    # ── 8. Remitly (Techstars) ──
    {
        "company_name": "Remitly",
        "email": "careers@remitly.com",
        "name": "Matt Oppenheimer",
        "industry": "FinTech / Payments",
        "company_size": "startup",
        "website": "https://remitly.com",
        "slug": "remitly",
        "description": (
            "Remitly is a digital financial services company enabling international money transfers. "
            "Publicly traded on NASDAQ (RELY). Went through Techstars Seattle 2011. Serves immigrants "
            "sending money to loved ones abroad. ~2,500 employees.\n\n"
            "Source: Techstars Portfolio | HQ: Seattle, WA"
        ),
        "founders": [
            {"name": "Matt Oppenheimer", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/mattoppenheimer"},
            {"name": "Josh Hug", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/joshhug"},
        ],
        "jobs": [
            {
                "title": "Software Development Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Seattle, WA",
                "salary_min": 7500,
                "salary_max": 9400,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Java, Kotlin, or Python",
                    "Interest in payments, fintech, or financial inclusion",
                    "Experience with distributed systems or mobile development is a plus",
                ],
                "description": (
                    "Software Development Engineer Intern at Remitly — Summer 2026\n\n"
                    "Build technology that powers international money transfers for millions "
                    "of customers. Join a 3-month program in Seattle working on collaborative "
                    "product development teams. $47/hr. NASDAQ-listed Techstars alum.\n\n"
                    "Source: Techstars Portfolio / Remitly Careers"
                ),
            },
        ],
    },

    # ── 9. Cosm (Techstars) ──
    {
        "company_name": "Cosm",
        "email": "careers@cosm.com",
        "name": "Jeb Terry",
        "industry": "Immersive Entertainment / Technology",
        "company_size": "startup",
        "website": "https://cosm.com",
        "slug": "cosm",
        "description": (
            "Cosm builds immersive reality technology and large-scale LED dome venues for live "
            "sports and entertainment experiences. Venues in Hollywood Park (LA) and Grandscape (TX). "
            "Techstars unicorn valued at $1B+. ~620 employees.\n\n"
            "Source: Techstars Portfolio | HQ: Los Angeles, CA"
        ),
        "founders": [
            {"name": "Jeb Terry", "title": "President & CEO", "linkedin": "https://linkedin.com/in/jebterry"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Los Angeles, CA",
                "salary_min": 6500,
                "salary_max": 8500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Experience with C++, Python, or real-time systems",
                    "Interest in immersive media, video processing, or graphics programming",
                    "Ability to work hybrid in Playa Vista, CA or Salt Lake City, UT",
                ],
                "description": (
                    "Software Engineering Intern at Cosm — Summer 2026\n\n"
                    "Build immersive dome technology for live sports and entertainment. Work on "
                    "12K+ video, real-time rendering, and immersive display systems powering "
                    "Cosm's next-generation venues. Techstars unicorn.\n\n"
                    "Source: Techstars Portfolio / Cosm Careers"
                ),
            },
            {
                "title": "Design Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Chadds Ford, PA",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Mechanical, Electrical, or Computer Engineering",
                    "Experience with CAD tools and hardware prototyping",
                    "Interest in display systems, LED technology, or immersive environments",
                    "Ability to work on-site in Chadds Ford, PA",
                ],
                "description": (
                    "Design Engineering Intern at Cosm — Summer 2026\n\n"
                    "Work on planetarium display systems and immersive dome structures. "
                    "Design and prototype hardware components for Cosm's LED dome venues "
                    "that transform how people experience live events.\n\n"
                    "Source: Techstars Portfolio / Cosm Careers"
                ),
            },
        ],
    },

    # ── 10. Synack (Techstars) ──
    {
        "company_name": "Synack",
        "email": "careers@synack.com",
        "name": "Jay Kaplan",
        "industry": "Cybersecurity",
        "company_size": "startup",
        "website": "https://synack.com",
        "slug": "synack",
        "description": (
            "Synack is a crowdsourced cybersecurity platform combining elite human security researchers "
            "(Red Team) with AI-driven technology for enterprise penetration testing. Founded by former "
            "NSA analysts. CNBC Disruptor 50 four-time winner. ~100 staff + 1,500 researchers.\n\n"
            "Source: Techstars Portfolio | HQ: Redwood City, CA"
        ),
        "founders": [
            {"name": "Jay Kaplan", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/jaykap"},
        ],
        "jobs": [
            {
                "title": "Security Analyst Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.QA_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 3500,
                "salary_max": 4500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science with cybersecurity focus",
                    "Understanding of web application security and common vulnerabilities",
                    "Familiarity with penetration testing tools and methodologies",
                    "Interest in offensive security and vulnerability research",
                ],
                "description": (
                    "Security Analyst Intern at Synack — Summer 2026\n\n"
                    "Assist the Vulnerability Operations team reviewing security vulnerability "
                    "reports from Synack's elite Red Team researchers. Learn offensive security "
                    "from a team founded by former NSA analysts. $20/hr.\n\n"
                    "Source: Techstars Portfolio / Synack Careers"
                ),
            },
        ],
    },

    # ── 11. DataRobot (Techstars) ──
    {
        "company_name": "DataRobot",
        "email": "careers@datarobot.com",
        "name": "Tom de Godoy",
        "industry": "AI / Machine Learning",
        "company_size": "startup",
        "website": "https://datarobot.com",
        "slug": "datarobot",
        "description": (
            "DataRobot is an enterprise AI/ML platform that automates building, deploying, and "
            "managing machine learning models. Went through Techstars Boston. Highly rated "
            "internship program on Comparably. ~800-900 employees.\n\n"
            "Source: Techstars Portfolio | HQ: Boston, MA"
        ),
        "founders": [
            {"name": "Tom de Godoy", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/tom-de-godoy"},
        ],
        "jobs": [
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Boston, MA",
                "salary_min": 7000,
                "salary_max": 9000,
                "requirements": [
                    "Currently pursuing a degree in Data Science, CS, Statistics, or related field",
                    "Experience with Python, scikit-learn, and ML fundamentals",
                    "Understanding of model training, evaluation, and deployment",
                    "Interest in AutoML and enterprise AI applications",
                ],
                "description": (
                    "Data Science Intern at DataRobot — Summer 2026\n\n"
                    "Work on the platform that automates machine learning for the enterprise. "
                    "Build and improve AutoML capabilities used by Fortune 500 companies. "
                    "Techstars alum based in Boston.\n\n"
                    "Source: Techstars Portfolio / DataRobot Careers"
                ),
            },
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Boston, MA",
                "salary_min": 7000,
                "salary_max": 9000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Python, Java, or Go",
                    "Interest in AI/ML platforms and distributed systems",
                    "Experience with cloud services (AWS, GCP) is a plus",
                ],
                "description": (
                    "Software Engineer Intern at DataRobot — Summer 2026\n\n"
                    "Build enterprise AI/ML platform features used by leading organizations. "
                    "Work on model management, deployment pipelines, and platform engineering "
                    "at a Techstars-backed AI leader in Boston.\n\n"
                    "Source: Techstars Portfolio / DataRobot Careers"
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
