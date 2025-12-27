#!/bin/bash
# Hydepark Lyve Middleware - Ubuntu Deployment Script

set -e

echo "🚀 Hydepark Lyve Middleware - Ubuntu Deployment"
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

# Check if running on Ubuntu
check_ubuntu() {
    print_step "Checking Ubuntu system..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" ]]; then
            print_status "Ubuntu detected: $PRETTY_NAME"
        else
            print_warning "This script is optimized for Ubuntu. Current OS: $PRETTY_NAME"
        fi
    else
        print_warning "Unable to detect OS. Proceeding anyway..."
    fi
}

# Update system packages
update_system() {
    print_step "Updating system packages..."
    
    sudo apt update
    sudo apt upgrade -y
    print_status "System packages updated"
}

# Install system dependencies
install_dependencies() {
    print_step "Installing system dependencies..."
    
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        curl \
        wget \
        git \
        sqlite3 \
        libsqlite3-dev
    
    print_status "System dependencies installed"
}

# Check Python version
check_python() {
    print_step "Checking Python version..."
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python version: $PYTHON_VERSION"
    
    # Check if Python version is 3.8 or higher
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_status "Python version is compatible (3.8+)"
    else
        print_error "Python 3.8 or higher is required"
        exit 1
    fi
}

# Create application user
create_user() {
    print_step "Creating application user..."
    
    if id "hyde-lyve" &>/dev/null; then
        print_warning "User 'hyde-lyve' already exists"
    else
        sudo useradd -m -s /bin/bash -d /opt/hyde-lyve hyde-lyve
        print_status "User 'hyde-lyve' created"
    fi
}

# Setup application directory
setup_directory() {
    print_step "Setting up application directory..."
    
    APP_DIR="/opt/hyde-lyve"
    
    # Create directory if it doesn't exist
    sudo mkdir -p $APP_DIR
    sudo chown hyde-lyve:hyde-lyve $APP_DIR
    
    print_status "Application directory: $APP_DIR"
}

# Create virtual environment
setup_virtual_env() {
    print_step "Setting up virtual environment..."
    
    APP_DIR="/opt/hyde-lyve"
    
    # Switch to application user
    sudo -u hyde-lyve bash << EOF
        cd $APP_DIR
        
        if [ ! -d "venv" ]; then
            print_status "Creating virtual environment..."
            python3 -m venv venv
        else
            print_warning "Virtual environment already exists"
        fi
        
        print_status "Activating virtual environment..."
        source venv/bin/activate
        
        print_status "Upgrading pip..."
        pip install --upgrade pip
EOF
    
    print_status "Virtual environment setup completed"
}

# Install Python requirements
install_requirements() {
    print_step "Installing Python requirements..."
    
    APP_DIR="/opt/hyde-lyve"
    
    # Copy requirements file if it exists
    if [ -f "requirements.txt" ]; then
        sudo cp requirements.txt $APP_DIR/
        sudo chown hyde-lyve:hyde-lyve $APP_DIR/requirements.txt
    fi
    
    # Install requirements as application user
    sudo -u hyde-lyve bash << EOF
        cd $APP_DIR
        source venv/bin/activate
        
        if [ -f "requirements.txt" ]; then
            print_status "Installing from requirements.txt..."
            pip install -r requirements.txt
            print_status "Requirements installed successfully"
        else
            print_warning "requirements.txt not found, installing basic packages..."
            pip install Flask Flask-SQLAlchemy requests python-dotenv
        fi
EOF
    
    print_status "Python requirements installed"
}

# Copy application files
copy_application_files() {
    print_step "Copying application files..."
    
    APP_DIR="/opt/hyde-lyve"
    CURRENT_DIR=$(pwd)
    
    # Copy all Python files and directories
    for item in *.py *.md *.txt templates static services models utils config logs; do
        if [ -e "$item" ]; then
            sudo cp -r "$item" $APP_DIR/ 2>/dev/null || true
        fi
    done
    
    # Set ownership
    sudo chown -R hyde-lyve:hyde-lyve $APP_DIR
    
    print_status "Application files copied"
}

# Setup configuration
setup_configuration() {
    print_step "Setting up configuration..."
    
    APP_DIR="/opt/hyde-lyve"
    
    # Create .env file if it doesn't exist
    sudo -u hyde-lyve bash << EOF
        cd $APP_DIR
        
        if [ ! -f ".env" ]; then
            if [ -f ".env.production" ]; then
                print_status "Copying production configuration..."
                cp .env.production .env
            else
                print_warning "Creating basic .env file..."
                cat > .env << 'ENVEOF'
# Basic configuration - please update with your settings
DEBUG=False
SECRET_KEY=change-this-secret-key-in-production
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=True
LYVE_API_KEY=your-secure-api-key-here
REQUIRE_API_KEY=True
LOG_LEVEL=INFO
ENVEOF
            fi
        else
            print_warning ".env file already exists"
        fi
EOF
    
    print_status "Configuration setup completed"
}

# Create logs directory
setup_logs() {
    print_step "Setting up logs directory..."
    
    APP_DIR="/opt/hyde-lyve"
    
    sudo -u hyde-lyve mkdir -p $APP_DIR/logs
    print_status "Logs directory created"
}

# Initialize database
setup_database() {
    print_step "Setting up database..."
    
    APP_DIR="/opt/hyde-lyve"
    
    sudo -u hyde-lyve bash << EOF
        cd $APP_DIR
        source venv/bin/activate
        
        if [ -f "recreate_database.py" ]; then
            print_status "Setting up database schema..."
            python3 recreate_database.py
            print_status "Database setup completed"
        else
            print_warning "recreate_database.py not found, database will be created automatically"
        fi
EOF
    
    print_status "Database initialized"
}

