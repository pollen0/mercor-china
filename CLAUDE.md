# Claude Code Rules for Pathway

## Project Overview

Pathway is an AI-powered career platform for US college students. Students interview monthly to show their growth over time, connect their GitHub, and track their coursework. Employers can see candidates' progress trajectories, not just a single snapshot.

**Current Branch**: `us-college-pivot` (pivoted from `zhimian-china-backup` China market version)

## Core Value Proposition

- **For Students**: Stop grinding Leetcode. Interview monthly, show real growth, connect your GitHub.
- **For Employers**: See candidates' growth over 2-4 years. Hire based on trajectory, not just current state.

---

## Critical Rules

### 1. AI Services

**Approved AI Services:**
- **Anthropic Claude API** (Primary for all AI tasks)
  - General tasks: Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
  - Deep reasoning (scoring/analysis): Claude Opus 4.1 (`claude-opus-4-1-20250805`)
  - Env vars: `ANTHROPIC_API_KEY`

- **DeepSeek API** (Fallback/cost optimization)
  - LLM/Scoring: `deepseek-chat` model
  - Env vars: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`

- **OpenAI API** (Speech-to-text only — Claude has no native STT)
  - Whisper for interview transcription
  - Env vars: `OPENAI_API_KEY`

### 2. Design System (HEYTEA-Inspired)

**ALWAYS follow `apps/web/DESIGN_PRINCIPLES.md`**

| Element | Use | Never Use |
|---------|-----|-----------|
| Neutrals | `stone-*` | `gray-*` |
| Success/Active | `teal-50/700` | `green-*`, `indigo-*` |
| Warning | `amber-50/700` | `yellow-*`, `orange-*` |
| Error | `red-50/700` | - |
| Primary buttons | `bg-stone-900 text-white` | `bg-indigo-*`, `bg-blue-*` |
| Font weight | `font-medium`, `font-semibold` max | `font-bold` |
| Dropdowns | Custom styled components | Native `<select>` elements |
| Text | `text-stone-900` | `text-black` |

**Rule**: No more than 2 colors per component. Keep it minimal.

### 3. Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, PostgreSQL (Neon) |
| Storage | Cloudflare R2 (S3-compatible) |
| AI | Claude Sonnet 4.5 (general), Claude Opus 4.1 (scoring), DeepSeek (fallback), OpenAI Whisper (STT) |
| Auth | GitHub OAuth, Email/Password, JWT (1h access + 30-day refresh) |
| Email | Resend |
| Caching | Redis (optional) |
| Testing | pytest (backend), Jest (frontend unit), Playwright (E2E) |
| CI/CD | GitHub Actions |

### 4. Target Verticals

| Vertical | Enum Value | Target Students |
|----------|------------|-----------------|
| Software Engineering | `software_engineering` | CS, SE, CE majors |
| Data | `data` | Data Science, Stats, CS |
| Product | `product` | Business, Econ majors |
| Design | `design` | Design, HCI majors |
| Finance | `finance` | Finance, Econ majors |

### 5. Role Types

```python
# Software Engineering Vertical
SOFTWARE_ENGINEER, FRONTEND_ENGINEER, BACKEND_ENGINEER
EMBEDDED_ENGINEER, QA_ENGINEER

# Data Vertical
DATA_ANALYST, DATA_SCIENTIST, ML_ENGINEER, DATA_ENGINEER

# Product Vertical
PRODUCT_MANAGER, ASSOCIATE_PM

# Design Vertical
UX_DESIGNER, UI_DESIGNER, PRODUCT_DESIGNER

# Finance Vertical
IB_ANALYST, FINANCE_ANALYST, EQUITY_RESEARCH

