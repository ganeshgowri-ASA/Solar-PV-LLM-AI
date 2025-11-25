"""
API V1 Router
Aggregates all API endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, solar_pv, ml_models, rag, training

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(solar_pv.router, prefix="/solar-pv", tags=["Solar PV"])
api_router.include_router(ml_models.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(training.router, prefix="/training", tags=["Training"])
