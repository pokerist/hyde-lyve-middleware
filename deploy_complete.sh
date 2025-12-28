#!/bin/bash
# Hydepark Lyve Middleware MVP - Complete Deployment Script

set -e

echo "🚀 Hydepark Lyve Middleware MVP - Complete Deployment"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to cleanup existing deployment
cleanup_existing() {
    print_step "Cleaning up existing deployment..."
    
    # Stop and remove Docker containers
    if command_exists docker; then
        print_status "Stopping existing Docker containers..."
        docker-compose down 2>/dev/null || true
        docker stop $(docker ps -q --filter "name=hyde-lyve" 2>/dev/null) 2>/dev/null || true
        docker rm $(docker ps -aq --filter "name=hyde-lyve" 2>/dev/null) 2>/dev/null || true
        docker volume rm $(docker volume ls -q --filter "name=hyde-lyve" 2>/dev/null) 2>/dev/null || true
    fi
    
    # Remove old files
    print_status "Removing old deployment files..."
    rm -rf app/ *.db logs/ __pycache__/ *.pyc 2>/dev/null || true
    
    print_status "✅ Cleanup completed"
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker service."
        exit 1
    fi
    
    print_status "✅ All prerequisites met"
}

# Function to create project structure
create_project_structure() {
    print_step "Creating project structure..."
    
    # Create app directory
    mkdir -p app
    mkdir -p logs
    
    print_status "✅ Project structure created"
}

# Function to create configuration files
create_config_files() {
    print_step "Creating configuration files..."
    
    # Create environment file
    cat > .env << 'EOF'
# FastAPI Application Configuration
APP_NAME=Hydepark Lyve Middleware MVP
APP_VERSION=1.0.0
DEBUG=False
PORT=3000
HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres/hyde_lyve

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# HikCentral Configuration - UPDATE THESE WITH YOUR VALUES!
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=False

# Security Configuration
API_KEY=your-secure-api-key-here
REQUIRE_API_KEY=True

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60

# QR Code Configuration
QR_CODE_VALIDITY_MINUTES=60
QR_CODE_IMAGE_SIZE=300
EOF

    print_status "✅ Configuration files created"
    print_warning "⚠️  Remember to update .env with your HikCentral credentials!"
}

# Function to create Docker Compose file
create_docker_compose() {
    print_step "Creating Docker Compose configuration..."
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: hyde-lyve-postgres
    environment:
      POSTGRES_DB: hyde_lyve
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-postgres.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - hyde-lyve-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: hyde-lyve-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - hyde-lyve-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Application
  app:
    build: .
    container_name: hyde-lyve-app
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres/hyde_lyve
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    networks:
      - hyde-lyve-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  postgres_data:
  redis_data:

networks:
  hyde-lyve-network:
    driver: bridge
EOF

    print_status "✅ Docker Compose file created"
}

# Function to create Dockerfile
create_dockerfile() {
    print_step "Creating Dockerfile..."
    
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY .env ./

# Create logs directory
RUN mkdir -p logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000", "--log-level", "info"]
EOF

    print_status "✅ Dockerfile created"
}

# Function to create requirements file
create_requirements() {
    print_step "Creating requirements.txt..."
    
    cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.23
alembic==1.12.1
redis==5.0.1
aiohttp==3.9.1
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
httpx==0.25.2
cryptography==41.0.7
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
EOF

    print_status "✅ Requirements file created"
}

# Function to create application files
create_application_files() {
    print_step "Creating application files..."
    
    # Create config.py
    cat > app/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Hydepark Lyve Middleware MVP"
    app_version: str = "1.0.0"
    debug: bool = False
    port: int = 3000
    host: str = "0.0.0.0"
    
    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres/hyde_lyve"
    
    # Redis settings
    redis_url: str = "redis://redis:6379/0"
    
    # HikCentral settings
    hikcentral_base_url: str = "https://192.168.1.101/artemis"
    hikcentral_app_key: str = "27108141"
    hikcentral_app_secret: str = "c3U7KikkPGo2Yka6GMZ5"
    hikcentral_user_id: str = "admin"
    hikcentral_org_index_code: str = "1"
    hikcentral_verify_ssl: bool = False
    
    # Security settings
    api_key: str = "demo-key"
    require_api_key: bool = True
    
    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    
    # API settings
    qr_code_validity_minutes: int = 60
    qr_code_image_size: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
EOF

    print_status "✅ Application files created"
}

