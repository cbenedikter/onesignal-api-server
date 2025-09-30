# api/models/schemas.py
"""
Data models (schemas) for your API
These define what data your API expects and returns
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
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


class StoredOTP(BaseModel):
    """How we store OTP data internally"""
    phone_number: str
    code: str
    created_at: datetime
    used: bool = False


class FlightUpdateContentState(BaseModel):
    emoji: str = Field(..., min_length=1)  

class FlightUpdateLiveActivity(BaseModel):
    activity_type: Literal["flightUpdate"] = Field(..., alias="activity_type")
    activity_id: str = Field(..., alias="activity_id")
    content_state: FlightUpdateContentState = Field(..., alias="content_state")
    trace_id: Optional[str] = Field(None, alias="trace_id")
    timestamp: Optional[datetime] = Field(None, alias="time_stamp")