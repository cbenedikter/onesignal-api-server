# api/services/otp_service.py
"""
OTP Service - Handles all OTP-related business logic
This is separate from the HTTP layer (routers)
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from ..models.schemas import StoredOTP
from ..config import settings
from ..storage.kv_store import kv_store


class OTPService:
    """Service for managing OTP generation and verification"""
    
    def __init__(self):
        self.kv = kv_store
        self.otp_prefix = "otp:"
        self.rate_limit_prefix = "rate:"
        
    async def generate_otp(self, phone_number: str) -> str:
        """
        Generate a new OTP for the given phone number
        
        Args:
            phone_number: The phone number to send OTP to
            
        Returns:
            The generated OTP code
        """
        # Check rate limit
        rate_key = f"{self.rate_limit_prefix}{phone_number}"
        attempts = self.kv.get(rate_key) or 0
        
        if attempts >= 3:
            raise Exception("Too many OTP requests. Please try again later.")
        
        # Generate random 5-digit code
        code = str(random.randint(10000, 99999))
        
        # Create storage key
        key = f"{self.otp_prefix}{phone_number}:{code}"
        
        # Store the OTP with 5-minute TTL
        otp_data = {
            "phone_number": phone_number,
            "code": code,
            "created_at": datetime.now().isoformat(),
            "used": False
        }
        
        self.kv.set(key, otp_data, ttl=300)  # 5 minutes
        
        # Update rate limit (1 hour TTL)
        self.kv.increment(rate_key)
        if attempts == 0:  # First attempt, set TTL
            self.kv.set(rate_key, 1, ttl=3600)
        
        print(f"Generated OTP {code} for {phone_number}")
        
        # TODO: Send via OneSignal if configured
        if settings.has_onesignal:
            print(f"Would send OTP via OneSignal to {phone_number}")
            # await send_onesignal_notification(phone_number, code)
        else:
            print("OneSignal not configured - OTP not sent")
            
        return code
    
    async def verify_otp(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """
        Verify if the OTP is valid for the given phone number
        
        Args:
            phone_number: The phone number that requested OTP
            code: The OTP code to verify
            
        Returns:
            Tuple of (is_valid, message)
        """
        key = f"{self.otp_prefix}{phone_number}:{code}"
        
        # Get OTP from KV
        otp_data = self.kv.get(key)
        
        # Check if OTP exists
        if not otp_data:
            return False, "Invalid code or expired"
        
        # Check if already used
        if otp_data.get("used"):
            return False, "Code already used"
        
        # Mark as used
        otp_data["used"] = True
        self.kv.set(key, otp_data, ttl=60)  # Keep for 1 minute after use
        
        return True, "Code verified successfully"
    
    async def cleanup_expired_otps(self) -> int:
        """
        Cleanup is automatic with TTL, but this can force cleanup
        
        Returns:
            Number of OTPs cleaned up
        """
        # With TTL, Redis automatically removes expired keys
        # This method is kept for compatibility
        keys = self.kv.get_keys(f"{self.otp_prefix}*")
        return len(keys)  # Just return count of active OTPs
    
    async def get_storage_debug(self) -> dict:
        """Get current storage state for debugging"""
        debug_info = {
            "active_otps": [],
            "rate_limits": []
        }
        
        # Get all OTP keys
        otp_keys = self.kv.get_keys(f"{self.otp_prefix}*")
        for key in otp_keys:
            otp_data = self.kv.get(key)
            if otp_data:
                debug_info["active_otps"].append({
                    "key": key,
                    "data": otp_data
                })
        
        # Get rate limit info
        rate_keys = self.kv.get_keys(f"{self.rate_limit_prefix}*")
        for key in rate_keys:
            count = self.kv.get(key)
            debug_info["rate_limits"].append({
                "phone": key.replace(self.rate_limit_prefix, ""),
                "attempts": count
            })
        
        return debug_info


# Create a single instance to use across the app
otp_service = OTPService()