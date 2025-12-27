#!/bin/bash
# Hydepark Lyve Middleware Deployment Script

set -e

echo "🚀 Hydepark Lyve Middleware Deployment Script"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "📋 Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Set environment variables
echo "⚙️  Setting environment variables..."
export FLASK_APP=app_production.py
export FLASK_ENV=production
export PORT=3000

# Check if .env.production exists
if [ -f ".env.production" ]; then
    echo "📝 Loading production environment variables..."
    export $(cat .env.production | xargs)
else
    echo "⚠️  .env.production not found. Using default configuration."
fi

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
python3 -c "
from app_production import app, db
with app.app_context():
    db.create_all()
    print('✅ Database setup complete')
"

# Run tests
echo "🧪 Running tests..."
python3 enhanced_test.py || echo "⚠️  Some tests failed - check configuration"

# Start the application
echo "🚀 Starting Hydepark Lyve Middleware on port $PORT..."
echo "📖 Application will be available at: http://localhost:$PORT"
echo "🧪 Test UI available at: http://localhost:$PORT/test"
echo "📚 API Documentation available at: http://localhost:$PORT/api-docs"
echo ""
echo "Press Ctrl+C to stop the application"
echo "=================================================="

# Start the Flask application
python3 app_production.py