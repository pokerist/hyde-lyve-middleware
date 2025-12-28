#!/bin/bash
# Hydepark Lyve Middleware MVP - Quick Setup Script

set -e

echo "🚀 Hydepark Lyve Middleware MVP - Quick Setup"
echo "=============================================="

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

# Check if Docker is installed
check_docker() {
    print_step "Checking Docker installation..."
    
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        print_status "Docker found: $DOCKER_VERSION"
        
        # Check if Docker daemon is running
        if docker info &> /dev/null; then
            print_status "Docker daemon is running"
            return 0
        else
            print_error "Docker daemon is not running. Please start Docker service."
            return 1
        fi
    else
        print_error "Docker is not installed. Please install Docker first."
        return 1
    fi
}

# Check if Docker Compose is installed
check_docker_compose() {
    print_step "Checking Docker Compose installation..."
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        print_status "Docker Compose found: $COMPOSE_VERSION"
        return 0
    else
        print_error "Docker Compose is not installed. Please install Docker Compose."
        return 1
    fi
}

# Create environment file if it doesn't exist
create_env_file() {
    print_step "Creating environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
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

# HikCentral Configuration - UPDATE THESE!
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=True

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
        
        print_warning "⚠️  Please edit .env file with your HikCentral configuration before starting!"
    else
        print_warning ".env file already exists"
    fi
}

# Pull Docker images
pull_images() {
    print_step "Pulling Docker images..."
    
    docker-compose pull
    print_status "Docker images pulled successfully"
}

# Start services
start_services() {
    print_step "Starting services..."
    
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "Services started successfully"
    else
        print_error "Failed to start services"
        return 1
    fi
}

# Test health endpoint
test_health() {
    print_step "Testing health endpoint..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:3000/health > /dev/null; then
            print_status "✅ Health check passed"
            return 0
        else
            print_status "Waiting for service to be ready... (attempt $attempt/$max_attempts)"
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    print_error "❌ Health check failed after $max_attempts attempts"
    return 1
}

# Show service status
show_status() {
    print_step "Service Status"
    echo "=============================================="
    
    docker-compose ps
    
    echo ""
    echo "🌐 Access Points:"
    echo "   Health Check: http://localhost:3000/health"
    echo "   API Docs:     http://localhost:3000/docs"
    echo "   API Endpoints: http://localhost:3000/api/v1/"
    echo ""
    echo "📋 Available API Endpoints:"
    echo "   POST /api/v1/residents/check"
    echo "   POST /api/v1/residents/create"
    echo "   DELETE /api/v1/residents/"
    echo "   POST /api/v1/qrcodes/resident"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs:     docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart:       docker-compose restart"
    echo ""
    echo "⚠️  Remember to configure your HikCentral settings in .env file!"
}

# Create test script
create_test_script() {
    print_step "Creating test script..."
    
    cat > test_deployment.sh << 'EOF'
#!/bin/bash
# Test script for Hydepark Lyve Middleware MVP

echo "🧪 Testing Hydepark Lyve Middleware MVP"
echo "======================================="

# Test health endpoint
echo "🩺 Testing health endpoint..."
if curl -s http://localhost:3000/health | jq .; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
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
fi

echo ""
echo "🎉 Basic tests completed!"
echo "For full testing, run: python test_mvp.py"
EOF
    
    chmod +x test_deployment.sh
    print_status "Test script created: ./test_deployment.sh"
}

# Main setup function
main() {
    echo "Starting Hydepark Lyve Middleware MVP setup..."
    
    check_docker || exit 1
    check_docker_compose || exit 1
    create_env_file
    create_test_script
    pull_images
    start_services || exit 1
    test_health || exit 1
    show_status
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Configure your HikCentral settings in .env file"
    echo "2. Run tests: ./test_deployment.sh"
    echo "3. Test the API: python test_mvp.py"
    echo ""
    echo "🔧 For management:"
    echo "   View logs:     docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart:       docker-compose restart"
}

# Handle script interruption
trap 'print_error "Setup interrupted"; exit 1' INT

# Run main function
main