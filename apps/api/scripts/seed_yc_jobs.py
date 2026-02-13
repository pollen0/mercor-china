#!/usr/bin/env python3
"""
Seed script for YC startup intern jobs scraped from Work at a Startup.

Usage:
    cd apps/api
    python -m scripts.seed_yc_jobs

This script populates the database with real YC startup intern job listings,
including employer profiles, organizations, and all open roles.
"""
import sys
import os

# Add parent directory to path for imports
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


def generate_cuid(prefix: str = "") -> str:
    """Generate a CUID-like ID."""
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ─────────────────────────────────────────────────────────────
# All YC Companies with Intern Positions
# Source: https://www.workatastartup.com (Feb 2026)
# ─────────────────────────────────────────────────────────────

COMPANIES = [
    # ── Reacher (YC S25) ──
    {
        "company_name": "Reacher",
        "email": "careers@reacherapp.com",
        "name": "Jerry Qian",
        "industry": "AI / E-commerce / Creator Economy",
        "company_size": "startup",
        "website": "https://reacherapp.com/",
        "slug": "reacher",
        "description": (
            "Reacher is the #1 TikTok Shop partner helping brands like Under Armour, Hanes, "
            "HeyDude, and Logitech scale their affiliate marketing. We automate creator marketing "
            "workflows including discovery, outreach, campaign management, and content strategy "
            "across TikTok Shop, YouTube Shopping, Instagram, and Amazon.\n\n"
            "YC Batch: S25 | Team Size: 15 | HQ: San Francisco, CA\n"
            "7-figure ARR, raising seed round."
        ),
        "founders": [
            {"name": "Jerry Qian", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/j-qian", "background": "Meta, UC Berkeley, NASA"},
            {"name": "Bora Mutluoglu", "title": "Co-Founder",
             "linkedin": "https://www.linkedin.com/in/bora-mutluoglu", "background": "UC Berkeley, Palo Alto Networks"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Fall 2025 / Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA / Los Angeles, CA (In-person)",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Computer Science major with completed foundational coursework",
                    "Full-stack project experience (personal projects, hackathons, or coursework)",
                    "Available for 10-12 weeks (Fall: Sept/Oct-Dec 2025 or Summer: May/June-Aug 2026)",
                    "Resourceful and comfortable navigating ambiguity",
                    "US citizen or valid work visa",
                ],
                "description": (
                    "Software Engineer Intern at Reacher (YC S25)\n\n"
                    "Compensation: $6,000 - $10,000/month for 10-12 weeks\n\n"
                    "Build full-stack features that ship to production within days. "
                    "You'll work on AI agents, LLM-powered tools and ML pipelines processing millions of "
                    "creator/brand interactions, plus direct customer-facing features.\n\n"
                    "Tech Stack: Python, FastAPI, PostgreSQL, GCP, React, Tailwind, shadcn/ui\n\n"
                    "Source: https://www.workatastartup.com/jobs/80430"
                ),
            },
        ],
    },

    # ── Nowadays (YC S23) ──
    {
        "company_name": "Nowadays",
        "email": "careers@nowadays.ai",
        "name": "Anna Sun",
        "industry": "AI / B2B / Events",
        "company_size": "startup",
        "website": "https://nowadays.ai/",
        "slug": "nowadays",
        "description": (
            "Nowadays is the AI co-pilot for corporate retreat and event planning. "
            "Our AI contacts venues by email and phone to get availability, handles negotiations, "
            "and presents the best options. Customers include Amazon, Google, and Notion.\n\n"
            "YC Batch: S23 | Team Size: 5 | HQ: San Francisco, CA\n"
            "$3.4M in booked revenue within first 6 months of launch."
        ),
        "founders": [
            {"name": "Anna Sun", "title": "CEO",
             "linkedin": "https://www.linkedin.com/in/annasun19",
             "background": "MIT, PM & SWE at Datadog, DoorDash, Amazon"},
            {"name": "Amy Yan", "title": "COO",
             "linkedin": "https://www.linkedin.com/in/amysunyan",
             "background": "Strategy & Ops at Google, Meta, McKinsey"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Fall 2025 / Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA (In-person)",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Strong full-stack engineering skills",
                    "Available full-time (40+ hours/week) in-person in SF",
                    "At least 1 month commitment with opportunity to extend",
                    "Potential to convert to full-time offer upon graduation",
                ],
                "description": (
                    "Software Engineer Intern at Nowadays (YC S23)\n\n"
                    "Compensation: Competitive + generous housing stipend + commuter benefits\n\n"
                    "Work on foundational platforms and systems - both frontend and backend - "
                    "that enable us to build a high-quality product at scale. "
                    "Full-time, in-person role at our San Francisco office.\n\n"
                    "Source: https://www.workatastartup.com/jobs/78951"
                ),
            },
            {
                "title": "Product Engineer Intern (Spring / Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA (In-person)",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "User-oriented software engineering mindset",
                    "Available full-time (40+ hours/week) in-person in SF",
                    "At least 1 month commitment with opportunity to extend",
                    "Potential to convert to full-time offer upon graduation",
                ],
                "description": (
                    "Product Engineer Intern at Nowadays (YC S23)\n\n"
                    "Compensation: Competitive + generous housing stipend + commuter benefits\n\n"
                    "Build and shape the product that customers interact with every day. "
                    "Use our platform and tools as a user-oriented software engineer.\n\n"
                    "Source: https://www.workatastartup.com/jobs/78952"
                ),
            },
        ],
    },

    # ── Elayne (YC S24) ──
    {
        "company_name": "Elayne",
        "email": "careers@elayne.com",
        "name": "Adria Ferrier",
        "industry": "Fintech / AI / Estate Planning",
        "company_size": "startup",
        "website": "https://www.elayne.com/",
        "slug": "elayne",
        "description": (
            "Elayne is an AI copilot for growing, organizing, and transferring family estates. "
            "We help families organize assets, estate documents, and key contacts in one place, "
            "then guide them through life transitions.\n\n"
            "YC Batch: S24 | Team Size: 6 | HQ: New York\n"
            "Backed by Accel and YC. $260B TAM with $80T in assets transferring in coming decades."
        ),
        "founders": [
            {"name": "Adria Ferrier", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/adria-ferrier-8b242836/",
             "background": "Private equity at Permira and Blackstone, Wharton"},
            {"name": "Jake Grafenstein", "title": "CTO",
             "linkedin": "https://www.linkedin.com/in/jake-grafenstein-33737270/",
             "background": "Truebill (YC W16), fintech"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Full-stack engineering skills (React, NestJS, PostgreSQL)",
                    "Interest in mobile and responsive design",
                    "Ability to ship production features",
                    "Experience with Supabase and AWS a plus",
                ],
                "description": (
                    "Software Engineer Intern at Elayne (YC S24)\n\n"
                    "Work closely with the founding team to build and ship production features "
                    "across the stack. Focus on mobile and responsive design, polish, and quality.\n\n"
                    "Tech Stack: React, NestJS, PostgreSQL (Supabase), AWS\n\n"
                    "Source: https://www.workatastartup.com/jobs/81959"
                ),
            },
        ],
    },

    # ── Novaflow (YC S25) ──
    {
        "company_name": "Novaflow",
        "email": "careers@novaflowapp.com",
        "name": "Aman Agarwal",
        "industry": "AI / Bioinformatics / Life Sciences",
        "company_size": "startup",
        "website": "https://novaflowapp.com/",
        "slug": "novaflow",
        "description": (
            "Novaflow is the AI data analyst for biology labs. We automate bioinformatics analysis, "
            "turning raw sequencing data into insights in minutes instead of weeks.\n\n"
            "YC Batch: S25 | Team Size: 2 | HQ: San Francisco, CA\n"
            "Customers at Mount Sinai, UCSF, Harvard, and Caltech."
        ),
        "founders": [
            {"name": "Aman Agarwal", "title": "Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/aman-agarwal-ca",
             "background": "Computational biologist, published in Nature and Cell"},
            {"name": "Amulya Balakrishnan", "title": "Founder & CTO",
             "linkedin": "https://www.linkedin.com/in/amulya-balakrishnan",
             "background": "Former SWE at Zoom, USC CS & Business"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 9000,
                "requirements": [
                    "Strong foundation in Python, JavaScript/TypeScript, or React",
                    "Interest in AI, data visualization, or bioinformatics",
                    "No prior biology background required",
                    "Excited to build at the intersection of AI, biology, and data infrastructure",
                ],
                "description": (
                    "Software Engineer Intern at Novaflow (YC S25)\n\n"
                    "Build features from intuitive React interfaces to optimizing backend "
                    "performance for large-scale genomic data processing. "
                    "Work closely with the founding team.\n\n"
                    "Source: https://www.workatastartup.com/jobs/84315"
                ),
            },
        ],
    },

    # ── Candle (YC F24) ──
    {
        "company_name": "Candle",
        "email": "careers@trycandle.app",
        "name": "Alex Ruber",
        "industry": "AI / Consumer / Social",
        "company_size": "startup",
        "website": "https://www.trycandle.app/",
        "slug": "candle",
        "description": (
            "Candle helps couples and friends grow closer daily in just 5 minutes through "
            "daily prompts, games, shared canvases, date-matching features, and memory tracking.\n\n"
            "YC Batch: F24 | Team Size: 2 | HQ: San Francisco, CA\n"
            "110K MAUs, 46K DAUs at launch."
        ),
        "founders": [
            {"name": "Alex Ruber", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/alex-ruber",
             "background": "iOS/Architecture Engineer at Apple, Flight Systems at NASA JPL"},
            {"name": "Parth Chopra", "title": "Co-Founder & CTO",
             "linkedin": "https://www.linkedin.com/in/parthematics",
             "background": "Ads relevance & ranking at Twitter, sharing/permissions at Asana"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA (Hybrid)",
                "salary_min": 6500,
                "salary_max": 9000,
                "requirements": [
                    "Experience with React Native or Expo",
                    "Strong mobile development skills",
                    "Available for summer 2026",
                    "Passion for consumer products",
                ],
                "description": (
                    "Software Engineer Intern at Candle (YC F24)\n\n"
                    "Compensation: $6,500 - $9,000/month\n\n"
                    "Build features for our mobile app used by hundreds of thousands of people. "
                    "Work on React Native/Expo + Convex backend.\n\n"
                    "Source: https://www.workatastartup.com/companies/candle"
                ),
            },
        ],
    },

    # ── CTGT (YC F24) ──
    {
        "company_name": "CTGT",
        "email": "careers@ctgt.ai",
        "name": "Cyril Gorlla",
        "industry": "AI / Enterprise / SaaS",
        "company_size": "startup",
        "website": "https://www.ctgt.ai/",
        "slug": "ctgt",
        "description": (
            "CTGT safeguards against reputational risk from GenAI across your org by detecting "
            "and eliminating AI hallucinations while ensuring compliance and policy adherence. "
            "We reduce hallucinations by 80-90% and train models 10x faster.\n\n"
            "YC Batch: F24 | Team Size: 7 | HQ: San Francisco\n"
            "Raised $7M from Google's Gradient Ventures. Backed by General Catalyst and Paul Graham."
        ),
        "founders": [
            {"name": "Cyril Gorlla", "title": "CEO & Founder",
             "linkedin": "https://www.linkedin.com/in/cyrilgorlla",
             "background": "Stanford research, UCSD, ICLR publications"},
            {"name": "Trevor Tuttle", "title": "CTO & Founder",
             "linkedin": "https://www.linkedin.com/in/trevor-j-tuttle",
             "background": "Distributed systems for ML workloads, MLsys@UCSD"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing BS in Computer Science or related field",
                    "Experience in JavaScript, Python, or other general-purpose languages",
                    "Ability to clearly communicate technical concepts",
                    "Available for full-time 10-12 week internship (May/June - Aug/Sept 2026)",
                    "Familiarity with Git, AWS, and GCP",
                ],
                "description": (
                    "Software Engineering Intern at CTGT (YC F24)\n\n"
                    "Work on AI safety and reliability tools used by Fortune 500 companies. "
                    "Help shape the behavior of the world's most powerful AI models.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80513"
                ),
            },
        ],
    },

    # ── Speak (YC W17) ──
    {
        "company_name": "Speak",
        "email": "careers@speak.com",
        "name": "Andrew Hsu",
        "industry": "AI / Education / Language Learning",
        "company_size": "startup",
        "website": "https://speak.com/",
        "slug": "speak",
        "description": (
            "Speak is a superhuman, AI-powered language tutor in your pocket. "
            "We compete with Duolingo using deep AI integration for language learning.\n\n"
            "YC Batch: W17 | Team Size: 40 | HQ: San Francisco\n"
            "Reached $1B valuation (Dec 2024). Raised $20M+ in recent rounds."
        ),
        "founders": [
            {"name": "Andrew Hsu", "title": "Co-Founder & CTO",
             "linkedin": "https://www.linkedin.com/in/andrewdhsu",
             "background": "AI/Education technology"},
        ],
        "jobs": [
            {
                "title": "Full-stack Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7000,
                "salary_max": 12000,
                "requirements": [
                    "Strong TypeScript and React skills",
                    "Experience with Supabase, Next.js, or Vercel",
                    "Familiarity with Effect library a plus",
                    "Interest in AI and education technology",
                ],
                "description": (
                    "Full-stack Engineer Intern at Speak (YC W17)\n\n"
                    "Build features for a $1B+ AI language learning platform used by millions. "
                    "Work with TypeScript, Supabase, Next.js, Vercel, and Effect.\n\n"
                    "Source: https://www.workatastartup.com/jobs/82822"
                ),
            },
        ],
    },

    # ── Mesh (YC W25) ──
    {
        "company_name": "Mesh",
        "email": "careers@usemesh.com",
        "name": "Erin Kim",
        "industry": "Fintech / AI / FinOps",
        "company_size": "startup",
        "website": "https://usemesh.com/",
        "slug": "mesh",
        "description": (
            "Mesh automates accruals and month-end close processes for finance teams. "
            "We capture real-time usage signals from AP inboxes, Slack, Teams, and historical "
            "journals to automate 90% of accruals work.\n\n"
            "YC Batch: W25 | Team Size: 3 | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Erin Kim", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/erinkim720/",
             "background": "Scaled Carta's fund accounting from $20M to $100M"},
            {"name": "Nandini Ramakrishnan", "title": "Co-Founder & CTO",
             "linkedin": "https://www.linkedin.com/in/nandiniramakrishnan/",
             "background": "5+ years at Carta, ML patent at eBay, CMU CS & ECE"},
        ],
        "jobs": [
            {
                "title": "AI Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Strong programming skills in Python or TypeScript",
                    "Interest in AI/ML and financial technology",
                    "Ability to work in a fast-paced startup environment",
                    "Available for summer 2026",
                ],
                "description": (
                    "AI Engineer Intern at Mesh (YC W25)\n\n"
                    "Compensation: $6,000 - $8,000/month\n\n"
                    "Build AI systems that automate financial workflows. "
                    "Work directly with the founding team on core product features.\n\n"
                    "Source: https://www.ycombinator.com/companies/mesh-2"
                ),
            },
        ],
    },

    # ── Garage (YC W24) ──
    {
        "company_name": "Garage",
        "email": "careers@joingarage.com",
        "name": "Cedric Foudjet",
        "industry": "AI / Finance / B2B",
        "company_size": "startup",
        "website": "https://joingarage.com/",
        "slug": "garage",
        "description": (
            "Garage builds tools for the next generation of automotive commerce.\n\n"
            "YC Batch: W24 | HQ: New York, NY\n"
            "Will sponsor work visas for qualified candidates."
        ),
        "founders": [
            {"name": "Gwanygha'a Gana", "title": "Co-Founder",
             "linkedin": "https://www.linkedin.com/in/ggana/",
             "background": "BS EE & MS Data Science Georgia Tech, MBA Harvard Business School"},
            {"name": "Cedric Foudjet", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/cedric-foudjet-0470064b/",
             "background": "Ex-founder and VC, MBA Wharton"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Full-stack development skills",
                    "Available for summer 2026",
                    "Will sponsor work visa",
                ],
                "description": (
                    "Software Engineer Intern at Garage (YC W24)\n\n"
                    "Compensation: $6,000 - $8,000/month\n\n"
                    "Full-stack engineering internship in NYC. Will sponsor visa.\n\n"
                    "Source: https://www.workatastartup.com/companies/garage"
                ),
            },
        ],
    },

    # ── SubImage (YC W25) ──
    {
        "company_name": "SubImage",
        "email": "careers@subimage.io",
        "name": "Alex Chantavy",
        "industry": "Cybersecurity / Infrastructure",
        "company_size": "startup",
        "website": "https://subimage.io/",
        "slug": "subimage",
        "description": (
            "SubImage provides infrastructure mapping software giving security teams visibility "
            "on what assets they have and how they relate to each other. "
            "Built around Cartography, an open-source project.\n\n"
            "YC Batch: W25 | Team Size: 5 | HQ: San Francisco, CA\n"
            "Raised $4.2M (October 2025)."
        ),
        "founders": [
            {"name": "Alex Chantavy", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/alexchantavy/",
             "background": "Staff Engineer at Lyft, created Cartography, Microsoft Red Team, NSA"},
            {"name": "Kunaal Sikka", "title": "Co-Founder & President",
             "linkedin": "https://www.linkedin.com/in/kunaals/",
             "background": "Staff at Anthropic, Staff Engineer at Lyft, UW CS in 2 years"},
        ],
        "jobs": [
            {
                "title": "Full Stack Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Full-stack development skills",
                    "Interest in cybersecurity and infrastructure",
                    "Available for summer 2026",
                ],
                "description": (
                    "Full Stack SWE Intern at SubImage (YC W25)\n\n"
                    "Build infrastructure mapping tools used by security teams. "
                    "Founded by former Lyft, Anthropic, and NSA engineers.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80749"
                ),
            },
        ],
    },

    # ── 14.ai (YC W24) ──
    {
        "company_name": "14.ai",
        "email": "careers@14.ai",
        "name": "Marie Schneegans",
        "industry": "AI / Customer Support / Developer Tools",
        "company_size": "startup",
        "website": "https://14.ai/",
        "slug": "14-ai",
        "description": (
            "14.ai is an AI Customer Service Platform and BPO for B2C businesses. "
            "A Zendesk alternative built from the ground up for AI agents.\n\n"
            "YC Batch: W24 | Team Size: 3 | HQ: San Francisco, CA\n"
            "Backed by YC, SV Angel, and founders from Vercel, Slack, Dropbox, and Algolia."
        ),
        "founders": [
            {"name": "Marie Schneegans", "title": "Co-Founder",
             "linkedin": "https://www.linkedin.com/in/marie-schneegans",
             "background": "Co-founded Motif (collaborative docs), design and AI"},
            {"name": "Michael Fester", "title": "Co-Founder",
             "linkedin": "https://www.linkedin.com/in/michaelfester",
             "background": "Co-founded Snips (acquired by Sonos), co-founded Motif"},
        ],
        "jobs": [
            {
                "title": "Full Stack Engineering Internship (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 3000,
                "salary_max": 10000,
                "requirements": [
                    "TypeScript proficiency",
                    "Experience with Supabase, Next.js, or Vercel",
                    "High bar for candidates",
                    "Available now or summer 2026",
                ],
                "description": (
                    "Full Stack Engineering Intern at 14.ai (YC W24)\n\n"
                    "Compensation: $3,000 - $10,000/month\n\n"
                    "Work on CI/CD, telemetry, third-party integrations, and frontend. "
                    "Tech: TypeScript, Supabase, Next.js, Vercel, Effect.\n\n"
                    "Source: https://www.workatastartup.com/jobs/75639"
                ),
            },
            {
                "title": "AI Internship (Now and Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA (Lower Haight)",
                "salary_min": 3000,
                "salary_max": 10000,
                "requirements": [
                    "Direct customer engagement capability",
                    "Ability to work with AI systems and prompt optimization",
                    "Strong builder mentality",
                    "Housing provided at company SF house",
                ],
                "description": (
                    "AI Internship at 14.ai (YC W24)\n\n"
                    "Compensation: $3,000 - $10,000/month + company housing\n\n"
                    "Build and optimize AI agents, refine prompts based on live interactions, "
                    "serve as human liaison for complex situations. "
                    "Intense, tightly-knit team focused on AI customer service.\n\n"
                    "Source: https://www.workatastartup.com/jobs/87062"
                ),
            },
        ],
    },

    # ── Fresco (YC F24) ──
    {
        "company_name": "Fresco",
        "email": "careers@fresco-ai.com",
        "name": "Arvind Veluvali",
        "industry": "AI / Construction Technology",
        "company_size": "startup",
        "website": "https://fresco-ai.com/",
        "slug": "fresco",
        "description": (
            "Fresco is the AI copilot for the $12T construction industry. "
            "We help large general contractors save millions per job by streamlining communication "
            "and eliminating information bottlenecks.\n\n"
            "YC Batch: F24 | Team Size: 2 | HQ: San Francisco, CA\n"
            "Backed by YC, SignalFire, and Bessemer Venture Partners."
        ),
        "founders": [
            {"name": "Arvind Veluvali", "title": "Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/arvindveluvali",
             "background": "NASA scientist, VC experience, Brown BA+MS, dropped out of Wharton"},
            {"name": "Akhil Gupta", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/akhil-climate",
             "background": "GenAI at MIT and TikTok, solar software at Lumen Energy"},
        ],
        "jobs": [
            {
                "title": "AI SWE Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA (In-person, 9am-7pm M-F)",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Shipped meaningful projects (apps, tools, or research)",
                    "Proficiency with React/TypeScript, Node, SQL or willingness to learn",
                    "Interest in construction industry applications",
                    "High ownership mentality with bias toward rapid iteration",
                    "Must relocate to San Francisco",
                    "US citizen or valid work visa",
                ],
                "description": (
                    "AI SWE Intern at Fresco (YC F24)\n\n"
                    "Compensation: $6,000 - $10,000/month for 10-12+ weeks\n\n"
                    "Develop end-to-end features across web and mobile, enhance AI retrieval systems, "
                    "design data models and APIs. Direct mentorship from CEO and CTO.\n\n"
                    "Tech: React+TS, Next.js+TS, Expo (React Native), Postgres+pgvector, "
                    "Prisma, Vercel, AWS, OpenAI GPT-4, RAG systems\n\n"
                    "Source: https://www.workatastartup.com/jobs/80559"
                ),
            },
        ],
    },

    # ── Waypoint Transit (YC W25) ──
    {
        "company_name": "Waypoint Transit",
        "email": "contact@waypointtransit.com",
        "name": "Varun Tandon",
        "industry": "AI / Urban Planning / Government",
        "company_size": "startup",
        "website": "https://waypointtransit.com/",
        "slug": "waypoint-transit",
        "description": (
            "Waypoint Transit automates urban planning so cities can build cheaper and faster. "
            "We generate civil infrastructure studies, delivering plans at 30% of the cost "
            "in a fraction of the time.\n\n"
            "YC Batch: W25 | Team Size: 2 | HQ: San Francisco, CA\n"
            "Working with 10+ municipalities across the US."
        ),
        "founders": [
            {"name": "Varun Tandon", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/vrntandon/",
             "background": "Led applied ML at Microsoft (Copilot, Designer), Stanford BS+MS CS"},
            {"name": "Ryan Johnston", "title": "Co-Founder & CTO",
             "linkedin": "https://www.linkedin.com/in/ryan-johnston-b919a7180/",
             "background": "Chip design at Apple, Stanford BS+MS EE"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Strong software engineering skills",
                    "Interest in AI and urban planning",
                    "Available for summer 2026 (open to other times too)",
                ],
                "description": (
                    "Software Engineering Intern at Waypoint Transit (YC W25)\n\n"
                    "Compensation: $6,000 - $8,000/month\n\n"
                    "Work on real customer-facing projects that shape how cities operate. "
                    "Founded by Stanford engineers from Microsoft and Apple.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80387"
                ),
            },
        ],
    },

    # ── ThirdLayer (YC W25) ──
    {
        "company_name": "ThirdLayer",
        "email": "careers@joindex.com",
        "name": "Regina Lin",
        "industry": "AI / Productivity / Consumer",
        "company_size": "startup",
        "website": "https://joindex.com/",
        "slug": "thirdlayer",
        "description": (
            "ThirdLayer is an applied research lab building interfaces for human-AI collaboration. "
            "Our product Dex is Cursor for everyday operations - an AI copilot for the browser.\n\n"
            "YC Batch: W25 | Team Size: 2 | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Regina Lin", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/reginaclin",
             "background": "Harvard Math + CS, co-founded Contour AI, ecommerce marketplace"},
            {"name": "Kevin Gu", "title": "Co-Founder",
             "linkedin": "https://www.linkedin.com/in/kevinrgu",
             "background": "Harvard Math & Stats, Jump Trading, IBM Research, Meta"},
        ],
        "jobs": [
            {
                "title": "Full-Stack Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Strong React/Next.js and TypeScript foundation",
                    "Experience building and shipping complex web apps or browser extensions",
                    "Familiarity with design systems like Figma",
                    "Open-source contributions and strong UI/UX portfolio preferred",
                ],
                "description": (
                    "Full-Stack Engineer Intern at ThirdLayer (YC W25)\n\n"
                    "Compensation: $6,000 - $10,000/month\n\n"
                    "Build browser extension interfaces, AI-powered features using React/Next.js, "
                    "Python, and SQL. Create integrations with iMessage, Slack, and wearables.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80751"
                ),
            },
        ],
    },

    # ── Swif.ai (YC S20) ──
    {
        "company_name": "Swif.ai",
        "email": "careers@swif.ai",
        "name": "Angelo Huang",
        "industry": "SaaS / Security / Compliance",
        "company_size": "startup",
        "website": "https://www.swif.ai/",
        "slug": "swif-ai",
        "description": (
            "Swif.ai is a real-time device compliance and security platform for Mac, Windows, "
            "and Linux. We enforce policies during work, auto-remediate drift, govern Shadow IT/AI, "
            "and stream audit evidence.\n\n"
            "YC Batch: S20 | Team Size: 20 | HQ: Sunnyvale, CA"
        ),
        "founders": [
            {"name": "Angelo (KC) Huang", "title": "CEO & Founder",
             "linkedin": "https://www.linkedin.com/in/angelokh",
             "background": "Co-founded LeadIQ, managed 50-person remote team"},
        ],
        "jobs": [
            {
                "title": "Full Stack Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "US / Taiwan / Remote",
                "salary_min": 500,
                "salary_max": 2000,
                "requirements": [
                    "Pursuing CS, IT, or related degree",
                    "Strong problem-solving and attention to detail",
                    "Basic understanding of computer systems, networks, and operating systems",
                    "Experience with Golang, Scala, or JavaScript a plus",
                    "Comfortable working 6 days per week",
                ],
                "description": (
                    "Full Stack SWE Intern at Swif.ai (YC S20)\n\n"
                    "Compensation: $500 - $2,000/month (part-time)\n\n"
                    "Build and optimize backend systems, leverage AI-powered coding tools, "
                    "write clean and testable code. Tech: Golang, Scala, JavaScript.\n\n"
                    "Source: https://www.workatastartup.com/jobs/62132"
                ),
            },
        ],
    },

    # ── Crustdata (YC F24) ──
    {
        "company_name": "Crustdata",
        "email": "careers@crustdata.com",
        "name": "Abhilash Chowdhary",
        "industry": "AI / B2B Data / APIs",
        "company_size": "startup",
        "website": "https://crustdata.com/",
        "slug": "crustdata",
        "description": (
            "Crustdata provides real-time B2B data via simple APIs. We build gateway technology "
            "enabling AI agents to access real-time internet data.\n\n"
            "YC Batch: F24 | Team Size: 20 | HQ: San Francisco, CA\n"
            "300+ enterprise customers. Backed by YC, General Catalyst, SV Angel."
        ),
        "founders": [
            {"name": "Abhilash Chowdhary", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/abhilash-chowdhary",
             "background": "Yahoo, Postmates X (Uber), Waymo, IIIT Hyderabad CS"},
            {"name": "Manmohit Grewal", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/manmohitgrewal/",
             "background": "Built data products for D2C and POS, Northeastern CS"},
            {"name": "Chris Pisarski", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/chris-pisarski",
             "background": "Founding team PrivCo, ex-Interim CEO, Cornell"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern - Forward Deployed (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 4000,
                "salary_max": 8000,
                "requirements": [
                    "Undergraduate CS/EE/Math background",
                    "Strong Python and/or TypeScript/JavaScript coding skills",
                    "End-to-end project building experience",
                    "Solid technical fundamentals with fast learning ability",
                    "US citizen or valid work visa",
                ],
                "description": (
                    "SWE Intern (Forward Deployed) at Crustdata (YC F24)\n\n"
                    "Compensation: $4,000 - $8,000/month\n\n"
                    "Build rapid prototypes and POCs for prospects, create demo tooling, "
                    "implement integrations (APIs, pipelines, dashboards), develop AI agents.\n\n"
                    "Tech: Python, TypeScript, JavaScript, SQL, APIs\n\n"
                    "Interview: 30-min intro -> 60-min tech screen -> 60-min in-person -> "
                    "30-min co-founder chat -> Offer\n\n"
                    "Source: https://www.workatastartup.com/jobs/89156"
                ),
            },
        ],
    },

    # ── Bloom (YC X25) ──
    {
        "company_name": "Bloom",
        "email": "careers@bloom.diy",
        "name": "David Oort Alonso",
        "industry": "AI / Mobile / No-Code",
        "company_size": "startup",
        "website": "https://bloom.diy/",
        "slug": "bloom",
        "description": (
            "Bloom lets anyone build and share mobile apps in seconds. "
            "The first AI app builder that lets you create full-stack native apps "
            "directly from your phone, publish to the App Store, and airdrop apps to friends.\n\n"
            "YC Batch: X25 | Team Size: 2 | HQ: Zurich, Switzerland\n"
            "Raised $3.4M from YC and angels from Expo, Convex, and Hugging Face."
        ),
        "founders": [
            {"name": "David Oort Alonso", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/david-oort-alonso",
             "background": "Built award-winning consumer mobile apps"},
            {"name": "Sirian Maathuis", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/sirian-maathuis",
             "background": "Designer and developer, 2+ years mobile app projects"},
        ],
        "jobs": [
            {
                "title": "AI / Full-Stack Student Internship (Winter or Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Zurich, Switzerland",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Fluent in TypeScript, comfortable across the full stack",
                    "Love building (side projects, hackathons, weekends)",
                    "High agency and curiosity with fast learning",
                    "Understanding of user experience for first-time app builders",
                    "Sophomore and above",
                    "US visa NOT required",
                ],
                "description": (
                    "AI / Full-Stack Student Intern at Bloom (YC X25)\n\n"
                    "Compensation: $6,000 - $10,000/month\n\n"
                    "Build AI systems, backend infrastructure, user-facing tools, "
                    "and internal dashboards.\n\n"
                    "Tech: TypeScript, React Native, Expo, Swift, Kotlin, Convex, AI SDK\n\n"
                    "Interview: CEO chat -> CPO chat -> Take-home challenge\n\n"
                    "Source: https://www.workatastartup.com/jobs/82957"
                ),
            },
        ],
    },

    # ── Partcl (YC batch unknown) ──
    {
        "company_name": "Partcl",
        "email": "careers@partcl.com",
        "name": "Partcl Team",
        "industry": "AI / Chip Design / EDA",
        "company_size": "startup",
        "website": "https://partcl.com/",
        "slug": "partcl",
        "description": (
            "Partcl is developing the next generation of chip design automation tools. "
            "Using GPUs and AI, we build design tools that are 1000x faster than legacy options.\n\n"
            "HQ: San Francisco, CA"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "ML Systems Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Experience with PyTorch/Torch",
                    "Rust programming skills",
                    "GPU programming and CUDA experience",
                    "Machine learning fundamentals",
                    "Will sponsor visa",
                ],
                "description": (
                    "ML Systems Intern at Partcl\n\n"
                    "Compensation: $6,000 - $10,000/month\n\n"
                    "Train custom models for optimization problems, build CUDA kernels "
                    "for training and inference, build parsers and data structures, "
                    "integrate LLM interfaces to design tools.\n\n"
                    "Required: Take-home challenge (GitHub repo)\n\n"
                    "Source: https://www.workatastartup.com/jobs/82020"
                ),
            },
        ],
    },

    # ── PearAI (YC F24) ──
    {
        "company_name": "PearAI",
        "email": "careers@trypear.ai",
        "name": "Nang Ang",
        "industry": "AI / Developer Tools",
        "company_size": "startup",
        "website": "https://trypear.ai/",
        "slug": "pearai",
        "description": (
            "PearAI is the AI Code Editor for your next project. "
            "An open-source solution with curated AI tools natively integrated for "
            "effortless AI-powered coding.\n\n"
            "YC Batch: F24 | Team Size: 4 | HQ: New York"
        ),
        "founders": [
            {"name": "Nang Ang", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/nathanang",
             "background": "CMU, IMC Trading, Coinbase, Two Sigma, 150K+ YouTube subscribers"},
            {"name": "Duke Pan", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/dukepan",
             "background": "Meta, Cisco, Tesla Autopilot"},
        ],
        "jobs": [
            {
                "title": "SWE / Marketing Internship (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote",
                "salary_min": 2000,
                "salary_max": 5000,
                "requirements": [
                    "Sophomore/Junior/Senior studying CS, Engineering, or related field",
                    "Funny and passionate, able to create good memes",
                    "Obsessed with coding and making",
                    "Experience running a meme or social media account is a bonus",
                ],
                "description": (
                    "SWE / Marketing Intern at PearAI (YC F24)\n\n"
                    "Open-source AI code editor. Looking for passionate builders who are also "
                    "great at memes and social media. Apply with resume + memes!\n\n"
                    "Source: https://www.workatastartup.com/jobs/75841"
                ),
            },
        ],
    },

    # ── a0.dev (YC W25) ──
    {
        "company_name": "a0.dev",
        "email": "careers@a0.dev",
        "name": "Seth Setse",
        "industry": "AI / Developer Tools / Mobile",
        "company_size": "startup",
        "website": "https://a0.dev/",
        "slug": "a0-dev",
        "description": (
            "a0.dev makes mobile apps using AI. We generate custom React Native projects "
            "to help developers build high-quality apps in days instead of weeks.\n\n"
            "YC Batch: W25 | Team Size: 3 | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Seth Setse", "title": "Co-Founder",
             "linkedin": "https://www.linkedin.com/in/seth-setse-0641b6175",
             "background": "CMU '23, Serial App Developer"},
            {"name": "Ayomide Omolewa", "title": "Co-Founder",
             "linkedin": "https://www.linkedin.com/in/omolewa",
             "background": "Nvidia, Paramount, Google, Lockheed Martin"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 9000,
                "requirements": [
                    "Passionate about mobile app development",
                    "Experience with Next.js or React Native",
                    "Available June - September 2026",
                    "Excited about building an AI platform",
                ],
                "description": (
                    "Software Engineering Intern at a0.dev (YC W25)\n\n"
                    "Implement new features in Next.JS for the a0.dev website, "
                    "test the app creation process, create and launch mobile apps, "
                    "enhance AI models to generate cleaner React Native code.\n\n"
                    "Source: https://www.workatastartup.com/jobs/83361"
                ),
            },
        ],
    },

    # ── Cekura (YC F24) ──
    {
        "company_name": "Cekura",
        "email": "careers@cekura.ai",
        "name": "Tarush Agarwal",
        "industry": "AI / Developer Tools / QA",
        "company_size": "startup",
        "website": "https://www.cekura.ai/",
        "slug": "cekura",
        "description": (
            "Cekura provides Voice AI and Chat AI agents testing and observability. "
            "We automate QA from pre-production simulation to production call monitoring.\n\n"
            "YC Batch: F24 | Team Size: 15 | HQ: San Francisco, CA\n"
            "75+ customers. Raised $2.4M seed (July 2025)."
        ),
        "founders": [
            {"name": "Tarush Agarwal", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/tarush-agarwal-b14851160/",
             "background": "3 years quant finance, ultra-low latency systems, IIT Bombay CS"},
            {"name": "Shashij Gupta", "title": "Co-Founder & CTO",
             "linkedin": "https://www.linkedin.com/in/shashij-gupta-671aa614a",
             "background": "NLP at Google Research, ETH Zurich, IIT Bombay CS"},
            {"name": "Sidhant Kabra", "title": "Co-Founder & President",
             "linkedin": "https://www.linkedin.com/in/sidhantkabra",
             "background": "Consulting Fortune 500 CEOs, edtech 0 to 200K+ users"},
        ],
        "jobs": [
            {
                "title": "AI Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 9000,
                "requirements": [
                    "Strong programming skills",
                    "Interest in AI/ML and voice technology",
                    "Experience with Python or TypeScript",
                    "Available for summer 2026",
                ],
                "description": (
                    "AI Engineer Intern at Cekura (YC F24)\n\n"
                    "Build automated QA tools for AI voice and chat agents. "
                    "Work on simulation, evaluation, and monitoring systems.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80342"
                ),
            },
        ],
    },

    # ── Camfer (YC S24) ──
    {
        "company_name": "Camfer",
        "email": "careers@camfer.dev",
        "name": "Arya Bastani",
        "industry": "AI / Hardware / Manufacturing",
        "company_size": "startup",
        "website": "https://www.camfer.dev/",
        "slug": "camfer",
        "description": (
            "Camfer is the world's first AI mechanical engineer. "
            "An AI CAD tool enabling engineers to create parametric designs using natural language.\n\n"
            "YC Batch: S24 | Team Size: 4 | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Arya Bastani", "title": "Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/arya-bastani/",
             "background": "AI and mechanical engineering"},
            {"name": "Keaton Elvins", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/keatonelvins/",
             "background": "Engineering"},
            {"name": "Roth Vann", "title": "Founder",
             "linkedin": "https://www.linkedin.com/in/rothvann/",
             "background": "Engineering"},
        ],
        "jobs": [
            {
                "title": "Research Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 9000,
                "requirements": [
                    "Strong programming skills",
                    "Interest in AI and CAD/mechanical engineering",
                    "Research experience a plus",
                    "Available for summer 2026",
                ],
                "description": (
                    "Research Intern at Camfer (YC S24)\n\n"
                    "Work on AI-powered CAD tools. Help build the world's first "
                    "AI mechanical engineer using natural language.\n\n"
                    "Source: https://www.workatastartup.com/jobs/71321"
                ),
            },
        ],
    },

    # ── Athelas / Commure (YC S16) ──
    {
        "company_name": "Athelas",
        "email": "careers@athelas.com",
        "name": "Tanay Tandon",
        "industry": "Healthcare / AI",
        "company_size": "enterprise",
        "website": "https://athelas.com",
        "slug": "athelas",
        "description": (
            "Extensible, integrated technology that simplifies health systems. "
            "Athelas (merged with Commure) develops AI solutions for clinical "
            "documentation, provider support tools, and revenue cycle management. "
            "Serves 500,000+ clinicians across hundreds of care sites, processing "
            "$10B+ annually."
        ),
        "founders": [
            {
                "name": "Deepika Bodapati",
                "title": "Co-Founder",
                "linkedin": "https://www.linkedin.com/pub/deepika-bodapati/73/297/102",
            },
            {
                "name": "Tanay Tandon",
                "title": "Co-Founder",
                "linkedin": "https://www.linkedin.com/pub/tanay-tandon/52/452/231",
            },
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco / Mountain View, CA",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Bachelor's or Master's in CS or related field by June 2027",
                    "Proficiency in TypeScript/Node, Python, or Go",
                    "Strong CS fundamentals and debugging skills",
                    "Product sense and builder mentality",
                ],
                "description": (
                    "Software Engineering Intern at Athelas/Commure (YC S16)\n\n"
                    "Design and ship product features across web, mobile, and backend. "
                    "Support clinical workflow platforms serving 500K+ clinicians.\n\n"
                    "Tech Stack: JavaScript, React, TypeScript, Flutter, Python, Flask, "
                    "FastAPI, GCP, AWS, Docker, Kubernetes, PostgreSQL\n\n"
                    "In-office 5 days/week in SF or Mountain View.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80681"
                ),
            },
        ],
    },

    # ── Circleback (YC W24) ──
    {
        "company_name": "Circleback",
        "email": "careers@circleback.ai",
        "name": "Ali Haghani",
        "industry": "AI / Productivity",
        "company_size": "startup",
        "website": "https://circleback.ai",
        "slug": "circleback",
        "description": (
            "AI-powered meeting notes and automations. Circleback builds the "
            "source of truth for everything said at a company — AI meeting notes, "
            "action items, and search across conversations."
        ),
        "founders": [
            {
                "name": "Ali Haghani",
                "title": "Co-Founder & CEO",
                "linkedin": "https://www.linkedin.com/in/alihaghani",
            },
            {
                "name": "Kevin Jacyna",
                "title": "Co-Founder",
                "linkedin": "https://www.linkedin.com/in/kevinjacyna",
            },
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7000,
                "salary_max": 10000,
                "requirements": [
                    "Experience with React, React Native, TypeScript, PostgreSQL",
                    "Hands-on building experience and high attention to detail",
                    "Curiosity about how great products work",
                    "Values ownership, urgency, and software quality",
                ],
                "description": (
                    "Software Engineering Intern at Circleback (YC W24)\n\n"
                    "Build end-to-end features from database models to APIs and UI "
                    "components for web (React), desktop (Electron), and mobile "
                    "(React Native) applications. Enhance product foundations including "
                    "AI outcomes, search, transcription, and performance.\n\n"
                    "Tech Stack: TypeScript, Next.js, React, Tailwind, GCP, Prisma, PostgreSQL\n\n"
                    "Source: https://www.workatastartup.com/jobs/80433"
                ),
            },
        ],
    },

    # ── SID (YC S23) ──
    {
        "company_name": "SID",
        "email": "careers@sid.ai",
        "name": "Maximilian-David Rumpf",
        "industry": "AI / Infrastructure",
        "company_size": "startup",
        "website": "https://www.sid.ai",
        "slug": "sid",
        "description": (
            "AI research lab training models that can retrieve and reason over "
            "any data source. SID makes AI capable of accessing and reasoning "
            "over diverse data beyond internet-available information. Backed by "
            "Y Combinator, Canaan, Rebel, and General Catalyst."
        ),
        "founders": [
            {
                "name": "Maximilian-David Rumpf",
                "title": "Co-Founder & CEO",
                "linkedin": "https://www.linkedin.com/in/maximiliandavid",
            },
            {
                "name": "Lotte Seifert",
                "title": "Co-Founder",
                "linkedin": "https://www.linkedin.com/in/lotte-seifert",
            },
        ],
        "jobs": [
            {
                "title": "Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 10000,
                "requirements": [
                    "Comfort with mathematical concepts and technical backgrounds",
                    "Python proficiency",
                    "Familiarity with RL pipelines for language models",
                    "Experience with torchrun/accelerate/multi-node training",
                    "Ability to work across abstraction layers (PyTorch/CUDA)",
                ],
                "description": (
                    "Research Intern at SID (YC S23)\n\n"
                    "Post-train reasoning into LLMs using GRPO and SFT. Design and "
                    "iterate RL training environments for retrieval across unstructured, "
                    "structured, and web data. Develop next-generation vision-first "
                    "embedding models.\n\n"
                    "Tech Stack: PyTorch, Reinforcement Learning, CUDA, torchrun\n\n"
                    "In-person in San Francisco.\n\n"
                    "Source: https://www.workatastartup.com/jobs/81528"
                ),
            },
        ],
    },

    # ── Cuckoo Labs (YC W25) ──
    {
        "company_name": "Cuckoo Labs",
        "email": "careers@cuckoo.so",
        "name": "Yong Hee Lee",
        "industry": "AI / Sales / Marketing",
        "company_size": "startup",
        "website": "https://www.cuckoo.so",
        "slug": "cuckoo-labs",
        "description": (
            "Real-time AI translator for global sales, marketing, and support. "
            "Instantly learns technical details from conversations and documents, "
            "and interprets into 20+ languages. Customers include Snowflake, "
            "PagerDuty, ClickHouse, dbt Labs, and Weights & Biases."
        ),
        "founders": [
            {
                "name": "Yong Hee Lee",
                "title": "Co-Founder & CEO",
                "linkedin": "https://www.linkedin.com/in/harryyongheelee/",
            },
            {
                "name": "Gunwoo Kim",
                "title": "Co-Founder & CTO",
                "linkedin": "https://www.linkedin.com/in/gunwooterry/",
            },
        ],
        "jobs": [
            {
                "title": "Full Stack Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA / Seoul, KR",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Experience with real-time systems and distributed infrastructure",
                    "Familiarity with AI/ML and web platforms",
                    "Interest in enterprise security and multilingual systems",
                ],
                "description": (
                    "Full Stack Engineering Intern at Cuckoo Labs (YC W25)\n\n"
                    "Scale infrastructure for 1,000+ concurrent multilingual meetings. "
                    "Build resilient fallback systems across Zoom, desktop, and mobile. "
                    "Implement enterprise-grade security (SOC 2 Type II). Extract and "
                    "apply context using RAG with integrations to Notion, HubSpot.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80699"
                ),
            },
        ],
    },
]


