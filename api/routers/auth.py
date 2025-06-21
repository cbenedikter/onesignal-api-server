# api/routers/auth.py
"""
Authentication router - Handles all OTP-related HTTP endpoints
"""
from fastapi import APIRouter, HTTPException

from ..models.schemas import (
    OTPRequest, 
    VerifyOTPRequest, 
    OTPResponse, 
    VerifyResponse
)
from ..services.otp_service import otp_service


# Create a router instance (like a mini FastAPI app)
router = APIRouter(
    prefix="/auth",  # All routes will start with /auth
    tags=["authentication"]  # For documentation organization
)


@router.post("/otp", response_model=OTPResponse)
def generate_otp(request: OTPRequest):
    """Generate a 5-digit OTP for a specific phone number"""
    
    # TODO: Add phone number validation
    # TODO: Add rate limiting (max OTPs per phone per hour)
    
    # Generate the OTP using our service
    code = otp_service.generate_otp(request.phone_number)
    
    # TODO: Send via OneSignal here
    # await onesignal_service.send_sms(request.phone_number, code)
    
    return OTPResponse(
        status="success",
        message=f"OTP sent to {request.phone_number}",
        signal_code=code,  # Remove in production!
        debug="In production, don't return the code!"
    )


@router.post("/verify", response_model=VerifyResponse)
def verify_otp(request: VerifyOTPRequest):
    """Verify if the provided OTP belongs to the specific phone number"""
    
    # Use the service to verify
    is_valid, message = otp_service.verify_otp(
        request.phone_number, 
        request.signal_code
    )
    
    return VerifyResponse(
        status="success" if is_valid else "error",
        valid=is_valid,
        message=message
    )


@router.post("/cleanup")
def cleanup_otps():
    """Manually clean up expired OTPs"""
    count = otp_service.cleanup_expired_otps()
    return {
        "status": "success",
        "message": f"Cleaned up {count} expired OTPs"
    }


# Debug endpoint - remove in production
@router.get("/debug/storage")
def debug_storage():
    """See current OTP storage (remove in production!)"""
    return {"storage": otp_service.get_storage_debug()}