# Business/Consulting
CONSULTANT, MARKETING_ASSOCIATE, BUSINESS_ANALYST
```

### 6. Database Models — CUID Prefixes

| Prefix | Model | Purpose |
|--------|-------|---------|
| `c_` | Candidate | Student profiles |
| `e_` | Employer | Company profiles |
| `i_` | Interview | Interview sessions |
| `j_` | Job | Job postings |
| `o_` | Organization | Company organizations |
| `tm_` | OrganizationMember | Team members |
| `r_` | Referral | Referral tracking |
| `rv_` | ResumeVersion | Resume version history |
| `gah_` | GitHubAnalysisHistory | GitHub score snapshots |
| `pcl_` | ProfileChangeLog | Profile audit trail |
| `ga_` | GitHubAnalysis | Latest GitHub scores |
| `cn_` | CandidateNote | Employer notes on candidates |
| `cc_` | CodingChallenge | Coding challenges |
| `vc_` | VibeCodeSession | Vibe code sessions |
| `si_` | ScheduledInterview | Scheduled interviews |
| `sl_` | SchedulingLink | Self-scheduling links |
| `avl_` | Availability | Interviewer availability |
| `rm_` | Reminder | Interview reminders |
| `act_` | Activity | Student activities/awards |
| `cr_` | Course | Course database |
| `maj_` | Major | University majors |
| `pt_` | ProfileToken | Shareable profile tokens |
| `ps_` | ProfileScore | Profile scoring metadata |
| `mls_` | MLScoring | ML training data |
| `mr_` | MarketingReferrer | Marketing source tracking |
| `msg_` | Message | Messaging system |

**CUID Generation**: `f"{prefix}{uuid.uuid4().hex[:24]}"`

### 7. Scoring System (5 Dimensions)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Communication | 20% | Clarity, articulation, confidence |
| Problem Solving | 25% | Analytical thinking, approach to challenges |
| Technical Knowledge | 25% | Relevant skills, depth of understanding |
| Growth Mindset | 15% | Learning from failures, curiosity, adaptability |
| Culture Fit | 15% | Teamwork, values alignment, enthusiasm |

Score range: 0-10 (floating point)

---

## Project Structure

```
pathway/
├── CLAUDE.md                      # This file — full project documentation
├── TODO.md                        # Product backlog
├── GTM_STRATEGY.md                # Go-to-market approach (invite-only beta)
├── MATCHING_LOGIC.md              # Preference boost algorithm docs
├── .env.example                   # Environment variable template
├── docker-compose.yml             # PostgreSQL 15 for local dev
├── .github/workflows/ci.yml      # CI pipeline (pytest, Jest, Playwright)
├── .husky/pre-commit              # Pre-commit hook (runs frontend lint)
├── docs/                          # Market research docs
│
├── apps/
│   ├── api/                       # FastAPI Backend
│   │   ├── app/
│   │   │   ├── main.py            # App entry point, router registration, auto-seeding
│   │   │   ├── config.py          # Settings (env vars, model configs)
│   │   │   ├── database.py        # SQLAlchemy engine, session
│   │   │   ├── models/            # 24 SQLAlchemy ORM models
│   │   │   ├── routers/           # 17 API endpoint modules
│   │   │   ├── services/          # 28 business logic services
│   │   │   ├── schemas/           # 13 Pydantic validation modules
│   │   │   ├── utils/             # 7 helper modules
│   │   │   ├── middleware/        # 1 middleware (security headers)
│   │   │   └── data/              # 9 seed data files (universities, courses, clubs)
│   │   ├── migrations/versions/   # 39 Alembic migrations
│   │   ├── scripts/               # 31 seed/utility scripts
│   │   └── tests/                 # 17 test files (pytest)
│   │
│   └── web/                       # Next.js Frontend
│       ├── app/
│       │   ├── page.tsx            # Landing page
│       │   ├── (candidate)/        # Student pages (dashboard, interview, settings, resume)
│       │   ├── (employer)/         # Employer pages (dashboard, talent pool, jobs, team, admin)
│       │   ├── (auth)/             # Auth pages (forgot/reset password)
│       │   ├── auth/               # OAuth callbacks (GitHub, Google)
│       │   ├── api/                # Next.js API routes (4 route handlers)
│       │   ├── schedule/[slug]/    # Public self-scheduling
│       │   ├── talent/[id]/        # Public candidate profiles
│       │   └── verify-email/       # Email verification
│       ├── components/             # 49 React components
│       │   ├── ui/                 # shadcn base components (10)
│       │   ├── dashboard/          # Candidate dashboard components (12)
│       │   ├── employer/           # Employer-specific components (5)
│       │   ├── interview/          # Interview flow components (9)
│       │   ├── scheduling/         # Scheduling components (4)
│       │   ├── calendar/           # Calendar components (2)
│       │   ├── layout/             # Layout components (3 + container)
│       │   └── verification/       # Verification banners (2)
│       ├── lib/
│       │   ├── api.ts              # Typed API client (~4800 lines)
│       │   ├── auth.ts             # JWT token management
│       │   ├── utils.ts            # General utilities
│       │   ├── sanitize.ts         # XSS prevention
│       │   ├── prisma.ts           # Prisma client
│       │   ├── hooks/              # Custom React hooks
│       │   └── validations/        # Form validation schemas
│       ├── __tests__/              # 7 Jest unit tests
│       ├── e2e/                    # 5 Playwright E2E tests
│       ├── scripts/                # 3 scraping utilities
│       └── DESIGN_PRINCIPLES.md    # UI/UX guidelines
│
└── packages/
    └── shared/                    # @pathway/shared TypeScript package
        └── src/index.ts           # Shared types/utilities
