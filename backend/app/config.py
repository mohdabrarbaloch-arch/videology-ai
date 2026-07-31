from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_service_role_key: str

    # OpenAI
    openai_api_key: str
    ai_model: str = "gpt-4o"
    transcription_model: str = "whisper-1"
    image_model: str = "dall-e-3"
    embedding_model: str = "text-embedding-3-small"

    # Processing
    max_video_size_mb: int = 500
    max_video_duration_seconds: int = 7200
    chunk_duration_seconds: int = 600  # 10 min chunks for Whisper

    # Backend auth
    backend_api_key: str = "change-me-in-production"

    # Temp storage
    temp_dir: str = "/tmp/videology"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
