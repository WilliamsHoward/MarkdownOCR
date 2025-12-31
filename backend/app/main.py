from app.api.endpoints import download, status, upload
from app.core.config import settings
from app.services.ocr_service import ocr_service
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MarkDown OCR API",
    description="API for converting PDF documents to Markdown using Local LLMs with Vision Support",
    version="2.0.0",
)

# Configure CORS
# In production, you should restrict the origins to your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(status.router, prefix="/api/v1", tags=["status"])
app.include_router(download.router, prefix="/api/v1", tags=["download"])


@app.get("/")
async def root():
    """
    Root endpoint to verify the API is running.
    """
    return {
        "message": "Welcome to MarkDown OCR API v2.0 - Now with Vision Model Support!",
        "status": "online",
        "docs": "/docs",
        "version": "2.0.0",
        "features": {
            "vision_processing": settings.USE_VISION_MODEL,
            "text_extraction": True,
        },
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint that verifies LLM connectivity and configuration.
    """
    health_info = {
        "status": "healthy",
        "version": "2.0.0",
        "configuration": {
            "llm_provider": settings.LLM_PROVIDER,
            "text_model": settings.LLM_MODEL,
            "vision_enabled": settings.USE_VISION_MODEL,
        },
    }

    # Add vision-specific configuration if enabled
    if settings.USE_VISION_MODEL:
        health_info["configuration"]["vision_model"] = settings.VISION_MODEL
        health_info["configuration"]["pdf_dpi"] = settings.PDF_DPI
        health_info["configuration"]["image_format"] = settings.IMAGE_FORMAT

    # Test text LLM connection
    try:
        llm = ocr_service._get_llm()
        health_info["text_llm"] = "connected"
    except Exception as e:
        health_info["status"] = "degraded"
        health_info["text_llm"] = "error"
        health_info["text_llm_error"] = str(e)

    # Test vision LLM connection if enabled
    if settings.USE_VISION_MODEL:
        try:
            vision_llm = ocr_service._get_vision_llm()
            health_info["vision_llm"] = "connected"
        except Exception as e:
            health_info["status"] = "degraded"
            health_info["vision_llm"] = "error"
            health_info["vision_llm_error"] = str(e)
            health_info["message"] = (
                "Vision model unavailable. Will fallback to text extraction."
            )

    # Return error if both models fail
    if health_info["status"] == "degraded" and health_info.get("text_llm") == "error":
        raise HTTPException(
            status_code=503,
            detail={
                **health_info,
                "message": "Cannot connect to LLM. Please ensure Ollama or LM Studio is running.",
            },
        )

    if health_info["status"] == "healthy":
        health_info["message"] = "All systems operational"

    return health_info


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
