"""Search router for Solar PV standards."""

from fastapi import APIRouter, HTTPException
from typing import List

from ..models.schemas import SearchRequest, SearchResponse
from ..services.rag_service import rag_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/standards", response_model=SearchResponse)
async def search_standards(request: SearchRequest):
    """
    Search solar PV standards database.

    Args:
        request: Search request with query and filters

    Returns:
        Matching standards with relevance scores
    """
    try:
        results, total_count, categories_found = await rag_service.search_standards(
            query=request.query,
            categories=request.categories,
            max_results=request.max_results,
            include_summaries=request.include_summaries
        )

        return SearchResponse(
            results=results,
            total_count=total_count,
            query=request.query,
            categories_found=categories_found
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/categories", response_model=List[str])
async def get_categories():
    """
    Get all available standard categories.

    Returns:
        List of category names
    """
    return rag_service.get_categories()


@router.get("/health")
async def search_health():
    """Health check for search service."""
    return {"status": "healthy", "service": "search"}
