# Claude Code Rules for Pathway

## Project Overview

Pathway is an AI-powered career platform for US college students. Students interview monthly to show their growth over time, connect their GitHub, and track their coursework. Employers can see candidates' progress trajectories, not just a single snapshot.

**Current Branch**: `us-college-pivot` (pivoted from `zhimian-china-backup` China market version)

## Core Value Proposition

- **For Students**: Stop grinding Leetcode. Interview monthly, show real growth, connect your GitHub.
- **For Employers**: See candidates' growth over 2-4 years. Hire based on trajectory, not just current state.

## Critical Rules

### 1. AI Services

**Approved AI Services:**
- **Anthropic Claude API** (Primary for all AI tasks)
  - LLM/Scoring: Claude Sonnet 4.5 (`claude-sonnet-4-5-20251101`)
  - Env vars: `ANTHROPIC_API_KEY`

- **DeepSeek API** (Fallback/cost optimization)
  - LLM/Scoring: `deepseek-chat` model
  - Env vars: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`

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

**Rule**: No more than 2 colors per component. Keep it minimal.

### 3. Target Verticals (Student-Focused)

| Vertical | Description | Target Students |
|----------|-------------|-----------------|
| `software_engineering` | Software Engineering, DevOps | CS, SE, CE majors |
| `data` | Data Science, ML, Analytics | Data Science, Stats, CS |
| `product` | PM, Business Ops | Business, Econ majors |
| `design` | UX/UI, Product Design | Design, HCI majors |
| `finance` | Finance, Investment | Finance, Econ majors |

### 4. Role Types

```python
# Engineering
SOFTWARE_ENGINEER, FRONTEND_ENGINEER, BACKEND_ENGINEER
FULLSTACK_ENGINEER, MOBILE_ENGINEER, DEVOPS_ENGINEER, EMBEDDED_ENGINEER, QA_ENGINEER

# Data
DATA_ANALYST, DATA_SCIENTIST, ML_ENGINEER, DATA_ENGINEER

# Product
PRODUCT_MANAGER, ASSOCIATE_PM

# Design
UX_DESIGNER, UI_DESIGNER, PRODUCT_DESIGNER

# Finance
IB_ANALYST, FINANCE_ANALYST, EQUITY_RESEARCH
```

### 5. Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, PostgreSQL (Neon) |
| Storage | Cloudflare R2 (S3-compatible) |
| AI | Claude Sonnet 4.5 (primary), DeepSeek (fallback) |
| Auth | GitHub OAuth, Email/Password, JWT |
| Email | Resend |

### 6. Database Models

All models use **CUID** prefixes:
- `c_` - Candidates
- `e_` - Employers
- `i_` - Interviews
- `j_` - Jobs
- `o_` - Organizations
- `rv_` - ResumeVersions (growth tracking)
- `gah_` - GitHubAnalysisHistory (growth tracking)
- `pcl_` - ProfileChangeLogs (growth tracking)

### 7. Scoring System (5 Dimensions)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Communication | 20% | Clarity, articulation, confidence |
| Problem Solving | 25% | Analytical thinking, approach to challenges |
| Technical Knowledge | 25% | Relevant skills, depth of understanding |
| Growth Mindset | 15% | Learning from failures, curiosity, adaptability |
| Culture Fit | 15% | Teamwork, values alignment, enthusiasm |

Score range: 0-10 (floating point)

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/pathway

# Security
API_SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# Anthropic (Primary AI)
ANTHROPIC_API_KEY=sk-ant-...

# DeepSeek (Fallback)
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com

# GitHub OAuth
GITHUB_CLIENT_ID=Iv1.xxxx
GITHUB_CLIENT_SECRET=xxxx

# Google Calendar OAuth
GOOGLE_CLIENT_ID=xxxx
GOOGLE_CLIENT_SECRET=xxxx

# Cloudflare R2 (Storage)
R2_ACCOUNT_ID=xxxx
R2_ACCESS_KEY_ID=xxxx
R2_SECRET_ACCESS_KEY=xxxx
R2_BUCKET_NAME=pathway-videos

# Email (Resend)
RESEND_API_KEY=re_xxxx
EMAIL_FROM=Pathway <noreply@pathway.careers>

# URLs
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

---

## Growth Tracking System

**Recruiter-only feature** that tracks all key datapoints with timestamps to show student growth over time.

### Overview

| Component | Purpose |
|-----------|---------|
| `ResumeVersion` | Track all resume uploads (versioned, not overwritten) |
| `GitHubAnalysisHistory` | Track GitHub score changes over time |
| `ProfileChangeLog` | Audit trail for GPA, major, education changes |
| Growth Timeline API | Concise endpoint for recruiter consumption |
| Growth Timeline UI | Progressive disclosure component |

### Database Tables

#### `resume_versions`
```python
class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(String, primary_key=True)  # rv_{uuid}
    candidate_id = Column(String, ForeignKey("candidates.id"))
    version_number = Column(Integer, nullable=False)
    storage_key = Column(String, nullable=False)
    raw_text = Column(Text)
    parsed_data = Column(JSONB)
    skills_added = Column(JSONB)      # Delta from previous version
    skills_removed = Column(JSONB)    # Delta from previous version
    is_current = Column(Boolean, default=True)
    uploaded_at = Column(DateTime(timezone=True))
