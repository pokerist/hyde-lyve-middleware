import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models import ResidentMapping, SyncLog, QrCode
from app.hikcentral_client import HikCentralClient
from app.circuit_breaker import get_circuit_breaker
from app.config import settings

logger = logging.getLogger(__name__)

class ResidentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.hikcentral_client = HikCentralClient()
        self.circuit_breaker = get_circuit_breaker()
    
    async def check_resident(self, email: str, community: str) -> Optional[ResidentMapping]:
        """Check if resident exists in local database"""
        try:
            stmt = select(ResidentMapping).where(
                and_(
                    ResidentMapping.email == email,
                    ResidentMapping.community == community,
                    ResidentMapping.is_active == True
                )
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error checking resident {email}@{community}: {e}")
            return None
    
    def split_name(self, full_name: str) -> tuple[str, str]:
        """Split full name into first and last name"""
        if not full_name:
            return "", ""
        
        parts = full_name.strip().split()
        if len(parts) == 1:
            return parts[0], ""
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            # For names with more than 2 parts, first is first name, rest is last name
            return parts[0], " ".join(parts[1:])
    
    async def create_resident(self, resident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create resident in HikCentral and store mapping"""
        start_time = datetime.now()
        operation = "CREATE"
        
        try:
            email = resident_data["email"]
            community = resident_data["community"]
            name = resident_data["name"]
            
            # Check if resident already exists
            existing_resident = await self.check_resident(email, community)
            if existing_resident:
                await self._log_sync(
                    operation=operation,
                    email=email,
                    community=community,
                    status_code=409,
                    error_message="Resident already exists",
                    response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )
                return {
                    "success": False,
                    "error": "Resident already exists",
                    "ownerId": existing_resident.owner_id,
                    "status_code": 409
                }
            
            # Generate unique IDs
            owner_id = str(uuid.uuid4())
            hikcentral_person_id = f"LYVE_{owner_id}"
            
            # Split name for HikCentral
            first_name, last_name = self.split_name(name)
            
            # Prepare HikCentral person data
            person_data = {
                "personCode": hikcentral_person_id,
                "personFamilyName": last_name,
                "personGivenName": first_name,
                "gender": 1,  # Default to male
                "orgIndexCode": self.hikcentral_client.org_index_code,
                "phoneNo": resident_data.get("phone", ""),
                "email": email,
                "certificateType": 111,  # ID card
                "certificateNum": "",  # Could be added if needed
                "personType": 1,  # Normal person
                "beginTime": resident_data.get("fromDate", datetime.now().strftime("%Y-%m-%dT%H:%M:%S")),
                "endTime": resident_data.get("toDate", (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S"))
            }
            
            # Create person in HikCentral with circuit breaker
            try:
                hikcentral_response = await self.circuit_breaker.call(
                    self.hikcentral_client.add_person,
                    person_data
                )
            except Exception as e:
                await self._log_sync(
                    operation=operation,
                    email=email,
                    community=community,
                    status_code=503,
                    error_message=f"Circuit breaker open: {str(e)}",
                    response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )
                return {
                    "success": False,
                    "error": "Service temporarily unavailable",
                    "status_code": 503
                }
            
            # Log HikCentral response
            await self._log_sync(
                operation=operation,
                email=email,
                community=community,
                owner_id=owner_id,
                unit_id=resident_data.get("unitId"),
                hikcentral_person_id=hikcentral_person_id,
                hikcentral_response=json.dumps(hikcentral_response) if hikcentral_response else None,
                status_code=201 if hikcentral_response and hikcentral_response.get("success") else 500,
                error_message=hikcentral_response.get("message") if hikcentral_response and not hikcentral_response.get("success") else None,
                response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
            
            if not hikcentral_response or not hikcentral_response.get("success"):
                error_msg = hikcentral_response.get("message", "Failed to create person in HikCentral") if hikcentral_response else "HikCentral service error"
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": 500
                }
            
            # Create resident mapping in local database
            resident = ResidentMapping(
                email=email,
                community=community,
                hikcentral_person_id=hikcentral_person_id,
                owner_id=owner_id,
                unit_id=resident_data.get("unitId", ""),
                name=name,
                first_name=first_name,
                last_name=last_name,
                phone=resident_data.get("phone", ""),
                owner_type=resident_data.get("ownerType", ""),
                from_date=datetime.fromisoformat(resident_data.get("fromDate", datetime.now().isoformat())),
                to_date=datetime.fromisoformat(resident_data.get("toDate", (datetime.now() + timedelta(days=365)).isoformat())),
                is_active=True
            )
            
            self.db.add(resident)
            await self.db.commit()
            await self.db.refresh(resident)
            
            return {
                "success": True,
                "ownerId": owner_id,
                "email": email,
                "community": community,
                "name": name,
                "firstName": first_name,
                "lastName": last_name,
                "phone": resident.phone,
                "ownerType": resident.owner_type,
                "unitId": resident.unit_id,
                "fromDate": resident.from_date.isoformat(),
                "toDate": resident.to_date.isoformat(),
                "status_code": 201
            }
            
        except Exception as e:
            logger.error(f"Error creating resident {email}@{community}: {e}")
            await self.db.rollback()
            await self._log_sync(
                operation=operation,
                email=email,
                community=community,
                status_code=500,
                error_message=str(e),
                response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }
    
    async def delete_resident(self, owner_id: str, unit_id: str) -> Dict[str, Any]:
        """Delete resident from HikCentral and local database"""
        start_time = datetime.now()
        operation = "DELETE"
        
        try:
            # Find resident by owner_id and unit_id
            stmt = select(ResidentMapping).where(
                and_(
                    ResidentMapping.owner_id == owner_id,
                    ResidentMapping.unit_id == unit_id,
                    ResidentMapping.is_active == True
                )
            )
            result = await self.db.execute(stmt)
            resident = result.scalar_one_or_none()
            
            if not resident:
                await self._log_sync(
                    operation=operation,
                    owner_id=owner_id,
                    unit_id=unit_id,
                    status_code=404,
                    error_message="Resident not found",
                    response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )
                return {
                    "success": False,
                    "error": "Resident not found",
                    "status_code": 404
                }
            
            # Delete from HikCentral with circuit breaker
            try:
                hikcentral_response = await self.circuit_breaker.call(
                    self.hikcentral_client.delete_person,
                    resident.hikcentral_person_id
                )
            except Exception as e:
                await self._log_sync(
                    operation=operation,
                    owner_id=owner_id,
                    unit_id=unit_id,
                    hikcentral_person_id=resident.hikcentral_person_id,
                    status_code=503,
                    error_message=f"Circuit breaker open: {str(e)}",
                    response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )
                return {
                    "success": False,
                    "error": "Service temporarily unavailable",
                    "status_code": 503
                }
            
            # Log HikCentral response
            await self._log_sync(
                operation=operation,
                email=resident.email,
                community=resident.community,
                owner_id=owner_id,
                unit_id=unit_id,
                hikcentral_person_id=resident.hikcentral_person_id,
                hikcentral_response=json.dumps(hikcentral_response) if hikcentral_response else None,
                status_code=200 if hikcentral_response and hikcentral_response.get("success") else 500,
                error_message=hikcentral_response.get("message") if hikcentral_response and not hikcentral_response.get("success") else None,
                response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
            
            if not hikcentral_response or not hikcentral_response.get("success"):
                error_msg = hikcentral_response.get("message", "Failed to delete person from HikCentral") if hikcentral_response else "HikCentral service error"
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": 500
                }
            
            # Mark as inactive in local database
            resident.is_active = False
            await self.db.commit()
            
            return {
                "success": True,
                "status_code": 200
            }
            
        except Exception as e:
            logger.error(f"Error deleting resident {owner_id}@{unit_id}: {e}")
            await self.db.rollback()
            await self._log_sync(
                operation=operation,
                owner_id=owner_id,
                unit_id=unit_id,
                status_code=500,
                error_message=str(e),
                response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }
    
    async def generate_qr_code(self, unit_id: str, owner_id: str, validity_minutes: int = 60) -> Dict[str, Any]:
        """Generate QR code for resident"""
        start_time = datetime.now()
        operation = "QR_CODE"
        
        try:
            # Find resident
            stmt = select(ResidentMapping).where(
                and_(
                    ResidentMapping.owner_id == owner_id,
                    ResidentMapping.unit_id == unit_id,
                    ResidentMapping.is_active == True
                )
            )
            result = await self.db.execute(stmt)
            resident = result.scalar_one_or_none()
            
            if not resident:
                await self._log_sync(
                    operation=operation,
                    owner_id=owner_id,
                    unit_id=unit_id,
                    status_code=404,
                    error_message="Resident not found",
                    response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )
                return {
                    "success": False,
                    "error": "Resident not found",
                    "status_code": 404
                }
            
            # Generate QR code with circuit breaker
            try:
                hikcentral_response = await self.circuit_breaker.call(
                    self.hikcentral_client.generate_qr_code,
                    resident.hikcentral_person_id,
                    unit_id,
                    validity_minutes
                )
            except Exception as e:
                await self._log_sync(
                    operation=operation,
                    email=resident.email,
                    community=resident.community,
                    owner_id=owner_id,
                    unit_id=unit_id,
                    hikcentral_person_id=resident.hikcentral_person_id,
                    status_code=503,
                    error_message=f"Circuit breaker open: {str(e)}",
                    response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )
                return {
                    "success": False,
                    "error": "Service temporarily unavailable",
                    "status_code": 503
                }
            
            # Log HikCentral response
            await self._log_sync(
                operation=operation,
                email=resident.email,
                community=resident.community,
                owner_id=owner_id,
                unit_id=unit_id,
                hikcentral_person_id=resident.hikcentral_person_id,
                hikcentral_response=json.dumps(hikcentral_response) if hikcentral_response else None,
                status_code=200 if hikcentral_response and hikcentral_response.get("success") else 500,
                error_message=hikcentral_response.get("message") if hikcentral_response and not hikcentral_response.get("success") else None,
                response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
            
            if not hikcentral_response or not hikcentral_response.get("success"):
                error_msg = hikcentral_response.get("message", "Failed to generate QR code") if hikcentral_response else "HikCentral service error"
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": 500
                }
            
            # Extract QR code data
            qr_data = hikcentral_response.get("data", {})
            qr_code_base64 = qr_data.get("qrCode", "")
            expires_at_str = qr_data.get("expiresAt", "")
            
            if not qr_code_base64:
                return {
                    "success": False,
                    "error": "No QR code data received",
                    "status_code": 500
                }
            
            # Parse expires_at
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00')) if expires_at_str else datetime.now() + timedelta(minutes=validity_minutes)
            except:
                expires_at = datetime.now() + timedelta(minutes=validity_minutes)
            
            # Store QR code in database
            qr_code = QrCode(
                owner_id=owner_id,
                unit_id=unit_id,
                qr_code_data=qr_code_base64,
                expires_at=expires_at,
                validity_minutes=validity_minutes,
                is_used=False
            )
            
            self.db.add(qr_code)
            await self.db.commit()
            
            return {
                "success": True,
                "qrCode": qr_code_base64,
                "expiresAt": expires_at.isoformat(),
                "status_code": 200
            }
            
        except Exception as e:
            logger.error(f"Error generating QR code for {owner_id}@{unit_id}: {e}")
            await self.db.rollback()
            await self._log_sync(
                operation=operation,
                owner_id=owner_id,
                unit_id=unit_id,
                status_code=500,
                error_message=str(e),
                response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
            return {
                "success": False,
                "error": "Internal server error",
                "status_code": 500
            }
    
    async def _log_sync(self, operation: str, **kwargs) -> None:
        """Log sync operation for audit trail"""
        try:
            log_entry = SyncLog(
                operation=operation,
                email=kwargs.get("email"),
                community=kwargs.get("community"),
                owner_id=kwargs.get("owner_id"),
                unit_id=kwargs.get("unit_id"),
                hikcentral_person_id=kwargs.get("hikcentral_person_id"),
                hikcentral_response=kwargs.get("hikcentral_response"),
                status_code=kwargs.get("status_code"),
                error_message=kwargs.get("error_message"),
                response_time_ms=kwargs.get("response_time_ms"),
                request_data=json.dumps(kwargs.get("request_data", {})) if kwargs.get("request_data") else None,
                response_data=json.dumps(kwargs.get("response_data", {})) if kwargs.get("response_data") else None
            )
            
            self.db.add(log_entry)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Error logging sync operation: {e}")
            await self.db.rollback()