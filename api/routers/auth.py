# api/routers/auth.py
"""
Authentication router - Handles all OTP-related HTTP endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
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
async def generate_otp(request: OTPRequest):
    """Generate a 5-digit OTP for a specific phone number"""
    print(f"Rquest: phone={request.phone_number}, request_otp={request.request_otp}")
    if not request.request_otp:
        return OTPResponse(
            status="error",
            message="request_otp must be 'true' to generate an OTP"
        )
        print(f"Response: {response.model_dump()}")
        return response
    try:
        # Generate the OTP using our service
        code = await otp_service.generate_otp(request.phone_number)
        
        # TODO: Send via OneSignal here
        # await onesignal_service.send_sms(request.phone_number, code)
        
        return OTPResponse(
            status="success",
            message=f"OTP sent to {request.phone_number}",
            signal_code=code,  
            debug="In production, don't return the code!"
        )
        print(f"Response: {response.model_dump()}")
        return response
    
    
    except Exception as e:
        return OTPResponse(
            status="error",
            message=str(e)
        )
        print(f" Error message: {response.model_dump()}")
        return response

@router.post("/verify", response_model=VerifyResponse)
async def verify_otp(request: VerifyOTPRequest):
    """Verify if the provided OTP belongs to the specific phone number"""
    
    # Use the service to verify
    is_valid, message = await otp_service.verify_otp(
        request.phone_number, 
        request.signal_code
    )
    
    return VerifyResponse(
        status="success" if is_valid else "error",
        valid=is_valid,
        message=message
    )


@router.post("/cleanup")
async def cleanup_otps():
    """Manually clean up expired OTPs"""
    count = await otp_service.cleanup_expired_otps()
    return {
        "status": "success",
        "message": f"Found {count} active OTPs (expired ones auto-removed by TTL)"
    }


# Debug endpoint - remove in production
@router.get("/debug/storage")
async def debug_storage():
    """See current OTP storage (remove in production!)"""
    return {"storage": await otp_service.get_storage_debug()}