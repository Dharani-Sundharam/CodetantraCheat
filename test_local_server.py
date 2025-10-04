#!/usr/bin/env python3
"""
Test local server startup to identify issues
"""

import os
import sys
import subprocess
import time

def test_local_server():
    """Test if we can start the server locally"""
    print("Testing Local Server Startup...")
    print("=" * 50)
    
    # Set environment variables
    os.environ["DATABASE_URL"] = "postgresql://admin:l9F1rk7UXCmY8UnOFcYeUiULbJ1kHeYO@dpg-d3fv09vdiees73bh8g2g-a.oregon-postgres.render.com/codetantradb"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["ENVIRONMENT"] = "production"
    os.environ["FRONTEND_URL"] = "https://codetantra-frontend.onrender.com"
    os.environ["ADMIN_EMAIL"] = "admin@codetantra.ac.in"
    os.environ["ADMIN_PASSWORD"] = "admin123"
    
    # Add backend to Python path
    sys.path.insert(0, "backend")
    
    try:
        # Try to import main.py to check for import errors
        print("Testing imports...")
        import main
        print("[SUCCESS] All imports successful")
        
        # Try to create the FastAPI app
        print("Testing FastAPI app creation...")
        app = main.app
        print("[SUCCESS] FastAPI app created")
        
        # Try to start the server (non-blocking)
        print("Testing server startup...")
        import uvicorn
        import threading
        
        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(5)
        
        # Test if server is responding
        import requests
        try:
            response = requests.get("http://localhost:8001/api/health", timeout=5)
            print(f"[SUCCESS] Server responding: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"[ERROR] Server not responding: {e}")
        
    except Exception as e:
        print(f"[ERROR] Server startup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_server()
