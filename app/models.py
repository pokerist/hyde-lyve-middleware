from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class ResidentMapping(Base):
    __tablename__ = "resident_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    community = Column(String(255), nullable=False, index=True)
    hikcentral_person_id = Column(String(255), nullable=False, unique=True, index=True)
    owner_id = Column(String(255), nullable=False, unique=True, index=True)
    unit_id = Column(String(255), nullable=False)
    
    # Resident information
    name = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    owner_type = Column(String(50), nullable=True)
    
    # Date range
    from_date = Column(DateTime, nullable=False)
    to_date = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_email_community', 'email', 'community', unique=True),
        Index('idx_owner_id', 'owner_id'),
        Index('idx_unit_id', 'unit_id'),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "community": self.community,
            "hikcentral_person_id": self.hikcentral_person_id,
            "owner_id": self.owner_id,
            "unit_id": self.unit_id,
            "name": self.name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "owner_type": self.owner_type,
            "from_date": self.from_date.isoformat() if self.from_date else None,
            "to_date": self.to_date.isoformat() if self.to_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class SyncLog(Base):
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, CHECK, QR_CODE
    email = Column(String(255), nullable=True, index=True)
    community = Column(String(255), nullable=True, index=True)
    owner_id = Column(String(255), nullable=True, index=True)
    unit_id = Column(String(255), nullable=True, index=True)
    
    # Request/response data
    request_data = Column(Text, nullable=True)
    response_data = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # HikCentral specific
    hikcentral_person_id = Column(String(255), nullable=True, index=True)
    hikcentral_response = Column(Text, nullable=True)
    
    # Timing and performance
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_ms = Column(Integer, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "operation": self.operation,
            "email": self.email,
            "community": self.community,
            "owner_id": self.owner_id,
            "unit_id": self.unit_id,
            "request_data": self.request_data,
            "response_data": self.response_data,
            "status_code": self.status_code,
            "error_message": self.error_message,
            "hikcentral_person_id": self.hikcentral_person_id,
            "hikcentral_response": self.hikcentral_response,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "response_time_ms": self.response_time_ms,
        }

class QrCode(Base):
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(String(255), nullable=False, index=True)
    unit_id = Column(String(255), nullable=False, index=True)
    qr_code_data = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    validity_minutes = Column(Integer, nullable=False, default=60)
    
    # Status
    is_used = Column(Boolean, default=False, index=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "unit_id": self.unit_id,
            "qr_code_data": self.qr_code_data,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "validity_minutes": self.validity_minutes,
            "is_used": self.is_used,
            "used_at": self.used_at.isoformat() if self.used_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# Database engine and session factory
engine = None
AsyncSessionLocal = None

def create_database_engine(database_url: str):
    global engine, AsyncSessionLocal
    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()