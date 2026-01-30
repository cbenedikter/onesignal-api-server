# api/routers/webhooks.py
"""
Webhook endpoints for receiving OneSignal events.
These endpoints store notification events for inbox reconstruction.
"""
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, desc

from ..models.schemas import OneSignalWebhookEvent, MessagesResponse, MessageEventResponse
from ..models.database import MessageEvent
from ..services.database_service import database_service

router = APIRouter(tags=["Webhooks"])


@router.post("/webhooks/onesignal")
async def receive_onesignal_webhook(request: Request):
    """
    Receive and store OneSignal webhook events.

    OneSignal will POST events to this endpoint when notifications are:
    - Sent (notification.sent)
    - Delivered (notification.delivered)
    - Clicked (notification.clicked)
    - Dismissed (notification.dismissed)
    - And other event types

    Configure this URL in your OneSignal dashboard under:
    Settings > Webhooks
    """
    # Check if database is available
    if not database_service.is_initialized:
        print("⚠️ Webhook received but database not initialized - event discarded")
        return {
            "status": "warning",
            "message": "Webhook received but storage not configured"
        }

    try:
        # Parse the raw JSON payload
        payload = await request.json()
        print(f"📥 Webhook received: {payload.get('event', 'unknown')} for app {payload.get('app_id', 'unknown')}")

        # Extract key fields
        event_type = payload.get("event")
        app_id = payload.get("app_id")
        external_id = payload.get("external_id")
        notification_id = payload.get("notification_id") or payload.get("id")

        # Validate required fields
        if not event_type or not app_id:
            print(f"⚠️ Webhook missing required fields: event={event_type}, app_id={app_id}")
            return {
                "status": "error",
                "message": "Missing required fields: event and app_id"
            }

        # Extract message contents for inbox reconstruction
        message_contents = {}

        # Title (headings)
        headings = payload.get("headings")
        if headings:
            message_contents["title"] = headings.get("en") or list(headings.values())[0] if headings else None

        # Body (contents)
        contents = payload.get("contents")
        if contents:
            message_contents["body"] = contents.get("en") or list(contents.values())[0] if contents else None

        # Additional content fields
        if payload.get("data"):
            message_contents["data"] = payload.get("data")
        if payload.get("url"):
            message_contents["url"] = payload.get("url")
        if payload.get("big_picture"):
            message_contents["image"] = payload.get("big_picture")
        if payload.get("ios_attachments"):
            message_contents["ios_attachments"] = payload.get("ios_attachments")

        # Create the database record
        async with database_service.session_factory() as session:
            event = MessageEvent(
                app_id=app_id,
                external_id=external_id or "unknown",
                event_type=event_type,
                notification_id=notification_id,
                message_contents=message_contents if message_contents else None,
                event_payload=payload
            )
            session.add(event)
            await session.commit()

            print(f"✅ Stored event: {event_type} for user {external_id} (notification: {notification_id})")

        return {
            "status": "success",
            "message": f"Event {event_type} stored successfully",
            "event_id": str(event.id)
        }

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@router.get("/messages/{app_id}/{external_id}", response_model=MessagesResponse)
async def get_user_messages(
    app_id: str,
    external_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum messages to return"),
    event_types: Optional[str] = Query(
        None,
        description="Comma-separated event types to filter (e.g., 'notification.sent,notification.delivered')"
    ),
    since_days: Optional[int] = Query(
        None,
        ge=1,
        le=90,
        description="Only return messages from the last N days"
    )
):
    """
    Retrieve notification history for a specific user.

    This endpoint is called by the iOS app to populate the notification inbox.
    Returns messages sorted by newest first.

    Args:
        app_id: Your OneSignal App ID
        external_id: The user's external_id (from OneSignal.login())
        limit: Maximum number of messages to return (default 50, max 200)
        event_types: Optional filter for specific event types
        since_days: Optional filter for recent messages only
    """
    if not database_service.is_initialized:
        raise HTTPException(
            status_code=503,
            detail="Message storage not configured"
        )

    try:
        async with database_service.session_factory() as session:
            # Build the query
            query = select(MessageEvent).where(
                and_(
                    MessageEvent.app_id == app_id,
                    MessageEvent.external_id == external_id
                )
            )

            # Filter by event types if specified
            if event_types:
                types_list = [t.strip() for t in event_types.split(",")]
                query = query.where(MessageEvent.event_type.in_(types_list))

            # Filter by date if specified
            if since_days:
                cutoff = datetime.utcnow() - timedelta(days=since_days)
                query = query.where(MessageEvent.created_at >= cutoff)

            # Order by newest first and apply limit
            query = query.order_by(desc(MessageEvent.created_at)).limit(limit)

            # Execute query
            result = await session.execute(query)
            events = result.scalars().all()

            # Convert to response format
            messages = [
                MessageEventResponse(
                    id=str(event.id),
                    event_type=event.event_type,
                    notification_id=event.notification_id,
                    message_contents=event.message_contents,
                    created_at=event.created_at.isoformat() if event.created_at else None
                )
                for event in events
            ]

            print(f"📤 Returning {len(messages)} messages for {external_id} in app {app_id}")

            return MessagesResponse(
                app_id=app_id,
                external_id=external_id,
                message_count=len(messages),
                messages=messages
            )

    except Exception as e:
        print(f"❌ Error retrieving messages: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")


@router.delete("/messages/{app_id}/{external_id}")
async def delete_user_messages(
    app_id: str,
    external_id: str
):
    """
    Delete all messages for a specific user.

    Useful for:
    - GDPR data deletion requests
    - Clearing demo data
    - User account deletion
    """
    if not database_service.is_initialized:
        raise HTTPException(
            status_code=503,
            detail="Message storage not configured"
        )

    try:
        async with database_service.session_factory() as session:
            # Delete matching records
            result = await session.execute(
                select(MessageEvent).where(
                    and_(
                        MessageEvent.app_id == app_id,
                        MessageEvent.external_id == external_id
                    )
                )
            )
            events = result.scalars().all()

            for event in events:
                await session.delete(event)

            await session.commit()

            print(f"🗑️ Deleted {len(events)} messages for {external_id} in app {app_id}")

            return {
                "status": "success",
                "message": f"Deleted {len(events)} messages",
                "app_id": app_id,
                "external_id": external_id
            }

    except Exception as e:
        print(f"❌ Error deleting messages: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting messages: {str(e)}")


@router.get("/webhooks/health")
async def webhook_health():
    """
    Health check for webhook system.

    Returns the status of:
    - Database connectivity
    - Webhook endpoint availability
    """
    db_health = await database_service.health_check()

    return {
        "webhook_endpoint": "healthy",
        "database": db_health,
        "message": "Webhook system operational" if db_health["status"] == "healthy" else "Webhook system degraded"
    }
