# Claude Code Rules for ZhiMian (智面)

## Project Overview
ZhiMian is an AI-powered video interview platform for the Chinese market, targeting New Energy/EV and Sales verticals.

## Critical Rules

### 1. NO OpenAI API
**DO NOT use OpenAI APIs** (GPT-4, Whisper, etc.) in this project. We must use Chinese-based AI services only.

**Approved AI Services:**
- **DeepSeek API** (https://platform.deepseek.com/)
  - LLM/Scoring: `deepseek-chat` model
  - Speech-to-Text: `whisper-1` model (OpenAI-compatible)
  - Env vars: `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`

**Why**: OpenAI services are unreliable in China due to network restrictions and compliance requirements.

### 2. Target Verticals
This platform focuses on two verticals:
- **New Energy/EV** (新能源): Battery Engineers, Embedded Software, Autonomous Driving, Supply Chain, EV Sales
- **Sales/BD** (销售): Sales Representatives, BD Managers, Account Managers

### 3. Tech Stack
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Storage**: Cloudflare R2 (S3-compatible)
- **AI**: DeepSeek (LLM + ASR)

### 4. Branding
- Name: **ZhiMian 智面** (not "ZhiPin AI")
- Colors: Emerald/Teal gradient (`from-emerald-600 to-teal-600`)
- Logo: Chinese character 智 in emerald gradient square

### 5. Language Support
- Primary: Chinese (Simplified)
- Secondary: English
- UI should support bilingual display where appropriate

## Environment Variables Required

```env
# Database
DATABASE_URL=postgresql://...

# Security
API_SECRET_KEY=...
JWT_SECRET=...

# DeepSeek (LLM + ASR)
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Cloudflare R2 (Storage)
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=zhimian-videos

# Email
RESEND_API_KEY=re_...

# URLs
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

## Scoring Dimensions
The AI evaluates candidates on 5 dimensions:
1. **沟通能力 Communication** (20%)
2. **解决问题 Problem Solving** (20%)
3. **专业知识 Domain Knowledge** (25%)
4. **动机 Motivation** (15%)
5. **文化契合 Culture Fit** (20%)

## Testing Requirements (MANDATORY)

**Every new feature MUST include tests before being considered complete.**

### Backend Tests (pytest)
Location: `apps/api/tests/`

For every new endpoint or service:
1. **Unit tests** for business logic and services
2. **Integration tests** for API endpoints
3. **Edge cases** for validation and error handling

```bash
# Run backend tests
cd apps/api && pytest -v
```

Example test structure:
```python
# tests/test_candidates.py
async def test_create_candidate_success(client, db_session):
    """Test successful candidate registration."""

async def test_create_candidate_duplicate_email(client, db_session):
    """Test duplicate email returns 409."""

async def test_create_candidate_invalid_phone(client, db_session):
    """Test invalid phone returns 400."""
```

### Frontend Tests (Jest + Playwright)
Location: `apps/web/__tests__/` and `apps/web/e2e/`

For every new component or page:
1. **Unit tests** for components (Jest + React Testing Library)
2. **E2E tests** for user flows (Playwright)

```bash
# Run frontend tests
cd apps/web && npm test        # Unit tests
cd apps/web && npm run test:e2e # E2E tests
```

### Test Coverage Requirements
- **New features**: Must have >80% test coverage
- **Bug fixes**: Must include regression test
- **API endpoints**: Must test success + all error cases

### When Writing Tests
- Test the happy path first
- Test validation errors (400)
- Test authentication errors (401/403)
- Test not found errors (404)
- Test duplicate/conflict errors (409)
- Test with realistic data (Chinese names, phone numbers)

## User Flows (Mercor-style)

### Candidate Flow
1. **Register** (`/candidate/register`) → Enter profile info → Select target roles
2. **Start Interview** → Redirected to interview room automatically
3. **Complete Interview** → 5 video questions, AI-scored
4. **Dashboard** (`/candidate/dashboard`) → View available jobs, start more interviews
5. **Get Matched** → Employers contact qualified candidates

### Employer Flow
1. **Register/Login** (`/login`) → Create company account
2. **Post Jobs** (`/dashboard/jobs`) → Define role, vertical, requirements
3. **Generate Invite Links** → Share with candidates or post publicly
4. **Review Results** (`/dashboard/interviews`) → Watch videos, see AI scores, shortlist/reject

### Key URLs
- `/` - Landing page with Candidate/Employer split CTAs
- `/candidate/register` - Candidate signup → immediate interview
- `/candidate/login` - Returning candidate login
- `/candidate/dashboard` - Candidate home (job listings)
- `/login` - Employer login/register
- `/dashboard` - Employer dashboard
- `/interview/[sessionId]` - Interview room

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
    │   ├── (candidate)/ # Candidate interview flow
    │   └── (employer)/  # Employer dashboard
    ├── components/      # React components
    └── lib/             # API client, utilities
```
