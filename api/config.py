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
    
    # OneSignal Configuration
    ONESIGNAL_APP_ID: Optional[str] = os.getenv("ONESIGNAL_APP_ID")
    ONESIGNAL_API_KEY: Optional[str] = os.getenv("ONESIGNAL_API_KEY")
    
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
        return bool(self.ONESIGNAL_APP_ID and self.ONESIGNAL_API_KEY)
    
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