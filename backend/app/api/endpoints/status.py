from app.services.ocr_service import ocr_service
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status of a conversion task.
    """
    status = ocr_service.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")

    return status
