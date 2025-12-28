# 🚀 Hydepark Lyve Middleware MVP - Deployment Guide

## Overview
This guide will help you deploy the **Hydepark Lyve Middleware MVP** that bridges **Lyve Access Control** with **HikCentral Professional** using FastAPI, PostgreSQL, and Redis.

## 🎯 MVP Features

### API Endpoints
- ✅ **POST /api/v1/residents/check** - Check resident existence
- ✅ **POST /api/v1/residents/create** - Create new resident  
- ✅ **DELETE /api/v1/residents/** - Delete resident
- ✅ **POST /api/v1/qrcodes/resident** - Generate QR code

### Technical Stack
- **FastAPI** - Modern async web framework
- **PostgreSQL** - Primary database with async support
- **Redis** - Circuit breaker and caching
- **Async SQLAlchemy** - High-performance ORM
- **aiohttp** - Async HTTP client for HikCentral
- **HMAC-SHA256** - HikCentral authentication
- **Circuit Breaker** - 5 failures = 60s open protection

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
- **Python** 3.11+ (for manual setup)
- **PostgreSQL** 15+ (if external)
- **Redis** 7+ (if external)

## 🚀 Quick Deployment (Docker)

### 1. Install Docker & Docker Compose
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository
```bash
git clone https://github.com/pokerist/hyde-lyve-middleware.git
cd hyde-lyve-middleware
```

### 3. Configure Environment
```bash
# Copy environment template
cp .env .env.production

# Edit with your HikCentral settings
nano .env.production
```

**Critical Settings to Update:**
```env
# HikCentral Configuration (REQUIRED!)
HIKCENTRAL_BASE_URL=https://your-hikcentral-server-ip/artemis
HIKCENTRAL_APP_KEY=your-actual-app-key
HIKCENTRAL_APP_SECRET=your-actual-app-secret
HIKCENTRAL_USER_ID=your-actual-user-id

# Security (CHANGE FROM DEFAULT!)
API_KEY=your-secure-api-key-here
REQUIRE_API_KEY=True

# Database (if external)
DATABASE_URL=postgresql+asyncpg://user:password@your-db-server/hyde_lyve
REDIS_URL=redis://your-redis-server:6379/0
```

### 4. Deploy with Docker Compose
```bash
# Make setup script executable
chmod +x setup_mvp.sh

# Run automated setup
./setup_mvp.sh

# Or manual deployment
docker-compose up -d
```

### 5. Verify Deployment
```bash
# Check service status
docker-compose ps

# Test health endpoint
curl -X GET http://localhost:3000/health

# Run comprehensive tests
python test_mvp.py
```

## 🔧 Manual Deployment (Advanced)

### 1. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb hyde_lyve
sudo -u postgres psql -c "CREATE USER hydeuser WITH PASSWORD 'your-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hyde_lyve TO hydeuser;"
```

### 2. Install Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 3. Install Python & Dependencies
```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_new.txt
```

### 4. Configure Application
```bash
# Copy environment file
cp .env .env.local

# Edit configuration
nano .env.local
```

### 5. Initialize Database
```bash
# Initialize database schema
python init_db.py
```

### 6. Start Application
```bash
# Start FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 3000 --log-level info

# Or with auto-reload (development)
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

## 🔒 Security Configuration

### API Security
```env
# Change from default!
API_KEY=your-very-secure-api-key-here
REQUIRE_API_KEY=True

# Rate limiting (optional)
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
```

### SSL/TLS Configuration
```bash
# Generate SSL certificates (for production)
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Update environment
HIKCENTRAL_VERIFY_SSL=True
```

### Firewall Configuration
```bash
# Allow port 3000
sudo ufw allow 3000/tcp comment "Hydepark Lyve Middleware"

# Allow PostgreSQL (if external)
sudo ufw allow 5432/tcp comment "PostgreSQL"

# Allow Redis (if external)
sudo ufw allow 6379/tcp comment "Redis"
```

## 📊 Monitoring & Health Checks

### Health Endpoint
```bash
# Basic health check
curl -X GET http://localhost:3000/health

# Detailed health with service status
curl -X GET http://localhost:3000/health | jq
```

### Service Monitoring
```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f postgres

# View Redis logs
docker-compose logs -f redis
```

### Performance Monitoring
```bash
# Monitor resource usage
docker stats

# Check database performance
docker exec -it hyde-lyve-postgres psql -U postgres -d hyde_lyve -c "SELECT * FROM pg_stat_activity;"

# Check Redis performance
docker exec -it hyde-lyve-redis redis-cli INFO
```

## 🧪 Testing the Deployment

### 1. Health Check Test
```bash
curl -X GET http://localhost:3000/health
```

### 2. API Authentication Test
```bash
# Test without API key (should fail)
curl -X POST http://localhost:3000/api/v1/residents/check \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "community": "Test_Community"}'

# Test with API key (should succeed)
curl -X POST http://localhost:3000/api/v1/residents/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"email": "test@example.com", "community": "Test_Community"}'
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

## 🔧 Configuration Reference

### Application Settings
```env
# FastAPI Configuration
APP_NAME=Hydepark Lyve Middleware MVP
APP_VERSION=1.0.0
DEBUG=False
PORT=3000
HOST=0.0.0.0
```

### Database Settings
```env
# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/hyde_lyve

# Redis Cache
REDIS_URL=redis://host:6379/0
```

### HikCentral Settings
```env
# HikCentral API Configuration
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=True
```

### Security Settings
```env
# API Security
API_KEY=your-secure-api-key-here
REQUIRE_API_KEY=True

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
```

## 🆘 Troubleshooting

### Common Issues

#### 1. HikCentral Connection Failed
```bash
# Check network connectivity
ping your-hikcentral-server-ip

# Check SSL certificates
curl -v https://your-hikcentral-server/artemis

# Verify credentials
grep HIKCENTRAL .env
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Test database connection
docker exec -it hyde-lyve-postgres psql -U postgres -d hyde_lyve -c "SELECT 1;"
```

#### 3. Redis Connection Issues
```bash
# Check Redis status
docker-compose logs redis

# Test Redis connection
docker exec -it hyde-lyve-redis redis-cli ping
```

#### 4. Circuit Breaker Open
```bash
# Check circuit breaker logs
docker-compose logs app | grep -i "circuit"

# Wait for recovery timeout (60 seconds)
# Or restart services: docker-compose restart
```

### Performance Issues

#### High Response Times
```bash
# Check database performance
docker exec -it hyde-lyve-postgres psql -U postgres -d hyde_lyve -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"

# Check Redis memory usage
docker exec -it hyde-lyve-redis redis-cli INFO memory
```

#### Memory Issues
```bash
# Monitor container memory
docker stats --no-stream

# Check application logs for memory errors
docker-compose logs app | grep -i memory
```

## 📈 Production Considerations

### Scaling
- **Horizontal Scaling**: Multiple app instances with load balancer
- **Database Scaling**: PostgreSQL read replicas
- **Cache Scaling**: Redis cluster
- **Load Balancing**: Nginx/HAProxy

### Backup Strategy
```bash
# Database backup
docker exec -t hyde-lyve-postgres pg_dump -U postgres hyde_lyve > backup_$(date +%Y%m%d).sql

# Redis backup
docker exec -it hyde-lyve-redis redis-cli SAVE
docker cp hyde-lyve-redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

### Monitoring
- **Application Monitoring**: Prometheus + Grafana
- **Log Aggregation**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Alerting**: AlertManager or PagerDuty

## 🎉 Success!

Your **Hydepark Lyve Middleware MVP** is now deployed and ready to bridge **Lyve Access Control** with **HikCentral Professional**!

### Next Steps
1. **Configure HikCentral** with your actual server details
2. **Test Integration** with your Lyve system
3. **Set up Monitoring** for production use
4. **Configure Backups** for data protection
5. **Review Security** settings for production

### Support
- Check application logs: `docker-compose logs -f app`
- Test API endpoints: `python test_mvp.py`
- Review documentation: [README_MVP.md](README_MVP.md)
- Monitor health: `curl -X GET http://localhost:3000/health`

---

**🚀 Ready to integrate Lyve with HikCentral!**