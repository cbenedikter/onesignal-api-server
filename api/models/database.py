# api/models/database.py
"""
Database models for storing OneSignal webhook events
Uses SQLAlchemy with async support for Postgres
"""
from sqlalchemy import Column, String, DateTime, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class MessageEvent(Base):
    """
    Stores OneSignal webhook events for notification inbox reconstruction.

    Each row represents a single event (sent, delivered, clicked, etc.)
    for a notification sent to a specific user.
    """
    __tablename__ = "message_events"

    # Primary key - auto-generated UUID
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for this event"
    )

    # OneSignal App ID - identifies which of the 10 apps sent this
    app_id = Column(
        String(36),
        nullable=False,
        index=True,
        comment="OneSignal App ID that sent this notification"
    )

    # User identity - the external_id from OneSignal.login()
    external_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="User's external_id (from OneSignal.login())"
    )

    # Event type - what happened
    event_type = Column(
        String(50),
        nullable=False,
        comment="Event type: notification.sent, notification.delivered, notification.clicked, etc."
    )

    # OneSignal's notification ID - links related events together
    notification_id = Column(
        String(36),
        nullable=True,
        index=True,
        comment="OneSignal's unique notification ID"
    )

    # The actual notification content (title, body, image, etc.)
    message_contents = Column(
        JSONB,
        nullable=True,
        comment="Notification content: title, body, image, action buttons, custom data"
    )

    # Full webhook payload - stored for debugging and future flexibility
    event_payload = Column(
        JSONB,
        nullable=True,
        comment="Complete webhook payload from OneSignal"
    )

    # Timestamp when we received this event
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When this event was received"
    )

    # Composite index for the most common query pattern:
    # "Get all messages for this user in this app, newest first"
    __table_args__ = (
        Index(
            'idx_user_lookup',
            'app_id',
            'external_id',
            created_at.desc()
        ),
    )

    def __repr__(self):
        return f"<MessageEvent(id={self.id}, app_id={self.app_id}, external_id={self.external_id}, event_type={self.event_type})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": str(self.id),
            "app_id": self.app_id,
            "external_id": self.external_id,
            "event_type": self.event_type,
            "notification_id": self.notification_id,
            "message_contents": self.message_contents,
            "event_payload": self.event_payload,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
