import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "MarkDown OCR"
    API_V1_STR: str = "/api/v1"

    # Storage Configuration
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"

    # LLM Configurations
    # Default to Ollama local URL
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    # Default to LM Studio local URL
    LM_STUDIO_BASE_URL: str = os.getenv(
        "LM_STUDIO_BASE_URL", "http://localhost:1234/v1"
    )

    # Active LLM Provider: "ollama" or "lm_studio"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "lm_studio")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "zai-org/glm-4.6v-flash")

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
