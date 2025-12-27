# 🚀 Hydepark Lyve Middleware

A production-ready middleware system that seamlessly integrates **Lyve Access Control** with **HikCentral Professional**, providing a robust bridge for person management operations.

## ✨ Features

### 🔧 Core Functionality
- **Person Management**: Complete CRUD operations for persons
- **Face Data Support**: Upload and validate face images for HikCentral
- **ID Mapping**: Automatic mapping between Lyve and HikCentral person IDs
- **Batch Operations**: Process multiple persons in a single request
- **Advanced Search**: Search persons with multiple criteria and pagination

### 🔒 Security & Authentication
- **API Key Authentication**: Secure API access with configurable authentication
- **HMAC-SHA256**: Industry-standard authentication for HikCentral API
- **SSL/TLS Support**: Full HTTPS support for production environments
- **Rate Limiting**: Configurable request rate limiting
- **Comprehensive Logging**: Detailed audit trails and performance metrics

### 🌐 Web Interface
- **Interactive Test UI**: Web-based interface for testing all API operations
- **API Documentation**: Complete interactive documentation
- **Real-time Monitoring**: Live system status and health checks
- **Configuration Management**: Runtime configuration viewing and updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Access to HikCentral server
- Network connectivity between systems

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/pokerist/hyde-lyve-middleware.git
cd hyde-lyve-middleware
```

2. **Install dependencies**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Copy production configuration
cp .env.production .env

# Edit configuration with your HikCentral details
nano .env
```

4. **Initialize database**
```bash
python3 recreate_database.py
```

5. **Start the application**
```bash
python3 app_production.py
```

6. **Access the web interface**
- **Homepage**: http://localhost:3000
- **Test UI**: http://localhost:3000/test
- **API Docs**: http://localhost:3000/api-docs

## 📋 Configuration

### Environment Variables

#### HikCentral Configuration
```env
HIKCENTRAL_BASE_URL=https://your-hikcentral-server/artemis
HIKCENTRAL_APP_KEY=your-app-key
HIKCENTRAL_APP_SECRET=your-app-secret
HIKCENTRAL_USER_ID=your-user-id
HIKCENTRAL_ORG_INDEX_CODE=1
HIKCENTRAL_VERIFY_SSL=True
```

#### Security Configuration
```env
LYVE_API_KEY=your-secure-api-key-here
REQUIRE_API_KEY=True
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
```

#### Face Data Configuration
```env
MAX_FACE_IMAGES=5
FACE_IMAGE_MAX_SIZE=2097152
FACE_IMAGE_QUALITY_THRESHOLD=70
```

## 🌐 API Endpoints

### Authentication
All API endpoints require `X-API-Key` header:
```http
X-API-Key: your-api-key-here
```

### Core Endpoints

#### Health Check
```http
GET /health
```

#### Person Operations
```http
POST /api/person/check        # Check person existence
POST /api/person/create       # Create new person
PUT  /api/person/update       # Update person
DELETE /api/person/delete     # Delete person
POST /api/person/search       # Search persons
POST /api/person/batch/create # Batch create persons
```

#### Face Data Operations
```http
POST /api/face/validate       # Validate face image
```

#### Configuration
```http
GET /api/config               # Get system configuration
```

### Example API Calls

#### Create Person with Face Image
```bash
curl -X POST http://localhost:3000/api/person/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{
    "personId": "lyve_person_123",
    "name": "John Doe",
    "phone": "1234567890",
    "email": "john@example.com",
    "gender": 1,
    "faceImages": ["base64_encoded_face_image"]
  }'
```

#### Batch Create Persons
```bash
curl -X POST http://localhost:3000/api/person/batch/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{
    "persons": [
      {
        "personId": "person_1",
        "name": "Person 1",
        "phone": "1111111111",
        "email": "person1@example.com"
      },
      {
        "personId": "person_2",
        "name": "Person 2",
        "phone": "2222222222",
        "email": "person2@example.com"
      }
    ]
  }'
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Deployment
```bash
# Build image
docker build -t hyde-lyve-middleware .

# Run container
docker run -d \
  -p 3000:3000 \
  -e HIKCENTRAL_BASE_URL=https://your-server/artemis \
  -e HIKCENTRAL_APP_KEY=your-key \
  -e HIKCENTRAL_APP_SECRET=your-secret \
  -e LYVE_API_KEY=your-api-key \
  --name hyde-lyve-middleware \
  hyde-lyve-middleware
```

## 🔒 Security Best Practices

### Production Deployment
1. **Change default API key immediately**
2. **Enable SSL/TLS for all connections**
3. **Configure firewall rules**
4. **Implement proper log rotation**
5. **Regular security updates**

### Network Security
- Use HTTPS in production
- Implement VPN access if needed
- Monitor access logs regularly
- Configure rate limiting

### Data Protection
- Face images are base64 encoded and validated
- No sensitive data in error messages
- Comprehensive audit logging
- Secure credential storage

## 📊 Monitoring & Logging

### Log Files
- **Application Logs**: `logs/hydepark_lyve.log`
- **Response Times**: All API calls are logged with duration
- **Error Tracking**: Detailed error logging with context

### Health Monitoring
- **Health Endpoint**: `/health`
- **Configuration**: `/api/config`
- **Real-time Status**: Available in web interface

### Performance Metrics
- API response times
- Database query performance
- Memory usage tracking
- Error rate monitoring

## 🧪 Testing

### Automated Testing
```bash
# Run comprehensive test suite
python3 enhanced_test.py

# Run basic tests
python3 simple_test.py
```

### Manual Testing
Use the interactive web interface at `http://localhost:3000/test` to test all API endpoints with a user-friendly interface.

## 🔄 Integration Flow

### Typical Person Creation Flow
1. **Lyve** sends person data to middleware
2. **Middleware** checks local database for existing mapping
3. If not found, **middleware** creates person in HikCentral
4. **Middleware** stores ID mapping in local database
5. **Middleware** returns HikCentral ID to Lyve

### Person Update Flow
1. **Lyve** sends update request with Lyve person ID
2. **Middleware** looks up HikCentral ID from mapping
3. **Middleware** updates person in HikCentral
4. **Middleware** updates local database record
5. **Middleware** confirms update to Lyve

## 🛠️ Troubleshooting

### Common Issues

#### HikCentral Connection Failed
- Check network connectivity
- Verify HikCentral server URL and credentials
- Check SSL certificate configuration
- Review firewall settings

#### Database Errors
- Check file permissions for SQLite database
- Verify disk space availability
- Review database schema
- Check log files for detailed errors

#### API Authentication Failed
- Verify API key configuration
- Check request headers
- Review authentication requirements
- Test with development mode

### Debug Mode
Enable debug mode for troubleshooting:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 📚 Documentation

### API Documentation
- **Complete API Reference**: [ENHANCED_API_DOCUMENTATION.md](ENHANCED_API_DOCUMENTATION.md)
- **Interactive Docs**: Available at `/api-docs` endpoint
- **Test Interface**: Available at `/test` endpoint

### Deployment Guides
- **Production Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Docker Deployment**: See `docker-compose.yml`
- **Systemd Service**: Instructions in deployment guide

### Configuration
- **Environment Variables**: [`.env.production`](.env.production)
- **Configuration Options**: See [config.py](config.py)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is proprietary to Hydepark Lyve. All rights reserved.

## 📞 Support

For support and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/` directory
3. Test with the provided test scripts
4. Check GitHub issues for known problems

---

**🎉 Ready to bridge Lyve and HikCentral with enterprise-grade middleware!**