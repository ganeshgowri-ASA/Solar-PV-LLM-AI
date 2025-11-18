"""
Health Check Endpoints
System health and readiness checks
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
import time
import redis.asyncio as redis
from app.core.config import settings

router = APIRouter()


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"status": "pong", "timestamp": time.time()}


@router.get("/liveness")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": time.time()}


@router.get("/readiness")
async def readiness(db: AsyncSession = Depends(get_db)):
    """
    Kubernetes readiness probe
    Checks all critical dependencies
    """
    checks = {
        "database": False,
        "redis": False,
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        checks["database"] = result.scalar() == 1
    except Exception as e:
        checks["database_error"] = str(e)

    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        checks["redis"] = True
        await redis_client.close()
    except Exception as e:
        checks["redis_error"] = str(e)

    # Determine overall status
    all_healthy = checks["database"] and checks["redis"]

    return {
        "status": "ready" if all_healthy else "not_ready",
        "timestamp": time.time(),
        "checks": checks,
    }