```

#### `github_analysis_history`
```python
class GitHubAnalysisHistory(Base):
    __tablename__ = "github_analysis_history"

    id = Column(String, primary_key=True)  # gah_{uuid}
    candidate_id = Column(String, ForeignKey("candidates.id"))
    overall_score = Column(Float)
    originality_score = Column(Float)
    activity_score = Column(Float)
    depth_score = Column(Float)
    collaboration_score = Column(Float)
    total_repos_analyzed = Column(Integer)
    score_delta = Column(Float)       # Change from previous analysis
    repos_delta = Column(Integer)
    analyzed_at = Column(DateTime(timezone=True))
```

#### `profile_change_logs`
```python
class ProfileChangeLog(Base):
    __tablename__ = "profile_change_logs"

    id = Column(String, primary_key=True)  # pcl_{uuid}
    candidate_id = Column(String, ForeignKey("candidates.id"))
    change_type = Column(String)  # gpa_update, major_change, etc.
    field_name = Column(String)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    change_source = Column(String)  # "manual", "resume_parse", "transcript_verify"
    changed_at = Column(DateTime(timezone=True))
```

### API Endpoint

```
GET /api/employers/talent-pool/{profile_id}/growth-timeline
Query: time_range = "6m" | "1y" | "2y" | "all" (default: "1y")
```

**Response:**
```json
{
  "candidate_id": "c_xxx",
  "candidate_name": "John Doe",
  "summary": {
    "total_interviews": 4,
    "interview_score_change": 1.8,
    "github_connected": true,
    "github_score_change": 12,
    "resume_versions_count": 3,
    "skills_growth_count": 8
  },
  "events": [
    {
      "event_type": "interview",
      "event_date": "2026-01-15T...",
      "title": "Completed Interview #4",
      "delta": 0.5,
      "icon": "interview"
    },
    {
      "event_type": "resume",
      "event_date": "2025-12-01T...",
      "title": "Resume Updated (v3)",
      "subtitle": "+2 skills, +1 project",
      "icon": "document"
    }
  ]
}
```

### Frontend Component

**File**: `apps/web/components/employer/growth-timeline.tsx`

- Progressive disclosure: summary always visible, details expandable
- Time range filter: 6m, 1y, 2y, all
- Stone/teal color palette per DESIGN_PRINCIPLES.md

### Key Files

| File | Purpose |
|------|---------|
| `apps/api/app/models/resume_version.py` | ResumeVersion model |
| `apps/api/app/models/github_analysis_history.py` | GitHubAnalysisHistory model |
| `apps/api/app/models/profile_change_log.py` | ProfileChangeLog model |
| `apps/api/app/services/growth_tracking.py` | GrowthTrackingService |
| `apps/api/app/utils/date_parser.py` | Date string parser utility |
| `apps/api/app/schemas/growth.py` | Pydantic schemas |
| `apps/web/components/employer/growth-timeline.tsx` | UI component |

### Integration Points

1. **Resume Upload** (`candidates.py`): Creates `ResumeVersion` on each upload
2. **GitHub Analysis** (`github_analysis.py`): Creates `GitHubAnalysisHistory` snapshot
3. **Profile Updates** (`candidates.py`): Logs changes to `ProfileChangeLog`

---

## Key Features

### Student Profile

```typescript
interface Candidate {
  // Basic info
  name: string
  email: string
  phone: string

  // Education
  university?: string
  major?: string
  graduationYear?: number
  gpa?: number
  courses?: string[]

  // GitHub integration
  githubUsername?: string
  githubData?: GitHubData
  githubConnectedAt?: string

  // Resume
  resumeUrl?: string
  resumeParsedData?: ParsedResumeData

  // Growth tracking relationships
  resumeVersions: ResumeVersion[]
  githubAnalysisHistory: GitHubAnalysisHistory[]
  profileChangeLogs: ProfileChangeLog[]
}
```

### Monthly Interview System

- Students can interview **once per month per vertical** (30-day cooldown)
- Best score shown to employers, but full history available
- Visual progress chart showing improvement over time
- Comparison to cohort averages (anonymized)

```python
class CandidateVerticalProfile:
    vertical: Vertical
    role_type: RoleType
    total_interviews: int  # Total interviews taken
    best_score: float      # Best score achieved
    last_interview_at: datetime
    next_eligible_at: datetime  # 30 days after last
