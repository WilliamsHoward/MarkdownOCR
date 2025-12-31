import os
import shutil

from app.core.config import settings
from app.services.ocr_service import ocr_service
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

router = APIRouter()


@router.post("/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload a PDF file to start the conversion process.
    The conversion happens in the background.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Create a unique task and filename
    task_id = ocr_service.create_task(file.filename)
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{task_id}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)

    try:
        # Save the uploaded file to the upload directory
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Start the background task for processing
        background_tasks.add_task(ocr_service.process_pdf, task_id, file_path)

        return {
            "task_id": task_id,
            "filename": file.filename,
            "status": "pending",
            "message": "File uploaded successfully. Conversion started.",
        }
    except Exception as e:
        # Update task status if upload fails
        if task_id in ocr_service.tasks:
            ocr_service.tasks[task_id]["status"] = "failed"
            ocr_service.tasks[task_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
