# Hydepark Lyve Middleware - Enhanced API Documentation

## 🚀 What's New in v2.0

### ✨ Enhanced Features
- **Face Data Support**: Upload and validate face images for HikCentral
- **Batch Operations**: Create multiple persons in a single request
- **Advanced Search**: Search persons with multiple criteria
- **API Authentication**: Secure API key authentication
- **Face Validation**: Real-time face image quality validation
- **Comprehensive Logging**: Detailed API call logging with performance metrics
- **Configuration Management**: Runtime configuration endpoints

### 🔧 New API Endpoints

#### 1. Face Validation
```http
POST /api/face/validate
```
Validate face image data before person creation.

#### 2. Batch Person Creation
```http
POST /api/person/batch/create
```
Create up to 100 persons in a single request.

#### 3. Person Search
```http
POST /api/person/search
```
Search persons with multiple criteria and pagination.

#### 4. Person Face Data
```http
GET /api/person/{personId}/faces
```
Get face data associated with a person.

#### 5. Person Sync
```http
POST /api/person/sync/{hikcentralPersonId}
```
Sync person data from HikCentral to local database.

#### 6. Configuration
```http
GET /api/config
```
Get current system configuration settings.

## 📋 Updated API Reference

### Authentication
All API endpoints now require authentication via `X-API-Key` header:

```http
X-API-Key: your-api-key-here
```

Default API key: `demo-key` (change in production)

### Face Data Support

#### Face Image Requirements
- **Supported Formats**: JPEG, JPG, PNG, BMP
- **Maximum Size**: 2MB per image
- **Recommended Dimensions**: 800x600 pixels
- **Minimum Face Size**: 100x100 pixels
- **Maximum Faces**: 5 per person

#### Face Data Structure
```json
{
  "faceData": "base64_encoded_image",
  "faceType": 1,
  "name": "face_1234567890",
  "bornTime": "2024-01-01T00:00:00",
  "sex": 1,
  "certificateType": 111,
  "certificateNum": "",
  "faceQuality": 80
}
```

### Enhanced Person Data

#### Person Creation with Face Images
```http
POST /api/person/create
Content-Type: application/json
X-API-Key: demo-key

{
    "personId": "lyve_person_123",
    "name": "John Doe",
    "givenName": "John",
    "phone": "1234567890",
    "email": "john@example.com",
    "gender": 1,
    "faceImages": [
        "base64_encoded_face_image_1",
        "base64_encoded_face_image_2"
    ],
    "certificateType": 111,
    "certificateNum": "123456789012345",
    "personType": 1,
    "beginTime": "2024-01-01T00:00:00",
    "endTime": "2030-01-01T00:00:00"
}
```

#### Response
```json
{
    "success": true,
    "hikcentralId": "hikcentral_456",
    "message": "Person created successfully",
    "faceCount": 2
}
```

### Batch Operations

#### Batch Person Creation
```http
POST /api/person/batch/create
Content-Type: application/json
X-API-Key: demo-key

{
    "persons": [
        {
            "personId": "lyve_person_1",
            "name": "Person 1",
            "phone": "1111111111",
            "email": "person1@example.com",
            "gender": 1,
            "faceImages": ["base64_face_image"]
        },
        {
            "personId": "lyve_person_2",
            "name": "Person 2",
            "phone": "2222222222",
            "email": "person2@example.com",
            "gender": 2,
            "faceImages": ["base64_face_image"]
        }
    ]
}
```

#### Response
```json
{
    "success": true,
    "total": 2,
    "successCount": 2,
    "errorCount": 0,
    "results": [
        {
            "index": 0,
            "personId": "lyve_person_1",
            "success": true,
            "message": "Person created successfully",
            "hikcentral_id": "hikcentral_789"
        },
        {
            "index": 1,
            "personId": "lyve_person_2",
            "success": true,
            "message": "Person created successfully",
            "hikcentral_id": "hikcentral_790"
        }
    ]
}
```

### Advanced Search

#### Person Search
```http
POST /api/person/search
Content-Type: application/json
X-API-Key: demo-key

{
    "name": "John",
    "phone": "123",
    "email": "john@",
    "gender": 1,
    "orgIndexCode": "1",
    "limit": 50,
    "offset": 0
}
```