```

### GitHub Integration

- OAuth connection with GitHub
- Code quality analysis (originality, activity, depth, collaboration scores)
- **History tracking**: Each analysis creates a snapshot for growth tracking
- Can be refreshed to update data

```python
# GitHub OAuth endpoints
GET  /api/candidates/auth/github/url      # Get OAuth URL
POST /api/candidates/auth/github/callback  # Exchange code
DELETE /api/candidates/me/github           # Disconnect
GET  /api/candidates/me/github             # Get GitHub info
POST /api/candidates/me/github/refresh     # Refresh data
POST /api/candidates/me/github/analyze     # Run code analysis
```

---

## User Flows

### Student Flow

```
Register (/register)
    ↓
Complete Profile (education info)
    ↓
Upload Resume (creates ResumeVersion v1)
    ↓
Connect GitHub (OAuth)
    ↓
Analyze GitHub (creates GitHubAnalysisHistory)
    ↓
Start Interview (/interview/select)
    ↓
Select Vertical (Engineering/Data/Product/Design/Finance)
    ↓
Complete 5 Video Questions (15 min)
    ↓
View Results & Feedback
    ↓
Return Monthly to Interview Again
    ↓
Get Matched (employers reach out)
```

### Employer Flow

```
Register/Login (/employer/login)
    ↓
Create Job Postings (select vertical, role type)
    ↓
Browse Talent Pool (/employer/dashboard/talent-pool)
    ↓
Filter (vertical, school, graduation year, score)
    ↓
View Candidate Profiles
    ↓
View Growth Timeline (interview progress, GitHub changes, resume versions)
    ↓
Update Candidate Status (New/Contacted/In Review/Shortlisted/Rejected/Hired)
    ↓
Contact Promising Candidates
```

---

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/register` | Student signup |
| `/login` | Student login |
| `/dashboard` | Student dashboard with progress |
| `/interview/select` | Start new monthly interview |
| `/auth/github/callback` | GitHub OAuth callback |
| `/employer/login` | Employer login/register |
| `/employer/dashboard` | Employer dashboard |
| `/employer/dashboard/talent-pool` | Browse talent pool |
| `/employer/dashboard/talent-pool/[id]` | View candidate + growth timeline |
| `/schedule/[slug]` | Public self-scheduling page |

---

## Project Structure

```
apps/
├── api/                           # FastAPI backend
│   ├── app/
│   │   ├── main.py               # App entry point
│   │   ├── config.py             # Settings
│   │   ├── models/
│   │   │   ├── candidate.py      # Candidate + growth relationships
│   │   │   ├── employer.py       # Employer + jobs + orgs
│   │   │   ├── resume_version.py # Resume version tracking
│   │   │   ├── github_analysis_history.py # GitHub snapshots
│   │   │   ├── profile_change_log.py # Profile audit trail
│   │   │   └── activity.py       # Activities + Awards
│   │   ├── routers/
│   │   │   ├── auth.py           # Authentication
│   │   │   ├── candidates.py     # Student endpoints + growth hooks
│   │   │   ├── employers.py      # Employer endpoints + growth timeline
│   │   │   ├── interviews.py     # Interview flow
│   │   │   └── scheduling.py     # Self-scheduling
│   │   ├── services/
│   │   │   ├── scoring.py        # AI scoring
│   │   │   ├── growth_tracking.py # Growth tracking service
│   │   │   ├── github.py         # GitHub OAuth
│   │   │   ├── github_analysis.py # Code quality analysis
│   │   │   ├── calendar.py       # Google Calendar
│   │   │   └── email.py          # Resend emails
│   │   ├── schemas/
│   │   │   ├── candidate.py      # Pydantic schemas
│   │   │   └── growth.py         # Growth timeline schemas
│   │   └── utils/
│   │       ├── date_parser.py    # Parse "Fall 2022" to Date
│   │       └── auth.py           # JWT helpers
│   └── migrations/               # Alembic migrations
│
└── web/                           # Next.js frontend
    ├── app/
    │   ├── page.tsx              # Landing page
    │   ├── layout.tsx            # Root layout
    │   ├── (candidate)/          # Student pages
    │   │   └── dashboard/        # Student dashboard
    │   ├── (employer)/           # Employer pages
    │   │   └── dashboard/
    │   │       ├── talent-pool/
    │   │       │   └── [profileId]/ # Candidate detail + growth timeline
    │   │       └── interviews/   # Scheduled interviews
    │   └── schedule/             # Public scheduling
    │       └── [slug]/
    ├── components/
    │   ├── employer/
    │   │   ├── growth-timeline.tsx # Growth timeline display
    │   │   ├── candidate-notes.tsx # Private notes
    │   │   └── match-alerts.tsx    # Match notifications
    │   ├── scheduling/
    │   │   ├── availability-grid.tsx
    │   │   └── slot-picker.tsx
    │   └── ui/                   # shadcn components
    └── lib/
        └── api.ts                # API client (~4700 lines)
```

