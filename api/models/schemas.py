# api/models/schemas.py
"""
Data models (schemas) for your API
These define what data your API expects and returns
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime


# Request models (what users send to your API)
class OTPRequest(BaseModel):
    """Request to generate an OTP"""
    phone_number: str = Field(
        ..., 
        example="+1234567890",
        description="Phone number with country code"
    )
    request_otp: bool = Field(
        ...,
        example=True,  # Changed from 'true' to True (no quotes for boolean)
        description="must be 'true' to request an OTP"
    )
    
class VerifyOTPRequest(BaseModel):
    """Request to verify an OTP"""
    phone_number: str = Field(
        ..., 
        example="+1234567890",
        description="Phone number that requested the OTP"
    )
    signal_code: str = Field(
        ...,
        example="12345",
        description="The 5-digit OTP code"
    )

class DeliveryRequest(BaseModel):  # Fixed: BaseModel not baseModel
    """Request to start Signal Post Parcel Delivery"""  # Fixed: proper quotes
    external_id: str = Field(  # Fixed: added colon after external_id
        ...,
        example="YCYEL51G",
        description="unique user id"
    )
    send_parcel: bool = Field(  # Fixed: added colon after send_parcel
        ...,
        example=True,  # Fixed: True not 'true'
        description="must be 'true' to send a parcel"
    )
    parcel_destination: str = Field(  # Fixed: added colon after parcel_destination
        ...,
        example="Locker",
        description="The destination of the parcel"  # Fixed typo: destination
    )
    parcel_size: str = Field(
        ...,
        example="Medium",
        description="Size of the parcel (Small, Medium, Large)"
    )
    parcel_description: str = Field(
        ...,
        example="Books",
        description="Description of the parcel contents"
    )
    tracking_id: str = Field(
        ...,
        example="123456",
        description="Tracking ID for the parcel"
    )
    demo_mode: Optional[bool] = Field(
        False,
        example=True,
        description="Enable demo mode with faster notification intervals"
    )
    notification_interval: Optional[int] = Field(
        60,
        example=10,
        description="Seconds between notifications (default 60, demo mode: 10-20)"
    )

class CouponCodeRequest(BaseModel):
    """Request to fetch a coupon code"""
    coupon_request: bool = Field(
        ...,
        example=True,  # Changed from 'true' to True (no quotes for boolean)
        description="must be 'true' to request a coupon code"
    )
    user_id: str = Field(
        ...,
        example="user123",
        description="Unique identifier for the user requesting the coupon"
    )

class CouponValidationRequest(BaseModel):
    """Request to validate a coupon code"""
    coupon_code: str = Field(
        ...,
        example="SAVE-A1B2C3D4",
        description="The coupon code to validate"
    )
    user_id: str = Field(
        ...,
        example="user123",
        description="User ID attempting to use the coupon"
    )

class CalendarDataRequest(BaseModel):
    """Request to generate calendar event from OneSignal data feed"""
    summary: str = Field(
        ...,
        example="Booking Confirmation",
        description="Event summary/title"
    )
    description: str = Field(
        ...,
        example="Windglass Repair Appointment",
        description="Event description"
    )
    organizer_email: str = Field(
        ...,
        example="claudio+1@onesignal.com",
        description="Email of the event organizer"
    )
    attendees_emails: List[str] = Field(
        ...,
        example=["user@example.com"],
        description="List of attendee email addresses"
    )
    time_zone: str = Field(
        ...,
        example="Europe/Helsinki",
        description="Timezone for the event (IANA timezone format)"
    )
    location: str = Field(
        ...,
        example="Workshop Name",
        description="Event location"
    )
    start_time: str = Field(
        ...,
        example="16:00",
        description="Start time in HH:MM format (24-hour)"
    )
    end_time: str = Field(
        ...,
        example="17:00",
        description="End time in HH:MM format (24-hour)"
    )
    meeting_date: str = Field(
        ...,
        example="25-12-2025",
        description="Meeting date in DD-MM-YYYY format"
    )
    glass_type: Optional[str] = Field(
        None,
        example="windshield",
        description="Type of glass being serviced (custom field)"
    )


# Response models (what your API returns)
class OTPResponse(BaseModel):
    """Response after generating OTP"""
    status: str
    message: str
    signal_code: Optional[str] = None  # Only in debug mode
    debug: Optional[str] = None


class VerifyResponse(BaseModel):
    """Response after verifying OTP"""
    status: str
    valid: bool
    message: str

class CouponCodeResponse(BaseModel):
    """Response containing the generated coupon code"""
    coupon_code: str = Field(
        ...,
        example="SAVE-A1B2C3D4",
        description="Unique coupon code valid for 5 minutes"
    )
    expires_at: datetime = Field(
        ...,
        example="2024-01-20T10:30:00Z",
        description="ISO timestamp when the coupon expires"
    )
    user_id: str = Field(
        ...,
        example="user123",
        description="User ID associated with this coupon"
    )
class CouponValidationResponse(BaseModel):
    """Response for coupon validation"""
    is_valid: bool = Field(
        ...,
        example=True,
        description="Whether the coupon is valid"
    )

class CalendarDataResponse(BaseModel):
    """Response containing calendar URLs"""
    status: str = Field(
        ...,
        example="success",
        description="Status of the request"
    )
    google_url: Optional[str] = Field(
        None,
        example="https://calendar.google.com/calendar/render?action=TEMPLATE&text=...",
        description="Google Calendar add to calendar URL"
    )
    ics_url: Optional[str] = Field(
        None,
        example="https://your-railway-app.railway.app/calendar/appointment-123.ics",
        description="URL to download .ics calendar file"
    )
    message: Optional[str] = Field(
        None,
        description="Additional message or error details"
    )


class StoredOTP(BaseModel):
    """How we store OTP data internally"""
    phone_number: str
    code: str
    created_at: datetime
    used: bool = False


class FlightUpdateContentState(BaseModel):
    gate: str = Field(..., example="A12", description="Gate number")
    boardingTime: Optional[str] = Field(None, alias="boardingTime", example="2025-09-30T16:55:00Z", description="Boarding time in ISO format")
    status: Optional[str] = Field(None, example="boarding", description="Flight status (e.g., boarding, in-flight, landed)")
    group: Optional[str] = Field(None, example="Group A", description="Boarding group")  

class FlightUpdateLiveActivity(BaseModel):
    activity_type: Literal["flightUpdate"] = Field(..., alias="activity_type")
    activity_id: str = Field(..., alias="activity_id")
    content_state: FlightUpdateContentState = Field(..., alias="content_state")
    trace_id: Optional[str] = Field(None, alias="trace_id")
    timestamp: Optional[datetime] = Field(None, alias="time_stamp")