# Claude Code Agent Prompt — Seed VC Intern Jobs

Copy one of the prompts below into a new Claude Code instance. Each instance handles ONE VC firm independently.

---

## Generic Prompt Template

Replace `[BRACKETS]` before pasting:

```
Seed intern jobs from [VC_FIRM_NAME] portfolio companies into the Pathway database.

JOB BOARD: [JOB_BOARD_URL]
SCRIPT ID: [SHORT_ID]

INSTRUCTIONS:
1. Read the template at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py
2. Read the guide at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/SEED_JOBS_GUIDE.md
3. Read the model at: /Users/paullin/Desktop/mercor china/pathway/apps/api/app/models/employer.py

Then do this:
a) Use WebSearch and WebFetch to find ALL US-based intern/internship job listings on [JOB_BOARD_URL] and related pages. Search thoroughly — use multiple queries like:
   - site:[domain] intern
   - site:[domain] internship 2025 OR 2026
   - "[VC_FIRM_NAME]" portfolio intern jobs
   - Then fetch individual job pages for full details (salary, requirements, description)

b) For each company, also search for founder info:
   - "[company_name]" founders linkedin
   - site:ycombinator.com/companies/[slug] (if YC)
   - site:crunchbase.com/organization/[slug]

c) Copy /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py to /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_[SHORT_ID]_jobs.py

d) Fill in FIRM_NAME = "[VC_FIRM_NAME]" and SCRIPT_ID = "[SHORT_ID]"

e) Fill in the COMPANIES list with all scraped US intern jobs. Follow the exact schema from the template.

f) If any companies you found already exist in the DB (check by running: python -c "from app.database import SessionLocal; from app.models.employer import Employer; db=SessionLocal(); [print(e.company_name) for e in db.query(Employer).all()]; db.close()"), put their new jobs in ADDITIONAL_JOBS instead.

g) Run the script:
   cd "/Users/paullin/Desktop/mercor china/pathway/apps/api" && source venv/bin/activate && python -m scripts.seed_[SHORT_ID]_jobs

h) If you hit a "invalid input value for enum" error, add the missing value:
   python -c "from sqlalchemy import create_engine, text; from app.config import settings; e=create_engine(settings.database_url); c=e.connect(); c.execute(text(\"ALTER TYPE roletype ADD VALUE IF NOT EXISTS 'missing_value'\")); c.commit()"
   Then re-run.

i) Verify with:
   python -c "from app.database import SessionLocal; from app.models.employer import Employer, Job; db=SessionLocal(); print(f'Total: {db.query(Employer).count()} employers, {db.query(Job).count()} jobs'); db.close()"

j) Commit (do NOT push):
   cd "/Users/paullin/Desktop/mercor china/pathway" && git add apps/api/scripts/seed_[SHORT_ID]_jobs.py && git commit -m "Add [VC_FIRM_NAME] portfolio intern jobs: X companies, Y jobs"

RULES:
- US-based intern jobs ONLY (skip India, Europe, Singapore, etc.)
- Include salary as monthly USD integers (salary_min, salary_max)
- Include source URL in each job description
- One transaction per company (the template handles this)
- If WebSearch hits rate limits, work with what you have
- Do NOT modify any existing files. Only create your new seed script.
- Do NOT push to git. Only commit locally.
```

---

## Ready-to-Go Prompts

### a16z (Andreessen Horowitz)

```
Seed intern jobs from a16z (Andreessen Horowitz) portfolio companies into the Pathway database.

JOB BOARD: https://jobs.a16z.com
SCRIPT ID: a16z

INSTRUCTIONS:
1. Read the template at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py
2. Read the guide at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/SEED_JOBS_GUIDE.md
3. Read the model at: /Users/paullin/Desktop/mercor china/pathway/apps/api/app/models/employer.py

Then do this:
a) Use WebSearch and WebFetch to find ALL US-based intern/internship job listings. Search:
   - site:jobs.a16z.com intern
   - site:jobs.a16z.com internship 2025 OR 2026
   - "a16z" portfolio intern jobs 2026
   - a16z portfolio companies hiring interns
   Then fetch individual job pages for details.

b) For each company, search for founder info on LinkedIn and Crunchbase.

c) Copy seed_template.py to seed_a16z_jobs.py, fill in FIRM_NAME="a16z", SCRIPT_ID="a16z"

d) Fill in COMPANIES list with all scraped US intern jobs.

e) Check existing DB companies first:
   cd "/Users/paullin/Desktop/mercor china/pathway/apps/api" && source venv/bin/activate && python -c "from app.database import SessionLocal; from app.models.employer import Employer; db=SessionLocal(); [print(e.company_name) for e in db.query(Employer).all()]; db.close()"
   Put any overlapping companies' new jobs in ADDITIONAL_JOBS instead.

f) Run: python -m scripts.seed_a16z_jobs

g) Fix any enum errors, re-run if needed.

h) Verify totals, then commit (do NOT push):
   cd "/Users/paullin/Desktop/mercor china/pathway" && git add apps/api/scripts/seed_a16z_jobs.py && git commit -m "Add a16z portfolio intern jobs"

RULES: US-based intern jobs ONLY. Include salary as monthly USD. Include source URL. Do NOT modify existing files. Do NOT push.
```