#### Response
```json
{
    "success": true,
    "total": 15,
    "count": 2,
    "limit": 50,
    "offset": 0,
    "persons": [
        {
            "id": 1,
            "lyve_person_id": "lyve_person_123",
            "hikcentral_person_id": "hikcentral_456",
            "name": "John Doe",
            "given_name": "John",
            "phone": "1234567890",
            "email": "john@example.com",
            "gender": 1,
            "certificate_type": 111,
            "certificate_num": "123456789012345",
            "person_type": 1,
            "face_count": 2,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "org_index_code": "1",
            "begin_time": "2024-01-01T00:00:00",
            "end_time": "2030-01-01T00:00:00",
            "is_active": true
        }
    ]
}
```

### Face Validation

#### Validate Face Image
```http
POST /api/face/validate
Content-Type: application/json
X-API-Key: demo-key

{
    "faceImage": "base64_encoded_face_image"
}
```

#### Response
```json
{
    "success": true,
    "valid": true,
    "qualityScore": 85,
    "faceInfo": {
        "size_chars": 24576,
        "format": "JPEG",
        "dimensions": "800x600",
        "mode": "RGB",
        "quality_score": 85
    },
    "message": "Face image is valid"
}
```

## ⚙️ Configuration

### Environment Variables

#### Authentication
```bash
LYVE_API_KEY=your-secure-api-key
REQUIRE_API_KEY=True
```

#### Face Data Settings
```bash
MAX_FACE_IMAGES=5
FACE_IMAGE_MAX_SIZE=2097152
FACE_IMAGE_QUALITY_THRESHOLD=70
```

#### Batch Operations
```bash
MAX_BATCH_SIZE=100
BATCH_TIMEOUT=300
```

#### Performance & Security
```bash
MAX_CONTENT_LENGTH=16777216
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
ENABLE_CACHING=True
CACHE_TTL=300
```

### Configuration Endpoint

#### Get Current Settings
```http
GET /api/config
X-API-Key: demo-key
```

## 🔒 Security Features

### API Security
- **API Key Authentication**: All endpoints require valid API key
- **Rate Limiting**: Configurable request rate limits
- **Input Validation**: Comprehensive data validation
- **Error Sanitization**: No sensitive data in error messages

### Data Security
- **Base64 Encoding**: Face images are base64 encoded
- **Size Limits**: Maximum file size restrictions
- **Format Validation**: Only supported image formats
- **Quality Control**: Face image quality validation

## 📊 Error Handling

### Error Response Format
```json
{
    "error": "Error description",
    "message": "Detailed error information"
}
```

### Common Error Codes
- `400`: Bad Request - Invalid data format
- `401`: Unauthorized - Invalid or missing API key
- `404`: Not Found - Resource not found
- `409`: Conflict - Resource already exists
- `413`: Payload Too Large - Request exceeds size limits
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error

## 🧪 Testing

### Enhanced Test Script
```bash
python enhanced_test.py
```

### Test Coverage
- ✅ Health check and configuration
- ✅ Face image validation
- ✅ Person CRUD operations with face data
- ✅ Batch person creation
- ✅ Person search functionality
- ✅ API authentication
- ✅ Error handling

## 🚀 Deployment

### Production Checklist
1. **Change API Key**: Update `LYVE_API_KEY` from default
2. **Enable SSL**: Set `HIKCENTRAL_VERIFY_SSL=True`
3. **Configure Rate Limiting**: Enable `RATE_LIMIT_ENABLED`
4. **Set Production Logging**: Change `LOG_LEVEL=WARNING`
5. **Enable Caching**: Set `ENABLE_CACHING=True`
6. **Update HikCentral Credentials**: Use real API credentials
7. **Database Backup**: Set up regular database backups

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 📞 Support

### Troubleshooting
1. **Check Logs**: Review `logs/hydepark_lyve.log`
2. **Verify API Key**: Ensure correct `X-API-Key` header
3. **Validate Face Images**: Use `/api/face/validate` endpoint
4. **Test Connectivity**: Check HikCentral server connectivity
5. **Review Configuration**: Use `/api/config` endpoint

### Performance Optimization
- Enable caching for frequently accessed data
- Use batch operations for multiple person creation
- Implement proper database indexing
- Monitor API response times
- Set appropriate rate limits

---

**🎉 The enhanced Hydepark Lyve Middleware is now ready for production use with comprehensive face data support, batch operations, and advanced security features!**