# api/models/schemas.py
"""
Data models (schemas) for your API
These define what data your API expects and returns
"""
from pydantic import BaseModel, Field
from typing import Optional
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
    parcel_description: Optional[str] = Field(default="Package", example="Books")
    
    tracking_id: str = Field(
        ...,
        example="123456",
        description="Tracking ID for the parcel"
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


# Internal models (for storage)
class StoredOTP(BaseModel):
    """How we store OTP data internally"""
    phone_number: str
    code: str
    created_at: datetime
    used: bool = False