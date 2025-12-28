# 🚀 Hydepark Lyve Middleware MVP - Final Deployment Instructions

## 🎯 Overview
Complete deployment guide for the **Hydepark Lyve Middleware MVP** that bridges **Lyve Access Control** with **HikCentral Professional** using FastAPI, PostgreSQL, and Redis.

## ✅ What's Fixed

### 🔧 Database Connectivity Issues
- **Fixed database connection pooling** with proper async handling
- **Added connection testing** during startup
- **Improved error logging** for database issues
- **Added connection recovery** mechanisms

### 🔒 HikCentral Authentication
- **Updated HMAC-SHA256 signature** to match your working example
- **Fixed signature format** with proper header ordering
- **Added Content-MD5 calculation** for request bodies
- **Implemented proper x-ca-* headers** as required by HikCentral

### 📊 Enhanced Monitoring
- **Improved health check** with detailed service status
- **Better error logging** throughout the application
- **Circuit breaker monitoring** with Redis fallback
- **Request/response logging** for debugging

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 2+ cores
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 20GB+ SSD
- **Network**: Access to HikCentral server

### Software Dependencies
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** (for repository management)

## 🚀 Quick Deployment (Recommended)

### 1. Clean Up Old Deployment
```bash
# Stop any existing containers
docker-compose down 2>/dev/null || true

# Remove old containers and volumes
docker stop $(docker ps -q --filter "name=hyde-lyve" 2>/dev/null) 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=hyde-lyve" 2>/dev/null) 2>/dev/null || true
docker volume rm $(docker volume ls -q --filter "name=hyde-lyve" 2>/dev/null) 2>/dev/null || true

# Clean up old files
rm -rf hyde-lyve-middleware/
```

### 2. Clone Fresh Repository
```bash
# Clone the updated repository
git clone https://github.com/pokerist/hyde-lyve-middleware.git
cd hyde-lyve-middleware

# Make deployment script executable
chmod +x deploy_complete.sh
```

### 3. Run Complete Deployment
```bash
# Run the complete deployment script
./deploy_complete.sh
```

This script will:
- ✅ Clean up any existing deployment
- ✅ Create fresh Docker containers
- ✅ Set up PostgreSQL with proper configuration
- ✅ Configure Redis for circuit breaker
- ✅ Create all application files
- ✅ Build and start the FastAPI application
- ✅ Run health checks and tests

### 4. Configure HikCentral Settings
```bash
# Edit the environment file with your HikCentral details
nano .env
```

**Update these critical settings:**
```env
# HikCentral Configuration - UPDATE THESE!
HIKCENTRAL_BASE_URL=https://your-hikcentral-server-ip/artemis
HIKCENTRAL_APP_KEY=your-actual-app-key
HIKCENTRAL_APP_SECRET=your-actual-app-secret
HIKCENTRAL_USER_ID=your-actual-user-id
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=True

# Security - CHANGE FROM DEFAULT!
API_KEY=your-secure-api-key-here
```

### 5. Start Services
```bash
# Start all services
./manage.sh start

# Check status
./manage.sh status

# View logs
./manage.sh logs
```

### 6. Test Deployment
```bash
# Run comprehensive tests
./test_deployment.sh

# Or use the management script
./manage.sh test
```

## 🔧 Manual Deployment (Alternative)

### 1. Create Project Structure
```bash
mkdir hyde-lyve-middleware && cd hyde-lyve-middleware
mkdir -p app logs
```

### 2. Create All Files
Copy all the files from the deployment script:
- `docker-compose.yml`
- `Dockerfile`
- `requirements.txt`
- `app/main.py`
- `app/config.py`
- `app/models.py`
- `app/hikcentral_client.py`
- `app/resident_service.py`
- `app/circuit_breaker.py`
- `.env` (with your configuration)

### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Test deployment
curl -X GET http://localhost:3000/health
```

## 📊 Testing the Deployment

### 1. Health Check
```bash
# Basic health check
curl -X GET http://localhost:3000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### 2. API Authentication Test
```bash
# Test without API key (should fail)
curl -X POST http://localhost:3000/api/v1/residents/check \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "community": "Test_Community"}'
# Expected: 401 Unauthorized

# Test with API key (should succeed)
curl -X POST http://localhost:3000/api/v1/residents/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"email": "test@example.com", "community": "Test_Community"}'
# Expected: 404 Not Found (for non-existent resident)
```

