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