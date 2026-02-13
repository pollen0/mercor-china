# Seed Jobs from VC Job Boards — Claude Code Agent Guide

## Overview

This guide tells a Claude Code instance how to scrape intern job listings from a VC firm's job board and seed them into the Pathway database. Each agent works on ONE VC firm and produces ONE isolated seed script.

## Quick Start (copy this as the Claude Code prompt)

```
You are seeding intern job data into the Pathway platform database.

YOUR ASSIGNED VC FIRM: [FIRM_NAME]
YOUR ASSIGNED JOB BOARD URL: [URL]
YOUR SCRIPT ID: [SHORT_ID, e.g. "a16z", "greylock", "sequoia", "neo", "kpcb"]

Follow the instructions in:
/Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/SEED_JOBS_GUIDE.md

Read that file first, then execute every step. Do NOT deviate from the schema or naming conventions.
```

---

## Step-by-Step Process

### Step 1: Read the template and understand the schema

Read these files first:
```
/Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py
/Users/paullin/Desktop/mercor china/pathway/apps/api/app/models/employer.py
```

The template has the exact Python structure you must use. Do NOT improvise the DB schema.

### Step 2: Scrape the job board

Use `WebSearch` and `WebFetch` to find all **US-based intern** job listings.

**Search strategy** (in this order):
1. `WebSearch: site:[jobboard_domain] intern` — get overview
2. `WebFetch` on the main intern/jobs listing page
3. `WebSearch: site:[jobboard_domain] intern 2025 OR 2026` — find more
4. For each company found, `WebFetch` its individual job page to get details

**Data to collect per company:**
| Field | Required | Example |
|-------|----------|---------|
| company_name | YES | "Cloudglue" |
| email | YES (can be careers@domain) | "careers@cloudglue.dev" |
| name | YES (founder or "Team") | "Amy Chen" |
| industry | YES | "AI / Video / Infrastructure" |
| website | YES | "https://cloudglue.dev" |
| slug | YES (lowercase, hyphens) | "cloudglue" |
| description | YES (2-4 sentences + batch/HQ) | "Cloudglue builds..." |
| founders[] | BEST EFFORT | [{name, title, linkedin}] |

**Data to collect per job:**
| Field | Required | Example |
|-------|----------|---------|
| title | YES (include "Summer 2026" etc.) | "SWE Intern (Summer 2026)" |
| vertical | YES (enum) | Vertical.SOFTWARE_ENGINEERING |
| role_type | YES (enum) | RoleType.SOFTWARE_ENGINEER |
| location | YES | "San Francisco, CA" |
| salary_min | YES (monthly USD integer) | 5000 |
| salary_max | YES (monthly USD integer) | 8000 |
| requirements | YES (list of 3-5 strings) | ["Strong Python...", ...] |
| description | YES (include source URL) | "SWE Intern at...\n\nSource: URL" |

### Step 3: Filter rules

- **US-based only** — skip India, Europe, Singapore, etc.
- **Intern/internship only** — skip full-time roles
- **No duplicates** — check existing DB companies before adding
- If salary is not listed, estimate based on similar roles ($4,000-$8,000/mo is typical)

### Step 4: Map to correct enums

```python
# Verticals
Vertical.SOFTWARE_ENGINEERING  # SWE, full-stack, frontend, backend, embedded, DevOps, robotics
Vertical.DATA                  # ML, data science, data engineering, AI research
Vertical.PRODUCT               # PM, growth, marketing, business ops
Vertical.DESIGN                # UX, UI, product design
Vertical.FINANCE               # Finance, accounting, IB

# Role types (most common for interns)
RoleType.SOFTWARE_ENGINEER     # Generic SWE, full-stack
RoleType.FRONTEND_ENGINEER     # Frontend-specific
RoleType.BACKEND_ENGINEER      # Backend-specific
RoleType.EMBEDDED_ENGINEER     # Robotics, hardware, embedded
RoleType.ML_ENGINEER           # ML, AI research
RoleType.DATA_SCIENTIST        # Data science
RoleType.DATA_ENGINEER         # Data pipelines
RoleType.PRODUCT_MANAGER       # PM
RoleType.MARKETING_ASSOCIATE   # Marketing, growth
RoleType.PRODUCT_DESIGNER      # Design
```

