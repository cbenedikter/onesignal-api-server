"""
Delivery Service - Handles package tracking notifications
"""
import asyncio
from datetime import datetime
from typing import Dict

from ..models.schemas import DeliveryRequest
from .one_signal_message_service import onesignal_message_service


class DeliveryService:
    """Service for managing 3 step delivery process"""
    
    def __init__(self):
        self.active_jobs: Dict[str, bool] = {}

    async def schedule_delivery_sequence(self, request: DeliveryRequest) -> Dict:
        """Schedule 3 notifications delivery in 1 minute intervals
        
        Args:
            request: Delivery request with tracking info
            
        Returns:
            Status of scheduling
        """

        if request.tracking_id in self.active_jobs and self.active_jobs[request.tracking_id]:
            return {
                "status": "error",
                "message": f"Already tracking {request.tracking_id}"
            }
        
        # Mark as active
        self.active_jobs[request.tracking_id] = True
        
        # Start the notification sequence
        asyncio.create_task(self._send_delivery_sequence(request))
        
        return {
            "status": "success",
            "message": f"Started tracking {request.tracking_id}",
            "tracking_id": request.tracking_id
        }
    async def _send_delivery_sequence(self, request: DeliveryRequest):
        """Send 3 notifications with 1 minute intervals"""
        try:
            await onesignal_message_service.send_delivery_notification(request, "Delivery Pickup")
            await asyncio.sleep(60)
            await onesignal_message_service.send_delivery_notification(request, "In transit")
            await asyncio.sleep(60)
            await onesignal_message_service.send_delivery_notification(request, "Delivered")
        except Exception as e:
            print(f"Error in delivery sequence {e}")
        finally:
            self.active_jobs[request.tracking_id] = False

delivery_service = DeliveryService()    
        
     