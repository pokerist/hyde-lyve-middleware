# Hydepark Lyve Middleware - API Documentation

## Base URL
`http://localhost:5000`

## Authentication
Currently, no authentication is required for the middleware API. All requests from Lyve application are trusted.

## API Endpoints

### 1. Health Check
Check if the middleware service is running and healthy.

**Request:**
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-12-27T20:17:29.812596"
}
```

**Status Codes:**
- `200`: Service is healthy

---

### 2. Check Person Existence
Check if a person exists in the local database and get their HikCentral mapping.

**Request:**
```http
POST /api/person/check
Content-Type: application/json

{
    "personId": "lyve_person_123"
}
```

**Response - Person Found:**
```json
{
    "exists": true,
    "hikcentralId": "hikcentral_456",
    "personData": {
        "name": "John Doe",
        "phone": "1234567890",
        "email": "john@example.com",
        "createdAt": "2024-01-01T00:00:00",
        "updatedAt": "2024-01-01T00:00:00"
    }
}
```

**Response - Person Not Found:**
```json
{
    "exists": false,
    "message": "Person not found in local database"
}
```

**Status Codes:**
- `200`: Request successful
- `400`: Bad request - Missing personId
- `500`: Internal server error

---

### 3. Create Person
Create a new person in HikCentral and store the mapping in the local database.

**Request:**
```http
POST /api/person/create
Content-Type: application/json

{
    "personId": "lyve_person_123",
    "name": "John Doe",
    "phone": "1234567890",
    "email": "john@example.com",
    "gender": 1,
    "beginTime": "2024-01-01T00:00:00",
    "endTime": "2030-01-01T00:00:00"
}
```

**Response - Success:**
```json
{
    "success": true,
    "hikcentralId": "hikcentral_456",
    "message": "Person created successfully"
}
```

**Response - Person Already Exists:**
```json
{
    "error": "Person already exists",
    "hikcentralId": "hikcentral_456"
}
```

**Response - Creation Failed:**
```json
{
    "error": "Failed to create person",
    "message": "Error message from HikCentral"
}
```

**Status Codes:**
- `201`: Person created successfully
- `400`: Bad request - Missing required fields
- `409`: Conflict - Person already exists
- `500`: Internal server error

**Field Descriptions:**
- `personId` (required): Unique Lyve person identifier
- `name` (required): Person's full name
- `phone` (optional): Phone number
- `email` (optional): Email address
- `gender` (optional): 1 for Male, 2 for Female (default: 1)
- `beginTime` (optional): Validity start time (default: current time)
- `endTime` (optional): Validity end time (default: 2030-12-31)

---

### 4. Update Person
Update an existing person's information in both HikCentral and local database.

**Request:**
```http
PUT /api/person/update
Content-Type: application/json

{
    "personId": "lyve_person_123",
    "name": "John Updated Doe",
    "phone": "0987654321",
    "email": "john.updated@example.com"
}
```

**Response - Success:**
```json
{
    "success": true,
    "message": "Person updated successfully"
}
```

**Response - Person Not Found:**
```json
{
    "error": "Person not found"
}
```

**Response - Update Failed:**
```json
{
    "error": "Failed to update person",
    "message": "Error message from HikCentral"
}
```

**Status Codes:**
- `200`: Update successful
- `400`: Bad request - Missing required fields
- `404`: Not found - Person doesn't exist
- `500`: Internal server error

---

### 5. Delete Person
Delete a person from both HikCentral and local database.

**Request:**
```http
DELETE /api/person/delete
Content-Type: application/json

{
    "personId": "lyve_person_123"
}
```

**Response - Success:**
```json
{
    "success": true,
    "message": "Person deleted successfully"
}
```

**Response - Person Not Found:**
```json
{
    "error": "Person not found"
}
```

**Response - Deletion Failed:**
```json
{
    "error": "Failed to delete person",
    "message": "Error message from HikCentral"
}
```

**Status Codes:**
- `200`: Deletion successful
- `400`: Bad request - Missing personId
- `404`: Not found - Person doesn't exist
- `500`: Internal server error

## Integration Flow

### Typical Person Creation Flow
1. **Check Existence**: Lyve calls `/api/person/check` to see if person exists
2. **Create if Not Found**: If person doesn't exist, Lyve calls `/api/person/create`
3. **Use HikCentral ID**: Use the returned `hikcentralId` for subsequent HikCentral operations

### Typical Person Update Flow
1. **Check Existence**: Lyve calls `/api/person/check` to verify person exists
2. **Update**: If person exists, Lyve calls `/api/person/update` with new data

### Typical Person Deletion Flow
1. **Check Existence**: Lyve calls `/api/person/check` to verify person exists
2. **Delete**: If person exists, Lyve calls `/api/person/delete`

## Error Handling

All endpoints return consistent error responses:

```json
{
    "error": "Error description",
    "message": "Detailed error message (optional)"
}
```

Common error scenarios:
- **Missing Required Fields**: Returns 400 with field validation errors
- **Person Not Found**: Returns 404 for operations on non-existent persons
- **Person Already Exists**: Returns 409 when trying to create duplicate persons
- **HikCentral Errors**: Returns 500 with HikCentral error details
- **Database Errors**: Returns 500 with database error details

## Data Mapping

### Lyve to HikCentral Field Mapping

| Lyve Field | HikCentral Field | Notes |
|------------|------------------|-------|
| `personId` | `personCode` | Prefixed with "LYVE_" and timestamp |
| `name` | `personFamilyName` | Full name used |
| `phone` | `phoneNo` | Direct mapping |
| `email` | `email` | Direct mapping |
| `gender` | `gender` | 1=Male, 2=Female |
| `beginTime` | `beginTime` | ISO format datetime |
| `endTime` | `endTime` | ISO format datetime |

### Local Database Schema

**PersonMapping Table:**
- `lyve_person_id`: Unique Lyve identifier
- `hikcentral_person_id`: Corresponding HikCentral identifier
- `name`: Person's full name
- `phone`: Phone number
- `email`: Email address
- `gender`: Gender code
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `org_index_code`: Organization index
- `begin_time`: Validity start time
- `end_time`: Validity end time
- `is_active`: Active status flag

## Configuration

The middleware can be configured via environment variables or `.env` file:

```env
# HikCentral Configuration
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=False

# Middleware Configuration
DEBUG=True
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///hydepark_lyve.db
```

## Testing

Use the provided test scripts:
- `simple_test.py`: Basic functionality test
- `test_middleware.py`: Comprehensive test suite

Example test command:
```bash
python simple_test.py
```

## Support

For issues or questions:
1. Check the logs in `logs/hydepark_lyve.log`
2. Verify HikCentral connectivity and credentials
3. Ensure all required fields are provided in requests
4. Check database permissions and disk space