#!/usr/bin/env python3
"""
Simple test script to check if the backend is working
"""

import requests
import json

def test_backend():
    base_url = "https://ctautomationpro.onrender.com"
    
    print("Testing CodeTantra Backend...")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"[OK] Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
    
    # Test 2: Login endpoint
    try:
        login_data = {
            "email": "admin@codetantra.ac.in",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=login_data, 
                               timeout=10)
        print(f"[OK] Login test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Token received: {len(data.get('access_token', ''))} chars")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"[ERROR] Login test failed: {e}")
    
    # Test 3: Frontend page
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"[OK] Frontend page: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content length: {len(response.text)} chars")
        else:
            print(f"   Error: {response.text[:200]}...")
    except Exception as e:
        print(f"[ERROR] Frontend test failed: {e}")

if __name__ == "__main__":
    test_backend()
