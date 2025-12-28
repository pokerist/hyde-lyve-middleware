# 🚀 Hydepark Lyve Middleware - MVP Version

A production-ready FastAPI middleware that seamlessly integrates **Lyve Access Control** with **HikCentral Professional**, following exact MVP specifications.

## ✨ MVP Features

### 🔧 Core API Endpoints
- **POST /api/v1/residents/check** - Check resident existence
- **POST /api/v1/residents/create** - Create new resident
- **DELETE /api/v1/residents/** - Delete resident
- **POST /api/v1/qrcodes/resident** - Generate QR code for resident

### 🔒 Security & Authentication
- **API Key Authentication** via `X-API-Key` header
- **HMAC-SHA256** authentication for HikCentral API
- **Circuit Breaker** pattern (5 failures = 60s open)
- **PostgreSQL** with async SQLAlchemy
- **Redis** for circuit breaker state management

### 🗄️ Data Management
- **PostgreSQL** database with proper indexing
- **Async SQLAlchemy** for high performance
- **Resident Mapping** between Lyve and HikCentral
- **Sync Logs** for complete audit trail
- **Name Splitting** (first/last) for HikCentral compatibility

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for manual setup)
- PostgreSQL 15+
- Redis 7+
- Access to HikCentral server

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/pokerist/hyde-lyve-middleware.git
cd hyde-lyve-middleware

# Configure environment
nano .env  # Update HikCentral settings

# Deploy with Docker Compose
docker-compose up -d

# Test the deployment
curl -X GET http://localhost:3000/health
```

### Option 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements_new.txt

# Configure environment
cp .env .env.local
nano .env.local  # Update HikCentral settings

# Initialize database
python init_db.py

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

## 📋 API Specification

### Authentication
All API endpoints require `X-API-Key` header:
```http
X-API-Key: your-api-key-here
```

### 1. Check Resident
```http
POST /api/v1/residents/check
Content-Type: application/json
X-API-Key: demo-key

{
  "email": "john.doe@example.com",
  "community": "HydePark_Community_001"
}
```

**Response - Found (200 OK):**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "community": "HydePark_Community_001",
  "hikcentral_person_id": "LYVE_12345",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "unit_id": "UNIT_001",
  "name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "1234567890",
  "owner_type": "Owner",
  "from_date": "2024-01-01T00:00:00",
  "to_date": "2025-01-01T00:00:00",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Response - Not Found (404 Not Found):**
```json
{
  "detail": "Resident not found"
}
```

### 2. Create Resident
```http
POST /api/v1/residents/create
Content-Type: application/json
X-API-Key: demo-key

{
  "name": "John Doe",
  "phone": "1234567890",
  "email": "john.doe@example.com",
  "community": "HydePark_Community_001",
  "fromDate": "2024-01-01T00:00:00",
  "toDate": "2025-01-01T00:00:00",
  "ownerType": "Owner",
  "unitId": "UNIT_001"
}
```

**Response - Created (201 Created):**
```json
{
  "success": true,
  "ownerId": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "community": "HydePark_Community_001",
  "name": "John Doe",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "1234567890",
  "ownerType": "Owner",
  "unitId": "UNIT_001",
  "fromDate": "2024-01-01T00:00:00",
  "toDate": "2025-01-01T00:00:00",
  "status_code": 201
}
```

**Response - Duplicate (409 Conflict):**
```json
{
  "detail": "Resident already exists"
}
```

### 3. Delete Resident
```http
DELETE /api/v1/residents/
Content-Type: application/json
X-API-Key: demo-key

{
  "ownerId": "550e8400-e29b-41d4-a716-446655440000",
  "unitID": "UNIT_001"
}
```

**Response - Success (200 OK):**
```json
{
  "success": true
}
```

**Response - Not Found (404 Not Found):**
```json
{
  "detail": "Resident not found"
}
```

### 4. Generate QR Code
```http
POST /api/v1/qrcodes/resident
Content-Type: application/json
X-API-Key: demo-key

{
  "unitId": "UNIT_001",
  "ownerId": "550e8400-e29b-41d4-a716-446655440000",
  "validityMinutes": 60
}
```

**Response - Success (200 OK):**
```json
{
  "qrCode": "base64_encoded_qr_code_image",
  "expiresAt": "2024-01-01T01:00:00"
}
```

**Response - Not Found (404 Not Found):**
```json
{
  "detail": "Resident not found"
}
```

## ⚙️ Configuration

### Environment Variables

```env
# Application
APP_NAME=Hydepark Lyve Middleware
APP_VERSION=1.0.0
DEBUG=False
PORT=3000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/hyde_lyve

# Redis
REDIS_URL=redis://localhost:6379/0

# HikCentral
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=True

# Security
API_KEY=your-secure-api-key-here
REQUIRE_API_KEY=True

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
```

### HikCentral Configuration

Update these critical settings in your `.env` file:

```env
HIKCENTRAL_BASE_URL=https://your-hikcentral-server-ip/artemis
HIKCENTRAL_APP_KEY=your-actual-app-key
HIKCENTRAL_APP_SECRET=your-actual-app-secret
HIKCENTRAL_USER_ID=your-actual-user-id
HIKCENTRAL_VERIFY_SSL=True
```

## 🧪 Testing

### Automated Testing
```bash
# Run comprehensive test suite
python test_mvp.py
```

### Manual Testing
```bash
# Health check
curl -X GET http://localhost:3000/health

# Check resident
curl -X POST http://localhost:3000/api/v1/residents/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"email": "test@example.com", "community": "Test_Community"}'

# Create resident
curl -X POST http://localhost:3000/api/v1/residents/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{
    "name": "John Doe",
    "phone": "1234567890",
    "email": "john.doe@example.com",
    "community": "HydePark_Community_001",
    "fromDate": "2024-01-01T00:00:00",
    "toDate": "2025-01-01T00:00:00",
    "ownerType": "Owner",
    "unitId": "UNIT_001"
  }'
```

## 🔒 Security Features

### API Security
- **API Key Authentication**: All endpoints require valid API key
- **Input Validation**: Comprehensive request validation
- **Error Sanitization**: No sensitive data in error messages
- **Rate Limiting**: Configurable request limits

### HikCentral Security
- **HMAC-SHA256**: Industry-standard authentication
- **SSL/TLS**: Encrypted communication
- **Request Signing**: All requests signed with app secret
- **Circuit Breaker**: Protection against cascading failures

### Data Protection
- **PostgreSQL**: Secure database storage
- **Redis**: Encrypted cache storage
- **Audit Logging**: Complete operation audit trail
- **Name Privacy**: Automatic name splitting for HikCentral

## 📊 Monitoring & Logging

### Health Monitoring
- **Health Endpoint**: `GET /health`
- **Database Health**: PostgreSQL connectivity
- **Redis Health**: Cache system status
- **Circuit Breaker**: Protection system status

### Logging
- **Application Logs**: Detailed operation logging
- **Sync Logs**: Complete audit trail
- **Error Logs**: Comprehensive error tracking
- **Performance Logs**: Response time monitoring

## 🔄 Circuit Breaker Pattern

The middleware implements a circuit breaker pattern:

- **Closed State**: Normal operation (5 failures allowed)
- **Open State**: Requests blocked for 60 seconds after 5 failures
- **Half-Open State**: Limited requests to test recovery

This protects against cascading failures and provides system resilience.

## 🎯 Production Deployment

### Docker Deployment (Recommended)
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With SSL termination
docker-compose -f docker-compose.ssl.yml up -d
```

### System Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 20GB+ SSD
- **Network**: Stable connection to HikCentral

### Scaling Considerations
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis cluster for high availability
- **Load Balancing**: Multiple app instances
- **SSL Termination**: Nginx/Traefik for SSL

---

**🎉 Your Hydepark Lyve Middleware MVP is ready for production deployment!**