### Sequoia Capital

```
Seed intern jobs from Sequoia Capital portfolio companies into the Pathway database.

JOB BOARD: https://jobs.sequoiacap.com
SCRIPT ID: sequoia

INSTRUCTIONS:
1. Read the template at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py
2. Read the guide at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/SEED_JOBS_GUIDE.md
3. Read the model at: /Users/paullin/Desktop/mercor china/pathway/apps/api/app/models/employer.py

Then do this:
a) Use WebSearch and WebFetch to find ALL US-based intern/internship job listings. Search:
   - site:jobs.sequoiacap.com intern
   - site:jobs.sequoiacap.com internship 2025 OR 2026
   - "sequoia capital" portfolio intern jobs 2026
   - sequoia portfolio companies hiring interns
   Then fetch individual job pages for details.

b) For each company, search for founder info on LinkedIn and Crunchbase.

c) Copy seed_template.py to seed_sequoia_jobs.py, fill in FIRM_NAME="Sequoia", SCRIPT_ID="sequoia"

d) Fill in COMPANIES list with all scraped US intern jobs.

e) Check existing DB companies first:
   cd "/Users/paullin/Desktop/mercor china/pathway/apps/api" && source venv/bin/activate && python -c "from app.database import SessionLocal; from app.models.employer import Employer; db=SessionLocal(); [print(e.company_name) for e in db.query(Employer).all()]; db.close()"
   Put any overlapping companies' new jobs in ADDITIONAL_JOBS instead.

f) Run: python -m scripts.seed_sequoia_jobs

g) Fix any enum errors, re-run if needed.

h) Verify totals, then commit (do NOT push):
   cd "/Users/paullin/Desktop/mercor china/pathway" && git add apps/api/scripts/seed_sequoia_jobs.py && git commit -m "Add Sequoia portfolio intern jobs"

RULES: US-based intern jobs ONLY. Include salary as monthly USD. Include source URL. Do NOT modify existing files. Do NOT push.
```

### Greylock Partners

```
Seed intern jobs from Greylock Partners portfolio companies into the Pathway database.

JOB BOARD: https://greylock.com/portfolio-jobs
SCRIPT ID: greylock

INSTRUCTIONS:
1. Read the template at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py
2. Read the guide at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/SEED_JOBS_GUIDE.md
3. Read the model at: /Users/paullin/Desktop/mercor china/pathway/apps/api/app/models/employer.py

Then do this:
a) Use WebSearch and WebFetch to find ALL US-based intern/internship job listings. Search:
   - site:greylock.com intern
   - greylock portfolio intern jobs 2026
   - greylock partners companies hiring interns
   Then fetch individual job pages for details.

b) For each company, search for founder info on LinkedIn and Crunchbase.

c) Copy seed_template.py to seed_greylock_jobs.py, fill in FIRM_NAME="Greylock", SCRIPT_ID="greylock"

d) Fill in COMPANIES list with all scraped US intern jobs.

e) Check existing DB companies first:
   cd "/Users/paullin/Desktop/mercor china/pathway/apps/api" && source venv/bin/activate && python -c "from app.database import SessionLocal; from app.models.employer import Employer; db=SessionLocal(); [print(e.company_name) for e in db.query(Employer).all()]; db.close()"
   Put any overlapping companies' new jobs in ADDITIONAL_JOBS instead.

f) Run: python -m scripts.seed_greylock_jobs

g) Fix any enum errors, re-run if needed.

h) Verify totals, then commit (do NOT push):
   cd "/Users/paullin/Desktop/mercor china/pathway" && git add apps/api/scripts/seed_greylock_jobs.py && git commit -m "Add Greylock portfolio intern jobs"

RULES: US-based intern jobs ONLY. Include salary as monthly USD. Include source URL. Do NOT modify existing files. Do NOT push.
```

### Kleiner Perkins

```
Seed intern jobs from Kleiner Perkins portfolio companies into the Pathway database.

JOB BOARD: https://jobs.kleinerperkins.com
SCRIPT ID: kpcb

INSTRUCTIONS:
1. Read the template at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py
2. Read the guide at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/SEED_JOBS_GUIDE.md
3. Read the model at: /Users/paullin/Desktop/mercor china/pathway/apps/api/app/models/employer.py

Then do this:
a) Use WebSearch and WebFetch to find ALL US-based intern/internship job listings. Search:
   - site:jobs.kleinerperkins.com intern
   - "kleiner perkins" portfolio intern jobs 2026
   - "kleiner perkins" fellows program 2026
   - KPCB fellows internship
   Then fetch individual job pages for details.

b) For each company, search for founder info on LinkedIn and Crunchbase.

c) Copy seed_template.py to seed_kpcb_jobs.py, fill in FIRM_NAME="Kleiner Perkins", SCRIPT_ID="kpcb"

d) Fill in COMPANIES list with all scraped US intern jobs.

e) Check existing DB companies first:
   cd "/Users/paullin/Desktop/mercor china/pathway/apps/api" && source venv/bin/activate && python -c "from app.database import SessionLocal; from app.models.employer import Employer; db=SessionLocal(); [print(e.company_name) for e in db.query(Employer).all()]; db.close()"
   Put any overlapping companies' new jobs in ADDITIONAL_JOBS instead.

f) Run: python -m scripts.seed_kpcb_jobs

g) Fix any enum errors, re-run if needed.

h) Verify totals, then commit (do NOT push):
   cd "/Users/paullin/Desktop/mercor china/pathway" && git add apps/api/scripts/seed_kpcb_jobs.py && git commit -m "Add Kleiner Perkins portfolio intern jobs"

RULES: US-based intern jobs ONLY. Include salary as monthly USD. Include source URL. Do NOT modify existing files. Do NOT push.
```

