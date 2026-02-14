#!/usr/bin/env python3
"""
Seed intern jobs from TopStartups.io job board.

TopStartups.io aggregates job listings from newly funded & hiring startups.
This script captures US-based Summer 2026 internship positions across defense tech,
AI, SaaS, construction tech, sports tech, and marketplaces.

SCRIPT ID: topstartups
RUN: cd apps/api && python -m scripts.seed_topstartups_jobs
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
FIRM_NAME = "TopStartups.io"
SCRIPT_ID = "topstartups"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Asana ──
    {
        "company_name": "Asana",
        "email": "careers@asana.com",
        "name": "Dustin Moskovitz",
        "industry": "SaaS / Work Management",
        "company_size": "startup",
        "website": "https://asana.com",
        "slug": "asana",
        "description": (
            "Asana is a work management platform that helps teams organize, track, and manage "
            "their projects and workflows. Over 150,000 organizations worldwide use Asana for "
            "cross-functional collaboration with task management, timelines, goals tracking, and "
            "workflow automation. Public on NYSE (ASAN) with ~$724M annual revenue.\n\n"
            "Source: TopStartups.io | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Dustin Moskovitz", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/dmoskov"},
            {"name": "Justin Rosenstein", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/justinrosenstein"},
        ],
        "jobs": [
            {
                "title": "Product Design Intern - San Francisco (Summer 2026)",
                "vertical": Vertical.DESIGN,
                "role_type": RoleType.PRODUCT_DESIGNER,
                "location": "San Francisco, CA",
                "salary_min": 6500,
                "salary_max": 8500,
                "requirements": [
                    "Currently pursuing a degree in Design, HCI, or related field",
                    "Strong portfolio demonstrating product design skills",
                    "Proficiency with Figma or similar design tools",
                    "Interest in productivity software and workflow design",
                ],
                "description": (
                    "Product Design Intern at Asana — Summer 2026\n\n"
                    "Join Asana's design team in San Francisco and work on features used by "
                    "150,000+ organizations worldwide. Contribute to Asana's product experience "
                    "across web and mobile platforms.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
            {
                "title": "Product Design Intern - New York (Summer 2026)",
                "vertical": Vertical.DESIGN,
                "role_type": RoleType.PRODUCT_DESIGNER,
                "location": "New York, NY",
                "salary_min": 6500,
                "salary_max": 8500,
                "requirements": [
                    "Currently pursuing a degree in Design, HCI, or related field",
                    "Strong portfolio demonstrating product design skills",
                    "Proficiency with Figma or similar design tools",
                    "Interest in productivity software and workflow design",
                ],
                "description": (
                    "Product Design Intern at Asana — Summer 2026\n\n"
                    "Join Asana's design team in New York and work on features used by "
                    "150,000+ organizations worldwide. Contribute to Asana's product experience "
                    "across web and mobile platforms.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 2. Shield AI ──
    {
        "company_name": "Shield AI",
        "email": "careers@shield.ai",
        "name": "Brandon Tseng",
        "industry": "AI / Defense",
        "company_size": "startup",
        "website": "https://shield.ai",
        "slug": "shield-ai",
        "description": (
            "Shield AI builds autonomous systems for military and defense applications, including "
            "the V-BAT autonomous drone and Hivemind AI pilot software that enables aircraft to "
            "operate without GPS, communications, or remote pilots. Valued at $5.3B after Series F-1 "
            "led by L3Harris and Hanwha in March 2025.\n\n"
            "Source: TopStartups.io | HQ: San Diego, CA"
        ),
        "founders": [
            {"name": "Brandon Tseng", "title": "Co-Founder & President", "linkedin": "https://linkedin.com/in/brandontseng"},
            {"name": "Ryan Tseng", "title": "Co-Founder & Chief Strategy Officer", "linkedin": "https://linkedin.com/in/ryantseng"},
        ],
        "jobs": [
            {
                "title": "Quality Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.QA_ENGINEER,
                "location": "Dallas, TX",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science, Electrical Engineering, or related field",
                    "Strong understanding of software testing methodologies and QA processes",
                    "Experience with Python or C++ for test automation",
                    "Interest in defense technology and autonomous systems",
                ],
                "description": (
                    "Quality Engineering Intern at Shield AI — Summer 2026\n\n"
                    "Join Shield AI's engineering team in Dallas and help ensure the quality and "
                    "reliability of autonomous defense systems including the Hivemind AI pilot. "
                    "Work on testing autonomous aircraft software that operates without GPS or comms.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 3. Saronic ──
    {
        "company_name": "Saronic",
        "email": "careers@saronic.com",
        "name": "Dino Mavrookas",
        "industry": "AI / Defense / Maritime",
        "company_size": "startup",
        "website": "https://saronic.com",
        "slug": "saronic",
        "description": (
            "Saronic designs and manufactures autonomous surface vessels (unmanned ships) for "
            "defense and naval applications. The company combines hardware, software, and AI into "
            "scalable maritime platforms. Valued at $4B after a $600M Series C in early 2025, with "
            "a $300M shipyard expansion in Louisiana.\n\n"
            "Source: TopStartups.io | HQ: Austin, TX"
        ),
        "founders": [
            {"name": "Dino Mavrookas", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/dino-mavrookas"},
            {"name": "Vibhav Altekar", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/vibhavaltekar"},
            {"name": "Doug Lambert", "title": "Co-Founder & COO", "linkedin": "https://linkedin.com/in/doug-lambert-00463a1b"},
            {"name": "Rob Lehman", "title": "Co-Founder & CCO", "linkedin": "https://linkedin.com/in/rob-lehman-8387634"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science, Robotics, or related field",
                    "Strong programming skills in Python, C++, or Rust",
                    "Interest in autonomous systems, robotics, or maritime technology",
                    "US citizenship required for defense work",
                ],
                "description": (
                    "Software Engineer Intern at Saronic — Summer 2026\n\n"
                    "Build software for autonomous unmanned surface vessels at one of the fastest-growing "
                    "defense tech companies. Work on perception, navigation, and autonomous systems "
                    "for naval applications. Saronic is backed by a16z and General Catalyst.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 4. Skydio ──
    {
        "company_name": "Skydio",
        "email": "careers@skydio.com",
        "name": "Adam Bry",
        "industry": "AI / Drones / Enterprise",
        "company_size": "startup",
        "website": "https://skydio.com",
        "slug": "skydio",
        "description": (
            "Skydio manufactures autonomous drones for enterprise inspection, public safety, "
            "and national security. Their drones feature advanced AI-powered autonomous flight "
            "and obstacle avoidance. Skydio is the leading US-based drone manufacturer with "
            "$744M in total funding.\n\n"
            "Source: TopStartups.io | HQ: San Mateo, CA"
        ),
        "founders": [
            {"name": "Adam Bry", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/adambry"},
            {"name": "Abraham Bachrach", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/abachrach"},
            {"name": "Matt Donahoe", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/mattdonahoe1"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 6500,
                "salary_max": 8000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science, Robotics, or related field",
                    "Strong programming skills in C++ or Python",
                    "Interest in computer vision, autonomous systems, or robotics",
                    "Familiarity with Linux development environments",
                ],
                "description": (
                    "Software Engineer Intern at Skydio — Summer 2026\n\n"
                    "Work on the leading US-made autonomous drone platform. Contribute to AI-powered "
                    "flight systems, computer vision, and obstacle avoidance technology used by "
                    "enterprise and government customers. Backed by a16z and NVIDIA.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 5. HeyGen ──
    {
        "company_name": "HeyGen",
        "email": "careers@heygen.com",
        "name": "Joshua Xu",
        "industry": "AI / Video Generation",
        "company_size": "startup",
        "website": "https://heygen.com",
        "slug": "heygen",
        "description": (
            "HeyGen is an AI-powered video generation platform that creates professional-quality "
            "videos using AI avatars and voice cloning. The platform enables businesses to produce "
            "marketing, training, and sales content at scale without traditional video production. "
            "Hit $100M revenue by October 2025 with a ~150-person team.\n\n"
            "Source: TopStartups.io | HQ: Los Angeles, CA"
        ),
        "founders": [
            {"name": "Joshua Xu", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/buffxz"},
            {"name": "Wayne Liang", "title": "Co-Founder & CPO", "linkedin": "https://linkedin.com/in/wayneliang7"},
        ],
        "jobs": [
            {
                "title": "Product Manager Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "Los Angeles, CA",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Business, CS, or related field",
                    "Strong analytical and communication skills",
                    "Interest in AI, video technology, or content creation",
                    "Experience with product analytics tools is a plus",
                ],
                "description": (
                    "Product Manager Intern at HeyGen — Summer 2026\n\n"
                    "Join HeyGen's product team in LA and help shape the future of AI-powered video "
                    "generation. Work on features for a platform that hit $100M revenue in 2025. "
                    "Backed by Benchmark and Thrive Capital, valued at $500M.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 6. Air Space Intelligence ──
    {
        "company_name": "Air Space Intelligence",
        "email": "careers@airspace-intelligence.com",
        "name": "Phillip Buckendorf",
        "industry": "AI / Aviation",
        "company_size": "startup",
        "website": "https://airspace-intelligence.com",
        "slug": "air-space-intelligence",
        "description": (
            "Air Space Intelligence (ASI) builds AI-driven 4D simulation and decision support "
            "technology that optimizes airline flight operations, helping carriers achieve 3-5% "
            "fuel savings per flight. Their systems monitor tens of thousands of flights globally "
            "for major airlines and the US Air Force.\n\n"
            "Source: TopStartups.io | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Phillip Buckendorf", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/phillipbuckendorf"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Boston, MA",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science, Aerospace Engineering, or related field",
                    "Strong programming skills in Python or Java",
                    "Interest in AI, simulation, or aviation technology",
                    "Familiarity with machine learning concepts is a plus",
                ],
                "description": (
                    "Software Engineer Intern at Air Space Intelligence — Summer 2026\n\n"
                    "Build AI systems that optimize flight operations for the world's largest airlines. "
                    "Work on 4D airspace simulation and prediction systems that save millions in fuel "
                    "costs. Backed by a16z, Spark Capital, and Bloomberg Beta.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 7. EquipmentShare ──
    {
        "company_name": "EquipmentShare",
        "email": "careers@equipmentshare.com",
        "name": "Jabbok Schlacks",
        "industry": "Construction Technology",
        "company_size": "startup",
        "website": "https://equipmentshare.com",
        "slug": "equipmentshare",
        "description": (
            "EquipmentShare is a construction equipment rental and technology company that "
            "combines heavy equipment rental with its proprietary T3 technology platform for "
            "fleet tracking, telematics, and job site management. Operates 373+ locations "
            "across 45 US states. IPO'd on NASDAQ (EQPT) in January 2026 at ~$6.4B valuation.\n\n"
            "Source: TopStartups.io | HQ: Columbia, MO"
        ),
        "founders": [
            {"name": "Jabbok Schlacks", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/jabbok-schlacks-319a378a"},
            {"name": "Willy Schlacks", "title": "Co-Founder & President", "linkedin": "https://linkedin.com/in/william-schlacks-49796016"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Columbia, MO",
                "salary_min": 5000,
                "salary_max": 6500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming fundamentals in Python, JavaScript, or similar",
                    "Interest in IoT, telematics, or construction technology",
                    "Ability to work on-site at Columbia, MO headquarters",
                ],
                "description": (
                    "Software Engineer Intern at EquipmentShare — Summer 2026\n\n"
                    "Build technology that powers the T3 platform used across 373+ locations in 45 "
                    "states. Work on fleet tracking, telematics, and job site management software "
                    "for one of construction tech's fastest-growing companies. YC-backed, recently IPO'd.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 8. Faire ──
    {
        "company_name": "Faire",
        "email": "careers@faire.com",
        "name": "Max Rhodes",
        "industry": "E-Commerce / Wholesale Marketplace",
        "company_size": "startup",
        "website": "https://faire.com",
        "slug": "faire",
        "description": (
            "Faire is an online wholesale marketplace connecting independent retailers with brands, "
            "enabling small shops to discover and purchase products from thousands of makers and "
            "artisans. Uses ML to match retailers with products and offers net-60 payment terms "
            "with free returns. Valued at $5.2B with ~550 employees.\n\n"
            "Source: TopStartups.io | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Max Rhodes", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/maxrhodes"},
            {"name": "Marcelo Cortes", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/mmcortes"},
            {"name": "Jeff Kolovson", "title": "Co-Founder & COO", "linkedin": "https://linkedin.com/in/jeffkolovson"},
            {"name": "Daniele Perito", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/danieleperito"},
        ],
        "jobs": [
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "San Francisco, CA",
                "salary_min": 6500,
                "salary_max": 8500,
                "requirements": [
                    "Currently pursuing a degree in Data Science, Statistics, CS, or related field",
                    "Strong skills in Python, SQL, and statistical analysis",
                    "Experience with machine learning frameworks (scikit-learn, TensorFlow, PyTorch)",
                    "Interest in marketplace dynamics, recommendation systems, or e-commerce",
                ],
                "description": (
                    "Data Science Intern at Faire — Summer 2026\n\n"
                    "Join Faire's data team in SF and work on ML models that power the wholesale "
                    "marketplace connecting 700,000+ retailers with brands. Build recommendation "
                    "systems and predictive models. Backed by Sequoia, Lightspeed, and YC.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 9. Podium ──
    {
        "company_name": "Podium",
        "email": "careers@podium.com",
        "name": "Eric Rea",
        "industry": "SaaS / Customer Interaction",
        "company_size": "startup",
        "website": "https://podium.com",
        "slug": "podium",
        "description": (
            "Podium is an AI-powered customer interaction platform for local businesses, providing "
            "tools for messaging, reviews, payments, and customer communication through a unified "
            "inbox. Helps businesses manage online reputation, convert leads via text, and process "
            "payments. Unicorn since 2020 with ~1,400 employees.\n\n"
            "Source: TopStartups.io | HQ: Lehi, UT"
        ),
        "founders": [
            {"name": "Eric Rea", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/ericrea"},
            {"name": "Dennis Steele", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/dennissteele"},
        ],
        "jobs": [
            {
                "title": "Product Management Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "Lehi, UT",
                "salary_min": 5500,
                "salary_max": 7000,
                "requirements": [
                    "Currently pursuing a degree in Business, CS, or related field",
                    "Strong analytical and communication skills",
                    "Interest in AI-powered products and local business technology",
                    "Experience with data analysis tools is a plus",
                ],
                "description": (
                    "Product Management Intern at Podium — Summer 2026\n\n"
                    "Join Podium's product team in Lehi, UT and help build AI-powered features "
                    "used by thousands of local businesses. Work on messaging, reviews, and payment "
                    "products. YC and Accel-backed unicorn.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 10. Hudl ──
    {
        "company_name": "Hudl",
        "email": "careers@hudl.com",
        "name": "David Graff",
        "industry": "Sports Technology",
        "company_size": "startup",
        "website": "https://hudl.com",
        "slug": "hudl",
        "description": (
            "Hudl is a sports video analysis and coaching platform used by teams at every level "
            "from youth leagues to professional organizations. Serves 200,000+ teams across 40+ "
            "sports with tools for video exchange, performance analytics, and recruiting highlights. "
            "Over 4,000 employees, backed by Accel and Bain Capital.\n\n"
            "Source: TopStartups.io | HQ: Lincoln, NE"
        ),
        "founders": [
            {"name": "David Graff", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/davgraff"},
            {"name": "John Wirtz", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/johnwirtz"},
            {"name": "Brian Kaiser", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/briankaiser"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Lincoln, NE",
                "salary_min": 4500,
                "salary_max": 6000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in at least one language",
                    "Interest in sports technology and video analysis",
                    "Ability to work on-site in Lincoln, NE",
                ],
                "description": (
                    "Software Engineering Intern at Hudl — Summer 2026\n\n"
                    "Build technology that helps 200,000+ teams analyze game film and improve "
                    "performance. Work on video analysis, performance analytics, or recruiting "
                    "tools used by coaches from youth sports to the pros.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # ── 11. Clearco ──
    {
        "company_name": "Clearco",
        "email": "careers@clear.co",
        "name": "Andrew D'Souza",
        "industry": "FinTech / Revenue-Based Financing",
        "company_size": "startup",
        "website": "https://clear.co",
        "slug": "clearco",
        "description": (
            "Clearco (formerly Clearbanc) provides non-dilutive, revenue-based financing to "
            "e-commerce and SaaS companies, allowing founders to access growth capital without "
            "giving up equity. Has deployed over $3B to 10,000+ businesses. Backed by SoftBank "
            "and Founders Fund.\n\n"
            "Source: TopStartups.io | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Andrew D'Souza", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/andrewdsouza"},
            {"name": "Michele Romanow", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/micheleromanow"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Experience with TypeScript, React, or Node.js",
                    "Interest in fintech and financial products",
                    "Strong problem-solving skills",
                ],
                "description": (
                    "Software Engineering Intern at Clearco — Summer 2026\n\n"
                    "Build fintech products that help e-commerce and SaaS founders access "
                    "non-dilutive capital. Work on the platform that has deployed $3B+ to "
                    "10,000+ businesses.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
            {
                "title": "Product Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "New York, NY",
                "salary_min": 5500,
                "salary_max": 7000,
                "requirements": [
                    "Currently pursuing a degree in Business, CS, or related field",
                    "Strong analytical and communication skills",
                    "Interest in fintech, e-commerce, or SaaS products",
                    "Experience with product analytics tools is a plus",
                ],
                "description": (
                    "Product Intern at Clearco — Summer 2026\n\n"
                    "Shape the product strategy for Clearco's revenue-based financing platform. "
                    "Work alongside product and engineering teams to build features that help "
                    "founders access growth capital.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# These companies were seeded by previous scripts. Adding new
# intern positions discovered on TopStartups.io.

ADDITIONAL_JOBS = [
    # Ironclad — already has SWE Intern, adding UX Research
    {
        "company_name": "Ironclad",
        "jobs": [
            {
                "title": "UX Research Intern (Summer 2026)",
                "vertical": Vertical.DESIGN,
                "role_type": RoleType.UX_DESIGNER,
                "location": "New York, NY",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in HCI, Design Research, Psychology, or related field",
                    "Experience with user research methods (interviews, usability testing, surveys)",
                    "Strong analytical and synthesis skills",
                    "Interest in legal tech and contract management",
                ],
                "description": (
                    "UX Research Intern at Ironclad — Summer 2026\n\n"
                    "Conduct user research for Ironclad's digital contract management platform. "
                    "Help understand user needs and inform product decisions through qualitative "
                    "and quantitative research methods.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
            {
                "title": "Automation Quality Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.QA_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Experience with test automation frameworks",
                    "Strong programming skills in Python, JavaScript, or Java",
                    "Understanding of CI/CD pipelines",
                ],
                "description": (
                    "Automation Quality Engineering Intern at Ironclad — Summer 2026\n\n"
                    "Build and maintain automated test suites for Ironclad's contract lifecycle "
                    "management platform. Work on test automation, CI/CD, and quality engineering.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # Flock Safety — already has SWE Intern, adding specialized engineering roles
    {
        "company_name": "Flock Safety",
        "jobs": [
            {
                "title": "Site Reliability Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, USA",
                "salary_min": 5500,
                "salary_max": 7000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Experience with Linux, cloud infrastructure (AWS/GCP), and monitoring tools",
                    "Strong scripting skills in Python or Bash",
                    "Interest in reliability, infrastructure, and DevOps",
                ],
                "description": (
                    "SRE Intern at Flock Safety — Summer 2026\n\n"
                    "Help keep Flock Safety's public safety platform reliable and scalable. "
                    "Work on infrastructure, monitoring, and incident response for a platform "
                    "used by law enforcement agencies across the US.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
            {
                "title": "Firmware Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Remote, USA",
                "salary_min": 5500,
                "salary_max": 7000,
                "requirements": [
                    "Currently pursuing a degree in Computer Engineering, EE, or related field",
                    "Experience with embedded C/C++ programming",
                    "Understanding of microcontrollers and communication protocols",
                    "Interest in IoT devices and camera systems",
                ],
                "description": (
                    "Firmware Engineering Intern at Flock Safety — Summer 2026\n\n"
                    "Develop firmware for Flock Safety's camera and sensor devices used in "
                    "public safety applications. Work on embedded systems for IoT devices "
                    "deployed across thousands of locations.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # Together AI — already has Research Intern, adding SWE
    {
        "company_name": "Together AI",
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6500,
                "salary_max": 8500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Python, C++, or Rust",
                    "Experience with distributed systems or cloud infrastructure",
                    "Interest in AI infrastructure and model serving",
                ],
                "description": (
                    "Software Engineer Intern at Together AI — Summer 2026\n\n"
                    "Build AI infrastructure that powers model training and inference at scale. "
                    "Work on distributed systems, GPU programming, and AI platform engineering "
                    "at the forefront of open-source AI.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
            {
                "title": "Systems Research Engineer Intern - GPU Programming (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7000,
                "salary_max": 9000,
                "requirements": [
                    "Currently pursuing a Master's or PhD in CS, EE, or related field",
                    "Experience with CUDA, GPU programming, or HPC",
                    "Strong C/C++ skills and systems-level programming",
                    "Understanding of deep learning frameworks and model optimization",
                ],
                "description": (
                    "Systems Research Engineer Intern (GPU Programming) at Together AI — Summer 2026\n\n"
                    "Optimize GPU kernels and systems for AI model training and inference. "
                    "Work at the intersection of systems engineering and ML research, pushing "
                    "the boundaries of efficient AI compute.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },

    # Relativity Space — already has SWE Intern, adding Data Science
    {
        "company_name": "Relativity Space",
        "jobs": [
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Long Beach, CA",
                "salary_min": 6000,
                "salary_max": 7500,
                "requirements": [
                    "Currently pursuing a degree in Data Science, Statistics, CS, or related field",
                    "Strong skills in Python, SQL, and statistical analysis",
                    "Experience with data visualization and analysis tools",
                    "Interest in aerospace, 3D printing, or manufacturing",
                ],
                "description": (
                    "Data Science Intern at Relativity Space — Summer 2026\n\n"
                    "Apply data science to 3D-printed rocket manufacturing. Analyze manufacturing "
                    "data, build predictive models, and help optimize the world's largest 3D "
                    "metal printer. Work on the future of aerospace manufacturing.\n\n"
                    "Source: https://topstartups.io/jobs/?role=Intern"
                ),
            },
        ],
    },
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
