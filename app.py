from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os
from config import Config
from services.hikcentral_client import HikCentralClient
from services.person_service import PersonService
from models.database import db, PersonMapping, FaceData
from utils.logger import setup_logger
from utils.face_processor import FaceDataProcessor
from functools import wraps
import time

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

logger = setup_logger(__name__)

hikcentral_client = HikCentralClient()
person_service = PersonService(hikcentral_client, db)
face_processor = FaceDataProcessor()

with app.app_context():
    db.create_all()

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # In production, validate against database or config
        if api_key != os.environ.get('LYVE_API_KEY', 'demo-key'):
            return jsonify({'error': 'Invalid API key'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

def log_api_call(f):
    """Decorator to log API calls"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = f(*args, **kwargs)
            
            # Log successful call
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"API call: {request.method} {request.path} - Status: {response[1] if isinstance(response, tuple) else 200} - Duration: {duration_ms}ms")
            
            return response
            
        except Exception as e:
            # Log error
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"API call failed: {request.method} {request.path} - Error: {str(e)} - Duration: {duration_ms}ms")
            raise
            
    return decorated_function

def validate_json_request(required_fields=None):
    """Validate that request contains JSON and required fields"""
    if not request.is_json:
        return None, jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data:
        return None, jsonify({"error": "No JSON data provided"}), 400
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return None, jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    return data, None, None

@app.route('/health', methods=['GET'])
@log_api_call
def health_check():
    """Health check endpoint"""
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/person/check', methods=['POST'])
@require_api_key
@log_api_call
def check_person():
    """
    Check if person exists in local database
    Expected JSON: {"personId": "lyve_person_id"}
    """
    try:
        data, error_response, error_code = validate_json_request(['personId'])
        if error_response:
            return error_response, error_code
        
        lyve_person_id = data['personId']
        logger.info(f"Checking person: {lyve_person_id}")
        
        person = person_service.get_person_by_lyve_id(lyve_person_id)
        
        if person:
            return jsonify({
                "exists": True,
                "hikcentralId": person.hikcentral_person_id,
                "personData": person.to_dict()
            })
        else:
            return jsonify({"exists": False, "message": "Person not found in local database"})
            
    except Exception as e:
        logger.error(f"Error checking person: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/person/create', methods=['POST'])
@require_api_key
@log_api_call
def create_person():
    """
    Create new person in HikCentral and local database
    Expected JSON: {
        "personId": "lyve_person_id",
        "name": "Person Name",
        "phone": "1234567890",
        "email": "person@example.com",
        "gender": 1,
        "faceImages": ["base64_encoded_image_or_file_path"],
        "beginTime": "2024-01-01T00:00:00",
        "endTime": "2030-01-01T00:00:00"
    }
    """
    try:
        data, error_response, error_code = validate_json_request(['personId'])
        if error_response:
            return error_response, error_code
        
        lyve_person_id = data['personId']
        logger.info(f"Creating person: {lyve_person_id}")
        
        # Check if person already exists
        existing_person = person_service.get_person_by_lyve_id(lyve_person_id)
        if existing_person:
            return jsonify({
                "error": "Person already exists",
                "hikcentralId": existing_person.hikcentral_person_id
            }), 409
        
        # Create person in HikCentral and local database
        result = person_service.create_person(data)
        
        if result['success']:
            return jsonify({
                "success": True,
                "hikcentralId": result['hikcentral_id'],
                "message": result['message'],
                "faceCount": result.get('face_count', 0)
            }), 201
        else:
            return jsonify({
                "error": "Failed to create person",
                "message": result['message']
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating person: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/person/update', methods=['PUT'])
@require_api_key
@log_api_call
def update_person():
    """
    Update existing person in HikCentral and local database
    Expected JSON: {
        "personId": "lyve_person_id",
        "name": "Updated Name",
        "phone": "1234567890",
        "email": "updated@example.com",
        "faceImages": ["base64_encoded_image_or_file_path"]
    }
    """
    try:
        data, error_response, error_code = validate_json_request(['personId'])
        if error_response:
            return error_response, error_code
        
        lyve_person_id = data['personId']
        logger.info(f"Updating person: {lyve_person_id}")
        
        # Check if person exists
        existing_person = person_service.get_person_by_lyve_id(lyve_person_id)
        if not existing_person:
            return jsonify({"error": "Person not found"}), 404
        
        # Update person
        result = person_service.update_person(lyve_person_id, data)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": result['message'],
                "faceCount": result.get('face_count', 0)
            })
        else:
            return jsonify({
                "error": "Failed to update person",
                "message": result['message']
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating person: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/person/delete', methods=['DELETE'])
@require_api_key
@log_api_call
def delete_person():
    """
    Delete person from HikCentral and local database
    Expected JSON: {"personId": "lyve_person_id"}
    """
    try:
        data, error_response, error_code = validate_json_request(['personId'])
        if error_response:
            return error_response, error_code
        
        lyve_person_id = data['personId']
        logger.info(f"Deleting person: {lyve_person_id}")
        
        # Check if person exists
        existing_person = person_service.get_person_by_lyve_id(lyve_person_id)
        if not existing_person:
            return jsonify({"error": "Person not found"}), 404
        
        # Delete person
        result = person_service.delete_person(lyve_person_id)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": result['message']
            })
        else:
            return jsonify({
                "error": "Failed to delete person",
                "message": result['message']
            }), 500
            
    except Exception as e:
        logger.error(f"Error deleting person: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/person/batch/create', methods=['POST'])
@require_api_key
@log_api_call
def batch_create_persons():
    """
    Batch create multiple persons
    Expected JSON: {
        "persons": [
            {
                "personId": "lyve_person_1",
                "name": "Person 1",
                "phone": "1234567890",
                "email": "person1@example.com",
                "gender": 1,
                "faceImages": ["base64_image"]
            },
            {
                "personId": "lyve_person_2",
                "name": "Person 2",
                "phone": "0987654321",
                "email": "person2@example.com",
                "gender": 2,
                "faceImages": ["base64_image"]
            }
        ]
    }
    """
    try:
        data, error_response, error_code = validate_json_request(['persons'])
        if error_response:
            return error_response, error_code
        
        persons = data.get('persons', [])
        if not isinstance(persons, list):
            return jsonify({"error": "persons must be an array"}), 400
        
        if len(persons) > 100:  # Limit batch size
            return jsonify({"error": "Maximum 100 persons per batch"}), 400
        
        logger.info(f"Batch creating {len(persons)} persons")
        
        result = person_service.batch_create_persons(persons)
        
        return jsonify({
            "success": result['success'],
            "total": result['total'],
            "successCount": result['success_count'],
            "errorCount": result['error_count'],
            "results": result['results']
        })
        
    except Exception as e:
        logger.error(f"Error in batch create: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/person/sync/<hikcentral_person_id>', methods=['POST'])
@require_api_key
@log_api_call
def sync_person(hikcentral_person_id):
    """
    Sync person data from HikCentral to local database
    """
    try:
        logger.info(f"Syncing person from HikCentral: {hikcentral_person_id}")
        
        result = person_service.sync_person_from_hikcentral(hikcentral_person_id)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": result['message'],
                "person": result['person']
            })
        else:
            return jsonify({
                "error": "Sync failed",
                "message": result['message']
            }), 500
            
    except Exception as e:
        logger.error(f"Error syncing person: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/person/<lyve_person_id>/faces', methods=['GET'])
@require_api_key
@log_api_call
def get_person_faces(lyve_person_id):
    """
    Get face data for a person
    """
    try:
        person = person_service.get_person_by_lyve_id(lyve_person_id)
        if not person:
            return jsonify({"error": "Person not found"}), 404
        
        # Get face data from HikCentral
        response = hikcentral_client.get_person(person.hikcentral_person_id)
        if not response:
            return jsonify({"error": "Failed to get person data from HikCentral"}), 500
        
        person_data = response.get('data', {})
        faces = person_data.get('faces', [])
        
        return jsonify({
            "success": True,
            "personId": lyve_person_id,
            "hikcentralId": person.hikcentral_person_id,
            "faceCount": len(faces),
            "faces": faces
        })
        
    except Exception as e:
        logger.error(f"Error getting person faces: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/person/search', methods=['POST'])
@require_api_key
@log_api_call
def search_persons():
    """
    Search for persons with various criteria
    Expected JSON: {
        "name": "John",           // Optional: search by name
        "phone": "123",           // Optional: search by phone
        "email": "john@",         // Optional: search by email
        "gender": 1,              // Optional: filter by gender
        "orgIndexCode": "1",      // Optional: filter by organization
        "limit": 50,              // Optional: limit results (max 100)
        "offset": 0               // Optional: pagination offset
    }
    """
    try:
        data = request.get_json() or {}
        
        # Build query
        query = PersonMapping.query
        
        # Apply filters
        if data.get('name'):
            query = query.filter(PersonMapping.name.contains(data['name']))
        
        if data.get('phone'):
            query = query.filter(PersonMapping.phone.contains(data['phone']))
            
        if data.get('email'):
            query = query.filter(PersonMapping.email.contains(data['email']))
            
        if data.get('gender'):
            query = query.filter(PersonMapping.gender == data['gender'])
            
        if data.get('orgIndexCode'):
            query = query.filter(PersonMapping.org_index_code == data['orgIndexCode'])
        
        # Pagination
        limit = min(data.get('limit', 50), 100)  # Max 100 results
        offset = data.get('offset', 0)
        
        total = query.count()
        persons = query.offset(offset).limit(limit).all()
        
        return jsonify({
            "success": True,
            "total": total,
            "count": len(persons),
            "limit": limit,
            "offset": offset,
            "persons": [person.to_dict() for person in persons]
        })
        
    except Exception as e:
        logger.error(f"Error searching persons: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/face/validate', methods=['POST'])
@require_api_key
@log_api_call
def validate_face():
    """
    Validate face image data
    Expected JSON: {
        "faceImage": "base64_encoded_image_or_file_path"
    }
    """
    try:
        data, error_response, error_code = validate_json_request(['faceImage'])
        if error_response:
            return error_response, error_code
        
        face_image = data['faceImage']
        
        # Validate face image
        face_data = face_processor.validate_and_process_face_image(face_image)
        
        if face_data:
            face_info = face_processor.get_face_data_info(face_data)
            quality_score = face_processor.validate_face_quality(face_image)
            
            return jsonify({
                "success": True,
                "valid": True,
                "qualityScore": quality_score,
                "faceInfo": face_info,
                "message": "Face image is valid"
            })
        else:
            return jsonify({
                "success": True,
                "valid": False,
                "message": "Face image validation failed"
            }), 400
            
    except Exception as e:
        logger.error(f"Error validating face: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/config', methods=['GET'])
@require_api_key
@log_api_call
def get_config():
    """
    Get current configuration settings (sanitized)
    """
    return jsonify({
        "hikcentral": {
            "base_url": Config.HIKCENTRAL_BASE_URL,
            "verify_ssl": Config.HIKCENTRAL_VERIFY_SSL,
            "org_index_code": Config.HIKCENTRAL_ORG_INDEX_CODE
        },
        "api": {
            "timeout": Config.API_TIMEOUT,
            "max_retries": Config.MAX_RETRIES,
            "max_content_length": Config.MAX_CONTENT_LENGTH
        },
        "face_validation": {
            "supported_formats": face_processor.SUPPORTED_FORMATS,
            "max_size_bytes": face_processor.MAX_IMAGE_SIZE,
            "recommended_size": face_processor.RECOMMENDED_SIZE,
            "min_face_size": face_processor.MIN_FACE_SIZE
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Request payload too large"}), 413

if __name__ == '__main__':
    logger.info("Starting Hydepark Lyve Middleware...")
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)