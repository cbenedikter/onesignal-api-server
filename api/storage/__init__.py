def __init__(self):
    self.redis_client = None
    self.local_storage = {}
    
    print(f"Checking KV credentials...")
    print(f"KV_URL exists: {bool(settings.KV_URL)}")
    print(f"KV_REST_API_URL: {settings.KV_REST_API_URL}")
    print(f"KV_REST_API_TOKEN exists: {bool(settings.KV_REST_API_TOKEN)}")
    
    if settings.KV_REST_API_URL and settings.KV_REST_API_TOKEN:
        try:
            print(f"Attempting to connect to Redis...")
            self.redis_client = redis.from_url(
                settings.KV_URL,
                decode_responses=True
            )
            self.redis_client.ping()
            print("✅ Connected to Vercel KV")
        except Exception as e:
            self.redis_client = None
    else:
        print("📝 No KV credentials found - using local memory storage")