# Create systemd service
create_systemd_service() {
    print_step "Creating systemd service..."
    
    SERVICE_NAME="hyde-lyve-middleware"
    APP_DIR="/opt/hyde-lyve"
    
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Hydepark Lyve Middleware
After=network.target

[Service]
Type=simple
User=hyde-lyve
Group=hyde-lyve
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="FLASK_ENV=production"
Environment="PORT=3000"
ExecStart=$APP_DIR/venv/bin/python app_production.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    print_status "Systemd service created: $SERVICE_NAME"
}

# Create startup script
create_startup_script() {
    print_step "Creating startup script..."
    
    APP_DIR="/opt/hyde-lyve"
    
    sudo -u hyde-lyve tee $APP_DIR/start.sh > /dev/null << 'EOF'
#!/bin/bash
# Hydepark Lyve Middleware Startup Script

set -e

APP_DIR="/opt/hyde-lyve"

echo "🚀 Starting Hydepark Lyve Middleware..."
echo "======================================="

cd $APP_DIR

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_ENV=production
export PORT=3000

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(cat .env | xargs)
fi

echo "📖 Application will be available at: http://localhost:3000"
echo "🧪 Test UI available at: http://localhost:3000/test"
echo "📚 API Documentation available at: http://localhost:3000/api-docs"
echo ""
echo "Press Ctrl+C to stop the application"
echo "======================================="

# Start the application
python3 app_production.py
EOF
    
    sudo chmod +x $APP_DIR/start.sh
    sudo chown hyde-lyve:hyde-lyve $APP_DIR/start.sh
    
    print_status "Startup script created: $APP_DIR/start.sh"
}

# Create management script
create_management_script() {
    print_step "Creating management script..."
    
    sudo tee /usr/local/bin/hyde-lyve-manager > /dev/null << 'EOF'
#!/bin/bash
# Hydepark Lyve Middleware Manager

SERVICE_NAME="hyde-lyve-middleware"
APP_DIR="/opt/hyde-lyve"
USER="hyde-lyve"

case "$1" in
    start)
        echo "🚀 Starting Hydepark Lyve Middleware..."
        sudo systemctl start $SERVICE_NAME
        echo "✅ Service started"
        ;;
    stop)
        echo "🛑 Stopping Hydepark Lyve Middleware..."
        sudo systemctl stop $SERVICE_NAME
        echo "✅ Service stopped"
        ;;
    restart)
        echo "🔄 Restarting Hydepark Lyve Middleware..."
        sudo systemctl restart $SERVICE_NAME
        echo "✅ Service restarted"
        ;;
    status)
        echo "📊 Hydepark Lyve Middleware Status:"
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        echo "📋 Viewing logs..."
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    manual)
        echo "🔧 Starting in manual mode..."
        sudo -u $USER $APP_DIR/start.sh
        ;;
    config)
        echo "⚙️  Editing configuration..."
        sudo -u $USER nano $APP_DIR/.env
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|manual|config}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  restart - Restart the service"
        echo "  status  - Show service status"
        echo "  logs    - View service logs"
        echo "  manual  - Start in manual mode"
        echo "  config  - Edit configuration"
        exit 1
        ;;
esac
EOF
    
    sudo chmod +x /usr/local/bin/hyde-lyve-manager
    print_status "Management script created: hyde-lyve-manager"
}

# Create firewall rules (optional)
setup_firewall() {
    print_step "Setting up firewall..."
    
    read -p "Do you want to configure UFW firewall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v ufw &> /dev/null; then
            print_status "Configuring UFW firewall..."
            sudo ufw allow 3000/tcp comment "Hydepark Lyve Middleware"
            print_status "Firewall configured for port 3000"
        else
            print_warning "UFW not available, skipping firewall configuration"
        fi
    fi
}

# Create log rotation
setup_logrotate() {
    print_step "Setting up log rotation..."
    
    APP_DIR="/opt/hyde-lyve"
    
    sudo tee /etc/logrotate.d/hyde-lyve-middleware > /dev/null << EOF
$APP_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 hyde-lyve hyde-lyve
    postrotate
        systemctl reload hyde-lyve-middleware || true
    endscript
}
EOF
    
    print_status "Log rotation configured"
}

# Main deployment function
main() {
    echo "Starting Ubuntu deployment process..."
    
    check_ubuntu
    update_system
    install_dependencies
    check_python
    create_user
    setup_directory
    copy_application_files
    setup_virtual_env
    install_requirements
    setup_configuration
    setup_logs
    setup_database
    create_systemd_service
    create_startup_script
    create_management_script
    setup_firewall
    setup_logrotate
    
    echo ""
    echo "✅ Ubuntu deployment completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Configure HikCentral settings in /opt/hyde-lyve/.env"
    echo "2. Start the service: sudo hyde-lyve-manager start"
    echo "3. Check status: sudo hyde-lyve-manager status"
    echo "4. View logs: sudo hyde-lyve-manager logs"
    echo ""
    echo "🔧 Management commands:"
    echo "  sudo hyde-lyve-manager start   # Start service"
    echo "  sudo hyde-lyve-manager stop    # Stop service"
    echo "  sudo hyde-lyve-manager restart # Restart service"
    echo "  sudo hyde-lyve-manager status  # Show status"
    echo "  sudo hyde-lyve-manager logs    # View logs"
    echo "  sudo hyde-lyve-manager manual  # Manual start"
    echo "  sudo hyde-lyve-manager config  # Edit config"
    echo ""
    echo "🌐 Web Interface:"
    echo "  Homepage: http://your-server-ip:3000"
    echo "  Test UI: http://your-server-ip:3000/test"
    echo "  API Docs: http://your-server-ip:3000/api-docs"
    echo ""
    print_warning "Remember to configure your HikCentral credentials before starting the service!"
}

# Run main function
main