#!/usr/bin/env python3
"""
PDF API Specification Extractor Helper
This script helps you systematically extract key information from the PDF documents.
"""

import json

def create_extraction_template():
    """Create a template for extracting API specifications from PDFs"""
    
    template = {
        "hikcentral_api": {
            "document": "HikCentral Professional OpenAPI_Developer Guide_V3.0.1.pdf",
            "person_endpoints": {
                "create_person": {
                    "endpoint": "POST /artemis/api/resource/v1/person/single/add",
                    "required_fields": [],
                    "optional_fields": [],
                    "field_types": {},
                    "validation_rules": {},
                    "example_request": {}
                },
                "update_person": {
                    "endpoint": "PUT /artemis/api/resource/v1/person/single/update", 
                    "required_fields": [],
                    "optional_fields": [],
                    "field_types": {},
                    "validation_rules": {},
                    "example_request": {}
                },
                "delete_person": {
                    "endpoint": "POST /artemis/api/resource/v1/person/single/delete",
                    "required_fields": [],
                    "example_request": {}
                },
                "get_person": {
                    "endpoint": "POST /artemis/api/resource/v1/person/condition",
                    "required_fields": [],
                    "example_request": {}
                }
            },
            "face_data": {
                "image_format": "",
                "max_size": "",
                "encoding": "base64",
                "multiple_faces": False,
                "face_data_structure": {}
            },
            "authentication": {
                "method": "HMAC-SHA256",
                "required_headers": ["X-Ca-Key", "X-Ca-Nonce", "X-Ca-Timestamp", "X-Ca-Signature"],
                "signature_format": "",
                "timestamp_validity": "",
                "nonce_requirements": ""
            },
            "organization": {
                "orgIndexCode_valid_values": [],
                "default_orgIndexCode": "1",
                "hierarchy_structure": {}
            }
        },
        "lyve_api": {
            "document": "Lyve Access Control APIs.pdf",
            "authentication": {
                "method": "",
                "credentials_format": "",
                "required_headers": [],
                "token_lifetime": ""
            },
            "person_endpoints": {
                "create_person": {
                    "required_fields": [],
                    "field_mappings": {},
                    "data_formats": {},
                    "validation_rules": {}
                },
                "update_person": {
                    "updateable_fields": [],
                    "partial_update": True,
                    "validation_rules": {}
                },
                "delete_person": {
                    "identifier_field": "",
                    "soft_delete": False
                }
            },
            "error_handling": {
                "status_codes": {},
                "error_format": {},
                "retry_logic": {}
            }
        },
        "integration_requirements": {
            "field_transformations": {},
            "data_validation": {},
            "sync_frequency": "",
            "conflict_resolution": "",
            "audit_requirements": {}
        }
    }
    
    return template

def print_extraction_guide():
    """Print a guide for extracting information from PDFs"""
    
    guide = """
📋 PDF API SPECIFICATION EXTRACTION GUIDE
==========================================

🎯 OBJECTIVE: Extract key API specifications from both PDF documents

📁 DOCUMENTS TO ANALYZE:
1. HikCentral Professional OpenAPI_Developer Guide_V3.0.1.pdf
2. Lyve Access Control APIs.pdf

🔍 EXTRACTION CHECKLIST:

## HikCentral Professional OpenAPI (Document 1)

### 1. Person Management APIs
□ Find the person creation endpoint (likely POST /person/single/add)
□ List ALL required fields (not just the ones we currently have)
□ List optional fields with their default values
□ Note field data types (string, integer, boolean, datetime)
□ Identify validation rules (max length, format requirements)
□ Find example request/response payloads

### 2. Face Data Requirements  
□ Image format requirements (JPG, PNG, BMP?)
□ Maximum image size (in bytes or pixels)
□ Base64 encoding specifications
□ Multiple face support details
□ Face quality requirements (if any)

### 3. Authentication Specifications
□ HMAC signature generation steps
□ Header ordering requirements
□ Timestamp validity period (in seconds)
□ Nonce uniqueness requirements
□ Signature format details

### 4. Organization Structure
□ Valid orgIndexCode values
□ Organization hierarchy details
□ Default organization settings

## Lyve Access Control APIs (Document 2)

### 1. Authentication Method
□ How does Lyve authenticate? (API Key, OAuth, JWT?)
□ Required headers or tokens
□ Credential format and lifetime
□ Token refresh mechanisms

### 2. Person Data Structure
□ Required fields for person creation
□ Field naming conventions (camelCase, snake_case?)
□ Data format requirements (dates, phone numbers)
□ Validation rules specific to Lyve

### 3. API Endpoints
□ Person creation endpoint details
□ Update operations (partial vs full updates)
□ Delete operations (soft vs hard delete)
□ Any additional endpoints not in our current implementation

### 4. Error Handling
□ HTTP status codes used by Lyve
□ Error response format
□ Error code meanings
□ Retry logic recommendations

## Integration Requirements

### 1. Field Mapping Rules
□ Exact field transformations needed
□ Data type conversions required
□ Default value assignments
□ Validation rule translations

### 2. Synchronization Requirements
□ Real-time vs batch processing needs
□ Conflict resolution strategies
□ Data consistency requirements
□ Audit trail specifications

📝 OUTPUT FORMAT:
Please fill in the template above with the exact specifications from the PDFs.
Use the provided JSON structure or provide the information in any format you prefer.

⚠️ CRITICAL AREAS TO VERIFY:
1. Are we missing any REQUIRED fields in HikCentral?
2. Does Lyve require authentication for the middleware?
3. What are the exact face data requirements?
4. Are there any field name differences between the systems?
5. What are the specific validation rules for each system?

Once you provide this information, I can update the middleware to match the exact specifications.
"""
    
    print(guide)

if __name__ == "__main__":
    print("🚀 PDF API Specification Extractor Helper")
    print("=" * 50)
    
    # Create extraction template
    template = create_extraction_template()
    
    print("\n📋 EXTRACTION TEMPLATE:")
    print(json.dumps(template, indent=2))
    
    print("\n" + "=" * 50)
    print_extraction_guide()
    
    print("\n💡 TIP: You can also just provide the key information")
    print("   in plain text - whatever is easiest for you!")