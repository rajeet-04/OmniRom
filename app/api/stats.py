"""Statistics endpoint."""

from fastapi import APIRouter

from app.core.stats import get_stats

router = APIRouter(prefix="/v1", tags=["stats"])


@router.get("/stats")
async def get_statistics():
    """Get API usage statistics."""
    stats = get_stats()
    return stats.get_stats()
