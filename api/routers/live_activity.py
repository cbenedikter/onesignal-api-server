# api/routers/live_activity.py
"""
Live Activity Router - Handles the Signal Post Live Activity demo sequence
"""
from fastapi import APIRouter, HTTPException

from ..models.schemas import SignalPostLiveActivityRequest
from ..services.signal_post_live_activity_service import signal_post_live_activity_service


router = APIRouter(
    prefix="/live-activity",
    tags=["live-activity"]
)

@router.post("")
async def start_live_activity(request: SignalPostLiveActivityRequest):
    """Start a timed Live Activity update sequence for Signal Post parcel delivery"""

    result = await signal_post_live_activity_service.schedule_live_activity_sequence(request)
    return result