### General Catalyst

```
Seed intern jobs from General Catalyst portfolio companies into the Pathway database.

JOB BOARD: https://jobs.generalcatalyst.com
SCRIPT ID: gc

INSTRUCTIONS:
1. Read the template at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py
2. Read the guide at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/SEED_JOBS_GUIDE.md
3. Read the model at: /Users/paullin/Desktop/mercor china/pathway/apps/api/app/models/employer.py

Then do this:
a) Use WebSearch and WebFetch to find ALL US-based intern/internship job listings. Search:
   - site:jobs.generalcatalyst.com intern
   - "general catalyst" portfolio intern jobs 2026
   - general catalyst companies hiring interns
   Then fetch individual job pages for details.

b) For each company, search for founder info on LinkedIn and Crunchbase.

c) Copy seed_template.py to seed_gc_jobs.py, fill in FIRM_NAME="General Catalyst", SCRIPT_ID="gc"

d) Fill in COMPANIES list with all scraped US intern jobs.

e) Check existing DB companies first:
   cd "/Users/paullin/Desktop/mercor china/pathway/apps/api" && source venv/bin/activate && python -c "from app.database import SessionLocal; from app.models.employer import Employer; db=SessionLocal(); [print(e.company_name) for e in db.query(Employer).all()]; db.close()"
   Put any overlapping companies' new jobs in ADDITIONAL_JOBS instead.

f) Run: python -m scripts.seed_gc_jobs

g) Fix any enum errors, re-run if needed.

h) Verify totals, then commit (do NOT push):
   cd "/Users/paullin/Desktop/mercor china/pathway" && git add apps/api/scripts/seed_gc_jobs.py && git commit -m "Add General Catalyst portfolio intern jobs"

RULES: US-based intern jobs ONLY. Include salary as monthly USD. Include source URL. Do NOT modify existing files. Do NOT push.
```

### NEA (New Enterprise Associates)

```
Seed intern jobs from NEA (New Enterprise Associates) portfolio companies into the Pathway database.

JOB BOARD: https://www.nea.com/portfolio
SCRIPT ID: nea

INSTRUCTIONS:
1. Read the template at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/seed_template.py
2. Read the guide at: /Users/paullin/Desktop/mercor china/pathway/apps/api/scripts/SEED_JOBS_GUIDE.md
3. Read the model at: /Users/paullin/Desktop/mercor china/pathway/apps/api/app/models/employer.py

Then do this:
a) Use WebSearch and WebFetch to find ALL US-based intern/internship job listings. Search:
   - "new enterprise associates" portfolio intern 2026
   - NEA portfolio companies hiring interns
   - site:nea.com intern
   Then fetch individual job pages for details.

b) For each company, search for founder info on LinkedIn and Crunchbase.

c) Copy seed_template.py to seed_nea_jobs.py, fill in FIRM_NAME="NEA", SCRIPT_ID="nea"

d) Fill in COMPANIES list with all scraped US intern jobs.

e) Check existing DB companies first:
   cd "/Users/paullin/Desktop/mercor china/pathway/apps/api" && source venv/bin/activate && python -c "from app.database import SessionLocal; from app.models.employer import Employer; db=SessionLocal(); [print(e.company_name) for e in db.query(Employer).all()]; db.close()"
   Put any overlapping companies' new jobs in ADDITIONAL_JOBS instead.

f) Run: python -m scripts.seed_nea_jobs

g) Fix any enum errors, re-run if needed.

h) Verify totals, then commit (do NOT push):
   cd "/Users/paullin/Desktop/mercor china/pathway" && git add apps/api/scripts/seed_nea_jobs.py && git commit -m "Add NEA portfolio intern jobs"

RULES: US-based intern jobs ONLY. Include salary as monthly USD. Include source URL. Do NOT modify existing files. Do NOT push.
```

---

## After All Agents Finish

Once all agents have committed locally, you (the human) can:

```bash
cd "/Users/paullin/Desktop/mercor china/pathway"
git log --oneline -20          # See all commits
git push                       # Push everything at once
```

Verify final counts:
```bash
cd apps/api && source venv/bin/activate
python -c "
from app.database import SessionLocal
from app.models.employer import Employer, Job
db = SessionLocal()
print(f'Total: {db.query(Employer).count()} employers, {db.query(Job).count()} jobs')
db.close()
"
```
