#!/usr/bin/env python3
"""
Test script for Hydepark Lyve Middleware MVP
Tests all API endpoints with proper error handling
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:3000"
API_KEY = "demo-key"

# Test data
TEST_EMAIL = f"test.{int(time.time())}@example.com"
TEST_COMMUNITY = "HydePark_Community_001"
TEST_UNIT_ID = f"UNIT_{int(time.time())}"

async def make_request(session, method, endpoint, data=None):
    """Make HTTP request to API"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        if method == "GET":
            async with session.get(url, headers=headers) as response:
                return response.status, await response.json()
        elif method == "POST":
            async with session.post(url, headers=headers, json=data) as response:
                return response.status, await response.json()
        elif method == "PUT":
            async with session.put(url, headers=headers, json=data) as response:
                return response.status, await response.json()
        elif method == "DELETE":
            async with session.delete(url, headers=headers, json=data) as response:
                return response.status, await response.json()
    except Exception as e:
        return 500, {"error": str(e)}

async def test_health_check():
    """Test health check endpoint"""
    print("🩺 Testing health check...")
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_request(session, "GET", "/health")
        
        if status == 200:
            print(f"   ✅ Health check passed: {response.get('status')}")
            return True
        else:
            print(f"   ❌ Health check failed: {status} - {response}")
            return False

async def test_resident_check_not_found():
    """Test resident check - resident not found"""
    print("🔍 Testing resident check (not found)...")
    
    data = {
        "email": "nonexistent@example.com",
        "community": "Nonexistent_Community"
    }
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_request(session, "POST", "/api/v1/residents/check", data)
        
        if status == 404:
            print("   ✅ Resident check correctly returned 404")
            return True
        else:
            print(f"   ❌ Expected 404, got {status}: {response}")
            return False

async def test_resident_create():
    """Test resident creation"""
    print("👤 Testing resident creation...")
    
    data = {
        "name": "John Doe",
        "phone": "1234567890",
        "email": TEST_EMAIL,
        "community": TEST_COMMUNITY,
        "fromDate": datetime.now().isoformat(),
        "toDate": (datetime.now() + timedelta(days=365)).isoformat(),
        "ownerType": "Owner",
        "unitId": TEST_UNIT_ID
    }
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_request(session, "POST", "/api/v1/residents/create", data)
        
        if status == 201:
            print(f"   ✅ Resident created successfully")
            print(f"   📋 Owner ID: {response.get('ownerId')}")
            print(f"   📧 Email: {response.get('email')}")
            print(f"   🏠 Unit ID: {response.get('unitId')}")
            return response.get("ownerId")
        else:
            print(f"   ❌ Resident creation failed: {status} - {response}")
            return None

async def test_resident_check_found(owner_id):
    """Test resident check - resident found"""
    print("🔍 Testing resident check (found)...")
    
    data = {
        "email": TEST_EMAIL,
        "community": TEST_COMMUNITY
    }
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_request(session, "POST", "/api/v1/residents/check", data)
        
        if status == 200:
            print("   ✅ Resident found successfully")
            print(f"   📋 Owner ID: {response.get('ownerId')}")
            print(f"   📧 Email: {response.get('email')}")
            print(f"   🏠 Unit ID: {response.get('unitId')}")
            return True
        else:
            print(f"   ❌ Resident check failed: {status} - {response}")
            return False

async def test_resident_duplicate():
    """Test resident creation - duplicate"""
    print("🔄 Testing resident creation (duplicate)...")
    
    data = {
        "name": "John Doe Duplicate",
        "phone": "0987654321",
        "email": TEST_EMAIL,
        "community": TEST_COMMUNITY,
        "fromDate": datetime.now().isoformat(),
        "toDate": (datetime.now() + timedelta(days=365)).isoformat(),
        "ownerType": "Owner",
        "unitId": TEST_UNIT_ID + "_DUP"
    }
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_request(session, "POST", "/api/v1/residents/create", data)
        
        if status == 409:
            print("   ✅ Duplicate resident correctly returned 409")
            print(f"   📋 Existing Owner ID: {response.get('ownerId')}")
            return True
        else:
            print(f"   ❌ Expected 409, got {status}: {response}")
            return False

async def test_qr_code_generation(owner_id):
    """Test QR code generation"""
    print("📱 Testing QR code generation...")
    
    data = {
        "unitId": TEST_UNIT_ID,
        "ownerId": owner_id,
        "validityMinutes": 60
    }
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_request(session, "POST", "/api/v1/qrcodes/resident", data)
        
        if status == 200:
            print("   ✅ QR code generated successfully")
            print(f"   📱 QR Code Length: {len(response.get('qrCode', ''))} characters")
            print(f"   ⏰ Expires At: {response.get('expiresAt')}")
            return True
        else:
            print(f"   ❌ QR code generation failed: {status} - {response}")
            return False

