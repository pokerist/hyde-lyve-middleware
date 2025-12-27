# Hydepark Lyve Middleware - Project Structure

```
hydepark-lyve-middleware/
│
├── 📁 Root Files
│   ├── README.md                           # Main project documentation
│   ├── requirements.txt                    # Python dependencies
│   ├── .env.production                     # Production environment template
│   ├── .env                               # Environment configuration (created during setup)
│   ├── .gitignore                         # Git ignore file
│   ├── app_production.py                  # Main Flask application (port 3000)
│   ├── config.py                          # Configuration settings
│   ├── deploy_ubuntu.sh                   # Ubuntu deployment script
│   ├── setup.sh                           # Quick setup script
│   ├── recreate_database.py               # Database setup script
│   ├── migrate_database.py                # Database migration script
│   ├── enhanced_test.py                   # Comprehensive test suite
│   └── docker-compose.yml                 # Docker deployment configuration
│
├── 📁 Services/
│   ├── hikcentral_client.py               # HikCentral API client
│   └── person_service.py                  # Person management service
│
├── 📁 Models/
│   └── database.py                        # Database models (PersonMapping, FaceData, ApiLog)
│
├── 📁 Utils/
│   ├── logger.py                          # Logging configuration
│   └── face_processor.py                  # Face image processing utilities
│
├── 📁 Templates/
│   ├── index.html                         # Homepage with system overview
│   ├── test.html                          # Interactive API testing interface
│   ├── api_docs.html                      # Complete API documentation
│   ├── 404.html                           # Custom 404 error page
│   └── 500.html                           # Custom 500 error page
│
├── 📁 Static/
│   └── js/
│       └── test_ui.js                     # Frontend JavaScript for test interface
│
├── 📁 Logs/
│   └── hydepark_lyve.log                  # Application logs (created automatically)
│
└── 📁 Data/
    └── hydepark_lyve.db                     # SQLite database (created automatically)
```

## 🚀 Quick Start Commands

### Ubuntu Deployment
```bash
# Clone and setup
git clone https://github.com/pokerist/hyde-lyve-middleware.git
cd hyde-lyve-middleware

# Run Ubuntu deployment script
chmod +x deploy_ubuntu.sh
sudo ./deploy_ubuntu.sh

# Configure HikCentral settings
sudo nano /opt/hyde-lyve/.env

# Start the service
sudo hyde-lyve-manager start
```

### Manual Setup
```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.production .env
nano .env  # Update with your HikCentral settings

# Initialize database
python3 recreate_database.py

# Start application
python3 app_production.py
```

### Docker Deployment
```bash
# Configure Docker environment
nano docker-compose.yml  # Update HikCentral settings

# Deploy with Docker
docker-compose up -d

# Check logs
docker-compose logs -f
```

## 🌐 Access Points

### Web Interface
- **Homepage**: `http://your-server:3000`
- **Test UI**: `http://your-server:3000/test`
- **API Docs**: `http://your-server:3000/api-docs`

### API Endpoints
- **Health**: `GET /health`
- **Person Check**: `POST /api/person/check`
- **Person Create**: `POST /api/person/create`
- **Person Update**: `PUT /api/person/update`
- **Person Delete**: `DELETE /api/person/delete`
- **Person Search**: `POST /api/person/search`
- **Batch Create**: `POST /api/person/batch/create`
- **Face Validation**: `POST /api/face/validate`
- **Configuration**: `GET /api/config`

## 🔧 Management Commands

```bash
# Service management
sudo hyde-lyve-manager start    # Start service
sudo hyde-lyve-manager stop     # Stop service
sudo hyde-lyve-manager restart  # Restart service
sudo hyde-lyve-manager status   # Check status
sudo hyde-lyve-manager logs     # View logs
sudo hyde-lyve-manager config  # Edit configuration

# Manual startup
sudo -u hyde-lyve /opt/hyde-lyve/start.sh
```

## 📋 Configuration Checklist

Before deployment, ensure you have:

1. ✅ **HikCentral Server Details**
   - Base URL (e.g., `https://your-hikcentral-server/artemis`)
   - App Key and App Secret
   - User ID and Organization Index Code

2. ✅ **Security Settings**
   - Strong API key (change from default)
   - SSL/TLS configuration
   - Firewall rules (port 3000)

3. ✅ **Network Configuration**
   - Server can reach HikCentral
   - Port 3000 is available
   - DNS resolution working

4. ✅ **System Requirements**
   - Ubuntu 18.04+ or compatible
   - Python 3.8+
   - Minimum 2GB RAM
   - 1GB+ disk space

## 🚀 Deployment Ready!

Your Hydepark Lyve Middleware is now ready for deployment on your Ubuntu server with HikCentral access. The system provides:

- **Complete API Integration** between Lyve and HikCentral
- **Face Data Support** with validation and quality assessment
- **Batch Operations** for efficient processing
- **Web-based Testing Interface** for easy validation
- **Comprehensive Documentation** and error handling
- **Production-ready Security** with API key authentication
- **Docker Support** for containerized deployment
- **Systemd Integration** for reliable service management

**Next Steps:**
1. Push to GitHub repository
2. Deploy on your Ubuntu server
3. Configure HikCentral connection
4. Test with the web interface
5. Integrate with your Lyve system