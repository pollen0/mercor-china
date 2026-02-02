from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Database - REQUIRED
    database_url: str = ""

    # Security - REQUIRED in production
    api_secret_key: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 168  # 7 days

    # CORS
    cors_origins: str = "http://localhost:3000"
    debug: bool = False

    # R2 Storage (Cloudflare)
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "pathway-videos"
    r2_endpoint_url: Optional[str] = None  # Will be constructed from account_id

    # Claude API (primary - all AI/LLM features use Claude Sonnet 4.5)
    anthropic_api_key: str = ""  # Set via ANTHROPIC_API_KEY env var
    claude_model: str = "claude-sonnet-4-5-20250514"  # Claude Sonnet 4.5 - best balance of speed and accuracy

    # OpenAI API (for Whisper speech-to-text only - Claude doesn't have native STT)
    openai_api_key: str = ""  # Set via OPENAI_API_KEY env var

    # Admin authentication
    admin_password: str = ""  # Set via ADMIN_PASSWORD env var - REQUIRED for admin access

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""

    # Email (Resend)
    resend_api_key: str = ""
    email_from: str = "Pathway <noreply@pathway.careers>"

    # Frontend URL (for email links)
    frontend_url: str = "http://localhost:3000"

    # Google Calendar OAuth
    google_client_id: str = ""  # Set via GOOGLE_CLIENT_ID env var
    google_client_secret: str = ""  # Set via GOOGLE_CLIENT_SECRET env var
    google_redirect_uri: str = ""  # Set via GOOGLE_REDIRECT_URI env var (e.g., http://localhost:3000/auth/google/callback)
    google_employer_redirect_uri: str = ""  # Set via GOOGLE_EMPLOYER_REDIRECT_URI env var (e.g., http://localhost:3000/auth/google/callback for employers)

    # Redis (for caching)
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300  # 5 minutes default TTL

    # Encryption key for sensitive data (GitHub tokens, etc.)
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    encryption_key: str = ""  # Set via ENCRYPTION_KEY env var - REQUIRED for token encryption

    @property
    def r2_endpoint(self) -> str:
        if self.r2_endpoint_url:
            return self.r2_endpoint_url
        return f"https://{self.r2_account_id}.r2.cloudflarestorage.com"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
