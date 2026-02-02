# Pathway

AI-powered career platform for US college students. Interview monthly to show your growth, connect your GitHub, and get matched with top employers based on your trajectory.

## Core Value Proposition

**For Students**: Stop grinding Leetcode. Interview monthly, show real growth, connect your GitHub.

**For Employers**: See candidates' growth over 2-4 years. Hire based on trajectory, not just a single snapshot.

## Key Features

### Progressive AI Interview System
- **Monthly Interviews**: Interview once per month per vertical to show improvement
- **AI-Generated Questions**: Personalized questions based on resume, GitHub, transcript
- **Knowledge Evolution Testing**: Follow-up interviews probe deeper into weak areas to test improvement
- **No Redundancy**: AI avoids asking about topics already covered in previous interviews
- **Adaptive Difficulty**: Questions get harder as candidates improve (foundational → intermediate → advanced)

### 5-Dimension AI Scoring
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Communication | 20% | Clarity, articulation, confidence |
| Problem Solving | 25% | Analytical thinking, approach to challenges |
| Technical Knowledge | 25% | Relevant skills, depth of understanding |
| Growth Mindset | 15% | Learning from failures, curiosity, adaptability |
| Culture Fit | 15% | Teamwork, values alignment, enthusiasm |

### Comprehensive Student Profiles
- **GitHub Integration**: OAuth connection to showcase repos and contributions
- **Resume Parsing**: AI-powered resume analysis and skill extraction
- **Transcript Analysis**: Course-level GPA, difficulty tiers, technical depth
- **Clubs & Activities**: 147 Berkeley clubs with prestige tiers (1-5 scale)
- **Progress Tracking**: Visual charts showing improvement over time

### Talent Pool for Employers
- Browse candidates by vertical, school, graduation year, score
- View complete profiles: GitHub, resume, transcript, interview videos
- Track candidate improvement over time
- Auto-matching to relevant job postings

## Target Verticals

### Software Engineering
| Role | AI Assessment | Target |
|------|---------------|--------|
| Software Engineer | Coding, system design, problem solving | CS/SE majors |
| Frontend Engineer | React, TypeScript, UI/UX thinking | Web development focus |
| Backend Engineer | APIs, databases, scalability | Server-side focus |
| DevOps Engineer | CI/CD, cloud, infrastructure | Operations focus |

### Data
| Role | AI Assessment | Target |
|------|---------------|--------|
| Data Analyst | SQL, visualization, insights | Analytics focus |
| Data Scientist | ML, statistics, Python | Data science majors |
| ML Engineer | Deep learning, model deployment | AI/ML focus |

### Product
| Role | AI Assessment | Target |
|------|---------------|--------|
| Product Manager | Strategy, prioritization, communication | Business/Tech |
| Business Analyst | Analysis, requirements, stakeholders | Business majors |

### Design
| Role | AI Assessment | Target |
|------|---------------|--------|
| UX Designer | User research, wireframing, prototyping | HCI/Design majors |
| UI Designer | Visual design, design systems | Visual design focus |
| Product Designer | End-to-end design thinking | Design generalists |

### Finance
| Role | AI Assessment | Target |
|------|---------------|--------|
| IB Analyst | Financial modeling, valuation | Finance/Econ majors |
| Finance Analyst | Analysis, forecasting | Business majors |

## Tech Stack

### Frontend (apps/web)
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- MediaRecorder API for video capture

### Backend (apps/api)
- Python FastAPI
- SQLAlchemy ORM + Alembic migrations
- PostgreSQL (Neon serverless)
- Cloudflare R2 (video/resume storage)
- OpenAI API (primary) / DeepSeek (fallback) for AI scoring
- JWT authentication
- GitHub OAuth

## Project Structure