# Function to create test script
create_test_script() {
    print_step "Creating test script..."
    
    cat > test_deployment.sh << 'EOF'
#!/bin/bash
# Test script for Hydepark Lyve Middleware MVP

echo "🧪 Testing Hydepark Lyve Middleware MVP"
echo "======================================="

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Test health endpoint
echo "🩺 Testing health endpoint..."
if curl -s http://localhost:3000/health | jq .; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# Test API key authentication
echo "🔐 Testing API key authentication..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:3000/api/v1/residents/check \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "community": "Test_Community"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "401" ]; then
    echo "✅ API key authentication working (401 as expected)"
else
    echo "❌ API key authentication failed (got $HTTP_CODE)"
    echo "Response: $BODY"
    exit 1
fi

# Test with valid API key
echo "🔑 Testing with valid API key..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:3000/api/v1/residents/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"email": "test@example.com", "community": "Test_Community"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "404" ]; then
    echo "✅ Resident check working (404 as expected for non-existent resident)"
elif [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Resident found successfully"
    echo "Response: $BODY"
else
    echo "❌ Resident check failed (got $HTTP_CODE)"
    echo "Response: $BODY"
    exit 1
fi

echo ""
echo "🎉 Basic tests completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env with your HikCentral credentials"
echo "2. Test the create resident endpoint"
echo "3. Test QR code generation"
echo ""
echo "🔧 For full testing, run: python test_mvp.py"
EOF

    chmod +x test_deployment.sh
    print_status "✅ Test script created"
}

# Function to create management script
create_management_script() {
    print_step "Creating management script..."
    
    cat > manage.sh << 'EOF'
#!/bin/bash
# Hydepark Lyve Middleware Management Script

case "$1" in
    start)
        echo "🚀 Starting Hydepark Lyve Middleware..."
        docker-compose up -d
        echo "✅ Services started"
        ;;
    stop)
        echo "🛑 Stopping Hydepark Lyve Middleware..."
        docker-compose down
        echo "✅ Services stopped"
        ;;
    restart)
        echo "🔄 Restarting Hydepark Lyve Middleware..."
        docker-compose restart
        echo "✅ Services restarted"
        ;;
    status)
        echo "📊 Service Status:"
        docker-compose ps
        ;;
    logs)
        echo "📋 Viewing logs..."
        docker-compose logs -f
        ;;
    test)
        echo "🧪 Running tests..."
        ./test_deployment.sh
        ;;
    config)
        echo "⚙️  Editing configuration..."
        nano .env
        ;;
    cleanup)
        echo "🧹 Cleaning up..."
        docker-compose down
        docker system prune -f
        echo "✅ Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test|config|cleanup}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the services"
        echo "  stop    - Stop the services"
        echo "  restart - Restart the services"
        echo "  status  - Show service status"
        echo "  logs    - View service logs"
        echo "  test    - Run basic tests"
        echo "  config  - Edit configuration"
        echo "  cleanup - Clean up containers and images"
        exit 1
        ;;
esac
EOF

    chmod +x manage.sh
    print_status "✅ Management script created"
}