async def test_resident_delete(owner_id):
    """Test resident deletion"""
    print("🗑️ Testing resident deletion...")
    
    data = {
        "ownerId": owner_id,
        "unitID": TEST_UNIT_ID
    }
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_request(session, "DELETE", "/api/v1/residents/", data)
        
        if status == 200:
            print("   ✅ Resident deleted successfully")
            return True
        else:
            print(f"   ❌ Resident deletion failed: {status} - {response}")
            return False

async def test_resident_delete_not_found():
    """Test resident deletion - not found"""
    print("🗑️ Testing resident deletion (not found)...")
    
    data = {
        "ownerId": "nonexistent-owner-id",
        "unitID": "nonexistent-unit-id"
    }
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_request(session, "DELETE", "/api/v1/residents/", data)
        
        if status == 404:
            print("   ✅ Non-existent resident deletion correctly returned 404")
            return True
        else:
            print(f"   ❌ Expected 404, got {status}: {response}")
            return False

async def test_invalid_requests():
    """Test various invalid request scenarios"""
    print("⚠️ Testing invalid requests...")
    
    test_cases = [
        {
            "name": "Missing email in check",
            "method": "POST",
            "endpoint": "/api/v1/residents/check",
            "data": {"community": TEST_COMMUNITY},
            "expected_status": 400
        },
        {
            "name": "Missing community in check",
            "method": "POST",
            "endpoint": "/api/v1/residents/check",
            "data": {"email": TEST_EMAIL},
            "expected_status": 400
        },
        {
            "name": "Missing required fields in create",
            "method": "POST",
            "endpoint": "/api/v1/residents/create",
            "data": {"email": "test@example.com"},
            "expected_status": 400
        },
        {
            "name": "Missing ownerId in delete",
            "method": "DELETE",
            "endpoint": "/api/v1/residents/",
            "data": {"unitID": TEST_UNIT_ID},
            "expected_status": 400
        },
        {
            "name": "Missing unitId in QR code",
            "method": "POST",
            "endpoint": "/api/v1/qrcodes/resident",
            "data": {"ownerId": "test-owner"},
            "expected_status": 400
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        all_passed = True
        for test_case in test_cases:
            print(f"   Testing: {test_case['name']}")
            status, response = await make_request(
                session, 
                test_case["method"], 
                test_case["endpoint"], 
                test_case.get("data")
            )
            
            if status == test_case["expected_status"]:
                print(f"      ✅ Correctly returned {status}")
            else:
                print(f"      ❌ Expected {test_case['expected_status']}, got {status}")
                all_passed = False
    
    return all_passed

async def test_authentication():
    """Test API key authentication"""
    print("🔐 Testing API key authentication...")
    
    # Test without API key
    async with aiohttp.ClientSession() as session:
        status, response = await session.post(
            f"{BASE_URL}/api/v1/residents/check",
            json={"email": TEST_EMAIL, "community": TEST_COMMUNITY}
        )
        
        if status == 401:
            print("   ✅ Missing API key correctly returned 401")
        else:
            print(f"   ❌ Expected 401, got {status}")
            return False
    
    # Test with invalid API key
    async with aiohttp.ClientSession() as session:
        status, response = await session.post(
            f"{BASE_URL}/api/v1/residents/check",
            json={"email": TEST_EMAIL, "community": TEST_COMMUNITY},
            headers={"X-API-Key": "invalid-key"}
        )
        
        if status == 401:
            print("   ✅ Invalid API key correctly returned 401")
            return True
        else:
            print(f"   ❌ Expected 401, got {status}")
            return False

async def main():
    """Main test function"""
    print("🚀 Hydepark Lyve Middleware - MVP Test Suite")
    print("=" * 60)
    
    test_results = []
    owner_id = None
    
    try:
        # Basic tests
        test_results.append(await test_health_check())
        test_results.append(await test_resident_check_not_found())
        
        # Create resident
        owner_id = await test_resident_create()
        if owner_id:
            test_results.append(True)
            
            # Test with created resident
            test_results.append(await test_resident_check_found(owner_id))
            test_results.append(await test_resident_duplicate())
            test_results.append(await test_qr_code_generation(owner_id))
            
            # Delete resident
            test_results.append(await test_resident_delete(owner_id))
        else:
            test_results.append(False)
        
        # Additional tests
        test_results.append(await test_resident_delete_not_found())
        test_results.append(await test_invalid_requests())
        test_results.append(await test_authentication())
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        test_results.append(False)
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The middleware is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)