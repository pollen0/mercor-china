#!/usr/bin/env python3
"""
Batch 2: Additional YC startup intern jobs from Work at a Startup.

Usage:
    cd apps/api
    python -m scripts.seed_yc_batch2

This adds new companies AND new jobs for existing companies that were
missed in batch 1.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.employer import (
    Employer, Job, Organization, OrganizationMember,
    Vertical, RoleType, OrganizationRole,
)
from app.utils.auth import get_password_hash
from app.config import settings


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ─────────────────────────────────────────────────────────────
# NEW companies not yet in the database
# ─────────────────────────────────────────────────────────────

NEW_COMPANIES = [
    # ── Sonauto (YC S24) ──
    {
        "company_name": "Sonauto",
        "email": "careers@sonauto.ai",
        "name": "Mikey Shulman",
        "industry": "AI / Music / Generative Models",
        "company_size": "startup",
        "website": "https://sonauto.ai",
        "slug": "sonauto",
        "description": (
            "Sonauto builds Melodia, a generative music model that creates full songs "
            "from text prompts. Distributed training at the scale of hundreds of H100s "
            "on diffusion models, GANs, language models, and more.\n\n"
            "YC Batch: S24 | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Mikey Shulman", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/mikey-shulman/"},
            {"name": "Hayden Housen", "title": "Co-Founder",
             "linkedin": ""},
            {"name": "Ryan Tremblay", "title": "Co-Founder",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "ML Engineer / Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Strong PyTorch and deep learning experience",
                    "Experience with diffusion models, GANs, or language models",
                    "Distributed training experience (multi-GPU/multi-node)",
                    "Interest in generative audio/music",
                ],
                "description": (
                    "ML Engineer / Research Intern at Sonauto (YC S24)\n\n"
                    "Lead research efforts for improving the song and audio quality of "
                    "generative music models. Work on distributed training at the scale "
                    "of hundreds of H100s on diffusion models, GANs, language models.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80519"
                ),
            },
        ],
    },

    # ── Cloudglue (YC W25) ──
    {
        "company_name": "Cloudglue",
        "email": "careers@cloudglue.dev",
        "name": "Cloudglue Team",
        "industry": "AI / Video / Infrastructure",
        "company_size": "startup",
        "website": "https://cloudglue.dev",
        "slug": "cloudglue",
        "description": (
            "Cloudglue builds foundational infrastructure that enables AI to understand "
            "videos. APIs for developers to add video search, multi-video chat, and "
            "structured data extraction to their applications.\n\n"
            "YC Batch: W25 | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Amy", "title": "Co-Founder", "linkedin": ""},
            {"name": "Kevin", "title": "Co-Founder", "linkedin": ""},
            {"name": "Matt", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Full-Stack AI Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA / Remote (US)",
                "salary_min": 6500,
                "salary_max": 8500,
                "requirements": [
                    "Full-stack development experience",
                    "Interest in AI/ML and video processing",
                    "Experience with Python, TypeScript, or React",
                    "Available for summer 2026",
                ],
                "description": (
                    "Full-Stack AI Engineer Intern at Cloudglue (YC W25)\n\n"
                    "Build foundational infrastructure for AI video understanding. "
                    "Work on APIs for video search, multi-video chat, and structured "
                    "data extraction.\n\n"
                    "Compensation: $6,500 - $8,500/month\n\n"
                    "Source: https://www.workatastartup.com/jobs/80989"
                ),
            },
        ],
    },

    # ── Ember (YC W25) ──
    {
        "company_name": "Ember",
        "email": "careers@ember.health",
        "name": "Ember Team",
        "industry": "Healthcare / Operations",
        "company_size": "startup",
        "website": "https://ember.health",
        "slug": "ember",
        "description": (
            "Ember streamlines healthcare revenue cycle management (RCM) with "
            "AI-powered tools. Helping healthcare organizations improve billing "
            "efficiency and reduce claim denials.\n\n"
            "YC Batch: F24 | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Charlene Wang", "title": "Co-Founder",
             "linkedin": ""},
            {"name": "Warren Wang", "title": "Co-Founder",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Full Stack Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Full-stack development experience",
                    "Interest in healthcare technology",
                    "Experience with modern web frameworks",
                    "Available for summer 2026",
                ],
                "description": (
                    "Full Stack Engineering Intern at Ember (YC W25)\n\n"
                    "Build and ship features across the full stack for healthcare "
                    "operations platform.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80610"
                ),
            },
        ],
    },

    # ── Promptless (YC W25) ──
    {
        "company_name": "Promptless",
        "email": "careers@promptless.ai",
        "name": "Promptless Team",
        "industry": "AI / Enterprise Software",
        "company_size": "startup",
        "website": "https://promptless.ai",
        "slug": "promptless",
        "description": (
            "Promptless builds AI teammates that combine context-aware agents and "
            "embedded user experiences to deliver AI products accessible to everyone.\n\n"
            "YC Batch: W25 | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Frances", "title": "Co-Founder", "linkedin": ""},
            {"name": "Prithvi", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 15000,
                "requirements": [
                    "Strong programming skills in Python or TypeScript",
                    "Interest in AI agents and enterprise software",
                    "Experience with web development frameworks",
                    "Available for summer 2026",
                ],
                "description": (
                    "Software Engineering Intern at Promptless (YC W25)\n\n"
                    "Build AI teammates that combine context-aware agents and embedded "
                    "user experiences. Work on cutting-edge AI products.\n\n"
                    "Compensation: $6,000 - $15,000/month\n\n"
                    "Source: https://www.workatastartup.com/jobs/80434"
                ),
            },
        ],
    },

    # ── Tandem (YC S24) ──
    {
        "company_name": "Tandem",
        "email": "careers@withtandem.com",
        "name": "Sean Miller",
        "industry": "Real Estate / Marketplace / AI",
        "company_size": "startup",
        "website": "https://withtandem.com",
        "slug": "tandem",
        "description": (
            "Tandem is an AI-powered office leasing marketplace that matches companies "
            "with their perfect office. Making the commercial real estate process faster "
            "and more transparent. Founded by Stanford alumni.\n\n"
            "YC Batch: S24 | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Sean Miller", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Rafi Sands", "title": "Co-Founder",
             "linkedin": ""},
            {"name": "Brendan Suh", "title": "Co-Founder",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Strong programming fundamentals",
                    "Experience with modern web technologies",
                    "Interest in marketplaces and real estate tech",
                    "Available for summer 2026",
                ],
                "description": (
                    "Engineering Intern at Tandem (YC S24)\n\n"
                    "Build an AI-powered office leasing marketplace. Work across "
                    "the full stack on features that match companies with their "
                    "perfect office space.\n\n"
                    "Compensation: $5,000 - $8,000/month\n\n"
                    "Source: https://www.workatastartup.com/jobs/80518"
                ),
            },
        ],
    },

    # ── Gale (YC W25) ──
    {
        "company_name": "Gale",
        "email": "careers@gale.dev",
        "name": "Gale Team",
        "industry": "AI / Developer Tools",
        "company_size": "startup",
        "website": "https://gale.dev",
        "slug": "gale",
        "description": (
            "Gale builds developer tools for modern software teams.\n\n"
            "YC Batch: W25 | Remote (US/Canada)"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "Software Engineer Intern (Jan-Apr 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote (US / Canada)",
                "salary_min": 4000,
                "salary_max": 7000,
                "requirements": [
                    "16-week availability (Jan-Apr 2026)",
                    "Strong programming skills",
                    "Experience with modern web frameworks",
                ],
                "description": (
                    "Software Engineer Intern at Gale (YC W25)\n\n"
                    "16-week internship building developer tools. Remote position "
                    "available in US or Canada.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80843"
                ),
            },
        ],
    },

    # ── SafetyKit (YC S24) ──
    {
        "company_name": "SafetyKit",
        "email": "careers@safetykit.com",
        "name": "SafetyKit Team",
        "industry": "Trust & Safety / AI",
        "company_size": "startup",
        "website": "https://safetykit.com",
        "slug": "safetykit",
        "description": (
            "SafetyKit builds trust and safety tools for online platforms. "
            "AI-powered content moderation and policy enforcement.\n\n"
            "YC Batch: S24 | HQ: San Francisco"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "Full Stack Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Full-stack development experience",
                    "Interest in trust & safety",
                    "Experience with React or similar frameworks",
                    "Available for summer 2026",
                ],
                "description": (
                    "Full Stack Engineer Intern at SafetyKit (YC S24)\n\n"
                    "Build trust and safety tools for online platforms. Work on "
                    "AI-powered content moderation systems.\n\n"
                    "Source: https://www.workatastartup.com/jobs/75704"
                ),
            },
        ],
    },

    # ── Stack Auth (YC W25) ──
    {
        "company_name": "Stack Auth",
        "email": "careers@stack-auth.com",
        "name": "Stack Auth Team",
        "industry": "Developer Tools / Authentication",
        "company_size": "startup",
        "website": "https://stack-auth.com",
        "slug": "stack-auth",
        "description": (
            "Stack Auth is an open-source authentication and user management platform. "
            "Easy to set up, customizable, and developer-friendly.\n\n"
            "YC Batch: W25 | HQ: San Francisco"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "SWE Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Strong programming skills in TypeScript or Python",
                    "Interest in authentication/security",
                    "Open-source contribution experience a plus",
                    "Available for summer 2026",
                ],
                "description": (
                    "SWE Intern at Stack Auth (YC W25)\n\n"
                    "Build open-source authentication and user management tools. "
                    "Work on developer-facing infrastructure.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80350"
                ),
            },
        ],
    },

    # ── Bucket Robotics (YC S24) ──
    {
        "company_name": "Bucket Robotics",
        "email": "careers@bucketrobotics.com",
        "name": "Bucket Robotics Team",
        "industry": "Robotics / AI / Computer Vision",
        "company_size": "startup",
        "website": "https://bucketrobotics.com",
        "slug": "bucket-robotics",
        "description": (
            "Bucket Robotics builds cutting-edge robotics and vision systems for "
            "industrial applications. AI-driven defect detection and robotic inspection.\n\n"
            "YC Batch: S24 | HQ: San Francisco / Pittsburgh"
        ),
        "founders": [
            {"name": "Matt Puchalski", "title": "Co-Founder & CEO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Robotics Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Experience with robotics or computer vision",
                    "Python programming and deep learning familiarity",
                    "Interest in deploying AI to edge hardware",
                    "Hands-on prototyping skills",
                ],
                "description": (
                    "Robotics Engineering Intern at Bucket Robotics (YC S24)\n\n"
                    "Gain hands-on experience building cutting-edge robotics and vision "
                    "systems. Contribute to AI-driven defect detection projects, prototype "
                    "computer vision pipelines, write robotics software in Python, and "
                    "deploy models to edge AI hardware.\n\n"
                    "Source: https://www.workatastartup.com/jobs/73633"
                ),
            },
        ],
    },

    # ── CircuitHub (YC S14) ──
    {
        "company_name": "CircuitHub",
        "email": "careers@circuithub.com",
        "name": "CircuitHub Team",
        "industry": "Hardware / Robotics / Manufacturing",
        "company_size": "startup",
        "website": "https://circuithub.com",
        "slug": "circuithub",
        "description": (
            "CircuitHub is reshaping electronics manufacturing with The Grid — a "
            "factory-scale robotics platform for efficient small-batch, high-mix "
            "electronics assembly. Raised $20M from YC and Google Ventures.\n\n"
            "YC Batch: S14 | HQ: South Deerfield, MA"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "Full-Stack Robotics Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "South Deerfield, MA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Hands-on experience building robots or automation systems",
                    "Skills in mechanical CAD, Python or C++",
                    "Basic electronics knowledge and debugging skills",
                    "Available 10-12 weeks summer 2026",
                ],
                "description": (
                    "Full-Stack Robotics Engineer Intern at CircuitHub (YC S14)\n\n"
                    "Embedded in the factory, working on real hardware and software "
                    "systems. Tune camera networks, debug robot reliability, prototype "
                    "mechanical and software fixes, run experiments to push throughput.\n\n"
                    "10-12 weeks on-site in Western Massachusetts.\n\n"
                    "Source: https://www.workatastartup.com/jobs/80377"
                ),
            },
        ],
    },

    # ── Chunkr (YC W24) ──
    {
        "company_name": "Chunkr",
        "email": "careers@chunkr.ai",
        "name": "Chunkr Team",
        "industry": "AI / Developer Tools / Document Processing",
        "company_size": "startup",
        "website": "https://chunkr.ai",
        "slug": "chunkr",
        "description": (
            "Chunkr builds essential vision infrastructure for developers to unlock "
            "documents for AI. Supports teams in finance, healthcare, gov-tech, "
            "manufacturing, e-commerce, and dev-tools.\n\n"
            "YC Batch: W24 | HQ: San Francisco"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Experience with TypeScript, Python, or Rust",
                    "React front-end development skills",
                    "Interest in document processing and AI",
                    "Open-source contribution experience a plus",
                ],
                "description": (
                    "Software Engineer Intern at Chunkr (YC W24)\n\n"
                    "Develop and maintain SDKs and internal tools in TypeScript, Python, "
                    "and Rust. Enhance the React-based front-end. Build data pipelines "
                    "for document processing.\n\n"
                    "Source: https://www.workatastartup.com/jobs/75697"
                ),
            },
        ],
    },

    # ── Nixo (YC W25) ──
    {
        "company_name": "Nixo",
        "email": "careers@nixo.dev",
        "name": "Nixo Team",
        "industry": "AI / Developer Tools / Infrastructure",
        "company_size": "startup",
        "website": "https://nixo.dev",
        "slug": "nixo",
        "description": (
            "Nixo builds infrastructure for forward deployed engineers, providing "
            "FDEs the tools to make scaling customer deployments fast, organized, "
            "and repeatable.\n\n"
            "YC Batch: W25 | HQ: San Francisco"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "AI Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Strong programming skills in Python or TypeScript",
                    "Interest in AI and infrastructure tooling",
                    "Experience with cloud platforms",
                    "Available for summer 2026",
                ],
                "description": (
                    "AI Engineering Intern at Nixo (YC W25)\n\n"
                    "Build infrastructure tools for forward deployed engineers. "
                    "Help make scaling customer deployments fast and repeatable.\n\n"
                    "Source: https://www.workatastartup.com/jobs/84385"
                ),
            },
        ],
    },

    # ── Yondu (YC W24) ──
    {
        "company_name": "Yondu",
        "email": "careers@yondu.ai",
        "name": "Yondu Team",
        "industry": "Robotics / Logistics / AI",
        "company_size": "startup",
        "website": "https://yondu.ai",
        "slug": "yondu",
        "description": (
            "Yondu creates the robotic workforce of the future starting with logistics "
            "automation. Deploying humanoid robots in the first flexible, drop-in picking "
            "automation solution designed for 3PLs. Founded by MIT students.\n\n"
            "YC Batch: W24 | HQ: Gardena, CA (Los Angeles)"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "Robotics Software Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Gardena, CA (Los Angeles)",
                "salary_min": 4000,
                "salary_max": 10000,
                "requirements": [
                    "Experience with robotics software (ROS, Python, C++)",
                    "Interest in humanoid robots and warehouse automation",
                    "Hands-on prototyping experience",
                    "Available for summer 2026",
                ],
                "description": (
                    "Robotics Software Intern at Yondu (YC W24)\n\n"
                    "Work hands-on with humanoid robots deployed autonomously in warehouses. "
                    "Build software for the first flexible, drop-in picking automation "
                    "solution designed for 3PLs.\n\n"
                    "Compensation: $4,000 - $10,000/month\n\n"
                    "Source: https://www.ycombinator.com/companies/yondu/jobs"
                ),
            },
            {
                "title": "Robotics Hardware Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Gardena, CA (Los Angeles)",
                "salary_min": 4000,
                "salary_max": 10000,
                "requirements": [
                    "Mechanical or electrical engineering background",
                    "Experience with hardware prototyping",
                    "Interest in humanoid robots",
                    "Available for summer 2026",
                ],
                "description": (
                    "Robotics Hardware Intern at Yondu (YC W24)\n\n"
                    "Design and build hardware for humanoid robots deployed in "
                    "warehouse environments. Work at the office and 3PL warehouse "
                    "in Gardena, LA County.\n\n"
                    "Compensation: $4,000 - $10,000/month\n\n"
                    "Source: https://www.ycombinator.com/companies/yondu/jobs"
                ),
            },
        ],
    },

    # ── Mosaic (YC W25) ──
    {
        "company_name": "Mosaic",
        "email": "careers@mosaic.so",
        "name": "Mosaic Team",
        "industry": "AI / Video Editing / Creative Tools",
        "company_size": "startup",
        "website": "https://mosaic.so",
        "slug": "mosaic-video",
        "description": (
            "Mosaic is an agentic video editing platform — a canvas where anyone can "
            "create and run multimodal video editing agents in a node-based interface. "
            "Built by ex-Tesla engineers. Won $25K grand prize (1st/6,400) in Google "
            "Gemini Kaggle competition and SaaStr AI Pitch.\n\n"
            "YC Batch: W25 | HQ: San Francisco"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "Full Stack Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8500,
                "requirements": [
                    "Full-stack development experience",
                    "Interest in video processing and AI",
                    "Experience with Python, TypeScript, or React",
                    "Available for summer 2026",
                ],
                "description": (
                    "Full Stack Engineering Intern at Mosaic (YC W25)\n\n"
                    "Accelerate the development of an agentic video editing paradigm. "
                    "Build scaleable pipelines around video processing and inference. "
                    "Create thoughtful evals and help make high-level design and product "
                    "decisions.\n\n"
                    "Compensation: $5,000 - $8,500/month\n\n"
                    "Source: https://www.workatastartup.com/jobs/75700"
                ),
            },
        ],
    },

    # ── Browser Use (YC W25) ──
    {
        "company_name": "Browser Use",
        "email": "careers@browseruse.com",
        "name": "Browser Use Team",
        "industry": "AI / Browser Automation / Open Source",
        "company_size": "startup",
        "website": "https://browseruse.com",
        "slug": "browser-use",
        "description": (
            "Browser Use enables AI to control your browser. The biggest open-source "
            "project in the browser automation space. Interns work from the SF HackerHouse.\n\n"
            "YC Batch: W25 | HQ: San Francisco"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Strong programming skills in Python or TypeScript",
                    "Interest in browser automation and AI agents",
                    "Open-source contribution experience a plus",
                    "Available for summer 2026",
                ],
                "description": (
                    "Software Engineering Intern at Browser Use (YC W25)\n\n"
                    "Work on the biggest open-source browser automation project. "
                    "Join the HackerHouse in SF and build AI that controls browsers.\n\n"
                    "Source: https://www.workatastartup.com/jobs/75451"
                ),
            },
        ],
    },

    # ── CreativeMode (YC S24) ──
    {
        "company_name": "CreativeMode",
        "email": "careers@creativemode.gg",
        "name": "Wilson Spearman",
        "industry": "Gaming / AI / UGC",
        "company_size": "startup",
        "website": "https://creativemode.gg",
        "slug": "creativemode",
        "description": (
            "CreativeMode uses AI to supercharge the creation of Minecraft mods and UGC. "
            "Building tools that let anyone create game content with AI assistance. "
            "Founded by MIT and CMU alumni, ex-Crusoe engineers.\n\n"
            "YC Batch: S24 | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Wilson Spearman", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Jeffrey", "title": "Co-Founder & CTO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Growth Hacking Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.MARKETING_ASSOCIATE,
                "location": "San Francisco, CA",
                "salary_min": 3000,
                "salary_max": 6000,
                "requirements": [
                    "Interest in growth marketing and gaming communities",
                    "Analytical mindset with data-driven approach",
                    "Experience with social media or content marketing",
                    "Available for summer 2026",
                ],
                "description": (
                    "Growth Hacking Intern at CreativeMode (YC S24)\n\n"
                    "Drive user acquisition and growth for AI-powered Minecraft mod "
                    "creation tools. Work on campaigns, community building, and "
                    "growth experiments.\n\n"
                    "Source: https://www.workatastartup.com/jobs/79799"
                ),
            },
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5800,
                "salary_max": 7500,
                "requirements": [
                    "Strong programming skills in Python or TypeScript",
                    "Interest in gaming, AI, or UGC platforms",
                    "Experience with web development",
                    "Available for summer 2026",
                ],
                "description": (
                    "Software Engineering Intern at CreativeMode (YC S24)\n\n"
                    "Build AI-powered tools for Minecraft mod creation. Work on "
                    "the platform that lets anyone create game content with AI.\n\n"
                    "Compensation: $5,800 - $7,500/month\n\n"
                    "Source: https://www.workatastartup.com/jobs/79799"
                ),
            },
        ],
    },

    # ── Conductor Quantum (YC W25) ──
    {
        "company_name": "Conductor Quantum",
        "email": "careers@conductorquantum.com",
        "name": "Conductor Quantum Team",
        "industry": "Quantum Computing / AI / Hardware",
        "company_size": "startup",
        "website": "https://conductorquantum.com",
        "slug": "conductor-quantum",
        "description": (
            "Conductor Quantum builds quantum computers on silicon chips using AI. "
            "Pushing the boundaries of quantum computing hardware.\n\n"
            "YC Batch: W25 | HQ: San Francisco"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Strong STEM background (physics, CS, or EE)",
                    "Interest in quantum computing",
                    "Programming experience in Python or C++",
                    "Available for summer 2026",
                ],
                "description": (
                    "Intern at Conductor Quantum (YC W25)\n\n"
                    "Work on quantum computers built on silicon chips using AI. "
                    "Contribute to cutting-edge quantum computing research and development.\n\n"
                    "Source: https://www.ycombinator.com/companies/conductor-quantum"
                ),
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────
# Additional jobs for companies already in the database
# ─────────────────────────────────────────────────────────────

ADDITIONAL_JOBS = [
    # Speak: new job - AI Product Engineer Intern
    {
        "company_name": "Speak",
        "jobs": [
            {
                "title": "AI Product Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 10000,
                "requirements": [
                    "Experience with AI/ML product development",
                    "Full-stack development skills",
                    "Interest in language learning and education",
                    "Available for summer 2026",
                ],
                "description": (
                    "AI Product Engineer Intern at Speak (YC W18)\n\n"
                    "Build innovative AI-powered product experiences for language "
                    "learning. Work hands-on with cutting-edge Language Learning Models.\n\n"
                    "Source: https://www.workatastartup.com/jobs/82823"
                ),
            },
        ],
    },

    # Nowadays: Product Engineer Intern + Marketing Intern
    {
        "company_name": "Nowadays",
        "jobs": [
            {
                "title": "Product Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "CS student or new grad (graduating Spring 2026 or earlier)",
                    "Experience with React, Next.js, or similar",
                    "Product-minded with strong design sense",
                    "Full-time in-person at SF office",
                ],
                "description": (
                    "Product Engineer Intern at Nowadays (YC S23)\n\n"
                    "Build and shape products that customers interact with daily. "
                    "Own new features end-to-end on the AI event planning platform.\n\n"
                    "Source: https://www.workatastartup.com/jobs/78952"
                ),
            },
            {
                "title": "Marketing Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.MARKETING_ASSOCIATE,
                "location": "San Francisco, CA",
                "salary_min": 4000,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing degree in Marketing, Communications, or Business",
                    "Graduating Spring 2026 or earlier",
                    "Experience with content creation and social media",
                    "Full-time in-person at SF office",
                ],
                "description": (
                    "Marketing Intern at Nowadays (YC S23)\n\n"
                    "Shape the brand and drive company growth. Launch campaigns "
                    "and create content for blog, social media, case studies, "
                    "and newsletters.\n\n"
                    "Source: https://www.workatastartup.com/jobs/78953"
                ),
            },
        ],
    },

    # Crustdata: Forward Deployed SWE Intern
    {
        "company_name": "Crustdata",
        "jobs": [
            {
                "title": "Software Engineering Intern - Forward Deployed (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 9000,
                "requirements": [
                    "Strong programming skills",
                    "Customer-facing communication skills",
                    "Interest in AI agents and data infrastructure",
                    "Available for summer 2026",
                ],
                "description": (
                    "Software Engineering Intern (Forward Deployed) at Crustdata\n\n"
                    "Work as a technical partner to revenue and product teams. Build "
                    "prototypes and customer integrations. Ship real things that "
                    "customers use, working directly with founders.\n\n"
                    "Source: https://www.workatastartup.com/jobs/89156"
                ),
            },
        ],
    },

    # 14.ai: AI Internship
    {
        "company_name": "14.ai",
        "jobs": [
            {
                "title": "AI Internship (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 9000,
                "requirements": [
                    "Experience with AI/ML and modern AI frameworks",
                    "Strong programming skills in Python or TypeScript",
                    "Interest in enterprise AI applications",
                    "Available now or summer 2026",
                ],
                "description": (
                    "AI Internship at 14.ai (YC W24)\n\n"
                    "Work on AI-powered enterprise tools. Build and deploy AI "
                    "features using TypeScript, Supabase, Next.js.\n\n"
                    "Source: https://www.workatastartup.com/jobs/87062"
                ),
            },
        ],
    },
]


def seed_new_company(session, company_data):
    """Seed a brand new company with employer, organization, and jobs."""
    company_name = company_data["company_name"]

    existing = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()
    if existing:
        print(f"  {company_name} already exists, skipping...")
        return 0

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

    org_id = generate_cuid("o_")
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

    member_id = generate_cuid("tm_")
    membership = OrganizationMember(
        id=member_id,
        organization_id=org_id,
        employer_id=employer_id,
        role=OrganizationRole.OWNER,
    )
    session.add(membership)

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

    print(f"  Created {company_name}: {job_count} job(s)")
    return job_count


def add_jobs_to_existing(session, entry):
    """Add new jobs to a company that already exists in the DB."""
    company_name = entry["company_name"]
    employer = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()

    if not employer:
        print(f"  WARNING: {company_name} not found in DB, skipping additional jobs")
        return 0

    existing_titles = {
        j.title for j in session.query(Job).filter(Job.employer_id == employer.id).all()
    }

    job_count = 0
    for job_data in entry.get("jobs", []):
        if job_data["title"] in existing_titles:
            print(f"    {job_data['title']} already exists, skipping...")
            continue

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
            employer_id=employer.id,
            is_active=True,
        )
        session.add(job)
        job_count += 1
        salary = f"${job_data.get('salary_min', 0):,} - ${job_data.get('salary_max', 0):,}/mo"
        print(f"    NEW Job: {job.title} ({salary})")

    if job_count:
        print(f"  Added {job_count} new job(s) to {company_name}")
    else:
        print(f"  No new jobs needed for {company_name}")
    return job_count


def main():
    print("=" * 60)
    print("Seeding YC Intern Jobs — Batch 2")
    print("=" * 60)

    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    total_new = 0

    try:
        # Phase 1: Add new companies
        print("\n--- Phase 1: New Companies ---")
        for company_data in NEW_COMPANIES:
            company_name = company_data["company_name"]
            founders = company_data.get("founders", [])
            print(f"\n[{company_name}]")
            if founders:
                for f in founders:
                    print(f"  Founder: {f['name']} ({f.get('title', '')})")
                    if f.get("linkedin"):
                        print(f"    LinkedIn: {f['linkedin']}")
            total_new += seed_new_company(session, company_data)

        # Phase 2: Add jobs to existing companies
        print("\n--- Phase 2: Additional Jobs for Existing Companies ---")
        for entry in ADDITIONAL_JOBS:
            print(f"\n[{entry['company_name']}]")
            total_new += add_jobs_to_existing(session, entry)

        session.commit()

        total_jobs = session.query(Job).count()
        total_employers = session.query(Employer).count()
        print(f"\n{'=' * 60}")
        print(f"Batch 2: Added {total_new} new jobs")
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
