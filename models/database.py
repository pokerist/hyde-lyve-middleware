from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class PersonMapping(db.Model):
    __tablename__ = 'person_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    lyve_person_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    hikcentral_person_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Person data
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.Integer, default=1)  # 1: Male, 2: Female
    
    # Additional person fields
    given_name = db.Column(db.String(100), nullable=True)
    certificate_type = db.Column(db.Integer, nullable=True)
    certificate_num = db.Column(db.String(50), nullable=True)
    person_type = db.Column(db.Integer, default=1)  # 1: Normal person
    
    # Face data tracking
    face_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    org_index_code = db.Column(db.String(50), default='1')
    begin_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'lyve_person_id': self.lyve_person_id,
            'hikcentral_person_id': self.hikcentral_person_id,
            'name': self.name,
            'given_name': self.given_name,
            'phone': self.phone,
            'email': self.email,
            'gender': self.gender,
            'certificate_type': self.certificate_type,
            'certificate_num': self.certificate_num,
            'person_type': self.person_type,
            'face_count': self.face_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'org_index_code': self.org_index_code,
            'begin_time': self.begin_time.isoformat() if self.begin_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<PersonMapping lyve_id={self.lyve_person_id}, hikcentral_id={self.hikcentral_person_id}>'

class ApiLog(db.Model):
    __tablename__ = 'api_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    request_data = db.Column(db.Text, nullable=True)
    response_data = db.Column(db.Text, nullable=True)
    status_code = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_time_ms = db.Column(db.Integer, nullable=True)
    
    # Additional context
    client_ip = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<ApiLog {self.method} {self.endpoint} {self.status_code}>'

class FaceData(db.Model):
    __tablename__ = 'face_data'
    
    id = db.Column(db.Integer, primary_key=True)
    person_mapping_id = db.Column(db.Integer, db.ForeignKey('person_mappings.id'), nullable=False)
    face_data = db.Column(db.Text, nullable=False)  # Base64 encoded face image
    face_name = db.Column(db.String(100), nullable=False)
    face_type = db.Column(db.Integer, default=1)  # 1: Real person face
    face_quality = db.Column(db.Integer, default=80)  # Quality score 0-100
    born_time = db.Column(db.DateTime, default=datetime.utcnow)
    sex = db.Column(db.Integer, default=1)  # 1: Male, 2: Female
    certificate_type = db.Column(db.Integer, nullable=True)
    certificate_num = db.Column(db.String(50), nullable=True)
    
    # Face metadata
    image_format = db.Column(db.String(10), nullable=True)  # JPEG, PNG, etc.
    image_size = db.Column(db.Integer, nullable=True)  # Size in bytes
    image_dimensions = db.Column(db.String(20), nullable=True)  # WidthxHeight
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'person_mapping_id': self.person_mapping_id,
            'face_name': self.face_name,
            'face_type': self.face_type,
            'face_quality': self.face_quality,
            'born_time': self.born_time.isoformat() if self.born_time else None,
            'sex': self.sex,
            'certificate_type': self.certificate_type,
            'certificate_num': self.certificate_num,
            'image_format': self.image_format,
            'image_size': self.image_size,
            'image_dimensions': self.image_dimensions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<FaceData person_id={self.person_mapping_id}, name={self.face_name}>'