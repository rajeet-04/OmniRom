"""Single romanization endpoint."""

import time
from fastapi import APIRouter, HTTPException

from app.schemas.romanize import RomanizeRequest, RomanizeResponse
from app.core.detector import detect_script, get_script_type
from app.engines.router import route_romanization, get_supported_engines
from app.core.cache import get_cache
from app.core.stats import get_stats

router = APIRouter(prefix="/v1", tags=["romanize"])


@router.post("/romanize", response_model=RomanizeResponse)
async def romanize(request: RomanizeRequest):
    """Romanize text from any script to Latin."""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    start_time = time.time()
    style = request.style or "standard"
    stats = get_stats()

    # Check cache first
    cache = get_cache()
    cached = None
    if cache.enabled:
        cached = cache.get(request.text, style)

    if cached:
        stats.record_cache(hit=True)
        stats.record_request(
            language=cached["metadata"].get("detected_lang"),
            engine=cached["metadata"].get("engine_used"),
        )
        cached["metadata"]["cached"] = True
        cached["metadata"]["processing_time_ms"] = int(
            (time.time() - start_time) * 1000
        )
        return RomanizeResponse(
            original=request.text,
            romanized=cached["romanized"],
            metadata=cached["metadata"],
        )

    try:
        detection = detect_script(request.text)
        script_type = get_script_type(detection["language"], detection["script"])
        script_code = detection.get("script_code", "")

        romanized, engine_used = route_romanization(
            request.text,
            script_type,
            script_code,
            style,
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        metadata = {
            "detected_lang": detection["language"],
            "detected_script": detection["script"],
            "engine_used": engine_used,
            "cached": False,
            "processing_time_ms": processing_time_ms,
        }

        if cache.enabled:
            cache.set(request.text, romanized, metadata, style)
        stats.record_cache(hit=False)
        stats.record_request(language=detection["language"], engine=engine_used)

        return RomanizeResponse(
            original=request.text,
            romanized=romanized,
            metadata=metadata,
        )
    except Exception as e:
        stats.record_error()
        raise HTTPException(
            status_code=500, detail=f"Romanization failed: {str(e)}"
        )


@router.get("/engines")
async def list_engines():
    """List available romanization engines and their supported scripts."""
    return get_supported_engines()
