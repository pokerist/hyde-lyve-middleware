import logging
from datetime import datetime
from typing import Dict, Optional, List
import time
from models.database import PersonMapping, ApiLog
from utils.face_processor import FaceDataProcessor

logger = logging.getLogger(__name__)

class PersonService:
    def __init__(self, hikcentral_client, db):
        self.hikcentral_client = hikcentral_client
        self.db = db
        self.face_processor = FaceDataProcessor()
    
    def get_person_by_lyve_id(self, lyve_person_id: str) -> Optional[PersonMapping]:
        """Get person mapping by Lyve ID"""
        try:
            return PersonMapping.query.filter_by(lyve_person_id=lyve_person_id).first()
        except Exception as e:
            logger.error(f"Error getting person by Lyve ID {lyve_person_id}: {e}")
            return None
    
    def get_person_by_hikcentral_id(self, hikcentral_person_id: str) -> Optional[PersonMapping]:
        """Get person mapping by HikCentral ID"""
        try:
            return PersonMapping.query.filter_by(hikcentral_person_id=hikcentral_person_id).first()
        except Exception as e:
            logger.error(f"Error getting person by HikCentral ID {hikcentral_person_id}: {e}")
            return None
    
    def validate_person_data(self, data: Dict) -> Dict:
        """Validate person data before processing"""
        errors = []
        
        # Required fields
        if not data.get('personId'):
            errors.append("personId is required")
            
        if not data.get('name'):
            errors.append("name is required")
            
        # Validate gender
        gender = data.get('gender', 1)
        if gender not in [1, 2]:
            errors.append("gender must be 1 (Male) or 2 (Female)")
            
        # Validate phone format (basic validation)
        phone = data.get('phone', '')
        if phone and not phone.replace('-', '').replace(' ', '').isdigit():
            errors.append("phone number contains invalid characters")
            
        # Validate email format
        email = data.get('email', '')
        if email and '@' not in email:
            errors.append("invalid email format")
            
        # Validate face data if provided
        face_images = data.get('faceImages', [])
        if face_images:
            if not isinstance(face_images, list):
                errors.append("faceImages must be an array")
            else:
                for i, face_image in enumerate(face_images):
                    if not face_image:
                        errors.append(f"faceImages[{i}] is empty")
                        
        # Validate dates
        if data.get('beginTime'):
            try:
                datetime.fromisoformat(data['beginTime'].replace('Z', '+00:00'))
            except:
                errors.append("invalid beginTime format")
                
        if data.get('endTime'):
            try:
                datetime.fromisoformat(data['endTime'].replace('Z', '+00:00'))
            except:
                errors.append("invalid endTime format")
                
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def process_face_images(self, face_images: List[str], person_data: Dict) -> List[Dict]:
        """Process face images for HikCentral"""
        if not face_images:
            return []
            
        logger.info(f"Processing {len(face_images)} face images")
        
        processed_faces = []
        for i, face_image in enumerate(face_images):
            try:
                face_data = self.face_processor.validate_and_process_face_image(face_image)
                if face_data:
                    # Update face metadata with person information
                    face_data['name'] = f"{person_data.get('name', 'person')}_face_{i+1}"
                    face_data['sex'] = person_data.get('gender', 1)
                    
                    # Add certificate number if available
                    if 'certificateNum' in person_data:
                        face_data['certificateNum'] = person_data['certificateNum']
                        
                    processed_faces.append(face_data)
                    logger.info(f"Face image {i+1} processed successfully")
                else:
                    logger.warning(f"Face image {i+1} failed validation")
                    
            except Exception as e:
                logger.error(f"Error processing face image {i+1}: {e}")
                
        return processed_faces
    
    def create_person(self, data: Dict) -> Dict:
        """Create person in HikCentral and local database"""
        try:
            # Validate person data
            validation = self.validate_person_data(data)
            if not validation['valid']:
                return {
                    'success': False,
                    'message': f"Validation failed: {', '.join(validation['errors'])}"
                }
            
            lyve_person_id = data['personId']
            
            # Check if person already exists
            existing_person = self.get_person_by_lyve_id(lyve_person_id)
            if existing_person:
                return {
                    'success': False,
                    'message': 'Person already exists',
                    'hikcentral_id': existing_person.hikcentral_person_id
                }
            
            # Generate unique HikCentral person code
            hikcentral_person_code = f"LYVE_{lyve_person_id}_{int(time.time())}"
            
            # Process face images if provided
            face_images = data.get('faceImages', [])
            processed_faces = self.process_face_images(face_images, data)
            
            # Prepare HikCentral person data
            hikcentral_data = {
                'personCode': hikcentral_person_code,
                'personFamilyName': data.get('name', ''),
                'personGivenName': data.get('givenName', ''),
                'gender': data.get('gender', 1),
                'orgIndexCode': data.get('orgIndexCode', '1'),
                'phoneNo': data.get('phone', ''),
                'email': data.get('email', ''),
                'faces': processed_faces,
                'beginTime': data.get('beginTime', datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
                'endTime': data.get('endTime', '2030-12-31T23:59:59')
            }
            
            # Add optional fields if provided
            if 'certificateType' in data:
                hikcentral_data['certificateType'] = data['certificateType']
            if 'certificateNum' in data:
                hikcentral_data['certificateNum'] = data['certificateNum']
            if 'personType' in data:
                hikcentral_data['personType'] = data['personType']
            
            # Create person in HikCentral
            logger.info(f"Creating person in HikCentral: {hikcentral_person_code}")
            response = self.hikcentral_client.add_person(hikcentral_data)
            
            if not response:
                return {
                    'success': False,
                    'message': 'Failed to create person in HikCentral'
                }
            
            # Extract HikCentral person ID from response
            hikcentral_id = response.get('data', {}).get('personId') or hikcentral_person_code
            
            # Create local mapping
            person_mapping = PersonMapping(
                lyve_person_id=lyve_person_id,
                hikcentral_person_id=hikcentral_id,
                name=data.get('name', ''),
                phone=data.get('phone', ''),
                email=data.get('email', ''),
                gender=data.get('gender', 1),
                org_index_code=data.get('orgIndexCode', '1'),
                begin_time=datetime.fromisoformat(data.get('beginTime', datetime.now().isoformat())),
                end_time=datetime.fromisoformat(data.get('endTime', '2030-12-31T23:59:59')) if data.get('endTime') else None,
                is_active=True,
                face_count=len(processed_faces)
            )
            
            self.db.session.add(person_mapping)
            self.db.session.commit()
            
            logger.info(f"Person created successfully: Lyve ID {lyve_person_id}, HikCentral ID {hikcentral_id}, Faces: {len(processed_faces)}")
            
            return {
                'success': True,
                'hikcentral_id': hikcentral_id,
                'message': 'Person created successfully',
                'face_count': len(processed_faces)
            }
            
        except Exception as e:
            logger.error(f"Error creating person: {e}")
            self.db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating person: {str(e)}'
            }
    
    def update_person(self, lyve_person_id: str, data: Dict) -> Dict:
        """Update person in HikCentral and local database"""
        try:
            # Get existing person mapping
            person = self.get_person_by_lyve_id(lyve_person_id)
            if not person:
                return {
                    'success': False,
                    'message': 'Person not found in local database'
                }
            
            # Process new face images if provided
            face_images = data.get('faceImages', [])
            processed_faces = []
            if face_images:
                processed_faces = self.process_face_images(face_images, data)
            
            # Prepare HikCentral update data
            hikcentral_data = {
                'personFamilyName': data.get('name', person.name),
                'phoneNo': data.get('phone', person.phone),
                'email': data.get('email', person.email),
                'gender': data.get('gender', person.gender)
            }
            
            # Add faces if new ones were provided
            if processed_faces:
                hikcentral_data['faces'] = processed_faces
            
            # Add optional fields if provided
            if 'certificateType' in data:
                hikcentral_data['certificateType'] = data['certificateType']
            if 'certificateNum' in data:
                hikcentral_data['certificateNum'] = data['certificateNum']
            if 'personType' in data:
                hikcentral_data['personType'] = data['personType']
            if 'beginTime' in data:
                hikcentral_data['beginTime'] = data['beginTime']
            if 'endTime' in data:
                hikcentral_data['endTime'] = data['endTime']
            
            # Update person in HikCentral
            logger.info(f"Updating person in HikCentral: {person.hikcentral_person_id}")
            response = self.hikcentral_client.update_person(person.hikcentral_person_id, hikcentral_data)
            
            if not response:
                return {
                    'success': False,
                    'message': 'Failed to update person in HikCentral'
                }
            
            # Update local mapping
            person.name = data.get('name', person.name)
            person.phone = data.get('phone', person.phone)
            person.email = data.get('email', person.email)
            person.gender = data.get('gender', person.gender)
            if processed_faces:
                person.face_count = len(processed_faces)
            person.updated_at = datetime.utcnow()
            
            self.db.session.commit()
            
            logger.info(f"Person updated successfully: Lyve ID {lyve_person_id}")
            
            return {
                'success': True,
                'message': 'Person updated successfully',
                'face_count': len(processed_faces) if processed_faces else person.face_count
            }
            
        except Exception as e:
            logger.error(f"Error updating person: {e}")
            self.db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating person: {str(e)}'
            }
    
    def delete_person(self, lyve_person_id: str) -> Dict:
        """Delete person from HikCentral and local database"""
        try:
            # Get existing person mapping
            person = self.get_person_by_lyve_id(lyve_person_id)
            if not person:
                return {
                    'success': False,
                    'message': 'Person not found in local database'
                }
            
            # Delete person from HikCentral
            logger.info(f"Deleting person from HikCentral: {person.hikcentral_person_id}")
            response = self.hikcentral_client.delete_person(person.hikcentral_person_id)
            
            if not response:
                return {
                    'success': False,
                    'message': 'Failed to delete person from HikCentral'
                }
            
            # Delete local mapping
            self.db.session.delete(person)
            self.db.session.commit()
            
            logger.info(f"Person deleted successfully: Lyve ID {lyve_person_id}")
            
            return {
                'success': True,
                'message': 'Person deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting person: {e}")
            self.db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting person: {str(e)}'
            }
    
    def sync_person_from_hikcentral(self, hikcentral_person_id: str) -> Dict:
        """Sync person data from HikCentral to local database"""
        try:
            # Get person from HikCentral
            response = self.hikcentral_client.get_person(hikcentral_person_id)
            
            if not response:
                return {
                    'success': False,
                    'message': 'Person not found in HikCentral'
                }
            
            person_data = response.get('data', {})
            if not person_data:
                return {
                    'success': False,
                    'message': 'No person data returned from HikCentral'
                }
            
            # Update or create local mapping
            person = self.get_person_by_hikcentral_id(hikcentral_person_id)
            if not person:
                # Create new mapping
                person = PersonMapping(
                    lyve_person_id=f"SYNC_{hikcentral_person_id}",
                    hikcentral_person_id=hikcentral_person_id,
                    name=f"{person_data.get('personFamilyName', '')} {person_data.get('personGivenName', '')}".strip(),
                    phone=person_data.get('phoneNo', ''),
                    email=person_data.get('email', ''),
                    gender=person_data.get('gender', 1),
                    org_index_code=person_data.get('orgIndexCode', '1'),
                    is_active=True,
                    face_count=len(person_data.get('faces', []))
                )
                self.db.session.add(person)
            else:
                # Update existing mapping
                person.name = f"{person_data.get('personFamilyName', '')} {person_data.get('personGivenName', '')}".strip()
                person.phone = person_data.get('phoneNo', '')
                person.email = person_data.get('email', '')
                person.gender = person_data.get('gender', 1)
                person.face_count = len(person_data.get('faces', []))
                person.updated_at = datetime.utcnow()
            
            self.db.session.commit()
            
            logger.info(f"Person synced successfully: HikCentral ID {hikcentral_person_id}")
            
            return {
                'success': True,
                'message': 'Person synced successfully',
                'person': person.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error syncing person: {e}")
            self.db.session.rollback()
            return {
                'success': False,
                'message': f'Error syncing person: {str(e)}'
            }
    
    def batch_create_persons(self, persons_data: List[Dict]) -> Dict:
        """Batch create multiple persons"""
        results = []
        success_count = 0
        error_count = 0
        
        for i, person_data in enumerate(persons_data):
            try:
                result = self.create_person(person_data)
                results.append({
                    'index': i,
                    'personId': person_data.get('personId'),
                    'success': result['success'],
                    'message': result.get('message', ''),
                    'hikcentral_id': result.get('hikcentral_id')
                })
                
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Error in batch create person {i}: {e}")
                results.append({
                    'index': i,
                    'personId': person_data.get('personId'),
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
                error_count += 1
        
        return {
            'success': error_count == 0,
            'total': len(persons_data),
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        }