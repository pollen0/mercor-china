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
    r2_bucket_name: str = "zhipin-videos"
    r2_endpoint_url: Optional[str] = None  # Will be constructed from account_id

    # DeepSeek API (for LLM scoring)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # WeChat OAuth
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # Email (Resend)
    resend_api_key: str = ""
    email_from: str = "ZhiMian <noreply@zhimian.ai>"

    # Frontend URL (for email links)
    frontend_url: str = "http://localhost:3000"

    # Redis (for caching)
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300  # 5 minutes default TTL

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
