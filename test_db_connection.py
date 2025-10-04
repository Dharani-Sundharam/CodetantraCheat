#!/usr/bin/env python3
"""
Test PostgreSQL database connection
"""

import psycopg2
import requests
import time

def test_postgresql_connection():
    """Test if PostgreSQL database is accessible"""
    db_url = "postgresql://admin:l9F1rk7UXCmY8UnOFcYeUiULbJ1kHeYO@dpg-d3fv09vdiees73bh8g2g-a.oregon-postgres.render.com/codetantradb"
    
    print("Testing PostgreSQL Database Connection...")
    print("=" * 50)
    
    try:
        # Test connection
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"[SUCCESS] Database connected!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test table existence
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()
        print(f"Tables found: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def test_backend_server():
    """Test if backend server is running"""
    base_url = "https://ctautomationpro.onrender.com"
    
    print("\nTesting Backend Server...")
    print("=" * 50)
    
    endpoints = [
        "/",
        "/api/health", 
        "/test",
        "/login.html"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"[{response.status_code}] {endpoint}")
            if response.status_code == 200:
                print(f"   Content length: {len(response.text)} chars")
            else:
                print(f"   Error: {response.text[:100]}...")
        except Exception as e:
            print(f"[ERROR] {endpoint}: {e}")

def test_render_services():
    """Test Render services status"""
    print("\nTesting Render Services...")
    print("=" * 50)
    
    # Test if we can reach the domain
    try:
        response = requests.get("https://ctautomationpro.onrender.com", timeout=10)
        print(f"Backend domain reachable: {response.status_code}")
    except Exception as e:
        print(f"Backend domain error: {e}")
    
    # Test if we can reach the frontend
    try:
        response = requests.get("https://ctautomationpro.onrender.com", timeout=10)
        print(f"Frontend domain reachable: {response.status_code}")
    except Exception as e:
        print(f"Frontend domain error: {e}")

if __name__ == "__main__":
    print("CodeTantra Backend & Database Diagnostic")
    print("=" * 60)
    
    # Test database
    db_ok = test_postgresql_connection()
    
    # Test backend
    test_backend_server()
    
    # Test Render services
    test_render_services()
    
    print("\n" + "=" * 60)
    if db_ok:
        print("Database: [ONLINE]")
    else:
        print("Database: [OFFLINE]")
    
    print("Check Render dashboard for service status")
