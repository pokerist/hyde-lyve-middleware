from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import redis.asyncio as redis
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any

from app.config import settings
from app.models import ResidentMapping, SyncLog, QrCode, get_db, create_database_engine, test_database_connection
from app.resident_service import ResidentService
from app.circuit_breaker import initialize_circuit_breaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Hydepark Lyve Middleware MVP",
    description="MVP API for Lyve Access Control and HikCentral integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global variables
redis_client = None
database_engine = None

# Startup event
@app.on_event("startup")
async def startup_event():
    global redis_client, database_engine
    
    logger.info("🚀 Starting Hydepark Lyve Middleware MVP...")
    
    try:
        # Initialize database engine
        logger.info("🗄️ Initializing database connection...")
        database_engine = create_database_engine(settings.database_url)
        logger.info("✅ Database engine created")
        
        # Test database connection
        logger.info("🧪 Testing database connection...")
        if await test_database_connection():
            logger.info("✅ Database connection successful")
        else:
            logger.error("❌ Database connection failed")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.info("💡 Make sure PostgreSQL is running and accessible")
    
    # Initialize Redis
    try:
        logger.info("🔄 Initializing Redis connection...")
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Redis connected successfully")
        
        # Initialize circuit breaker
        await initialize_circuit_breaker(redis_client)
        logger.info("✅ Circuit breaker initialized")
        
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        logger.info("💡 Circuit breaker will use in-memory fallback")
        await initialize_circuit_breaker(None)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down Hydepark Lyve Middleware...")
    
    if redis_client:
        await redis_client.close()
        logger.info("✅ Redis connection closed")

# API Key dependency
async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key from header"""
    if not settings.require_api_key:
        return "demo-key"
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required"
        )
    
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return x_api_key

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": "unknown",
            "redis": "unknown"
        }
    }
    
    # Check database
    try:
        if database_engine:
            async with AsyncSession(database_engine) as session:
                result = await session.execute("SELECT 1")
                await result.fetchone()
                health_status["services"]["database"] = "healthy"
        else:
            health_status["services"]["database"] = "not_initialized"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        if redis_client:
            await redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not_configured"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    
    return health_status

# API Endpoints as specified in MVP

@app.post("/api/v1/residents/check")
async def check_resident(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if resident exists in local database
    Input: {"email": "...", "community": "..."}
    Output: Full resident object or 404
    """
    try:
        email = request.get("email")
        community = request.get("community")
        
        if not email or not community:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both email and community are required"
            )
        
        logger.info(f"🔍 Checking resident: {email}@{community}")
        
        service = ResidentService(db)
        resident = await service.check_resident(email, community)
        
        if not resident:
            logger.warning(f"❌ Resident not found: {email}@{community}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resident not found"
            )
        
        logger.info(f"✅ Resident found: {email}@{community}")
        return resident.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error checking resident: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/v1/residents/create", status_code=status.HTTP_201_CREATED)
async def create_resident(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Create resident
    Input: {"name": "...", "phone": "...", "email": "...", "community": "...", "fromDate": "...", "toDate": "...", "ownerType": "...", "unitId": "..."}
    Output: Created resident with ownerId
    """
    try:
        # Validate required fields
        required_fields = ["name", "email", "community", "fromDate", "toDate", "ownerType", "unitId"]
        for field in required_fields:
            if field not in request or not request[field]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field} is required"
                )
        
        logger.info(f"👤 Creating resident: {request['email']}@{request['community']}")
        
        service = ResidentService(db)
        result = await service.create_resident(request)
        
        if not result["success"]:
            if result.get("status_code") == 409:
                logger.warning(f"⚠️ Resident already exists: {request['email']}@{request['community']}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=result["error"]
                )
            elif result.get("status_code") == 503:
                logger.error(f"🔒 Circuit breaker open: {result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=result["error"]
                )
            else:
                logger.error(f"❌ Failed to create resident: {result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["error"]
                )
        
        logger.info(f"✅ Resident created successfully: {result['ownerId']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating resident: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.delete("/api/v1/residents/")
async def delete_resident(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete resident
    Input: {"ownerId": "...", "unitID": "..."}
    Output: {"success": true}
    """
    try:
        owner_id = request.get("ownerId")
        unit_id = request.get("unitID")
        
        if not owner_id or not unit_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both ownerId and unitID are required"
            )
        
        logger.info(f"🗑️ Deleting resident: {owner_id}@{unit_id}")
        
        service = ResidentService(db)
        result = await service.delete_resident(owner_id, unit_id)
        
        if not result["success"]:
            if result.get("status_code") == 404:
                logger.warning(f"❌ Resident not found: {owner_id}@{unit_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["error"]
                )
            elif result.get("status_code") == 503:
                logger.error(f"🔒 Circuit breaker open: {result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=result["error"]
                )
            else:
                logger.error(f"❌ Failed to delete resident: {result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["error"]
                )
        
        logger.info(f"✅ Resident deleted successfully: {owner_id}@{unit_id}")
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting resident: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/v1/qrcodes/resident")
async def generate_qr_code(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate QR code for resident
    Input: {"unitId": "...", "ownerId": "...", "validityMinutes": 60}
    Output: {"qrCode": "base64string", "expiresAt": "..."}
    """
    try:
        unit_id = request.get("unitId")
        owner_id = request.get("ownerId")
        validity_minutes = request.get("validityMinutes", 60)
        
        if not unit_id or not owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both unitId and ownerId are required"
            )
        
        logger.info(f"📱 Generating QR code for: {owner_id}@{unit_id}")
        
        service = ResidentService(db)
        result = await service.generate_qr_code(unit_id, owner_id, validity_minutes)
        
        if not result["success"]:
            if result.get("status_code") == 404:
                logger.warning(f"❌ Resident not found: {owner_id}@{unit_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["error"]
                )
            elif result.get("status_code") == 503:
                logger.error(f"🔒 Circuit breaker open: {result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=result["error"]
                )
            else:
                logger.error(f"❌ Failed to generate QR code: {result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["error"]
                )
        
        logger.info(f"✅ QR code generated successfully for: {owner_id}@{unit_id}")
        return {
            "qrCode": result["qrCode"],
            "expiresAt": result["expiresAt"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )