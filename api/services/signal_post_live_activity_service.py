"""
Signal Post Live Activity Service - Handles timed Live Activity updates for parcel delivery demo

Timeline:
  T=0s  -> Activity started client-side with "Order Confirmed"
  T=7s  -> Update 1: "Out for Delivery" (progress 0.55, ETA 12 min)
  T=14s -> Update 2: "Delivered" (progress 1.0, ETA 0)
  T=20s -> End the Live Activity
"""
import asyncio
import aiohttp
import sys
from typing import Dict
from ..config import settings
from ..models.schemas import SignalPostLiveActivityRequest


# ---------- Content State Payloads ----------
# These match SignalPostAttributes.ContentState in Swift exactly

UPDATE_OUT_FOR_DELIVERY = {
    "status": "Out for Delivery",
    "statusEmoji": "\U0001F69A",
    "progress": 0.55,
    "etaMinutes": 12,
    "stopInfo": "Stop 4 of 10",
    "isDelivered": False,
}

UPDATE_DELIVERED = {
    "status": "Delivered",
    "statusEmoji": "\u2705",
    "progress": 1.0,
    "etaMinutes": 0,
    "stopInfo": "Arrived",
    "isDelivered": True,
}

ONESIGNAL_API_URL = "https://api.onesignal.com"


class SignalPostLiveActivityService:
    """Service for managing the Signal Post Live Activity demo sequence"""

    def __init__(self):
        self.active_jobs: Dict[str, bool] = {}

    async def schedule_live_activity_sequence(self, request: SignalPostLiveActivityRequest) -> Dict:
        """Schedule 3 timed Live Activity updates

        Args:
            request: Live Activity request with tracking info and activity ID

        Returns:
            Status of scheduling
        """

        # Prevent duplicate runs for the same activity_id
        if self.active_jobs.get(request.activity_id):
            return {
                "status": "error",
                "message": f"Sequence already running for {request.activity_id}"
            }

        # Mark as active
        self.active_jobs[request.activity_id] = True

        print(f"\n\U0001F4E6 ====== Live Activity Demo Started ======", file=sys.stderr, flush=True)
        print(f"\U0001F4E6 Tracking Number: {request.tracking_number}", file=sys.stderr, flush=True)
        print(f"\U0001F4E6 Activity ID: {request.activity_id}", file=sys.stderr, flush=True)
        print(f"\U0001F4E6 App ID: {request.app_id}", file=sys.stderr, flush=True)
        print(f"\U0001F4E6 External ID: {request.external_id or 'none'}", file=sys.stderr, flush=True)
        print(f"\U0001F4E6 Push Token: {request.push_token[:20] + '...' if request.push_token else 'none'}", file=sys.stderr, flush=True)
        print(f"\U0001F4E6 Timeline: Updates at T=7s, T=14s, End at T=20s", file=sys.stderr, flush=True)
        print(f"\U0001F4E6 ==========================================\n", file=sys.stderr, flush=True)

        # Spawn the async sequence
        asyncio.create_task(self._run_live_activity_sequence(request))

        return {
            "status": "success",
            "message": "Live Activity update sequence started",
            "tracking_number": request.tracking_number,
            "activity_id": request.activity_id,
            "timeline": {
                "update_1": "T+7s - Out for Delivery",
                "update_2": "T+14s - Delivered",
                "end": "T+20s - Activity dismissed"
            }
        }

    async def _run_live_activity_sequence(self, request: SignalPostLiveActivityRequest) -> None:
        """Send 3 timed Live Activity updates via OneSignal API

        Args:
            request: Live Activity request with app_id and activity_id
        """
        try:
            # T=7s: Update 1 - "Out for Delivery"
            await asyncio.sleep(7)
            print(f"\U0001F69A [T+7s] Sending update: Out for Delivery", file=sys.stderr, flush=True)
            await self._send_live_activity_update(
                app_id=request.app_id,
                activity_id=request.activity_id,
                content_state=UPDATE_OUT_FOR_DELIVERY,
                event="update"
            )

            # T=14s: Update 2 - "Delivered"
            await asyncio.sleep(7)
            print(f"\u2705 [T+14s] Sending update: Delivered", file=sys.stderr, flush=True)
            await self._send_live_activity_update(
                app_id=request.app_id,
                activity_id=request.activity_id,
                content_state=UPDATE_DELIVERED,
                event="update"
            )

            # T=20s: End the Live Activity
            await asyncio.sleep(6)
            print(f"\U0001F3C1 [T+20s] Ending Live Activity", file=sys.stderr, flush=True)
            await self._send_live_activity_update(
                app_id=request.app_id,
                activity_id=request.activity_id,
                content_state=UPDATE_DELIVERED,
                event="end"
            )

            print(f"\n\U0001F4E6 ====== Live Activity Demo Complete ======\n", file=sys.stderr, flush=True)

        except Exception as e:
            print(f"\u274C Error in live activity sequence for {request.activity_id}: {e}", file=sys.stderr, flush=True)
        finally:
            self.active_jobs[request.activity_id] = False
            print(f"\U0001F3C1 Completed live activity sequence for {request.activity_id}", file=sys.stderr, flush=True)

    async def _send_live_activity_update(self, app_id: str, activity_id: str, content_state: dict, event: str = "update") -> Dict:
        """Update a Live Activity via OneSignal's REST API

        Args:
            app_id: OneSignal App ID
            activity_id: The Live Activity ID to update
            content_state: Dict containing the content_state fields
            event: "update" or "end"

        Returns:
            Response from OneSignal API
        """
        url = f"{ONESIGNAL_API_URL}/apps/{app_id}/live_activities/{activity_id}/notifications"

        payload = {
            "event": event,
            "event_updates": content_state,
            "name": f"live-activity-{event}-{activity_id}",
            "priority": 10,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Key {settings.signal_post_api_key}",
            "Accept": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                print(f"\U0001F4E1 Making OneSignal Live Activity {event} request...", file=sys.stderr, flush=True)

                async with session.post(
                    url,
                    json=payload,
                    headers=headers
                ) as response:
                    print(f"\U0001F4E1 Response Status: {response.status}", file=sys.stderr, flush=True)

                    response_data = await response.json()
                    print(f"\u2705 OneSignal Live Activity Response: {response_data}", file=sys.stderr, flush=True)

                    return response_data

        except Exception as e:
            print(f"\u274C OneSignal Live Activity Request Failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            return {"error": str(e), "error_type": type(e).__name__}


# Create singleton instance
signal_post_live_activity_service = SignalPostLiveActivityService()
