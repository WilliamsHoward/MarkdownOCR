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

    # Vision Model Support
    # Set to True to use vision models for PDF page image processing
    USE_VISION_MODEL: bool = os.getenv("USE_VISION_MODEL", "true").lower() == "true"
    # Vision model name (e.g., "llava" for Ollama, or vision-capable model in LM Studio)
    VISION_MODEL: str = os.getenv("VISION_MODEL", "zai-org/glm-4.6v-flash")
    # Image quality for PDF rendering (DPI - higher = better quality but slower)
    PDF_DPI: int = int(os.getenv("PDF_DPI", "150"))
    # Image format for vision processing: "png" or "jpeg"
    IMAGE_FORMAT: str = os.getenv("IMAGE_FORMAT", "png")

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
