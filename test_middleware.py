#!/usr/bin/env python3
"""
Test script for Hydepark Lyve Middleware
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_person_operations():
    """Test person CRUD operations"""
    test_person_id = f"test_person_{int(time.time())}"
    
    # 1. Check non-existent person
    print("1. Checking non-existent person...")
    response = requests.post(f"{BASE_URL}/api/person/check", 
                           json={"personId": test_person_id})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 2. Create person
    print("2. Creating person...")
    person_data = {
        "personId": test_person_id,
        "name": "Test User",
        "phone": "1234567890",
        "email": "test@example.com",
        "gender": 1,
        "beginTime": "2024-01-01T00:00:00",
        "endTime": "2030-01-01T00:00:00"
    }
    response = requests.post(f"{BASE_URL}/api/person/create", 
                           json=person_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        created_data = response.json()
        hikcentral_id = created_data.get('hikcentralId')
        print(f"Created HikCentral ID: {hikcentral_id}")
    print()
    
    # 3. Check existing person
    print("3. Checking existing person...")
    response = requests.post(f"{BASE_URL}/api/person/check", 
                           json={"personId": test_person_id})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 4. Update person
    print("4. Updating person...")
    update_data = {
        "personId": test_person_id,
        "name": "Updated Test User",
        "phone": "0987654321",
        "email": "updated@example.com"
    }
    response = requests.put(f"{BASE_URL}/api/person/update", 
                          json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 5. Delete person
    print("5. Deleting person...")
    response = requests.delete(f"{BASE_URL}/api/person/delete", 
                             json={"personId": test_person_id})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 6. Check deleted person
    print("6. Checking deleted person...")
    response = requests.post(f"{BASE_URL}/api/person/check", 
                           json={"personId": test_person_id})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def main():
    """Run all tests"""
    print("Starting Hydepark Lyve Middleware Tests")
    print("=" * 50)
    
    try:
        test_health_check()
        test_person_operations()
        print("All tests completed successfully!")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the middleware server.")
        print("Please ensure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()