from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://zhipin:zhipin_password@localhost:5432/zhipin_ai"
    api_secret_key: str = "your-api-secret-key-change-in-production"
    cors_origins: str = "http://localhost:3000"
    debug: bool = True

    # R2 Storage
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "zhipin-videos"
    r2_endpoint_url: Optional[str] = None  # Will be constructed from account_id

    # DeepSeek API
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # OpenAI (for Whisper)
    openai_api_key: str = ""

    # JWT
    jwt_secret: str = "your-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 168  # 7 days

    # WeChat OAuth
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # Email (Resend)
    resend_api_key: str = ""
    email_from: str = "ZhiPin AI <noreply@zhipin.ai>"

    # Frontend URL (for email links)
    frontend_url: str = "http://localhost:3000"

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
