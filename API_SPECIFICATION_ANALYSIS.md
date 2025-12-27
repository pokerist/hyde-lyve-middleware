# API Specification Analysis Template

## HikCentral Professional OpenAPI Requirements

### 1. Person Management APIs
Please provide the specific details from HikCentral Professional OpenAPI_Developer Guide_V3.0.1.pdf:

#### Person Creation Endpoint
- **Endpoint**: `POST /artemis/api/resource/v1/person/single/add`
- **Required Fields** (from PDF):
  - [ ] List all required fields
  - [ ] Field data types and formats
  - [ ] Validation rules
  - [ ] Default values

#### Person Update Endpoint  
- **Endpoint**: `PUT /artemis/api/resource/v1/person/single/update`
- **Required Fields** (from PDF):
  - [ ] List all required fields
  - [ ] Which fields are mandatory vs optional
  - [ ] Update validation rules

#### Person Query/Delete Endpoints
- **Query**: `POST /artemis/api/resource/v1/person/condition`
- **Delete**: `POST /artemis/api/resource/v1/person/single/delete`
- **Required parameters**:
  - [ ] Person identifier field name
  - [ ] Query parameters supported

#### Face Data Requirements
- **Face Data Structure**:
  - [ ] Required face image format (JPG, PNG, etc.)
  - [ ] Image size requirements
  - [ ] Base64 encoding specifications
  - [ ] Multiple face support details

#### Organization Structure
- **orgIndexCode details**:
  - [ ] Valid organization codes
  - [ ] Hierarchy structure
  - [ ] Default values

### 2. Authentication Specifications
- **HMAC Details**:
  - [ ] Exact signature format requirements
  - [ ] Header ordering requirements
  - [ ] Timestamp validity period
  - [ ] Nonce uniqueness requirements

## Lyve Access Control APIs Requirements

### 1. Person Management APIs
Please provide details from Lyve Access Control APIs.pdf:

#### Authentication Method
- **Type**: (API Key, OAuth, JWT, etc.)
- **Headers required**:
- **Token/credential format**:

#### Person Data Structure
- **Person Creation**:
  - [ ] Required fields from Lyve
  - [ ] Field naming conventions
  - [ ] Data format requirements
  - [ ] Validation rules

- **Person Update**:
  - [ ] Updateable fields
  - [ ] Partial update support
  - [ ] Required vs optional fields

#### Field Mapping Requirements
- **Lyve → Middleware → HikCentral**:
  - [ ] Exact field name mappings
  - [ ] Data transformation rules
  - [ ] Default value assignments
  - [ ] Validation requirements

#### Error Response Format
- **Lyve Error Codes**:
  - [ ] HTTP status codes used
  - [ ] Error message format
  - [ ] Error code structure

## Current Implementation vs PDF Requirements

### Comparison Checklist

#### ✅ Currently Implemented (Working):
- [x] Basic person CRUD operations
- [x] HikCentral HMAC authentication
- [x] Local SQLite database mapping
- [x] RESTful API endpoints
- [x] Basic error handling
- [x] Logging system

#### ❓ Need PDF Verification:
- [ ] Exact HikCentral field requirements
- [ ] Lyve authentication method
- [ ] Face data handling specifications
- [ ] Organization code validation
- [ ] Specific error response formats
- [ ] Additional API endpoints needed
- [ ] Data transformation rules
- [ ] Rate limiting requirements

#### 🔧 Potential Updates Needed:
- [ ] Face image upload support
- [ ] Batch operations
- [ ] Advanced validation rules
- [ ] Additional authentication layers
- [ ] Real-time synchronization
- [ ] Audit trail enhancements

## Action Items

Please provide the following information from the PDFs:

1. **HikCentral Person API**: Exact required fields and validation rules
2. **Lyve Authentication**: How Lyve authenticates with the middleware
3. **Face Data Requirements**: Image format, size, and encoding specifications
4. **Field Mapping**: Any specific transformation rules between systems
5. **Error Handling**: Required error response formats for both systems
6. **Additional Endpoints**: Any APIs not currently implemented

Once you provide these details, I can update the middleware to match the exact specifications from both PDF documents.