def seed_company(session, company_data):
    """Seed a single company with employer, organization, and jobs."""
    company_name = company_data["company_name"]

    # Check if already seeded
    existing = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()
    if existing:
        print(f"  {company_name} already exists (employer_id={existing.id}), skipping...")
        return 0

    # 1. Create Employer
    employer_id = generate_cuid("e_")
    slug = company_data.get("slug", company_name.lower().replace(" ", "-"))
    employer = Employer(
        id=employer_id,
        name=company_data["name"],
        company_name=company_name,
        email=company_data["email"],
        password=get_password_hash(f"{slug}YC!seed2026"),
        industry=company_data.get("industry"),
        company_size=company_data.get("company_size", "startup"),
        is_verified=True,
    )
    session.add(employer)

    # 2. Create Organization
    org_id = generate_cuid("o_")
    organization = Organization(
        id=org_id,
        name=company_name,
        slug=slug,
        website=company_data.get("website"),
        industry=company_data.get("industry"),
        company_size=company_data.get("company_size", "startup"),
        description=company_data.get("description"),
        settings={
            "founders": company_data.get("founders", []),
        },
    )
    session.add(organization)

    # 3. Link employer to organization
    member_id = generate_cuid("tm_")
    membership = OrganizationMember(
        id=member_id,
        organization_id=org_id,
        employer_id=employer_id,
        role=OrganizationRole.OWNER,
    )
    session.add(membership)

    # 4. Create all jobs
    job_count = 0
    for job_data in company_data.get("jobs", []):
        job_id = generate_cuid("j_")
        job = Job(
            id=job_id,
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
        salary = f"${job_data.get('salary_min', 0):,} - ${job_data.get('salary_max', 0):,}/mo"
        print(f"    Job: {job.title} ({salary})")

    print(f"  Created {company_name}: {job_count} intern job(s)")
    return job_count


def main():
    print("=" * 60)
    print("Seeding YC Startup Intern Jobs")
    print("=" * 60)

    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    total_new_jobs = 0

    try:
        for company_data in COMPANIES:
            company_name = company_data["company_name"]
            founders = company_data.get("founders", [])
            print(f"\n[{company_name}]")
            if founders:
                for f in founders:
                    print(f"  Founder: {f['name']} ({f.get('title', '')})")
                    if f.get("linkedin"):
                        print(f"    LinkedIn: {f['linkedin']}")

            new_jobs = seed_company(session, company_data)
            total_new_jobs += new_jobs

        session.commit()

        # Print summary
        total_jobs = session.query(Job).count()
        total_employers = session.query(Employer).count()
        print(f"\n{'=' * 60}")
        print(f"Seeded {total_new_jobs} new intern jobs across {len(COMPANIES)} companies")
        print(f"Database totals: {total_employers} employers, {total_jobs} jobs")
        print(f"{'=' * 60}")

    except Exception as e:
        session.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
