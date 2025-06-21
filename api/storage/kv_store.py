# api/storage/kv_store.py
"""
Vercel KV Store wrapper
Handles all interactions with Vercel's KV (Redis) storage
"""
import json
import redis
from typing import Any, Dict, Optional
from ..config import settings


class KVStore:
    """
    Wrapper for Vercel KV operations
    Falls back to in-memory storage for local development
    """
    
    def __init__(self):
        self.redis_client = None
        self.local_storage = {}  # Fallback for local dev
        
        # Try to connect to Vercel KV
        if settings.KV_REST_API_URL and settings.KV_REST_API_TOKEN:
            try:
                # Parse the Redis URL
                self.redis_client = redis.from_url(
                    settings.KV_URL,
                    decode_responses=True  # Get strings instead of bytes
                )
                # Test connection
                self.redis_client.ping()
                print("✅ Connected to Vercel KV")
            except Exception as e:
                print(f"⚠️  Could not connect to Vercel KV: {e}")
                print("📝 Using local memory storage")
        else:
            print("📝 No KV credentials found - using local memory storage")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value with optional TTL (time to live in seconds)
        
        Args:
            key: The key to store
            value: The value (will be JSON serialized)
            ttl: Optional expiration time in seconds
        
        Returns:
            True if successful
        """
        try:
            # Serialize the value
            json_value = json.dumps(value)
            
            if self.redis_client:
                # Use Redis
                print(f"KV SET: Attempting to store key: {key}")
                if ttl:
                    result = self.redis_client.setex(key, ttl, json_value)
                else:
                    result = self.redis_client.set(key, json_value)
                print(f"KV SET: Result: {result}")
                
                # Verify it was stored
                test_get = self.redis_client.get(key)
                print(f"KV SET: Verification read: {test_get is not None}")
            else:
                # Use local storage
                print(f"LOCAL SET: Storing key: {key}")
                self.local_storage[key] = {
                    'value': json_value,
                    'ttl': ttl,
                    'timestamp': None  # Would need datetime for TTL simulation
                }
            
            return True
            
        except Exception as e:
            print(f"Error storing {key}: {e}")
            print(f"Error type: {type(e).__name__}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value by key
        
        Returns:
            The deserialized value or None if not found
        """
        try:
            if self.redis_client:
                json_value = self.redis_client.get(key)
            else:
                stored = self.local_storage.get(key)
                json_value = stored['value'] if stored else None
            
            if json_value:
                return json.loads(json_value)
            return None
            
        except Exception as e:
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a key
        
        Returns:
            True if the key was deleted
        """
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self.local_storage:
                    del self.local_storage[key]
                    return True
                return False
                
        except Exception as e:
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists
        
        Returns:
            True if the key exists
        """
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                return key in self.local_storage
                
        except Exception as e:
            return False
    
    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter
        
        Returns:
            The new value
        """
        try:
            if self.redis_client:
                return self.redis_client.incr(key, amount)
            else:
                # Local simulation
                current = self.get(key) or 0
                new_value = current + amount
                self.set(key, new_value)
                return new_value
                
        except Exception as e:
            return 0
    
    def get_keys(self, pattern: str = "*") -> list:
        """
        Get all keys matching a pattern
        
        Args:
            pattern: Redis pattern (e.g., "otp:*" for all OTP keys)
            
        Returns:
            List of matching keys
        """
        try:
            if self.redis_client:
                return self.redis_client.keys(pattern)
            else:
                # Local pattern matching (simple)
                import fnmatch
                return [k for k in self.local_storage.keys() 
                       if fnmatch.fnmatch(k, pattern)]
                
        except Exception as e:
            return []


# Create a singleton instance
print("Creating KV store instance...")
kv_store = KVStore()
print("KV store instance created")