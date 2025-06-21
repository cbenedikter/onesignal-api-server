# api/main.py
"""
Main FastAPI application
This file sets up the app and includes all routers
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth


# Create the FastAPI app
app = FastAPI(
    title="OneSignal API Server",
    description="Backend server for handling API logic and OneSignal integration",
    version="2.0.0"
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
        "message": "Welcome to your OneSignal API Server!",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "/": "This welcome message",
            "/auth/otp": "POST - Generate OTP",
            "/auth/verify": "POST - Verify OTP",
            "/docs": "Interactive API documentation",
            "/redoc": "Alternative API documentation"
        }
    }


# Include routers
app.include_router(auth.router)

# Future routers can be added like this:
# app.include_router(notifications.router)
# app.include_router(rules.router)