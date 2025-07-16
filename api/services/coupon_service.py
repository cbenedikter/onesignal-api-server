# api/services/coupon_service.py
"""
Service for generating and validating coupon codes
"""
import random
import string
from datetime import datetime, timedelta
from api.storage.kv_store import KVStore
from api.models.schemas import CouponCodeResponse
from api.config import settings

class CouponService:
    def __init__(self):
        self.kv_store = KVStore()
        self.settings = settings
        self.expiry_minutes = 5
    
    async def generate_coupon(self, user_id: str) -> CouponCodeResponse:
        """Generate a unique coupon code for the user"""
        
        # 1. Generate a unique code
        coupon_code = self._generate_unique_code()
        
        # 2. Calculate expiry time
        expires_at = datetime.utcnow() + timedelta(minutes=self.expiry_minutes)
        
        # 3. Store in KV with the coupon code as key
        self.kv_store.set(
            key=f"coupon:{coupon_code}",
            value={
                "user_id": user_id,
                "expires_at": expires_at.isoformat(),
                "used": False
            },
            ttl=self.expiry_minutes * 60  # Convert to seconds
        )
        
        # 4. Also store by user_id to track their coupons
        self.kv_store.set(
            key=f"user_coupon:{user_id}",
            value={
                "coupon_code": coupon_code,
                "expires_at": expires_at.isoformat()
            },
            ttl=self.expiry_minutes * 60
        )
        
        # 5. Return the response
        return CouponCodeResponse(
            coupon_code=coupon_code,
            expires_at=expires_at,
            user_id=user_id
        )
    
    async def validate_coupon(self, coupon_code: str, user_id: str) -> bool:
        """Check if a coupon is valid for the given user"""
        
        # 1. Retrieve coupon from KV store
        coupon_data = self.kv_store.get(f"coupon:{coupon_code}")
        
        # 2. Check if coupon exists
        if not coupon_data:
            return False
        
        # 3. Check if it belongs to this user
        if coupon_data.get("user_id") != user_id:
            return False
        
        # 4. Check if already used
        if coupon_data.get("used", False):
            return False
        
        # 5. Check if expired (belt and suspenders - KV TTL should handle this)
        expires_at = datetime.fromisoformat(coupon_data.get("expires_at"))
        if datetime.utcnow() > expires_at:
            return False
        
        # 6. Mark as used (optional - depends on your business logic)
        # If you want single-use coupons, uncomment this:
        # coupon_data["used"] = True
        # await self.kv_store.set(
        #     key=f"coupon:{coupon_code}",
        #     value=coupon_data,
        #     ttl=60  # Keep for 1 minute after use for logging
        # )
        
        return True
    
    def _generate_unique_code(self) -> str:
        """Generate a random 6-character coupon code"""
        return ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )