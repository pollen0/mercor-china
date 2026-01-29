# ZhiMian 智面

AI-powered video interview platform for China's job market. Automated 15-minute AI interviews with intelligent scoring, built for New Energy/EV and Sales verticals.

## Core Value Proposition

Cut screening time from weeks to hours by automating first-round interviews with AI.

## Target Verticals

### New Energy / EV
| Role | AI Assessment | Market Need |
|------|---------------|-------------|
| Battery Engineer | Technical knowledge tests | Huge talent shortage |
| Embedded Software | Coding + domain questions | Quality varies wildly |
| Autonomous Driving | Algorithm + simulation | 300k+ job gap |
| Supply Chain | Case studies | Need to hire fast |
| EV Sales | Role-play, product knowledge | High turnover |

### Sales / BD
| Role | AI Assessment |
|------|---------------|
| Sales Representative | Role-play scenarios, objection handling |
| BD Manager | Strategy + negotiation |
| Account Manager | Relationship building |

## Features

- **5-Dimension AI Scoring**
  - Communication (沟通能力)
  - Problem Solving (解决问题能力)
  - Domain Knowledge (专业知识)
  - Motivation (动机)
  - Culture Fit (文化契合度)

- **Vertical-Specific Questions**: Tailored interview templates for each role type
- **Async Video Interviews**: Candidates complete 15-minute interviews anytime
- **GPT-4o Evaluation**: Intelligent scoring with strengths/concerns analysis
- **Mandarin Support**: OpenAI Whisper transcription with Chinese language support
- **Employer Dashboard**: View ranked candidates, watch videos, read transcripts

## Tech Stack

### Frontend (apps/web)
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- MediaRecorder API for video capture

### Backend (apps/api)
- Python FastAPI
- SQLAlchemy ORM
- PostgreSQL (Neon serverless)
- Cloudflare R2 (video storage)
- OpenAI Whisper (transcription)
- GPT-4o (AI scoring)

## Project Structure

```
zhimian/
├── apps/
│   ├── web/                    # Next.js 14 Frontend
│   │   ├── app/
│   │   │   ├── (candidate)/    # Candidate interview flow
│   │   │   ├── (employer)/     # Employer dashboard
│   │   │   └── page.tsx        # Landing page
│   │   ├── components/
│   │   │   ├── interview/      # Video recorder, question display
│   │   │   └── dashboard/      # Candidate cards, score display
│   │   └── lib/
│   │       └── api.ts          # API client
│   │
│   └── api/                    # Python FastAPI Backend
│       ├── app/
│       │   ├── routers/        # API endpoints
│       │   ├── models/         # SQLAlchemy models
│       │   ├── schemas/        # Pydantic schemas
│       │   └── services/       # Business logic
│       └── requirements.txt
│
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - R2 storage credentials
# - Database URL
```

### 2. Start the Database

```bash
docker-compose up -d db
```

### 3. Set Up Frontend

```bash
cd apps/web
npm install
npm run dev
```

### 4. Set Up Backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Interview Flow

1. **Employer**: Creates job with vertical (New Energy/Sales) and role type
2. **Employer**: Generates invite link for candidates
3. **Candidate**: Opens link, registers, completes 5-question video interview
4. **System**: Transcribes audio with Whisper, scores with GPT-4o
5. **Employer**: Reviews ranked candidates, watches videos, makes decisions

## Database Schema

### Core Tables
- `employers` - Company accounts with industry/company_size
- `jobs` - Job postings with vertical and role_type
- `candidates` - Candidate profiles
- `interview_sessions` - Interview tracking with scores
- `interview_responses` - Individual question responses with transcripts
- `interview_questions` - Question templates by vertical/role
- `invite_tokens` - Shareable interview links
- `matches` - Candidate-job status (shortlisted/rejected)

## Development

```bash
# Terminal 1: Database
docker-compose up -d db

# Terminal 2: Frontend
cd apps/web && npm run dev

# Terminal 3: Backend
cd apps/api && source venv/bin/activate && uvicorn app.main:app --reload
```

## License

MIT
