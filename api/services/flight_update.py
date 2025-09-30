""" Service to generate a flight update live activity"""
import asyncio
from datetime import datetime, timezone
from api.storage.kv_store import KVStore
from api.models.schemas import FlightUpdateContentState, FlightUpdateLiveActivity
from api.config import settings
from api.services.one_signal_message_service import onesignal_message_service


class FlightLiveActivityService:
    def __init__(self, kv: KVStore, *, step_delay_seconds: int = 10):
        """
        kv: key-value store to persist activity_id and last state
        step_delay_seconds: pause between demo steps (default 10s)
        """
        self.kv = kv
        self.step_delay = step_delay_seconds
        self.active_jobs: dict[str, bool] = {}
    def register(self, req: FlightUpdateLiveActivity) -> dict:
        key = f"live:flightUpdate:{req.activity_id}"
        now = datetime.utcnow().isoformat()

        record = {
            "activity_id": req.activity_id,
            "type": req.activity_type,             # "flightUpdate"
            "state": {
                "gate": req.content_state.gate,
                "boardingTime": req.content_state.boardingTime,
            },
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }

    # Demo: overwrite if it exists; no idempotency needed
        self.kv.set(key, record)
        return {"ok": True, "activity_id": req.activity_id, "stored": record}

    async def schedule_emoji_sequence(self, payload: FlightUpdateLiveActivity) -> dict:
        """Persist and start the 10s→update→10s→update→10s→end sequence (emoji-only)."""
        aid = payload.activity_id

        # prevent duplicate runs for the same activity_id
        if self.active_jobs.get(aid):
            return {"status": "error", "message": f"Sequence already running for {aid}"}

        # 1) persist baseline state
        self.register(payload)

        # 2) mark active and spawn the runner 
        self.active_jobs[aid] = True
        asyncio.create_task(self._run_emoji_sequence(aid))

        return {"status": "started", "activity_id": aid}

    async def _run_emoji_sequence(self, activity_id: str) -> None:
        """10s → update → 10s → update → 10s → end (emoji-only MVP)."""
        try:
            # step 1: baggage claim
            await asyncio.sleep(self.step_delay)
            event = "update"
            event_updates = {"status": "boarding"}
            await onesignal_message_service.update_live_activity(
                activity_id=activity_id,
                event=event,
                event_updates=event_updates
            )
            self._kv_update_state(activity_id, status="boarding")

            # step 2: landed
            await asyncio.sleep(self.step_delay)
            event = "update"
            event_updates = {"status": "finalCall","group":2}
            await onesignal_message_service.update_live_activity(
                activity_id=activity_id,
                event=event,
                event_updates=event_updates
            )
            self._kv_update_state(activity_id, status="finalCall", group=2)

            # step 3: end the Live Activity
            await asyncio.sleep(self.step_delay)
            event = "end"
            event_updates = {"status": "closed","group":""}  # Final state before dismissal
            await onesignal_message_service.update_live_activity(
                activity_id=activity_id,
                event=event,
                event_updates=event_updates
            )
            self._kv_mark_ended(activity_id)

        except Exception as e:
            print(f"[flight_update] sequence error for {activity_id}: {e}")
        finally:
            self.active_jobs[activity_id] = False
    def _kv_update_state(self, activity_id: str, *, status: str = None, group: str = None) -> None:
        key = f"live:flightUpdate:{activity_id}"
        rec = self.kv.get(key) or {}
        if status:
            rec.setdefault("state", {})["status"] = status
        if group:
            rec.setdefault("state", {})["group"] = group
        rec["updated_at"] = datetime.utcnow().isoformat()
        self.kv.set(key, rec)

    def _kv_mark_ended(self, activity_id: str) -> None:
        key = f"live:flightUpdate:{activity_id}"
        rec = self.kv.get(key) or {}
        rec["status"] = "ended"
        rec["updated_at"] = datetime.utcnow().isoformat()
        self.kv.set(key, rec)
# Create singleton instance
from api.storage.kv_store import kv_store
flight_service = FlightLiveActivityService(kv=kv_store, step_delay_seconds=10)



