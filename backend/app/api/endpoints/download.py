import os

from app.core.config import settings
from app.services.ocr_service import ocr_service
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/download/{task_id}")
async def download_markdown(task_id: str):
    """
    Download the converted Markdown file if it exists.
    """
    status = ocr_service.get_task_status(task_id)

    if not status:
        raise HTTPException(status_code=404, detail="Task not found")

    if status["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"File is not ready. Current status: {status['status']}",
        )

    output_filename = status.get("output_file")
    if not output_filename:
        raise HTTPException(
            status_code=500, detail="Output filename missing in task status"
        )

    file_path = os.path.join(settings.OUTPUT_DIR, output_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Converted file not found on disk")

    return FileResponse(
        path=file_path,
        media_type="text/markdown",
        filename=f"{status.get('filename', 'converted')}.md",
    )
