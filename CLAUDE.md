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
- **OpenAI API** (Primary for US market)
  - LLM/Scoring: `gpt-4` or `gpt-4-turbo`
  - Speech-to-Text: `whisper-1`
  - Env vars: `OPENAI_API_KEY`

- **DeepSeek API** (Fallback/cost optimization)
  - LLM/Scoring: `deepseek-chat` model
  - Env vars: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`

### 2. Target Verticals (Student-Focused)

| Vertical | Description | Target Students |
|----------|-------------|-----------------|
| `engineering` | Software Engineering, DevOps | CS, SE, CE majors |
| `data` | Data Science, ML, Analytics | Data Science, Stats, CS |
| `business` | PM, Marketing, Finance | Business, Econ majors |
| `design` | UX/UI, Product Design | Design, HCI majors |

### 3. Role Types

```python
# Engineering
SOFTWARE_ENGINEER, FRONTEND_ENGINEER, BACKEND_ENGINEER
FULLSTACK_ENGINEER, MOBILE_ENGINEER, DEVOPS_ENGINEER

# Data
DATA_ANALYST, DATA_SCIENTIST, ML_ENGINEER, DATA_ENGINEER

# Business
PRODUCT_MANAGER, BUSINESS_ANALYST, MARKETING_ASSOCIATE
FINANCE_ANALYST, CONSULTANT

# Design
UX_DESIGNER, UI_DESIGNER, PRODUCT_DESIGNER
```

### 4. Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| Storage | Cloudflare R2 (S3-compatible) |
| AI | OpenAI (primary), DeepSeek (fallback) |
| Auth | GitHub OAuth, Email/Password, JWT |
| Email | Resend |

### 5. Branding

- **Name**: Pathway
- **Tagline**: "Show your growth, land your first job"
- **Colors**: Indigo/Purple gradient (`from-indigo-600 to-purple-600`)
- **Logo**: Growth chart icon in gradient background
- **Target**: US college students (primarily CS/Engineering initially)

### 6. Language

- **English only** - US market focus
- No internationalization needed initially
- All error messages, UI text, and API responses in English

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/pathway

# Security
API_SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# OpenAI (Primary AI)
OPENAI_API_KEY=sk-...

# DeepSeek (Fallback)
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com

# GitHub OAuth
GITHUB_CLIENT_ID=Iv1.xxxx
GITHUB_CLIENT_SECRET=xxxx

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

## Scoring Dimensions (Student-Focused)

The AI evaluates candidates on 5 dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Communication | 20% | Clarity, articulation, confidence |
| Problem Solving | 25% | Analytical thinking, approach to challenges |
| Technical Knowledge | 25% | Relevant skills, depth of understanding |
| Growth Mindset | 15% | Learning from failures, curiosity, adaptability |
| Culture Fit | 15% | Teamwork, values alignment, enthusiasm |

**Note**: "Growth Mindset" replaced "Motivation" from the China version to better align with US hiring practices.

## Key Features

### Student Profile

```typescript
interface Candidate {
  // Basic info
  name: string
  email: string
  phone: string

  // Education (new for Pathway)
  university?: string
  major?: string
  graduationYear?: number
  gpa?: number
  courses?: string[]

  // GitHub integration (new for Pathway)
  githubUsername?: string
  githubData?: {
    repos: Array<{ name, language, stars, url }>
    languages: Record<string, number>
    totalContributions?: number
  }
  githubConnectedAt?: string

