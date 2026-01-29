from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .routers import health, candidates, questions, interviews, employers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="ZhiMian 智面 API",
    description="AI-powered video interview platform for China's job market",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
app.include_router(health.router)

# Candidates
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])

# Interview questions
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])

# Interview sessions
app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])

# Employers
app.include_router(employers.router, prefix="/api/employers", tags=["employers"])


@app.get("/")
async def root():
    return {
        "name": "ZhiMian 智面 API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "candidates": "/api/candidates",
            "questions": "/api/questions",
            "interviews": "/api/interviews",
            "employers": "/api/employers",
        }
    }
