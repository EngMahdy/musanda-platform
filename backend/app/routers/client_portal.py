"""client_portal router - placeholder for future implementation"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def status():
    return {"router": "client_portal", "status": "ready_for_implementation"}
