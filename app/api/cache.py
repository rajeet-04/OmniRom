"""Cache management endpoints."""

from fastapi import APIRouter

from app.core.cache import get_cache

router = APIRouter(prefix="/v1", tags=["cache"])


@router.get("/cache/stats")
async def cache_stats():
    """Get Redis cache statistics."""
    cache = get_cache()

    if not cache.enabled:
        return {
            "enabled": False,
            "message": "Cache not configured. Set REDIS_URL environment variable.",
        }

    try:
        info = cache.client.info("stats")
        return {
            "enabled": True,
            "keys": cache.client.dbsize(),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
        }
    except Exception:
        return {"enabled": True, "keys": "unknown"}


@router.post("/cache/clear")
async def clear_cache():
    """Clear all cached romanization entries."""
    cache = get_cache()
    if not cache.enabled:
        return {"success": False, "message": "Cache not enabled"}

    cache.clear()
    return {"success": True, "message": "Cache cleared"}
