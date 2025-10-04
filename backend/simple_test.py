#!/usr/bin/env python3
"""
Simple test to check if FastAPI app is working
"""

import requests
import json

def test_simple():
    base_url = "https://codetantra-backend.onrender.com"
    
    print("Testing simple endpoints...")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Content type: {response.headers.get('content-type', 'unknown')}")
            print(f"Content length: {len(response.text)}")
        else:
            print(f"Error: {response.text[:200]}...")
    except Exception as e:
        print(f"Root endpoint failed: {e}")
    
    # Test docs endpoint
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        print(f"Docs endpoint: {response.status_code}")
        if response.status_code == 200:
            print("API documentation is accessible")
        else:
            print(f"Docs error: {response.text[:200]}...")
    except Exception as e:
        print(f"Docs endpoint failed: {e}")
    
    # Test openapi endpoint
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        print(f"OpenAPI endpoint: {response.status_code}")
        if response.status_code == 200:
            print("OpenAPI schema is accessible")
        else:
            print(f"OpenAPI error: {response.text[:200]}...")
    except Exception as e:
        print(f"OpenAPI endpoint failed: {e}")

if __name__ == "__main__":
    test_simple()