### 3. Complete API Test
```bash
# Run comprehensive test suite
python test_mvp.py
```

### 4. Manual API Testing
```bash
# Create resident
curl -X POST http://localhost:3000/api/v1/residents/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
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

# Generate QR code
curl -X POST http://localhost:3000/api/v1/qrcodes/resident \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "unitId": "UNIT_001",
    "ownerId": "generated-owner-id",
    "validityMinutes": 60
  }'
```

## 🆘 Troubleshooting

### Database Issues
```bash
# Check database logs
docker-compose logs postgres

# Test database connection
docker exec -it hyde-lyve-postgres psql -U postgres -d hyde_lyve -c "SELECT 1;"

# Check database tables
docker exec -it hyde-lyve-postgres psql -U postgres -d hyde_lyve -c "\dt"
```

### Redis Issues
```bash
# Check Redis logs
docker-compose logs redis

# Test Redis connection
docker exec -it hyde-lyve-redis redis-cli ping

# Check Redis memory usage
docker exec -it hyde-lyve-redis redis-cli INFO memory
```

### Application Issues
```bash
# Check application logs
docker-compose logs app

# Check service status
docker-compose ps

# Restart services
./manage.sh restart
```

### HikCentral Connection Issues
```bash
# Check HikCentral connectivity
curl -v https://your-hikcentral-server/artemis

# Check application logs for HikCentral errors
docker-compose logs app | grep -i "hikcentral"

# Test with debug logging
# Set DEBUG=True in .env and restart
```

### Circuit Breaker Issues
```bash
# Check circuit breaker logs
docker-compose logs app | grep -i "circuit"

# Check Redis circuit breaker keys
docker exec -it hyde-lyve-redis redis-cli KEYS "circuit_breaker:*"
```

## 🔒 Security Configuration

### Production Security Checklist
- [ ] **Change API key** from default "demo-key"
- [ ] **Enable SSL/TLS** for production
- [ ] **Configure firewall** rules
- [ ] **Set up monitoring** and alerting
- [ ] **Configure log rotation**
- [ ] **Set up backups**

### Environment Variables
```env
# Production settings
DEBUG=False
HIKCENTRAL_VERIFY_SSL=True
REQUIRE_API_KEY=True

# Change these from defaults!
API_KEY=your-very-secure-api-key-here
HIKCENTRAL_APP_KEY=your-actual-app-key
HIKCENTRAL_APP_SECRET=your-actual-app-secret
```

## 📈 Monitoring & Maintenance

### Health Monitoring
```bash
# Set up health check monitoring
# Add to crontab for regular health checks
*/5 * * * * curl -f http://localhost:3000/health || echo "Service down" | mail -s "Alert" admin@yourcompany.com
```

### Log Management
```bash
# View logs
docker-compose logs -f app

# Rotate logs
docker-compose logs --tail=1000 app > app.log.$(date +%Y%m%d)
docker-compose logs --tail=0 app
```

### Backup Strategy
```bash
# Database backup
docker exec -t hyde-lyve-postgres pg_dump -U postgres hyde_lyve > backup_$(date +%Y%m%d_%H%M%S).sql

# Redis backup
docker exec -it hyde-lyve-redis redis-cli SAVE
docker cp hyde-lyve-redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

## 🎉 Deployment Complete!

Your **Hydepark Lyve Middleware MVP** is now deployed with:

✅ **Fixed database connectivity** issues
✅ **Updated HikCentral authentication** matching your working example
✅ **Enhanced error handling** and logging
✅ **Complete Docker deployment** with health checks
✅ **Comprehensive testing** suite
✅ **Production-ready** configuration

**Next Steps:**
1. **Configure HikCentral** with your actual server details
2. **Test with Lyve** system integration
3. **Set up monitoring** for production use
4. **Configure backups** for data protection

**Access Points:**
- **Health Check**: `http://your-server:3000/health`
- **API Documentation**: `http://your-server:3000/docs`
- **API Endpoints**: `http://your-server:3000/api/v1/`

**Ready to bridge Lyve Access Control with HikCentral Professional!** 🚀