```

---

## Backend: Models (24 files)

`apps/api/app/models/`

| File | Model(s) | Purpose |
|------|----------|---------|
| `candidate.py` | Candidate, CandidateVerticalProfile | Student profiles, education, GitHub, vertical profiles |
| `employer.py` | Employer, Job, Organization, OrganizationMember, Match | Companies, jobs, orgs, team structure, matching |
| `interview.py` | InterviewSession, InterviewResponse | Interview sessions, Q&A, video responses |
| `activity.py` | Activity, Award, Club | Student activities, clubs, awards |
| `availability.py` | Availability | Interviewer time slot availability |
| `candidate_note.py` | CandidateNote | Private employer notes on candidates |
| `coding_challenge.py` | CodingChallenge | Coding challenge data and submissions |
| `course.py` | Course, University | Course database, university catalog |
| `github_analysis.py` | GitHubAnalysis | Latest GitHub code quality scores |
| `github_analysis_history.py` | GitHubAnalysisHistory | Timestamped GitHub score snapshots (growth) |
| `major.py` | Major | University major/degree options |
| `marketing_referrer.py` | MarketingReferrer | Marketing/referral source tracking |
| `message.py` | Message | Inter-user messaging |
| `ml_scoring.py` | MLScoring | ML model training data and predictions |
| `profile_change_log.py` | ProfileChangeLog | Audit trail for profile changes (growth) |
| `profile_score.py` | ProfileScore | Candidate profile scoring metadata |
| `profile_token.py` | ProfileToken | Shareable public profile tokens (7-day expiry) |
| `referral.py` | Referral | Referral system (code gen, status tracking) |
| `reminder.py` | Reminder | Interview reminder scheduling |
| `resume_version.py` | ResumeVersion | Versioned resume uploads with skill deltas (growth) |
| `scheduled_interview.py` | ScheduledInterview | Scheduled interviews with Google Meet |
| `scheduling_link.py` | SchedulingLink | Self-service scheduling links |
| `team_member.py` | TeamMember | Organization team members with roles |
| `vibe_code_session.py` | VibeCodeSession | Vibe code challenge sessions |

---

## Backend: Routers (17 files)

`apps/api/app/routers/`

| File | Key Endpoints | Purpose |
|------|---------------|---------|
| `auth.py` | POST login, register | Candidate/Employer authentication, JWT |
| `candidates.py` | GET/PATCH /me, POST resume | Student profiles, resume upload, GitHub connection |
| `employers.py` | GET talent-pool, PATCH status | Employer profiles, talent pool, candidate status, matches |
| `interviews.py` | POST start, POST response, POST complete | Interview flow (start, respond, score, complete) |
| `organizations.py` | CRUD | Organization management, settings |
| `team_members.py` | CRUD | Team member management with roles |
| `scheduling_links.py` | CRUD | Self-service scheduling link management |
| `calendar.py` | POST/GET | Google Calendar OAuth, scheduling (candidates) |
| `employer_calendar.py` | POST/GET/PATCH | Google Calendar OAuth, scheduling (employers) |
| `activities.py` | POST/GET | Student activities, clubs, awards |
| `courses.py` | GET | Course database lookup |
| `questions.py` | GET/POST | Question bank, progressive question generation |
| `referrals.py` | POST/GET | Referral code generation, stats, tracking |
| `public.py` | GET | Public profiles, shareable links, talent pages, stats |
| `vibe_code.py` | POST/GET | Vibe code challenge submission and scoring |
| `health.py` | GET | Health check endpoint |
| `admin.py` | Multiple | Admin utilities, batch operations, employer detail |

---

## Backend: Services (28 files)

`apps/api/app/services/`

| File | Purpose |
|------|---------|
| `scoring.py` | AI interview scoring (5 dimensions, Claude) |
| `progressive_questions.py` | AI question generation based on interview history |
| `matching.py` | Candidate-job matching with preference boost (+30 max) |
| `github.py` | GitHub API integration layer |
| `github_analysis.py` | GitHub OAuth, code quality analysis, token encryption |
| `growth_tracking.py` | Resume versions, GitHub history, profile change logs |
| `calendar.py` | Google Calendar OAuth, event creation, Google Meet links |
| `email.py` | Resend email templates (confirmations, notifications, digests) |
| `storage.py` | Cloudflare R2 file storage (videos, resumes) |
| `availability.py` | Interviewer availability slots and conflict detection |
| `self_scheduling.py` | Self-service scheduling link logic |
| `referral.py` | Referral code generation, status management |
| `resume.py` | Resume storage and retrieval |
| `resume_scoring.py` | Resume parsing, skill extraction, quality scoring |
| `transcript.py` | Transcript upload and GPA/major extraction |
| `transcript_verification.py` | Official transcript validation |
| `transcription.py` | Audio-to-text transcription (OpenAI Whisper) |
| `candidate_scoring.py` | Candidate profile overall scoring |
| `profile_scoring.py` | Profile completeness and strength scoring |
| `cohort.py` | Cohort analysis (percentile ranking, comparative stats) |
| `skill_gap.py` | Missing skills identification based on job requirements |
| `code_execution.py` | Sandbox code execution and evaluation |
| `vibe_code_analysis.py` | Vibe code submission evaluation |
| `ml_data_pipeline.py` | ML training data preparation |
| `panel_coordination.py` | Multi-interviewer coordination |
| `reminder_scheduler.py` | APScheduler-based interview reminders |
| `cache.py` | Redis caching layer (optional) |
| `tasks.py` | Background task queue |

---

## Backend: Schemas (13 files)

`apps/api/app/schemas/`

| File | Purpose |
|------|---------|
| `candidate.py` | Candidate profile, registration, update schemas |
| `employer.py` | Employer registration, job posting, talent pool schemas |
| `interview.py` | Interview session, question, response, results schemas |
| `growth.py` | Growth timeline response schemas |
| `availability.py` | Availability slot request/response |
| `coding_challenge.py` | Coding challenge request/response |
| `profile_token.py` | Public profile token and shareable links |
| `question.py` | Question bank, progressive question schemas |
| `referral.py` | Referral code, stats, list schemas |
| `scheduled_interview.py` | Scheduled interview CRUD |
| `scheduling_link.py` | Scheduling link creation, slot booking |
| `team_member.py` | Team member invitation, role update |
| `vibe_code.py` | Vibe code challenge submission |

---

## Backend: Utilities (7 files) & Middleware (1 file)

`apps/api/app/utils/`

| File | Purpose |
|------|---------|
| `auth.py` | JWT generation, password hashing, token validation |
| `crypto.py` | Fernet encryption for sensitive data (GitHub tokens) |
| `csrf.py` | CSRF state validation for OAuth |
| `date_parser.py` | Parse semester strings ("Fall 2022") to dates |
| `file_validation.py` | Resume/document file type validation |
| `rate_limit.py` | API rate limiting middleware (slowapi) |
| `sanitize.py` | XSS prevention, HTML sanitization |

`apps/api/app/middleware/`

| File | Purpose |
|------|---------|
| `security.py` | Security headers middleware (HSTS in production) |

---

## Backend: Auto-Seed Data (9 files)

`apps/api/app/data/`

On startup, `main.py` auto-seeds universities, courses, and clubs if tables are empty.

| File | Purpose |
|------|---------|
| `seed_courses.py` | Base university and course catalog |
| `seed_courses_extended.py` | Extended course data (batch 2) |
| `seed_courses_extended2.py` | Extended course data (batch 3) |
| `seed_courses_extended3.py` | Extended course data (batch 4) |
| `seed_clubs.py` | Base student clubs |
| `seed_clubs_extended.py` | Extended clubs (batch 2) |
| `seed_clubs_extended2.py` | Extended clubs (batch 3) |
| `seed_clubs_extended3.py` | Extended clubs (batch 4) |
| `seed_majors.py` | University majors catalog |

---

## Seed Scripts System (31 files)

`apps/api/scripts/`

Database seeding scripts that populate intern job listings from VC portfolio company job boards. Each script creates Employer + Organization + OrganizationMember + Job records.

| Script | VC Firm | Status |
|--------|---------|--------|
| `seed_template.py` | Template for new scripts | Reference |
| `seed_yc_jobs.py` | Y Combinator | Done |
| `seed_yc_batch2.py` | Y Combinator (Batch 2) | Done |
| `seed_a16z_jobs.py` | Andreessen Horowitz | Done |
| `seed_a16z_batch2_jobs.py` | Andreessen Horowitz (Batch 2) | Done |
| `seed_sequoia_jobs.py` | Sequoia Capital | Done |
| `seed_lightspeed_jobs.py` | Lightspeed Venture Partners | Done |
| `seed_khosla_jobs.py` | Khosla Ventures | Done |
| `seed_nea_jobs.py` | New Enterprise Associates | Done |
| `seed_accel_jobs.py` | Accel | Done |
| `seed_bessemer_jobs.py` | Bessemer Venture Partners | Done |
| `seed_dragoneer_jobs.py` | Dragoneer Investment Group | Done |
| `seed_legend_jobs.py` | Legend Venture Capital | Done |
| `seed_tigerglobal_jobs.py` | Tiger Global Management | Done |
| `seed_tcv_jobs.py` | Technology Crossover Ventures | Done |
| `seed_kpcb_jobs.py` | Kleiner Perkins | Done |
| `seed_kp_techstars_jobs.py` | Kleiner Perkins + Techstars | Done |
| `seed_firstround_jobs.py` | First Round Capital | Done |
| `seed_techstars_jobs.py` | Techstars | Done |
| `seed_500global_jobs.py` | 500 Global | Done |
| `seed_floodgate_jobs.py` | Floodgate | Done |
| `seed_pearvc_jobs.py` | Pear VC | Done |
| `seed_contrary_jobs.py` | Contrary | Done |
| `seed_hustlefund_jobs.py` | Hustle Fund | Done |
| `seed_precursor_jobs.py` | Precursor Ventures | Done |
| `seed_2048ventures_jobs.py` | 2048 Ventures | Done |
| `seed_gcffindex_jobs.py` | GCF Fund Index | Done |
| `seed_topstartups_jobs.py` | Top Startups (aggregator) | Done |
| `seed_from_json.py` | Generic JSON-based seeder | Utility |
| `seed_coding_challenges.py` | Coding challenges (standalone) | Done |
| `backfill_linkedin.py` | Backfill LinkedIn URLs for employers | Utility |

**Running**: `cd apps/api && python -m scripts.seed_[SCRIPT_ID]_jobs`

**Isolation**: Each script uses per-company transactions, dedup by `company_name` and `job.title`. Multiple scripts can run concurrently.

---

## Frontend: Key Pages (37 page.tsx files)

### Student Pages
| URL | File | Purpose |
|-----|------|---------|
| `/register` | `(candidate)/register/page.tsx` | Student registration |
| `/candidate/login` | `(candidate)/candidate/login/page.tsx` | Student login |
| `/candidate/dashboard` | `(candidate)/candidate/dashboard/page.tsx` | Main student dashboard |
| `/candidate/settings` | `(candidate)/candidate/settings/page.tsx` | Profile settings |
| `/candidate/resume` | `(candidate)/candidate/resume/page.tsx` | Resume management |
| `/interview/select` | `(candidate)/interview/select/page.tsx` | Vertical selection |
| `/interview/start` | `(candidate)/interview/start/page.tsx` | Interview start |
| `/interview/[id]` | `(candidate)/interview/[sessionId]/page.tsx` | Interview session |
| `/interview/[id]/room` | `(candidate)/interview/[sessionId]/room/page.tsx` | Video interview room |
| `/interview/[id]/complete` | `(candidate)/interview/[sessionId]/complete/page.tsx` | Interview results |
| `/practice` | `(candidate)/practice/page.tsx` | Practice mode |

### Employer Pages
| URL | File | Purpose |
|-----|------|---------|
| `/employer/login` | `(employer)/employer/login/page.tsx` | Employer login/register |
| `/employer` | `(employer)/employer/page.tsx` | Employer landing |
| `/employer/dashboard` | `(employer)/employer/dashboard/page.tsx` | Employer dashboard |
| `/employer/dashboard/interviews/[id]` | `(employer)/employer/dashboard/interviews/[id]/page.tsx` | Interview detail |
| `/employer/dashboard/scheduled-interviews` | `(employer)/employer/dashboard/scheduled-interviews/page.tsx` | Scheduled interviews |
| `/employer/dashboard/scheduling-links` | `(employer)/employer/dashboard/scheduling-links/page.tsx` | Scheduling links |
| `/employer/dashboard/team` | `(employer)/employer/dashboard/team/page.tsx` | Team management |
| `/employer/dashboard/team/[id]/availability` | `(employer)/employer/dashboard/team/[id]/availability/page.tsx` | Team member availability |
| `/dashboard` | `(employer)/dashboard/page.tsx` | Legacy employer dashboard |
| `/dashboard/jobs` | `(employer)/dashboard/jobs/page.tsx` | Job postings |
| `/dashboard/talent-pool` | `(employer)/dashboard/talent-pool/page.tsx` | Browse candidates |
| `/dashboard/talent-pool/[id]` | `(employer)/dashboard/talent-pool/[profileId]/page.tsx` | Candidate detail + growth timeline |
| `/dashboard/interviews` | `(employer)/dashboard/interviews/page.tsx` | All interviews |
| `/dashboard/interviews/[id]` | `(employer)/dashboard/interviews/[id]/page.tsx` | Interview detail (legacy) |
| `/dashboard/settings` | `(employer)/dashboard/settings/page.tsx` | Organization settings |
| `/admin` | `(employer)/admin/page.tsx` | Admin panel |
| `/admin/companies/[id]` | `(employer)/admin/companies/[employerId]/page.tsx` | Admin employer detail |

### Public Pages
| URL | File | Purpose |
|-----|------|---------|
| `/` | `page.tsx` | Landing page |
| `/talent/[id]` | `talent/[candidateId]/page.tsx` | Public candidate profile |
| `/schedule/[slug]` | `schedule/[slug]/page.tsx` | Self-service scheduling |
| `/privacy` | `privacy/page.tsx` | Privacy policy |
| `/verify-email` | `verify-email/page.tsx` | Email verification |

### Auth Pages
| URL | File | Purpose |
|-----|------|---------|
| `/forgot-password` | `(auth)/forgot-password/page.tsx` | Password reset request |
| `/reset-password` | `(auth)/reset-password/page.tsx` | Password reset form |
| `/auth/github/callback` | `auth/github/callback/page.tsx` | GitHub OAuth callback |
| `/auth/google/callback` | `auth/google/callback/page.tsx` | Google OAuth callback (candidates) |
| `/employer-auth/google/callback` | `(employer)/employer-auth/google/callback/page.tsx` | Google OAuth callback (employers) |

### Next.js API Routes
| Route | Purpose |
|-------|---------|
| `api/candidates/lookup/route.ts` | Candidate lookup |
| `api/candidates/register/route.ts` | Registration proxy |
| `api/interviews/start/route.ts` | Interview start proxy |
| `api/jobs/route.ts` | Jobs listing |

---

## Frontend: Components (49 files)

### Dashboard Components (`components/dashboard/`) — 12 files
| Component | Purpose |
|-----------|---------|
| `candidate-card.tsx` | Candidate summary card |
| `github-analysis.tsx` | GitHub code quality visualization |
| `match-score-card.tsx` | Match score display |
| `matching-readiness-alert.tsx` | Alert when matching prerequisites incomplete |
| `opportunities-tab.tsx` | Job opportunities tab on candidate dashboard |
| `score-card.tsx` | Interview score breakdown |
| `video-player.tsx` | Interview video playback |
| `transcript-viewer.tsx` | Document viewer |
| `vibe-code-section.tsx` | Vibe code challenge display |
| `bulk-action-toolbar.tsx` | Bulk actions for candidates |
| `contact-candidate-modal.tsx` | Contact/message modal |

### Employer Components (`components/employer/`) — 5 files
| Component | Purpose |
|-----------|---------|
| `growth-timeline.tsx` | Growth trajectory visualization (recruiter-only) |
| `candidate-notes.tsx` | Private notes CRUD |
| `match-alerts.tsx` | Real-time match notifications |
| `schedule-interview-modal.tsx` | Interview scheduling modal |
| `employer-calendar-settings.tsx` | Calendar settings for team |

### Interview Components (`components/interview/`) — 9 files
| Component | Purpose |
|-----------|---------|
| `video-recorder.tsx` | Video recording capture |
| `question-card.tsx` | Question display |
| `resume-uploader.tsx` | Resume upload |
| `code-editor.tsx` | Live code editing |
| `code-results-card.tsx` | Code execution results |
| `interview-progress.tsx` | Progress indicator |
| `permission-check.tsx` | Camera/mic permissions |
| `followup-modal.tsx` | Follow-up question prompts |
| `practice-feedback-card.tsx` | Practice mode feedback |

### Scheduling Components (`components/scheduling/`) — 4 files
| Component | Purpose |
|-----------|---------|
| `availability-grid.tsx` | Weekly time slot selector |
| `slot-picker.tsx` | Calendar-based slot picker |
| `conflict-alert.tsx` | Scheduling conflict warning |
| `interviewer-select.tsx` | Select interviewer dropdown |

### Calendar Components (`components/calendar/`) — 2 files
| Component | Purpose |
|-----------|---------|
| `calendar-settings.tsx` | Calendar configuration |
| `schedule-meeting.tsx` | Meeting scheduling |

### Layout Components (`components/layout/`) — 3 files
| Component | Purpose |
|-----------|---------|
| `container.tsx` | Page container |
| `footer.tsx` | Site footer |
| `navbar.tsx` | Navigation bar |

### Verification Components (`components/verification/`) — 2 files
| Component | Purpose |
|-----------|---------|
| `email-verification-banner.tsx` | Email verification prompt |
| `employer-verification-banner.tsx` | Employer verification prompt |

### Root Components — 2 files
| Component | Purpose |
|-----------|---------|
| `error-boundary.tsx` | React error boundary |
| `loading.tsx` | Loading spinner |

### UI Components (`components/ui/`) — 10 files (shadcn/ui)
`badge.tsx`, `button.tsx`, `card.tsx`, `custom-select.tsx`, `dialog.tsx`, `document-preview.tsx`, `input.tsx`, `label.tsx`, `textarea.tsx`, `upload-progress.tsx`

---

## Frontend: Lib (7 files)

`apps/web/lib/`

| File | Purpose |
|------|---------|
| `api.ts` | Typed API client (~4800 lines) |
| `auth.ts` | JWT token management |
| `utils.ts` | General utilities |
| `sanitize.ts` | XSS prevention |
| `prisma.ts` | Prisma client instance |
| `hooks/use-candidate-data.ts` | Custom hook for candidate data fetching |
| `validations/candidate.ts` | Candidate form validation schemas |

---

## Key API Endpoints

### Candidates
```
POST /api/candidates/                    # Register
GET  /api/candidates/me                  # Get profile
PATCH /api/candidates/me                 # Update profile
POST /api/candidates/{id}/resume         # Upload resume (creates ResumeVersion)
```

### GitHub
```
GET  /api/candidates/auth/github/url     # Get OAuth URL
POST /api/candidates/auth/github/callback # Exchange code
GET  /api/candidates/me/github           # Get GitHub info
DELETE /api/candidates/me/github         # Disconnect
POST /api/candidates/me/github/refresh   # Refresh data
POST /api/candidates/me/github/analyze   # Run analysis (creates snapshot)
GET  /api/candidates/me/github/analysis  # Get latest analysis
```

### Interviews
```
POST /api/interviews/start-vertical      # Start vertical interview
GET  /api/interviews/{id}                # Get session
POST /api/interviews/{id}/response       # Submit video response
POST /api/interviews/{id}/complete       # Complete interview
GET  /api/interviews/{id}/results        # Get results
```

### Employers / Talent Pool
```
POST /api/employers/register                           # Register
POST /api/employers/login                              # Login
GET  /api/employers/talent-pool                        # Browse candidates
GET  /api/employers/talent-pool/{id}                   # View candidate
PATCH /api/employers/talent-pool/{id}/status           # Update status
GET  /api/employers/talent-pool/{id}/growth-timeline   # Growth timeline
```

### Public
```
GET  /api/public/stats                   # Platform statistics (landing page)
```

### Referrals
```
GET  /api/referrals/me/code              # Get/generate referral code
GET  /api/referrals/me/stats             # Referral stats
GET  /api/referrals/me/list              # List referrals
```

### Scheduling
```
POST /api/employers/scheduling-links     # Create scheduling link
GET  /api/employers/scheduling-links     # List links
GET  /api/schedule/{slug}                # Public: Get available slots
POST /api/schedule/{slug}/book           # Public: Book slot
```

---

## Key Features

### Monthly Interview System
- Students interview **once per month per vertical** (30-day cooldown)
- Best score shown to employers, full history available
- Progressive AI questions based on interview history
- Difficulty levels: Foundational (< 5.5), Intermediate (5.5-7.5), Advanced (> 7.5)

### GitHub Integration
- OAuth connection with GitHub
- Code quality analysis: originality, activity, depth, collaboration scores
- History tracking: each analysis creates a snapshot for growth tracking
- Fernet-encrypted token storage

### Opportunities / Matching
- Candidates see matched job opportunities on their dashboard
- Eligibility requires: resume uploaded, transcript uploaded, GitHub connected
- Base score (0-100) from interview + skills + experience + GitHub
- Preference boost: +10 company stage, +10 location, +10 industry (max +30)
- Score capped at 100
- See `MATCHING_LOGIC.md` for full algorithm

### Growth Tracking System (Recruiter-Only)
Tracks all key datapoints with timestamps to show student growth over time:
- **ResumeVersion**: Versioned resume uploads with skill deltas
- **GitHubAnalysisHistory**: Timestamped GitHub score snapshots
- **ProfileChangeLog**: Audit trail for GPA, major, education changes
- **Growth Timeline UI**: Progressive disclosure component at `/employer/dashboard/talent-pool/[id]`

### Referral System
- Each candidate gets a unique referral code
- Auto-populated on registration via `?ref=` query param
- Status tracking: pending, registered, interviewed, hired
- Stats endpoint for referral leaderboard

---

## Testing

### Backend Tests (17 files)

`apps/api/tests/`

| File | Coverage |
|------|----------|
| `conftest.py` | Test fixtures, DB setup |
| `test_auth.py` | Login, registration, JWT |
| `test_bulk_actions.py` | Bulk candidate operations |
| `test_cache.py` | Redis caching |
| `test_candidates.py` | Candidate CRUD |
| `test_employers.py` | Employer operations |
| `test_followups.py` | Follow-up questions |
| `test_github.py` | GitHub integration |
| `test_health.py` | Health check |
| `test_interviews.py` | Interview flow |
| `test_invites.py` | Team invitations |
| `test_matching.py` | Matching algorithm |
| `test_onboarding.py` | Onboarding flow |
| `test_practice.py` | Practice interviews |
| `test_questions.py` | Question generation |
| `test_scoring.py` | AI scoring |
| `test_talent_pool.py` | Talent pool browsing |

### Frontend Unit Tests (7 files)

`apps/web/__tests__/`

| File | Coverage |
|------|----------|
| `components/dashboard.test.tsx` | Dashboard rendering |
| `components/error-boundary.test.tsx` | Error handling |
| `components/footer.test.tsx` | Footer component |
| `components/interview.test.tsx` | Interview flow |
| `components/loading.test.tsx` | Loading states |
| `components/navbar.test.tsx` | Navigation |
| `lib/api.test.ts` | API client |

### E2E Tests (5 files)

`apps/web/e2e/`

| File | Coverage |
|------|----------|
| `accessibility.spec.ts` | a11y checks |
| `employer-auth.spec.ts` | Employer auth flow |
| `employer-dashboard.spec.ts` | Employer dashboard |
| `home.spec.ts` | Landing page |
| `interview-flow.spec.ts` | Full interview flow |

### CI Pipeline

`.github/workflows/ci.yml` — Runs on push/PR to `main` and `us-college-pivot`:

1. **Backend Tests** — Python 3.11, pytest with coverage, PostgreSQL 15
2. **Frontend Lint & Type Check** — Node.js 20, TypeScript, ESLint
3. **Frontend Tests** — Jest with coverage
4. **E2E Tests** — Playwright (chromium), depends on backend + frontend tests

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/pathway
POSTGRES_USER=pathway
POSTGRES_PASSWORD=pathway_password
POSTGRES_DB=pathway_db

# Security
API_SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256                          # Default: HS256

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000

# Anthropic (Primary AI)
ANTHROPIC_API_KEY=sk-ant-...

# DeepSeek (Fallback)
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OpenAI (Whisper STT only)
OPENAI_API_KEY=sk-...

# Admin
ADMIN_PASSWORD=your-admin-password

# GitHub OAuth
GITHUB_CLIENT_ID=Iv1.xxxx
GITHUB_CLIENT_SECRET=xxxx

# Google Calendar OAuth
GOOGLE_CLIENT_ID=xxxx
GOOGLE_CLIENT_SECRET=xxxx
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
GOOGLE_EMPLOYER_REDIRECT_URI=http://localhost:3000/employer-auth/google/callback

# Cloudflare R2 (Storage)
R2_ACCOUNT_ID=xxxx
R2_ACCESS_KEY_ID=xxxx
R2_SECRET_ACCESS_KEY=xxxx
R2_BUCKET_NAME=pathway-videos

# Email (Resend)
RESEND_API_KEY=re_xxxx
EMAIL_FROM=Pathway <noreply@pathway.careers>

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300

# Encryption (for GitHub tokens)
ENCRYPTION_KEY=your-fernet-key

# URLs
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

---

## Common Tasks

### Running Locally

```bash
# Database (Docker)
docker-compose up -d

