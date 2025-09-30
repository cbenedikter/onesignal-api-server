# api/main.py
"""
Main FastAPI application
This file sets up the app and includes all routers
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, delivery, dashboard, coupon, flight_update
from .config import settings
from .storage.kv_store import kv_store 


print(f"KV configured: {settings.has_kv}")
print(f"KV Store initialized: {kv_store is not None}")
print(f"KV configured: {settings.has_kv}")


# Create the FastAPI app
app = FastAPI(
    title="OneSignal API Server",
    description="Claudio's backend server for handling API logic and OneSignal integration",
    version="2.0.2"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Claudio's OneSignal API Server!",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "/": "This welcome message",
            "/auth/otp": "POST - Generate OTP",
            "/auth/verify": "POST - Verify OTP",
            "/delivery": "POST - Start delivery tracking",
            "/coupon/request": "POST - Generate coupon code",
            "/coupon/validate": "POST - Validate coupon code",
            "/flight-update": "POST - Start flight update Live Activity",
            "/docs": "Interactive API documentation",
            "/redoc": "Alternative API documentation"
        }
    }


# Include routers
app.include_router(auth.router)
app.include_router(delivery.router)
app.include_router(dashboard.router)
app.include_router(coupon.router)
app.include_router(flight_update.router) 

# Future routers can be added like this:
# app.include_router(notifications.router)
# app.include_router(rules.router)