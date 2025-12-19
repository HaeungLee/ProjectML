"""
Configuration settings for Moonlight AI Core
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # App
    app_name: str = "Moonlight AI Core"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "moonlight"
    postgres_password: str = "moonlight_secret"
    postgres_db: str = "moonlight"

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_sync_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # LLM - OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "google/gemini-2.0-flash-exp:free"  # 무료 모델

    # gRPC - Voice Service
    voice_service_host: str = "localhost"
    voice_service_port: int = 50051

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # Constitution
    constitution_path: str = "../../docs/constitution.yaml"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤"""
    return Settings()


