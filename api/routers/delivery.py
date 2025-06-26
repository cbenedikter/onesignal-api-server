# api/routers/delivery.py
"""
Delivery router - Handles package tracking demonstration
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime

from ..models.schemas import DeliveryRequest
from ..services.delivery_service import delivery_service


router = APIRouter(
    prefix="/delivery",
    tags=["delivery"]       
)
@router.post("")
async def track_delivery(request: DeliveryRequest):
    """Starts the parcel delivery process"""
    
    if not request.send_parcel:
        return {
            "status": "error",
            "message": "send_parcel must be 'true' to start delivery"
        }
        print(f"📦 Delivery request received for tracking_id: {request.tracking_id}")  # ADD THIS
    
    # Call the service
    result = await delivery_service.schedule_delivery_sequence(request)  
    print(f"📦 Service response: {result}")  # ADD THIS
    
    return result