import asyncio
import time
import logging
from typing import Optional, Callable, Any
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker pattern implementation using Redis"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        redis_client: Optional[redis.Redis] = None
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.redis_client = redis_client
        self.state_key = "circuit_breaker:state"
        self.failure_count_key = "circuit_breaker:failure_count"
        self.last_failure_time_key = "circuit_breaker:last_failure_time"
        
    async def get_state(self) -> str:
        """Get current circuit breaker state"""
        if not self.redis_client:
            return "CLOSED"  # Default to closed if Redis not available
        
        state = await self.redis_client.get(self.state_key)
        return state.decode() if state else "CLOSED"
    
    async def set_state(self, state: str):
        """Set circuit breaker state"""
        if not self.redis_client:
            return
        
        await self.redis_client.set(self.state_key, state)
        logger.info(f"Circuit breaker state changed to: {state}")
    
    async def get_failure_count(self) -> int:
        """Get current failure count"""
        if not self.redis_client:
            return 0
        
        count = await self.redis_client.get(self.failure_count_key)
        return int(count.decode()) if count else 0
    
    async def increment_failure_count(self) -> int:
        """Increment failure count and return new count"""
        if not self.redis_client:
            return 0
        
        count = await self.redis_client.incr(self.failure_count_key)
        await self.redis_client.set(self.last_failure_time_key, str(int(time.time())))
        return count
    
    async def reset_failure_count(self):
        """Reset failure count to zero"""
        if not self.redis_client:
            return
        
        await self.redis_client.delete(self.failure_count_key)
        await self.redis_client.delete(self.last_failure_time_key)
        logger.info("Circuit breaker failure count reset")
    
    async def should_allow_request(self) -> bool:
        """Check if request should be allowed"""
        state = await self.get_state()
        
        if state == "CLOSED":
            return True
        elif state == "OPEN":
            # Check if recovery timeout has passed
            last_failure_time = await self.redis_client.get(self.last_failure_time_key)
            if last_failure_time:
                last_time = int(last_failure_time.decode())
                current_time = int(time.time())
                if current_time - last_time >= self.recovery_timeout:
                    # Transition to HALF_OPEN
                    await self.set_state("HALF_OPEN")
                    logger.info("Circuit breaker transitioning to HALF_OPEN state")
                    return True
            return False
        elif state == "HALF_OPEN":
            # Allow limited requests in half-open state
            return True
        
        return True
    
    async def record_success(self):
        """Record a successful request"""
        state = await self.get_state()
        
        if state == "HALF_OPEN":
            # Success in half-open state, close the circuit
            await self.reset_failure_count()
            await self.set_state("CLOSED")
            logger.info("Circuit breaker closed due to successful request")
        elif state == "CLOSED":
            # Reset failure count on success in closed state
            await self.reset_failure_count()
    
    async def record_failure(self):
        """Record a failed request"""
        state = await self.get_state()
        
        if state == "HALF_OPEN":
            # Failure in half-open state, reopen the circuit
            await self.set_state("OPEN")
            logger.warning("Circuit breaker reopened due to failure in HALF_OPEN state")
        elif state == "CLOSED":
            # Increment failure count
            count = await self.increment_failure_count()
            if count >= self.failure_threshold:
                # Open the circuit
                await self.set_state("OPEN")
                logger.error(f"Circuit breaker opened due to {count} consecutive failures")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with circuit breaker protection"""
        if not await self.should_allow_request():
            raise Exception("Circuit breaker is OPEN - requests not allowed")
        
        try:
            result = await func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception as e:
            await self.record_failure()
            raise e

# Global circuit breaker instance
circuit_breaker = None

def get_circuit_breaker() -> CircuitBreaker:
    """Get or create circuit breaker instance"""
    global circuit_breaker
    if circuit_breaker is None:
        circuit_breaker = CircuitBreaker(
            failure_threshold=settings.circuit_breaker_failure_threshold,
            recovery_timeout=settings.circuit_breaker_recovery_timeout
        )
    return circuit_breaker

async def initialize_circuit_breaker(redis_client: redis.Redis):
    """Initialize circuit breaker with Redis client"""
    global circuit_breaker
    circuit_breaker = CircuitBreaker(
        failure_threshold=settings.circuit_breaker_failure_threshold,
        recovery_timeout=settings.circuit_breaker_recovery_timeout,
        redis_client=redis_client
    )
    logger.info("Circuit breaker initialized")