import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hydepark_lyve.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # HikCentral Configuration
    HIKCENTRAL_BASE_URL = os.environ.get('HIKCENTRAL_BASE_URL') or 'https://192.168.1.101/artemis'
    HIKCENTRAL_APP_KEY = os.environ.get('HIKCENTRAL_APP_KEY') or '27108141'
    HIKCENTRAL_APP_SECRET = os.environ.get('HIKCENTRAL_APP_SECRET') or 'c3U7KikkPGo2Yka6GMZ5'
    HIKCENTRAL_USER_ID = os.environ.get('HIKCENTRAL_USER_ID') or 'admin'
    HIKCENTRAL_ORG_INDEX_CODE = os.environ.get('HIKCENTRAL_ORG_INDEX_CODE') or '1'
    HIKCENTRAL_VERIFY_SSL = os.environ.get('HIKCENTRAL_VERIFY_SSL', 'False').lower() == 'true'
    
    # API Configuration
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '30'))
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))
    
    # Authentication Configuration
    LYVE_API_KEY = os.environ.get('LYVE_API_KEY') or 'demo-key'
    REQUIRE_API_KEY = os.environ.get('REQUIRE_API_KEY', 'True').lower() == 'true'
    
    # Face Data Configuration
    MAX_FACE_IMAGES = int(os.environ.get('MAX_FACE_IMAGES', '5'))
    FACE_IMAGE_MAX_SIZE = int(os.environ.get('FACE_IMAGE_MAX_SIZE', '2097152'))  # 2MB
    FACE_IMAGE_QUALITY_THRESHOLD = int(os.environ.get('FACE_IMAGE_QUALITY_THRESHOLD', '70'))
    
    # Batch Operations Configuration
    MAX_BATCH_SIZE = int(os.environ.get('MAX_BATCH_SIZE', '100'))
    BATCH_TIMEOUT = int(os.environ.get('BATCH_TIMEOUT', '300'))  # 5 minutes
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/hydepark_lyve.log')
    
    # Security Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Performance Configuration
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'False').lower() == 'true'
    CACHE_TTL = int(os.environ.get('CACHE_TTL', '300'))  # 5 minutes
    
    # Monitoring Configuration
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'False').lower() == 'true'
    METRICS_ENDPOINT = os.environ.get('METRICS_ENDPOINT', '/metrics')