  // Resume
  resumeUrl?: string
  resumeParsedData?: ParsedResumeData
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
- Fetches: profile, repos, languages, contribution count
- Displayed on student profile for employers
- Can be refreshed to update data

```python
# GitHub OAuth endpoints
GET  /api/candidates/auth/github/url      # Get OAuth URL
POST /api/candidates/auth/github/callback  # Exchange code
DELETE /api/candidates/me/github           # Disconnect
GET  /api/candidates/me/github             # Get GitHub info
POST /api/candidates/me/github/refresh     # Refresh data
```

## User Flows

### Student Flow

```
Register (/register)
    ↓
Complete Profile (education info)
    ↓
Connect GitHub (OAuth)
    ↓
Start Interview (/interview/select)
    ↓
Select Vertical (Engineering/Data/Business/Design)
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
Browse Talent Pool (/employer/dashboard/talent)
    ↓
Filter (vertical, school, graduation year, score)
    ↓
View Candidate Profiles (progress charts, GitHub, videos)
    ↓
Contact Promising Candidates
```

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
| `/employer/dashboard/talent` | Browse talent pool |

## File Structure

```
apps/
├── api/                           # FastAPI backend
│   ├── app/
│   │   ├── main.py               # App entry point
│   │   ├── config.py             # Settings with GitHub OAuth
│   │   ├── models/
│   │   │   ├── candidate.py      # Candidate + education + GitHub
│   │   │   └── employer.py       # Employer + verticals/roles
│   │   ├── routers/
│   │   │   ├── auth.py           # Authentication
│   │   │   ├── candidates.py     # Student endpoints + GitHub OAuth
│   │   │   ├── employers.py      # Employer endpoints
│   │   │   ├── interviews.py     # Interview flow
│   │   │   └── questions.py      # Question management
│   │   ├── services/
│   │   │   ├── scoring.py        # AI scoring (Growth Mindset)
│   │   │   ├── github.py         # GitHub OAuth service
│   │   │   └── transcription.py  # Whisper transcription
│   │   └── schemas/
│   │       ├── candidate.py      # Pydantic schemas
│   │       └── question.py       # Student interview questions
│   └── requirements.txt
│
└── web/                           # Next.js frontend
    ├── app/
    │   ├── page.tsx              # Landing page (Pathway branding)
    │   ├── layout.tsx            # Root layout (English)
    │   ├── (auth)/
    │   │   ├── login/
    │   │   └── register/
    │   ├── auth/
    │   │   └── github/callback/  # GitHub OAuth callback
    │   ├── dashboard/            # Student dashboard
    │   └── employer/
    │       ├── login/
    │       └── dashboard/
    ├── components/
    │   ├── layout/
    │   │   ├── navbar.tsx        # Pathway logo + nav
    │   │   └── footer.tsx        # Pathway footer
    │   └── ui/                   # shadcn components
    └── lib/
        └── api.ts                # API client (updated types)
```

## Interview Questions (Examples)

### Engineering

1. "Tell me about a project you've built. What was the most challenging part?"
2. "Describe a bug that took you a long time to fix. How did you approach it?"
3. "What technology are you most excited to learn and why?"
4. "How do you stay updated with new technologies?"
5. "Tell me about a time you worked on a team project. What was your role?"

### Data

1. "Describe a time you used data to solve a problem or make a decision."
2. "How would you explain a complex analysis to a non-technical stakeholder?"
3. "What's your approach when you encounter messy or incomplete data?"
4. "Tell me about a project where you had to learn a new tool or technique."
5. "How do you validate that your analysis is correct?"

### Business

1. "Tell me about a time you had to analyze data to make a decision."
2. "Describe a project where you had to influence others without authority."
3. "How do you prioritize when you have multiple deadlines?"
4. "Tell me about a failure and what you learned from it."
5. "Why are you interested in this field?"

### Design

1. "Walk me through your design process for a recent project."
2. "How do you incorporate user feedback into your designs?"
3. "Describe a time when you had to advocate for your design decisions."
4. "How do you balance user needs with business requirements?"
5. "What design trends are you following, and how do they influence your work?"

## API Endpoints (Key)

### Candidates

```
POST /api/candidates/             # Register
GET  /api/candidates/me           # Get profile
PATCH /api/candidates/me          # Update profile
POST /api/candidates/me/resume    # Upload resume
```

### GitHub OAuth

```
GET  /api/candidates/auth/github/url      # Get OAuth URL
POST /api/candidates/auth/github/callback # Exchange code
GET  /api/candidates/me/github            # Get GitHub info
DELETE /api/candidates/me/github          # Disconnect
POST /api/candidates/me/github/refresh    # Refresh data
```

### Interviews

```
POST /api/interviews/start-vertical  # Start vertical interview
GET  /api/interviews/{id}            # Get session
POST /api/interviews/{id}/response   # Submit video response
POST /api/interviews/{id}/complete   # Complete interview
GET  /api/interviews/{id}/results    # Get results
```

### Employers

```
POST /api/employers/register   # Register
POST /api/employers/login      # Login
GET  /api/employers/talent-pool # Browse candidates
GET  /api/employers/talent-pool/{id} # View candidate
POST /api/employers/talent-pool/{id}/contact # Contact
```

## Database Models

### Key Model Changes (from China version)

```python
# Candidate model additions
university: str
major: str
graduation_year: int
gpa: float
courses: List[str]  # JSON
github_username: str
github_access_token: str  # Encrypted
github_data: dict  # JSON (repos, languages, contributions)
github_connected_at: datetime

# CandidateVerticalProfile changes
total_interviews: int  # Instead of attempt_count
last_interview_at: datetime
next_eligible_at: datetime  # 30 days after last

# InterviewHistoryEntry (new)
interview_session_id: UUID
score: float
completed_at: datetime
```

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

### Key Files
- `app/services/progressive_questions.py` - AI question generation
- `app/models/employer.py` - CandidateQuestionHistory model
- Question tracking in `candidate_question_history` table

## Admin Dashboard

Access at `/admin` with employer credentials:

### Tabs
- **Universities**: Manage university database, prestige rankings
- **Courses**: Course difficulty tiers, grade mappings
- **Clubs**: 147 Berkeley clubs with prestige tiers (1-5)
- **Candidates**: View all candidates, interview history

### Club Prestige Tiers
- **Tier 5**: Most prestigious (BIG, Free Ventures, BFR, SEB)
- **Tier 4**: Highly selective (VCG, NGC, Codeology)
- **Tier 3**: Selective (most professional clubs)
- **Tier 2**: Moderate (many academic clubs)
- **Tier 1**: Open membership

## Testing Requirements

All new features need tests:
- Unit tests for services
- Integration tests for API endpoints
- E2E tests for critical flows (registration, interview, GitHub OAuth)

## Migration Notes

### From China (ZhiMian) to US (Pathway)

1. **Verticals**: Changed from `new_energy`/`sales` to `software_engineering`/`data`/`product`/`design`/`finance`
2. **Roles**: Changed from China-specific (battery_engineer, ev_sales) to US entry-level roles
3. **Auth**: Removed WeChat OAuth, added GitHub OAuth
4. **Scoring**: Changed "Motivation" dimension to "Growth Mindset"
5. **Language**: All Chinese strings replaced with English
6. **Interview Cadence**: Changed from max-3-retries to monthly (30-day cooldown)
7. **Profile**: Added education fields, GitHub integration, transcript analysis
8. **Branding**: ZhiMian (智面) → Pathway, green → indigo/purple
9. **Questions**: Changed from static templates to AI-generated progressive questions

### Backup Branch

The original China market version is preserved in `zhimian-china-backup` branch.
