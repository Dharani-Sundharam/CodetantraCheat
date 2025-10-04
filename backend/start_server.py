#!/usr/bin/env python3
"""
Start the CodeTantra Automation Backend Server
This script starts the FastAPI server with proper environment setup
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set default environment variables if not already set
if not os.getenv("DATABASE_URL"):
    # Use default local PostgreSQL URL for development
    os.environ["DATABASE_URL"] = "postgresql://codetantra_user:codetantra123@localhost:5432/codetantra_local"

if not os.getenv("JWT_SECRET_KEY"):
    os.environ["JWT_SECRET_KEY"] = "your-super-secret-key-change-this-in-production"

if not os.getenv("JWT_ALGORITHM"):
    os.environ["JWT_ALGORITHM"] = "HS256"

if not os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"):
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

# Initialize database before starting server
try:
    from database import init_database
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
except Exception as e:
    print(f"Database initialization failed: {e}")
    print("Please check your DATABASE_URL and ensure PostgreSQL is accessible.")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting CodeTantra Automation Backend Server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable auto-reload for development
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
