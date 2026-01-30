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
- **DeepSeek AI Evaluation**: Intelligent scoring with strengths/concerns analysis
- **Mandarin Support**: DeepSeek ASR transcription with Chinese language support
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
- SQLAlchemy ORM + Alembic migrations
- PostgreSQL (Neon serverless)
- Cloudflare R2 (video storage)
- DeepSeek API (transcription + AI scoring)
- Redis (caching)
- JWT authentication

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
cp apps/api/.env.example apps/api/.env
# Edit .env with your credentials
```

#### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Always |
| `JWT_SECRET` | Secret key for JWT tokens | Production |
| `API_SECRET_KEY` | API secret key | Production |
| `DEEPSEEK_API_KEY` | DeepSeek API key for AI features | Recommended |
| `R2_ACCOUNT_ID` | Cloudflare R2 account ID | For video storage |
| `R2_ACCESS_KEY_ID` | R2 access key | For video storage |
| `R2_SECRET_ACCESS_KEY` | R2 secret key | For video storage |
| `RESEND_API_KEY` | Resend API key for emails | Optional |
| `REDIS_URL` | Redis connection string | Optional (caching) |
| `WECHAT_APP_ID` | WeChat Open Platform App ID | For WeChat login |
| `WECHAT_APP_SECRET` | WeChat Open Platform App Secret | For WeChat login |

---

## TODO: Production Setup Required

### WeChat OAuth Login Setup (微信登录配置)

WeChat login is implemented but requires credentials from WeChat Open Platform. Follow these steps:

#### Step 1: Register on WeChat Open Platform

1. Go to **WeChat Open Platform**: https://open.weixin.qq.com
2. Click "注册" (Register) to create a developer account
3. You'll need:
   - Valid email address
   - Mobile phone number (Chinese number preferred)
   - For business: Chinese business license (营业执照)
   - For individual: Chinese ID card or passport

#### Step 2: Complete Developer Verification

1. Log in to your Open Platform account
2. Go to "账号中心" (Account Center) → "开发者资质认证" (Developer Verification)
3. Submit required documents:
   - **Business account**: Business license, legal representative ID, authorization letter
   - **Individual account**: Personal ID verification
4. Pay verification fee (¥300 for businesses)
5. Wait for approval (typically 1-7 business days)

#### Step 3: Create Website Application (网站应用)

1. After verification, go to "管理中心" (Management Center)
2. Click "创建网站应用" (Create Website Application)
3. Fill in application details:
   - **应用名称** (App Name): Your app name (e.g., "智面招聘平台")
   - **应用简介** (Description): Brief description of your platform
   - **应用官网** (Official Website): Your production domain (e.g., `https://zhimian.ai`)
   - **授权回调域** (Callback Domain): Your domain WITHOUT protocol (e.g., `zhimian.ai`)
4. Upload app logo (108x108 pixels, PNG/JPG)
5. Submit for review (typically 1-3 business days)

#### Step 4: Get Credentials

Once approved, you'll find your credentials in the application details:
- **AppID** (应用ID): e.g., `wx1234567890abcdef`
- **AppSecret** (应用密钥): Click "查看" to reveal

#### Step 5: Configure Environment Variables

Add to your `apps/api/.env` file:

```env
# WeChat OAuth
WECHAT_APP_ID=wx1234567890abcdef
WECHAT_APP_SECRET=your_app_secret_here

# Must match your registered callback domain
FRONTEND_URL=https://yourdomain.com
```

#### Step 6: Verify Callback URL

Ensure your callback URL matches exactly:
- Registered callback domain: `zhimian.ai`
- Actual callback URL: `https://zhimian.ai/auth/wechat/callback`

#### Testing with WeChat Sandbox (Optional)

For development/testing before full approval:

1. Go to WeChat MP Sandbox: https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login
2. Scan QR code with WeChat to get test credentials
3. Note: Sandbox has limited features and only works with specific test accounts

#### Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "redirect_uri 参数错误" | Callback domain mismatch | Ensure domain in Open Platform matches your FRONTEND_URL |
| "invalid appid" | Wrong AppID | Double-check WECHAT_APP_ID in .env |
| "未获得授权" | App not approved | Wait for Open Platform approval |
| "scope参数错误" | Wrong scope | Ensure using `snsapi_login` for web login |

#### WeChat Login Flow

```
User clicks "微信登录"
    ↓
Frontend calls GET /api/candidates/auth/wechat/url
    ↓
Backend generates auth URL with state token
    ↓
User redirected to WeChat QR code page
    ↓
User scans QR with WeChat mobile app
    ↓
WeChat redirects to /auth/wechat/callback?code=xxx&state=xxx
    ↓
Frontend sends code to POST /api/candidates/auth/wechat/login
    ↓
Backend exchanges code for access_token + user info
    ↓
Backend creates/finds user, returns JWT token
    ↓
User logged in, redirected to dashboard
```

---

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
4. **System**: Transcribes audio and scores responses with DeepSeek AI
5. **Employer**: Reviews ranked candidates, watches videos, makes decisions

## Authentication

The API uses JWT-based authentication with two user types:
- **Candidates**: Can access their own profile, upload resumes, and complete interviews
- **Employers**: Can view candidates, manage jobs, and review interview results

Protected endpoints require a Bearer token in the Authorization header.

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