### Step 5: Write the seed script

Create your script at:
```
/Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_[SCRIPT_ID]_jobs.py
```

Use `seed_template.py` as the base. Fill in the `COMPANIES` list and `ADDITIONAL_JOBS` list.

### Step 6: Run it

```bash
cd "/Users/paullin/Desktop/mercor china/pathway/apps/api"
source venv/bin/activate
python -m scripts.seed_[SCRIPT_ID]_jobs
```

### Step 7: Verify

```bash
python -c "
from app.database import SessionLocal
from app.models.employer import Employer, Job
db = SessionLocal()
print(f'Total: {db.query(Employer).count()} employers, {db.query(Job).count()} jobs')
db.close()
"
```

### Step 8: Commit

```bash
cd "/Users/paullin/Desktop/mercor china/pathway"
git add apps/api/scripts/seed_[SCRIPT_ID]_jobs.py
git commit -m "Add [FIRM_NAME] intern jobs: X companies, Y jobs"
```

Do NOT push. The user will push manually.

---

## Isolation Rules (CRITICAL for parallel agents)

1. **Unique script filename**: `seed_[SCRIPT_ID]_jobs.py` — never `seed_yc_jobs.py` or `seed_yc_batch2.py`
2. **Per-company transactions**: Each company is committed individually. If one fails, others still succeed.
3. **Dedup by company_name**: Always check `Employer.company_name` before inserting. Skip if exists.
4. **Dedup jobs by title**: When adding jobs to existing companies, check `Job.title` for that employer.
5. **CUID uses uuid4**: No collision risk across parallel agents.
6. **Unique email per employer**: Use `careers@[domain]` or `jobs@[domain]`. If the company might already exist from another agent, the script handles it via the company_name check (it skips the whole insert including the email).
7. **Unique org slug**: Use company name slugified. The script checks company_name first, so slug collision is only possible if two agents add the SAME company — which the dedup prevents.
8. **No shared state**: Agents don't read/write any shared files. Each produces its own script.
9. **Git**: Each agent commits to a SEPARATE file. No merge conflicts possible. Do NOT amend or rebase.

---

## Common VC Job Boards

| VC Firm | Job Board URL | Script ID |
|---------|--------------|-----------|
| Y Combinator | workatastartup.com | `yc` (DONE) |
| a16z | jobs.a16z.com | `a16z` |
| Sequoia | jobs.sequoiacap.com | `sequoia` |
| Greylock | greylock.com/portfolio-jobs | `greylock` |
| NEA | nea.com/portfolio/jobs | `nea` |
| Kleiner Perkins | jobs.kleinerperkins.com | `kpcb` |
| Lightspeed | lsvp.com/portfolio/jobs | `lightspeed` |
| Index Ventures | indexventures.com/jobs | `index` |
| Founders Fund | foundersfund.com/portfolio-jobs | `ff` |
| Benchmark | benchmark.com | `benchmark` |
| Accel | jobs.accel.com | `accel` |
| General Catalyst | jobs.generalcatalyst.com | `gc` |
| Bessemer | bvp.com/jobs | `bessemer` |
| Ribbit Capital | ribbitcapital.com | `ribbit` |
| Neo | neo.com/jobs | `neo` |

---

## Troubleshooting

### "invalid input value for enum roletype"
The DB enum is missing a lowercase value. Run:
```python
conn.execute(text("ALTER TYPE roletype ADD VALUE IF NOT EXISTS 'the_value'"))
conn.commit()
```

### "duplicate key value violates unique constraint"
Another agent already inserted this company. The dedup check should prevent this, but if it happens, the per-company transaction will catch it and skip.

### WebSearch rate limits
If you hit rate limits, work with whatever data you've already collected. Partial data > no data. Write the script with what you have and note what's missing in a comment at the top.