# Backend
cd apps/api
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Frontend
cd apps/web
npm run dev  # Port 3000
```

### Database Migrations

```bash
cd apps/api
alembic upgrade head          # Apply migrations
alembic revision -m "message" # Create new migration
```

### Running Seed Scripts

```bash
cd apps/api
source venv/bin/activate
python -m scripts.seed_[SCRIPT_ID]_jobs
```

### Adding a New API Endpoint

1. Create schema in `app/schemas/`
2. Create/update model in `app/models/`
3. Add service logic in `app/services/`
4. Create router in `app/routers/`
5. Register router in `app/main.py`

### Adding a New Frontend Page

1. Create page in `apps/web/app/` under appropriate group
2. Follow design principles from `DESIGN_PRINCIPLES.md`
3. Use stone/teal color palette only
4. Add API types to `lib/api.ts` if needed

### Testing

```bash
# Backend tests
cd apps/api
python -m pytest

# Frontend unit tests
cd apps/web
npm test

# Frontend type check
cd apps/web
npm run type-check

# Lint
cd apps/web
npm run lint

# E2E tests
cd apps/web
npx playwright test
```

---

## Migration Notes

### From China (ZhiMian) to US (Pathway)

1. **Verticals**: Changed from `new_energy`/`sales` to `software_engineering`/`data`/`product`/`design`/`finance`
2. **Roles**: Changed from China-specific to US entry-level roles
3. **Auth**: Removed WeChat OAuth, added GitHub OAuth
4. **Scoring**: Changed "Motivation" dimension to "Growth Mindset"
5. **Language**: All Chinese strings replaced with English
6. **Interview Cadence**: Changed from max-3-retries to monthly (30-day cooldown)
7. **Profile**: Added education fields, GitHub integration, transcript analysis
8. **Branding**: ZhiMian (智面) → Pathway
9. **Design**: Changed from green/indigo to stone/teal (HEYTEA-inspired)
10. **Questions**: Changed from static templates to AI-generated progressive questions
11. **Growth Tracking**: Added resume versioning, GitHub history, profile change logs

### Backup Branch

The original China market version is preserved in `zhimian-china-backup` branch.

---

## Completed Features

- Monthly interview system with 30-day cooldown
- GitHub OAuth + code quality analysis
- Progressive AI question generation
- Transcript analysis & verification
- Profile sharing preferences
- Google Calendar integration + Google Meet (candidates + employers)
- Candidate status management (New/Contacted/In Review/Shortlisted/Rejected/Hired)
- GitHub analysis display (visual scores)
- Private candidate notes for employers
- Scheduled interviews page with Google Meet
- Self-scheduling links
- Match alerts for high-scoring candidates
- Organization teams with roles and invites
- Growth Tracking System (resume versions, GitHub history, profile change logs)
- Growth Timeline UI (recruiter-only progressive disclosure)
- Referral system with code generation and status tracking
- Vibe code challenge sessions
- Marketing referrer tracking
- ML scoring data pipeline
- Cohort analysis and percentile ranking
- Profile scoring and completeness
- Forgot password / password reset flow
- Welcome/onboarding email sequences
- Interview reminder emails
- Weekly digest emails
- Profile view notification emails
- Public candidate profiles with shareable tokens
- Admin panel with batch operations + employer detail view
- Opportunities tab on candidate dashboard (requires resume + transcript + GitHub)
- Public stats endpoint for landing page
- Email verification flow
- Security headers middleware (HSTS in production)
- Auto-seeding of universities, courses, and clubs on startup
- VC portfolio job seeding (25+ VC firms, 31 scripts)
- LinkedIn URL backfill for employers
- Frontend scraping utilities for job boards (Getro, Consider, NEA)
- CI/CD pipeline (GitHub Actions: pytest, Jest, Playwright)
- Pre-commit hook (frontend lint via Husky)

---

## Known Technical Debt

| Item | Priority |
|------|----------|
| `apps/web/lib/api.ts` (~4800 lines) should be split into modules | Medium |
| Apply grade inflation adjustment in transcript scoring | Low |
| Add CSRF state validation in GitHub OAuth callback | Medium |
| Add GitHub API rate limiting | Medium |
| Migrate existing plaintext GitHub tokens to encrypted | High |
| Add error notifications for failed background tasks | Low |
| `docker-compose.yml` still uses legacy `zhipin` naming | Low |

Recommended split for `api.ts`:
- `lib/api/types.ts` — All interfaces
- `lib/api/client.ts` — ApiError, apiRequest helper
- `lib/api/candidate.ts` — candidateApi
- `lib/api/employer.ts` — employerApi, talentPoolApi
- `lib/api/interview.ts` — interviewApi
- `lib/api/scheduling.ts` — calendarApi, schedulingLinkApi
- `lib/api/organization.ts` — organizationApi, teamMemberApi
- `lib/api/index.ts` — Re-export everything (backwards compatible)

---

*Last updated: 2026-02-16*
