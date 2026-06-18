"""ai_tenders router - placeholder for future implementation"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def status():
    return {"router": "ai_tenders", "status": "ready_for_implementation"}
