# api/services/otp_service.py
"""
OTP Service - Handles all OTP-related business logic
This is separate from the HTTP layer (routers)
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from ..models.schemas import StoredOTP


class OTPService:
    """Service for managing OTP generation and verification"""
    
    def __init__(self):
        # Temporary in-memory storage (will be replaced with Vercel KV)
        self.storage: Dict[str, StoredOTP] = {}
        
    def generate_otp(self, phone_number: str) -> str:
        """
        Generate a new OTP for the given phone number
        
        Args:
            phone_number: The phone number to send OTP to
            
        Returns:
            The generated OTP code
        """
        # Generate random 5-digit code
        code = str(random.randint(10000, 99999))
        
        # Create storage key
        key = f"{phone_number}:{code}"
        
        # Store the OTP
        self.storage[key] = StoredOTP(
            phone_number=phone_number,
            code=code,
            created_at=datetime.now(),
            used=False
        )
        
        print(f"Generated OTP {code} for {phone_number}")
        return code
    
    def verify_otp(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """
        Verify if the OTP is valid for the given phone number
        
        Args:
            phone_number: The phone number that requested OTP
            code: The OTP code to verify
            
        Returns:
            Tuple of (is_valid, message)
        """
        key = f"{phone_number}:{code}"
        
        # Check if OTP exists
        if key not in self.storage:
            return False, "Invalid code or phone number"
        
        stored_otp = self.storage[key]
        
        # Check if already used
        if stored_otp.used:
            return False, "Code already used"
        
        # Check if expired (5 minutes)
        age = datetime.now() - stored_otp.created_at
        if age > timedelta(minutes=5):
            return False, "Code expired"
        
        # Mark as used
        stored_otp.used = True
        self.storage[key] = stored_otp
        
        return True, "Code verified successfully"
    
    def cleanup_expired_otps(self, max_age_minutes: int = 5) -> int:
        """
        Remove OTPs older than max_age_minutes
        
        Returns:
            Number of OTPs cleaned up
        """
        current_time = datetime.now()
        keys_to_remove = []
        
        for key, otp in self.storage.items():
            age_minutes = (current_time - otp.created_at).total_seconds() / 60
            if age_minutes > max_age_minutes:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.storage[key]
            
        return len(keys_to_remove)
    
    def get_storage_debug(self) -> dict:
        """Get current storage state for debugging"""
        return {
            key: {
                "phone_number": otp.phone_number,
                "code": otp.code,
                "created_at": otp.created_at.isoformat(),
                "used": otp.used
            }
            for key, otp in self.storage.items()
        }


# Create a single instance to use across the app
otp_service = OTPService()