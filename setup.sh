#!/bin/bash
# Hydepark Lyve Middleware - Quick Setup Script

set -e

echo "🚀 Hydepark Lyve Middleware - Quick Setup"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Python is installed
check_python() {
    print_step "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_status "Python version: $PYTHON_VERSION"
        
        # Check if Python version is 3.8 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_status "Python version is compatible (3.8+)"
        else
            print_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Create virtual environment
setup_virtual_env() {
    print_step "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    else
        print_warning "Virtual environment already exists"
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate || source venv/Scripts/activate
    
    print_status "Upgrading pip..."
    pip install --upgrade pip
}

# Install requirements
install_requirements() {
    print_step "Installing Python requirements..."
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing from requirements.txt..."
        pip install -r requirements.txt
        print_status "Requirements installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup configuration
setup_configuration() {
    print_step "Setting up configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.production" ]; then
            print_status "Copying production configuration..."
            cp .env.production .env
            print_warning "Please edit .env file with your HikCentral configuration"
        else
            print_warning "No .env.production found, creating basic .env file..."
            cat > .env << EOF
# Basic configuration - please update with your settings
DEBUG=True
SECRET_KEY=change-this-secret-key
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id
LYVE_API_KEY=your-api-key-here
EOF
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Setup database
setup_database() {
    print_step "Setting up database..."
    
    print_status "Creating logs directory..."
    mkdir -p logs
    
    if [ -f "recreate_database.py" ]; then
        print_status "Setting up database schema..."
        python3 recreate_database.py
        print_status "Database setup completed"
    else
        print_warning "recreate_database.py not found, database will be created automatically"
    fi
}

# Run tests
run_tests() {
    print_step "Running basic tests..."
    
    if [ -f "simple_test.py" ]; then
        print_status "Running simple tests..."
        python3 simple_test.py || print_warning "Some tests failed - check configuration"
    else
        print_warning "Test files not found"
    fi
}

# Create startup script
create_startup_script() {
    print_step "Creating startup script..."
    
    cat > start.sh << 'EOF'
#!/bin/bash
# Hydepark Lyve Middleware Startup Script

echo "🚀 Starting Hydepark Lyve Middleware..."

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Set environment variables
export FLASK_APP=app_production.py
export FLASK_ENV=production
export PORT=3000

# Start the application
echo "📖 Application will be available at: http://localhost:3000"
echo "🧪 Test UI available at: http://localhost:3000/test"
echo "📚 API Documentation available at: http://localhost:3000/api-docs"
echo ""
echo "Press Ctrl+C to stop the application"
echo "========================================="

python3 app_production.py
EOF
    
    chmod +x start.sh
    print_status "Startup script created: ./start.sh"
}

# Create systemd service (optional)
create_systemd_service() {
    print_step "Creating systemd service (optional)..."
    
    if command -v systemctl &> /dev/null; then
        read -p "Do you want to create a systemd service? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            SERVICE_NAME="hyde-lyve-middleware"
            WORKING_DIR=$(pwd)
            
            sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Hydepark Lyve Middleware
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKING_DIR
Environment="PATH=$WORKING_DIR/venv/bin"
Environment="FLASK_ENV=production"
Environment="PORT=3000"
ExecStart=$WORKING_DIR/venv/bin/python app_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
            
            sudo systemctl daemon-reload
            print_status "Systemd service created: $SERVICE_NAME"
            print_warning "To enable and start the service:"
            print_status "  sudo systemctl enable $SERVICE_NAME"
            print_status "  sudo systemctl start $SERVICE_NAME"
            print_status "  sudo systemctl status $SERVICE_NAME"
        fi
    else
        print_warning "systemctl not available, skipping systemd service creation"
    fi
}

# Main setup function
main() {
    echo "Starting setup process..."
    
    check_python
    setup_virtual_env
    install_requirements
    setup_configuration
    setup_database
    run_tests
    create_startup_script
    create_systemd_service
    
    echo ""
    echo "✅ Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit .env file with your HikCentral configuration"
    echo "2. Run: ./start.sh to start the application"
    echo "3. Test the API at: http://localhost:3000/test"
    echo "4. View documentation at: http://localhost:3000/api-docs"
    echo ""
    echo "🔧 Configuration checklist:"
    echo "- Update HIKCENTRAL_BASE_URL in .env"
    echo "- Update HIKCENTRAL_APP_KEY in .env"
    echo "- Update HIKCENTRAL_APP_SECRET in .env"
    echo "- Update HIKCENTRAL_USER_ID in .env"
    echo "- Update LYVE_API_KEY in .env"
    echo ""
    print_warning "Remember to configure your HikCentral credentials before starting!"
}

# Run main function
main