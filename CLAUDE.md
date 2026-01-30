# Claude Code Rules for Pathway

## Project Overview
Pathway is an AI-powered career platform for US college students. Students interview monthly to show their growth over time, connect their GitHub, and track their coursework. Employers can see candidates' progress trajectories, not just a single snapshot.

## Core Value Proposition
- **For Students**: Stop grinding Leetcode. Interview monthly, show real growth, connect your GitHub.
- **For Employers**: See candidates' growth over 2-4 years. Hire based on trajectory, not just current state.

## Critical Rules

### 1. AI Services
**Approved AI Services:**
- **OpenAI API** for US market
  - LLM/Scoring: `gpt-4` or `gpt-4-turbo`
  - Speech-to-Text: `whisper-1`
  - Env vars: `OPENAI_API_KEY`

- **DeepSeek API** as fallback/cost optimization
  - LLM/Scoring: `deepseek-chat` model
  - Env vars: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`

### 2. Target Verticals (Student-Focused)
- **Engineering/Tech**: Software Engineering, Data Science, ML/AI, DevOps
- **Business**: Product Management, Marketing, Finance, Consulting
- **Design**: UX/UI Design, Product Design, Graphic Design
- **Research**: Research Assistant, Lab Positions, Academic

### 3. Target Roles (Entry-Level)
- Software Engineer Intern/New Grad
- Data Analyst / Data Scientist
- Product Manager
- UX Designer
- Business Analyst
- Marketing Associate
- Research Assistant

### 4. Tech Stack
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Storage**: Cloudflare R2 (S3-compatible)
- **AI**: OpenAI (primary), DeepSeek (fallback)
- **Auth**: GitHub OAuth, Email/Password

### 5. Branding
- Name: **Pathway**
- Tagline: "Show your growth, land your first job"
- Colors: Indigo/Purple gradient (`from-indigo-600 to-purple-600`)
- Target: US college students (primarily CS/Engineering initially)

### 6. Language
- **English only** - US market focus
- No internationalization needed initially

## Environment Variables Required

```env
# Database
DATABASE_URL=postgresql://...

# Security
API_SECRET_KEY=...
JWT_SECRET=...

# OpenAI (Primary)
OPENAI_API_KEY=sk-...

# DeepSeek (Fallback)
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com

# GitHub OAuth
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Cloudflare R2 (Storage)
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=pathway-videos

# Email
RESEND_API_KEY=re_...

# URLs
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

## Scoring Dimensions (Student-Focused)
The AI evaluates candidates on 5 dimensions:
1. **Communication** (20%) - Clarity, articulation, confidence
2. **Problem Solving** (25%) - Analytical thinking, approach to challenges
3. **Technical Knowledge** (25%) - Relevant skills, depth of understanding
4. **Growth Mindset** (15%) - Learning from failures, curiosity, adaptability
5. **Culture Fit** (15%) - Teamwork, values alignment, enthusiasm

## Key Features

### Student Profile
- **Education**: University, Major, Graduation Year, GPA (optional)
- **GitHub**: Connected account, repos, contribution stats
- **Courses**: Current and past relevant coursework
- **Interview History**: Monthly interviews with progress tracking

### Progress Tracking
- Students can interview once per month per vertical
- Best score shown to employers, but full history available
- Visual progress chart showing improvement over time
- Comparison to cohort averages (anonymized)

### GitHub Integration
- OAuth connection
- Display top repositories
- Show contribution graph
- Highlight languages/technologies used

## User Flows

### Student Flow
1. **Register** (`/register`) → Basic info + education details
2. **Connect GitHub** → OAuth flow to link GitHub account
3. **Add Courses** → List current/relevant coursework
4. **Start Interview** → Select vertical, complete 5 video questions
5. **View Progress** → Dashboard shows scores over time
6. **Get Matched** → Employers reach out based on trajectory

### Employer Flow
1. **Register/Login** (`/employer/login`)
2. **Browse Talent Pool** → Filter by vertical, school, graduation year
3. **View Candidate Profiles** → See progress charts, GitHub, coursework
4. **Watch Interviews** → View video responses, AI analysis
5. **Reach Out** → Contact promising candidates

### Key URLs
- `/` - Landing page
- `/register` - Student signup
- `/login` - Student login
- `/dashboard` - Student dashboard with progress
- `/interview/select` - Start new monthly interview
- `/employer/login` - Employer login/register
- `/employer/dashboard` - Employer dashboard
- `/employer/talent` - Browse talent pool

## File Structure
```
apps/
├── api/          # FastAPI backend
│   ├── app/
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic (scoring, transcription, storage)
│   │   └── schemas/     # Pydantic schemas
└── web/          # Next.js frontend
    ├── app/             # App Router pages
    │   ├── (student)/   # Student flow
    │   └── (employer)/  # Employer dashboard
    ├── components/      # React components
    └── lib/             # API client, utilities
```

## Interview Questions (Examples)

### Engineering/Tech
1. "Tell me about a project you've built. What was the most challenging part?"
2. "Describe a bug that took you a long time to fix. How did you approach it?"
3. "What technology are you most excited to learn and why?"
4. "How do you stay updated with new technologies?"
5. "Tell me about a time you worked on a team project. What was your role?"

### Business
1. "Tell me about a time you had to analyze data to make a decision."
2. "Describe a project where you had to influence others without authority."
3. "How do you prioritize when you have multiple deadlines?"
4. "Tell me about a failure and what you learned from it."
5. "Why are you interested in [this field]?"

## Testing Requirements

Same as before - all features need tests. See testing section for details.
