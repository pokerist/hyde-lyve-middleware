#!/usr/bin/env python3
"""
Simple test script for Hydepark Lyve Middleware
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_person_check():
    """Test person check endpoint"""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {"personId": "test_person_123"}
        
        response = requests.post(f"{BASE_URL}/api/person/check", 
                               headers=headers, 
                               data=json.dumps(data))
        
        print(f"Person check: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Parsed JSON: {result}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Person check failed: {e}")
        return False

def main():
    print("Testing Hydepark Lyve Middleware...")
    print("=" * 50)
    
    if test_health():
        test_person_check()

if __name__ == "__main__":
    main()