---

## API Endpoints (Key)

### Candidates
```
POST /api/candidates/             # Register
GET  /api/candidates/me           # Get profile
PATCH /api/candidates/me          # Update profile
POST /api/candidates/{id}/resume  # Upload resume (creates ResumeVersion)
```

### GitHub
```
GET  /api/candidates/auth/github/url      # Get OAuth URL
POST /api/candidates/auth/github/callback # Exchange code
GET  /api/candidates/me/github            # Get GitHub info
DELETE /api/candidates/me/github          # Disconnect
POST /api/candidates/me/github/refresh    # Refresh data
POST /api/candidates/me/github/analyze    # Run analysis (creates snapshot)
GET  /api/candidates/me/github/analysis   # Get latest analysis
```

### Interviews
```
POST /api/interviews/start-vertical  # Start vertical interview
GET  /api/interviews/{id}            # Get session
POST /api/interviews/{id}/response   # Submit video response
POST /api/interviews/{id}/complete   # Complete interview
GET  /api/interviews/{id}/results    # Get results
```

### Employers / Talent Pool
```
POST /api/employers/register                           # Register
POST /api/employers/login                              # Login
GET  /api/employers/talent-pool                        # Browse candidates
GET  /api/employers/talent-pool/{id}                   # View candidate
PATCH /api/employers/talent-pool/{id}/status           # Update candidate status
GET  /api/employers/talent-pool/{id}/growth-timeline   # Get growth timeline
```

### Scheduling
```
POST /api/employers/scheduling-links           # Create self-scheduling link
GET  /api/employers/scheduling-links           # List links
GET  /api/schedule/{slug}                      # Public: Get available slots
POST /api/schedule/{slug}/book                 # Public: Book slot
```

---

## Progressive Question System

When candidates re-interview after 30+ days, the AI generates personalized questions:

### How It Works
1. **First Interview**: AI generates questions based on resume, GitHub, transcript at foundational level
2. **Follow-up Interviews**:
   - Retrieves history: topics covered, scores, weak areas
   - Avoids redundancy: never repeats same themes
   - Tests improvement: probes deeper into weak areas
   - Adjusts difficulty based on past performance

### Difficulty Levels
- **Level 1 (Foundational)**: Score < 5.5 - Basic behavioral and intro technical
- **Level 2 (Intermediate)**: Score 5.5-7.5 - Deeper scenarios, trade-offs
- **Level 3 (Advanced)**: Score > 7.5 - System design, leadership, complex problems

---

## Testing Requirements

All new features need tests:
- Unit tests for services
- Integration tests for API endpoints
- E2E tests for critical flows (registration, interview, GitHub OAuth)

```bash
# Backend tests
cd apps/api
python -m pytest

# Frontend type check
cd apps/web
npm run type-check

# Lint
npm run lint
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

- ✅ Monthly interview system with 30-day cooldown
- ✅ GitHub OAuth + code quality analysis
- ✅ Progressive AI question generation
- ✅ Transcript analysis
- ✅ Profile sharing preferences
- ✅ Google Calendar integration
- ✅ Candidate status management (New/Contacted/In Review/Shortlisted/Rejected/Hired)
- ✅ GitHub analysis display (visual scores)
- ✅ Private candidate notes for employers
- ✅ Scheduled interviews page with Google Meet
- ✅ Self-scheduling links
- ✅ Match alerts for high-scoring candidates
- ✅ Organization teams with roles and invites
- ✅ **Growth Tracking System** (resume versions, GitHub history, profile change logs)
- ✅ **Growth Timeline UI** (recruiter-only progressive disclosure)

---

## Known Technical Debt

| File | Issue | Priority |
|------|-------|----------|
| `apps/web/lib/api.ts` | ~4700 lines, should be split into modules | Medium |

Recommended split for `api.ts`:
- `lib/api/types.ts` - All interfaces
- `lib/api/client.ts` - ApiError, apiRequest helper
- `lib/api/candidate.ts` - candidateApi
- `lib/api/employer.ts` - employerApi, talentPoolApi
- `lib/api/interview.ts` - interviewApi
- `lib/api/scheduling.ts` - calendarApi, schedulingLinkApi
- `lib/api/organization.ts` - organizationApi, teamMemberApi
- `lib/api/index.ts` - Re-export everything (backwards compatible)
