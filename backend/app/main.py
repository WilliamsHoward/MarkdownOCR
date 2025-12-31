from app.api.endpoints import download, status, upload
from app.services.ocr_service import ocr_service
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MarkDown OCR API",
    description="API for converting PDF documents to Markdown using Local LLMs",
    version="1.0.0",
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
        "message": "Welcome to MarkDown OCR API",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint that verifies LLM connectivity.
    """
    try:
        llm = ocr_service._get_llm()
        return {
            "status": "healthy",
            "llm_provider": "configured",
            "message": "LLM connection initialized successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "message": "Cannot connect to LLM. Please ensure Ollama or LM Studio is running.",
            },
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
