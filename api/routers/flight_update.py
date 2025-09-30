"""
Live Activity Router - Handles the Flight Update Live Activity from Signal Air
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..models.schemas import (FlightUpdateContentState, FlightUpdateLiveActivity)
from ..services.flight_update import flight_service

router = APIRouter(
    prefix="/flight-update",
    tags=["flight-update"]
)

@router.post("")
async def start_flight_update(request: FlightUpdateLiveActivity):
    """Start a sequence for live activity"""
    return await flight_service.schedule_emoji_sequence(request)