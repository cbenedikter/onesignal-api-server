# api/main.py
"""
Main FastAPI application
This file sets up the app and includes all routers
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, delivery, dashboard, coupon, flight_update, calendar, webhooks
from .config import settings
from .storage.kv_store import kv_store
from .services.database_service import database_service


print(f"KV configured: {settings.has_kv}")
print(f"KV Store initialized: {kv_store is not None}")
print(f"Database configured: {settings.has_database}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting OneSignal API Server...")
    await database_service.initialize()
    yield
    # Shutdown
    print("🛑 Shutting down...")
    await database_service.shutdown()


# Create the FastAPI app
app = FastAPI(
    title="OneSignal API Server",
    description="Claudio's backend server for handling API logic and OneSignal integration",
    version="2.1.0",
    lifespan=lifespan
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
        "version": "2.1.0",
        "status": "running",
        "endpoints": {
            "/": "This welcome message",
            "/auth/otp": "POST - Generate OTP",
            "/auth/verify": "POST - Verify OTP",
            "/delivery": "POST - Start delivery tracking",
            "/coupon/request": "POST - Generate coupon code",
            "/coupon/validate": "POST - Validate coupon code",
            "/flight-update": "POST - Start flight update Live Activity",
            "/calendar-data": "POST - Generate Google Calendar URL and ICS file",
            "/calendar/{id}.ics": "GET - Download ICS calendar file",
            "/webhooks/onesignal": "POST - Receive OneSignal webhook events",
            "/messages/{app_id}/{external_id}": "GET - Retrieve user's notification inbox",
            "/webhooks/health": "GET - Check webhook system health",
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
app.include_router(calendar.router)
app.include_router(webhooks.router)