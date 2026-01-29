from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health, candidates, questions, interviews, employers

app = FastAPI(
    title="智聘AI API",
    description="AI-powered recruiting platform API with async video interviews",
    version="0.2.0",
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
        "name": "智聘AI API",
        "version": "0.2.0",
        "docs": "/docs",
        "endpoints": {
            "candidates": "/api/candidates",
            "questions": "/api/questions",
            "interviews": "/api/interviews",
            "employers": "/api/employers",
        }
    }
