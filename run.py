# run.py
"""
Entry point for running the server locally
"""
import uvicorn

if __name__ == "__main__":
    print("Starting server at http://localhost:8000")
    print("View API docs at http://localhost:8000/docs")
    print("View alternative docs at http://localhost:8000/redoc")
    
    # Run the server
    uvicorn.run(
        "api.main:app",  # Path to your FastAPI app
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload when you change code!
    )