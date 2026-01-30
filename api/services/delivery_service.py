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
        """Schedule 3 notifications delivery with configurable intervals

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

        # Determine notification interval
        interval = request.notification_interval if request.notification_interval else 60

        # Log demo mode status
        if request.demo_mode:
            print(f"⚡ Demo mode enabled for {request.tracking_id} - {interval}s intervals")

        # Start the notification sequence
        asyncio.create_task(self._send_delivery_sequence(request, interval))

        response = {
            "status": "success",
            "message": f"Started tracking {request.tracking_id}",
            "tracking_id": request.tracking_id
        }

        if request.demo_mode:
            response["demo_mode"] = True
            response["notification_interval"] = interval

        return response

    async def _send_delivery_sequence(self, request: DeliveryRequest, interval: int = 60):
        """Send 3 notifications with configurable intervals

        Args:
            request: Delivery request with tracking info
            interval: Seconds between notifications (default 60)
        """
        try:
            print(f"📦 Starting delivery sequence for {request.tracking_id} (interval: {interval}s)")

            await onesignal_message_service.send_delivery_notification(request, "Delivery Pickup")
            print(f"📬 Sent 'Delivery Pickup' for {request.tracking_id}, waiting {interval}s...")

            await asyncio.sleep(interval)

            await onesignal_message_service.send_delivery_notification(request, "In transit")
            print(f"🚚 Sent 'In transit' for {request.tracking_id}, waiting {interval}s...")

            await asyncio.sleep(interval)

            await onesignal_message_service.send_delivery_notification(request, "Delivered")
            print(f"✅ Sent 'Delivered' for {request.tracking_id}")

        except Exception as e:
            print(f"❌ Error in delivery sequence for {request.tracking_id}: {e}")
        finally:
            self.active_jobs[request.tracking_id] = False
            print(f"🏁 Completed delivery sequence for {request.tracking_id}")

delivery_service = DeliveryService()
