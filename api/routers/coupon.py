# api/routers/coupon.py
"""
Coupon endpoints for generating and validating discount codes
"""
from fastapi import APIRouter, HTTPException, Depends
from api.models.schemas import (
    CouponCodeRequest, 
    CouponCodeResponse,
    CouponValidationRequest,
    CouponValidationResponse
)
from api.services.coupon_service import CouponService
from api.config import settings

router = APIRouter(prefix="/coupon", tags=["coupon"])
settings = settings

# Initialize the service
coupon_service = CouponService()

@router.post("/request", response_model=CouponCodeResponse)
async def request_coupon(request: CouponCodeRequest):
    """Generate a new coupon code valid for 5 minutes"""
    
    # Validate the coupon_request flag
    if not request.coupon_request:
        raise HTTPException(
            status_code=400,
            detail="coupon_request must be true"
        )
    
    # Call the service to generate the coupon
    return await coupon_service.generate_coupon(
        user_id=request.user_id
    )

@router.post("/validate", response_model=CouponValidationResponse)
async def validate_coupon(request: CouponValidationRequest):
    """Check if a coupon code is valid"""
    
    # Call the service to validate
    is_valid = await coupon_service.validate_coupon(
        coupon_code=request.coupon_code,
        user_id=request.user_id
    )
    
    return CouponValidationResponse(is_valid=is_valid)