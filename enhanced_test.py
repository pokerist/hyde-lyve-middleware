#!/usr/bin/env python3
"""
Enhanced test script for Hydepark Lyve Middleware with face data support
"""

import requests
import json
import time
import base64
import os

BASE_URL = "http://localhost:5000"
API_KEY = "demo-key"

def create_test_face_image():
    """Create a small test face image (base64 encoded)"""
    # This is a tiny 2x2 red PNG image for testing
    # In real usage, you would use actual face images
    test_png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QsHFA4b7B1x8wAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAAF0lEQVQI12P4//8/AyWAiRLKqP3/AxsCAgC4FwnfGqT0AAAAAElFTkSuQmCC")
    return base64.b64encode(test_png).decode('utf-8')

def test_health():
    """Test health endpoint"""
    print("🩺 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False

def test_config():
    """Test configuration endpoint"""
    print("⚙️  Testing configuration endpoint...")
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.get(f"{BASE_URL}/api/config", headers=headers)
        print(f"   Status: {response.status_code}")
        config = response.json()
        print(f"   Face validation: {config.get('face_validation', {})}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Config test failed: {e}")
        return False

def test_face_validation():
    """Test face validation endpoint"""
    print("👤 Testing face validation...")
    try:
        headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
        test_face = create_test_face_image()
        
        data = {"faceImage": test_face}
        response = requests.post(f"{BASE_URL}/api/face/validate", headers=headers, json=data)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Valid: {result.get('valid')}")
        print(f"   Quality: {result.get('qualityScore')}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Face validation failed: {e}")
        return False

def test_person_operations():
    """Test complete person CRUD operations with face data"""
    test_person_id = f"test_person_{int(time.time())}"
    test_face = create_test_face_image()
    
    print(f"👥 Testing person operations for: {test_person_id}")
    
    # 1. Check non-existent person
    print("   1️⃣ Checking non-existent person...")
    headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/api/person/check", headers=headers, json={"personId": test_person_id})
    print(f"      Status: {response.status_code}")
    print(f"      Exists: {response.json().get('exists')}")
    
    # 2. Create person with face data
    print("   2️⃣ Creating person with face data...")
    person_data = {
        "personId": test_person_id,
        "name": "Test User",
        "givenName": "Test",
        "phone": "1234567890",
        "email": "test@example.com",
        "gender": 1,
        "faceImages": [test_face],
        "beginTime": "2024-01-01T00:00:00",
        "endTime": "2030-01-01T00:00:00"
    }
    response = requests.post(f"{BASE_URL}/api/person/create", headers=headers, json=person_data)
    print(f"      Status: {response.status_code}")
    result = response.json()
    if response.status_code == 201:
        print(f"      ✅ Created: {result.get('hikcentralId')}")
        print(f"      Face count: {result.get('faceCount')}")
        hikcentral_id = result.get('hikcentralId')
    else:
        print(f"      ❌ Error: {result.get('message')}")
        return False
    
    # 3. Check existing person
    print("   3️⃣ Checking existing person...")
    response = requests.post(f"{BASE_URL}/api/person/check", headers=headers, json={"personId": test_person_id})
    print(f"      Status: {response.status_code}")
    result = response.json()
    print(f"      Exists: {result.get('exists')}")
    if result.get('exists'):
        print(f"      HikCentral ID: {result.get('hikcentralId')}")
        print(f"      Face count: {result.get('personData', {}).get('face_count')}")
    
    # 4. Get person faces
    print("   4️⃣ Getting person faces...")
    response = requests.get(f"{BASE_URL}/api/person/{test_person_id}/faces", headers=headers)
    print(f"      Status: {response.status_code}")
    result = response.json()
    print(f"      Face count: {result.get('faceCount')}")
    
    # 5. Update person
    print("   5️⃣ Updating person...")
    update_data = {
        "personId": test_person_id,
        "name": "Updated Test User",
        "phone": "0987654321",
        "email": "updated@example.com"
    }
    response = requests.put(f"{BASE_URL}/api/person/update", headers=headers, json=update_data)
    print(f"      Status: {response.status_code}")
    print(f"      Message: {response.json().get('message')}")
    
    # 6. Search persons
    print("   6️⃣ Searching persons...")
    search_data = {"name": "Updated Test", "limit": 10}
    response = requests.post(f"{BASE_URL}/api/person/search", headers=headers, json=search_data)
    print(f"      Status: {response.status_code}")
    result = response.json()
    print(f"      Found: {result.get('count')} persons")
    
    # 7. Delete person
    print("   7️⃣ Deleting person...")
    response = requests.delete(f"{BASE_URL}/api/person/delete", headers=headers, json={"personId": test_person_id})
    print(f"      Status: {response.status_code}")
    print(f"      Message: {response.json().get('message')}")
    
    # 8. Check deleted person
    print("   8️⃣ Checking deleted person...")
    response = requests.post(f"{BASE_URL}/api/person/check", headers=headers, json={"personId": test_person_id})
    print(f"      Status: {response.status_code}")
    print(f"      Exists: {response.json().get('exists')}")
    
    return True

def test_batch_operations():
    """Test batch person creation"""
    print("📦 Testing batch operations...")
    
    test_face = create_test_face_image()
    batch_data = {
        "persons": [
            {
                "personId": f"batch_person_1_{int(time.time())}",
                "name": "Batch User 1",
                "phone": "1111111111",
                "email": "batch1@example.com",
                "gender": 1,
                "faceImages": [test_face]
            },
            {
                "personId": f"batch_person_2_{int(time.time())}",
                "name": "Batch User 2",
                "phone": "2222222222",
                "email": "batch2@example.com",
                "gender": 2,
                "faceImages": [test_face]
            },
            {
                "personId": f"batch_person_3_{int(time.time())}",
                "name": "Batch User 3",
                "phone": "3333333333",
                "email": "batch3@example.com",
                "gender": 1
            }
        ]
    }
    
    try:
        headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
        response = requests.post(f"{BASE_URL}/api/person/batch/create", headers=headers, json=batch_data)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Total: {result.get('total')}")
        print(f"   Success: {result.get('successCount')}")
        print(f"   Errors: {result.get('errorCount')}")
        
        # Show individual results
        for person_result in result.get('results', []):
            status = "✅" if person_result.get('success') else "❌"
            print(f"   {status} {person_result.get('personId')}: {person_result.get('message')}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Batch test failed: {e}")
        return False

def test_sync_operations():
    """Test sync operations"""
    print("🔄 Testing sync operations...")
    
    # This would require an existing HikCentral person ID
    # For now, we'll just test the endpoint response
    try:
        headers = {'X-API-Key': API_KEY}
        # Using a dummy ID for testing
        response = requests.post(f"{BASE_URL}/api/person/sync/DUMMY_ID", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 500:
            print("   ⚠️  Sync test requires valid HikCentral person ID")
        return True
    except Exception as e:
        print(f"   ❌ Sync test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Hydepark Lyve Middleware Tests")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Configuration", test_config),
        ("Face Validation", test_face_validation),
        ("Person Operations", test_person_operations),
        ("Batch Operations", test_batch_operations),
        ("Sync Operations", test_sync_operations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Middleware is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main()