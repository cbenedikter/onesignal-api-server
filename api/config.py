# api/config.py
"""
Configuration management for the API
Loads environment variables and provides defaults
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # OneSignal App and API Keys
    signal_post_app_id: Optional[str] = os.getenv("signal_post_app_id")
    signal_post_api_key: Optional[str] = os.getenv("signal_post_api_key")
    emea_se_demo_app_id: Optional[str] = os.getenv("emea_se_demo_app_id")
    emea_se_demo_api_key: Optional[str] = os.getenv("emea_se_demo_api_key")  

    #OneSignal Teplate IDs
    emea_se_demo_sms_otp: str = "a6f35326-6b86-4076-952c-1b3bbee7d391"
    
    # Vercel KV Configuration
    KV_URL: Optional[str] = os.getenv("KV_URL")
    KV_REST_API_URL: Optional[str] = os.getenv("KV_REST_API_URL")
    KV_REST_API_TOKEN: Optional[str] = os.getenv("KV_REST_API_TOKEN")
    KV_REST_API_READ_ONLY_TOKEN: Optional[str] = os.getenv("KV_REST_API_READ_ONLY_TOKEN")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"
    
    @property
    def has_onesignal(self) -> bool:
        """Check if OneSignal is configured"""
        return True
    
    @property
    def has_kv(self) -> bool:
        """Check if Vercel KV is configured"""
        return bool(self.KV_REST_API_URL and self.KV_REST_API_TOKEN)


# Create a single instance
settings = Settings()

# Print configuration status on startup (helpful for debugging)
print(f"Environment: {settings.ENVIRONMENT}")
print(f"OneSignal configured: {settings.has_onesignal}")
print(f"Vercel KV configured: {settings.has_kv}")