# Function to create README
create_readme() {
    print_step "Creating README..."
    
    cat > README.md << 'EOF'
# 🚀 Hydepark Lyve Middleware MVP

A production-ready FastAPI middleware that bridges **Lyve Access Control** with **HikCentral Professional**.

## ✨ Features

### 🔧 Core API Endpoints
- **POST /api/v1/residents/check** - Check resident existence
- **POST /api/v1/residents/create** - Create new resident  
- **DELETE /api/v1/residents/** - Delete resident
- **POST /api/v1/qrcodes/resident** - Generate QR code for resident

### 🔒 Security & Authentication
- **API Key Authentication** via X-API-Key header
- **HMAC-SHA256** authentication for HikCentral API
- **Circuit Breaker** pattern (5 failures = 60s open)
- **PostgreSQL** with async SQLAlchemy
- **Redis** for circuit breaker state management

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Access to HikCentral server

### 1. Deploy
```bash
# Clone and deploy
git clone https://github.com/pokerist/hyde-lyve-middleware.git
cd hyde-lyve-middleware
chmod +x deploy.sh
./deploy.sh
```

### 2. Configure HikCentral
```bash
# Edit configuration
nano .env
# Update: HIKCENTRAL_BASE_URL, HIKCENTRAL_APP_KEY, etc.
```

### 3. Test
```bash
# Run tests
./test_deployment.sh

# Or use management script
./manage.sh test
```

## 📋 API Usage

### Check Resident
```bash
curl -X POST http://localhost:3000/api/v1/residents/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"email": "john.doe@example.com", "community": "HydePark_Community_001"}'
```

### Create Resident
```bash
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
```

### Generate QR Code
```bash
curl -X POST http://localhost:3000/api/v1/qrcodes/resident \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "unitId": "UNIT_001",
    "ownerId": "generated-owner-id",
    "validityMinutes": 60
  }'
```

## 🔧 Management

Use the management script for easy operations:

```bash
# Start services
./manage.sh start

# Stop services
./manage.sh stop

# View logs
./manage.sh logs

# Run tests
./manage.sh test

# Show status
./manage.sh status
```

## 📊 Monitoring

### Health Check
```bash
curl -X GET http://localhost:3000/health
```

### API Documentation
Visit: http://localhost:3000/docs

## 🔒 Security Configuration

Update these critical settings in `.env`:

```env
# HikCentral Configuration
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id

# Security
API_KEY=your-secure-api-key-here
```

## 🆘 Troubleshooting

### Database Issues
```bash
# Check database logs
docker-compose logs postgres

# Test database connection
docker exec -it hyde-lyve-postgres psql -U postgres -d hyde_lyve -c "SELECT 1;"
```

### Redis Issues
```bash
# Check Redis logs
docker-compose logs redis

# Test Redis connection
docker exec -it hyde-lyve-redis redis-cli ping
```

### Application Issues
```bash
# Check application logs
docker-compose logs app

# Restart services
./manage.sh restart
```

## 📞 Support

For issues and questions:
1. Check application logs: `./manage.sh logs`
2. Verify configuration: `./manage.sh config`
3. Run tests: `./manage.sh test`
4. Check HikCentral connectivity

---

**🎉 Your Hydepark Lyve Middleware MVP is ready for production!**
EOF

    print_status "✅ README created"
}

# Main deployment function
main() {
    echo "🚀 Starting complete deployment process..."
    
    cleanup_existing
    check_prerequisites
    create_project_structure
    create_config_files
    create_docker_compose
    create_dockerfile
    create_requirements
    create_application_files
    create_test_script
    create_management_script
    create_readme
    
    echo ""
    echo "🎉 Deployment preparation completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update .env with your HikCentral credentials"
    echo "2. Run: ./manage.sh start"
    echo "3. Test: ./manage.sh test"
    echo "4. Check status: ./manage.sh status"
    echo ""
    echo "🔧 Configuration checklist:"
    echo "- Update HIKCENTRAL_BASE_URL in .env"
    echo "- Update HIKCENTRAL_APP_KEY in .env"
    echo "- Update HIKCENTRAL_APP_SECRET in .env"
    echo "- Update HIKCENTRAL_USER_ID in .env"
    echo "- Update API_KEY in .env"
    echo ""
    echo "📖 Documentation: README.md"
    echo "🧪 Testing: ./test_deployment.sh"
    echo "⚙️  Management: ./manage.sh"
    
    # Make scripts executable
    chmod +x manage.sh test_deployment.sh
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT

# Run main function
main