```
pathway/
├── apps/
│   ├── web/                    # Next.js 14 Frontend
│   │   ├── app/
│   │   │   ├── (candidate)/    # Student dashboard, interviews
│   │   │   ├── (employer)/     # Employer dashboard, talent pool, admin
│   │   │   └── page.tsx        # Landing page
│   │   ├── components/
│   │   │   ├── interview/      # Video recorder, question display
│   │   │   ├── dashboard/      # Progress charts, profile cards
│   │   │   └── layout/         # Navbar, footer
│   │   └── lib/
│   │       └── api.ts          # API client with TypeScript types
│   │
│   └── api/                    # Python FastAPI Backend
│       ├── app/
│       │   ├── routers/        # API endpoints
│       │   │   ├── auth.py     # Authentication
│       │   │   ├── candidates.py # Student endpoints
│       │   │   ├── employers.py  # Employer endpoints
│       │   │   ├── interviews.py # Interview flow
│       │   │   ├── admin.py      # Admin dashboard
│       │   │   ├── courses.py    # Course/transcript management
│       │   │   └── activities.py # Clubs & activities
│       │   ├── models/         # SQLAlchemy models
│       │   │   ├── candidate.py  # Student + education + GitHub
│       │   │   ├── employer.py   # Employers + jobs + question history
│       │   │   ├── course.py     # Universities, courses, transcripts
│       │   │   ├── activity.py   # Clubs, activities, awards
│       │   │   └── ml_scoring.py # ML training data
│       │   ├── services/       # Business logic
│       │   │   ├── scoring.py    # AI scoring
│       │   │   ├── progressive_questions.py # AI question generation
│       │   │   ├── github.py     # GitHub OAuth
│       │   │   ├── github_analysis.py # Repo analysis
│       │   │   ├── transcript.py # Transcript parsing
│       │   │   └── resume.py     # Resume parsing & adaptive questions
│       │   ├── data/           # Seed data
│       │   │   ├── seed_clubs.py   # 147 Berkeley clubs with tiers
│       │   │   └── seed_courses.py # Course difficulty data
│       │   └── schemas/        # Pydantic schemas
│       └── migrations/         # Alembic database migrations
│
├── CLAUDE.md              # AI assistant context
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (or Neon)
- GitHub OAuth App

### 1. Environment Setup

```bash
cp apps/api/.env.example apps/api/.env
# Edit .env with your credentials
```

#### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Always |
| `JWT_SECRET` | Secret key for JWT tokens | Always |
| `API_SECRET_KEY` | API secret key | Always |
| `OPENAI_API_KEY` | OpenAI API key for AI features | Recommended |
| `DEEPSEEK_API_KEY` | DeepSeek API key (fallback) | Optional |
| `GITHUB_CLIENT_ID` | GitHub OAuth App client ID | For GitHub login |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App secret | For GitHub login |
| `R2_ACCOUNT_ID` | Cloudflare R2 account ID | For video storage |
| `R2_ACCESS_KEY_ID` | R2 access key | For video storage |
| `R2_SECRET_ACCESS_KEY` | R2 secret key | For video storage |
| `R2_BUCKET_NAME` | R2 bucket name | For video storage |
| `RESEND_API_KEY` | Resend API key for emails | Optional |

### 2. Start the Backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head  # Run migrations
uvicorn app.main:app --reload --port 8000
```

### 3. Start the Frontend

```bash
cd apps/web
npm install
npm run dev
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## User Flows

### Student Journey

1. **Register** (`/register`) - Create account with email + education info
2. **Connect GitHub** - OAuth flow to link GitHub account
3. **Upload Resume** - AI parses and extracts skills
4. **Add Transcript** - Course-level analysis with difficulty tiers
5. **Start Interview** - Select vertical (Engineering/Data/Product/Design/Finance)
6. **Complete Interview** - Answer 5 AI-generated personalized questions
7. **View Results** - See AI scores and feedback
8. **Track Progress** - Return monthly to interview again with new, progressive questions
9. **Get Matched** - Employers reach out based on trajectory

### Employer Journey

1. **Register/Login** (`/employer/login`)
2. **Create Job Posting** - Select vertical and role type
3. **Browse Talent Pool** - Filter by vertical, school, graduation year, score
4. **View Candidate Profiles** - See progress charts, GitHub, interview videos
5. **Contact Candidates** - Reach out to promising students

### Admin Dashboard

Access at `/admin` with employer credentials:
- **Universities Tab**: Manage university database, prestige rankings
- **Courses Tab**: Course difficulty tiers, grade mappings
- **Clubs Tab**: 147 Berkeley clubs with prestige tiers (1-5 scale)
- **Candidates Tab**: View all candidates, interview history

## Database Schema

### Core Tables
- `candidates` - Student profiles with education + GitHub data
- `candidate_vertical_profiles` - Per-vertical interview history
- `interview_sessions` - Individual interview instances
- `interview_responses` - Video responses with transcripts and scores
- `candidate_question_history` - Tracks questions asked to avoid repetition
- `employers` - Company accounts
- `jobs` - Job postings with vertical/role
- `matches` - Candidate-employer pipeline tracking

### Education Tables
- `universities` - University database with prestige rankings
- `courses` - Course catalog with difficulty tiers
- `course_grade_mappings` - Grade scale mappings per university
- `candidate_transcripts` - Uploaded transcripts with parsed data
- `candidate_course_grades` - Individual course grades

### Activity Tables
- `clubs` - Club database with prestige tiers (147 Berkeley clubs)
- `candidate_activities` - Student club memberships
- `candidate_awards` - Awards and achievements

## Progressive Question System

When candidates re-interview after 30+ days, the AI:
1. **Retrieves History**: Topics covered, scores, weak areas from previous interviews
2. **Avoids Redundancy**: Never asks the same themes twice
3. **Tests Improvement**: Generates follow-up questions in weak areas
4. **Adjusts Difficulty**:
   - Score < 5.5 → Foundational questions
   - Score 5.5-7.5 → Intermediate questions
   - Score > 7.5 → Advanced questions
5. **Personalizes**: References resume, GitHub projects, coursework

## Development

```bash
# Terminal 1: Backend
cd apps/api && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd apps/web && npm run dev
```

## Branch Information

- `main` - Production branch
- `us-college-pivot` - Current development (Pathway platform)
- `zhimian-china-backup` - Archived China market version

## License

MIT
