# 🚀 Hydepark Lyve Middleware - Deployment Guide

## Overview
This guide will help you deploy the Hydepark Lyve Middleware on your production server that has access to the HikCentral system.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux (Ubuntu/Debian/CentOS) or Windows Server
- **Network Access**: Server must be able to reach HikCentral server
- **Memory**: Minimum 2GB RAM
- **Storage**: Minimum 1GB free space

### Network Requirements
- **HikCentral Server**: Must be accessible from deployment server
- **Port 3000**: Must be available for the middleware
- **HTTPS**: Required for production (SSL certificates needed)

## 🔧 Configuration

### 1. Environment Configuration

Copy the production environment template:
```bash
cp .env.production .env
```

Update the following critical settings in `.env`:

```env
# HikCentral Configuration - UPDATE THESE!
HIKCENTRAL_BASE_URL=https://your-hikcentral-server-ip/artemis
HIKCENTRAL_APP_KEY=your-actual-app-key
HIKCENTRAL_APP_SECRET=your-actual-app-secret
HIKCENTRAL_USER_ID=your-actual-user
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=True

# Security Configuration - CHANGE THIS!
LYVE_API_KEY=your-very-secure-api-key-here
REQUIRE_API_KEY=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/hydepark_lyve_prod.log
```

### 2. SSL Configuration (Production)

For production deployment, configure SSL:

```env
# Enable SSL verification
HIKCENTRAL_VERIFY_SSL=True

# If using self-signed certificates, you may need to:
# 1. Add certificates to system trust store
# 2. Or set HIKCENTRAL_VERIFY_SSL=False (not recommended)
```

## 🚀 Deployment Options

### Option 1: Manual Deployment (Recommended for Testing)

1. **Install Dependencies**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

2. **Initialize Database**
```bash
# Create database tables
python3 recreate_database.py
```

3. **Run the Application**
```bash
# Set environment variables
export FLASK_ENV=production
export PORT=3000

# Run the application
python3 app_production.py
```

4. **Test the Deployment**
```bash
# Test health endpoint
curl -X GET http://localhost:3000/health

# Test with API key
curl -X POST http://localhost:3000/api/person/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"personId": "test_person_123"}'
```

### Option 2: Docker Deployment (Recommended for Production)

1. **Install Docker and Docker Compose**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Configure Docker Environment**
Edit `docker-compose.yml` and update the environment variables:

```yaml
environment:
  - HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
  - HIKCENTRAL_APP_KEY=your-actual-app-key
  - HIKCENTRAL_APP_SECRET=your-actual-app-secret
  - HIKCENTRAL_USER_ID=your-actual-user
  - LYVE_API_KEY=your-very-secure-api-key-here
```

3. **Deploy with Docker Compose**
```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Test the deployment
curl -X GET http://localhost:3000/health
```

### Option 3: Systemd Service (Linux Production)

1. **Create Systemd Service File**
```bash
sudo nano /etc/systemd/system/hyde-lyve-middleware.service
```

2. **Add Service Configuration**
```ini
[Unit]
Description=Hydepark Lyve Middleware
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
Environment="FLASK_ENV=production"
Environment="PORT=3000"
ExecStart=/path/to/your/venv/bin/python app_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Enable and Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable hyde-lyve-middleware
sudo systemctl start hyde-lyve-middleware
sudo systemctl status hyde-lyve-middleware
```

## 🔍 Testing the Deployment

### 1. Health Check
```bash
curl -X GET http://your-server-ip:3000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "version": "2.0.0"
}
```

### 2. Configuration Check
```bash
curl -X GET http://your-server-ip:3000/api/config \
  -H "X-API-Key: your-api-key"
```

### 3. Person Operations Test
```bash
# Create test person
curl -X POST http://your-server-ip:3000/api/person/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "personId": "test_person_123",
    "name": "Test User",
    "phone": "1234567890",
    "email": "test@example.com",
    "gender": 1
  }'

# Check person
curl -X POST http://your-server-ip:3000/api/person/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"personId": "test_person_123"}'
```

## 🌐 Web Interface Access

### Frontend UI
- **Test Interface**: `http://your-server-ip:3000/test`
- **API Documentation**: `http://your-server-ip:3000/api-docs`
- **Homepage**: `http://your-server-ip:3000/`

### Features
- ✅ Interactive API testing
- ✅ Face image validation
- ✅ Batch operations testing
- ✅ Configuration management
- ✅ Real-time response viewing

## 🔒 Security Considerations

### 1. API Key Security
- Change the default API key immediately
- Use strong, randomly generated API keys
- Consider implementing key rotation
- Store API keys securely (environment variables, not in code)

### 2. Network Security
- Use HTTPS in production (SSL certificates)
- Implement firewall rules
- Consider VPN access for HikCentral
- Monitor access logs regularly

### 3. Data Protection
- Enable SSL verification for HikCentral
- Implement rate limiting
- Log all API calls for audit
- Regular security updates

## 📊 Monitoring and Logging

### Log Files
- **Application Logs**: `logs/hydepark_lyve_prod.log`
- **System Logs**: Check systemd logs if using service
- **Docker Logs**: `docker-compose logs -f`

### Health Monitoring
- Health endpoint: `/health`
- Configuration endpoint: `/api/config`
- Response time tracking built-in

### Performance Monitoring
- API call duration logging
- Database query performance
- Memory usage tracking
- Error rate monitoring

## 🔄 Maintenance

### Regular Tasks
1. **Log Rotation**: Set up logrotate for log files
2. **Database Backup**: Regular SQLite database backups
3. **Security Updates**: Keep dependencies updated
4. **Certificate Renewal**: SSL certificate management
5. **Performance Review**: Monitor response times

### Backup Strategy
```bash
# Database backup
cp hydepark_lyve_prod.db backup_$(date +%Y%m%d_%H%M%S).db

# Log backup
tar -czf logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz logs/
```

## 🆘 Troubleshooting

### Common Issues

1. **HikCentral Connection Failed**
   - Check network connectivity
   - Verify HikCentral server URL
   - Check SSL certificates
   - Review authentication credentials

2. **Database Errors**
   - Check file permissions
   - Verify database file location
   - Review disk space
   - Check SQLite version compatibility

3. **API Authentication Failed**
   - Verify API key configuration
   - Check request headers
   - Review authentication requirements
   - Test with development mode

4. **Face Image Upload Issues**
   - Check image format and size
   - Verify base64 encoding
   - Review face validation settings
   - Check server memory limits

### Debug Mode
For troubleshooting, enable debug mode:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 📞 Support

### Getting Help
1. Check application logs first
2. Verify all configuration settings
3. Test with simple API calls
4. Review HikCentral connectivity
5. Check GitHub repository for updates

### Next Steps
1. Configure SSL certificates
2. Set up monitoring alerts
3. Implement backup automation
4. Configure log rotation
5. Set up CI/CD pipeline

---

**🎉 Your Hydepark Lyve Middleware is now ready for production deployment!**