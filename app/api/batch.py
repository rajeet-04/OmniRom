"""Batch romanization endpoint."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.detector import detect_script, get_script_type
from app.core.cache import get_cache
from app.core.stats import get_stats
from app.engines.router import route_romanization

router = APIRouter(prefix="/v1/romanize", tags=["batch"])

MAX_BATCH_SIZE = 100


class BatchRequest(BaseModel):
    texts: List[str] = Field(
        ..., description="List of texts to romanize (max 100)"
    )
    style: str = Field("standard", description="Romanization style")


class BatchItemResult(BaseModel):
    original: str
    romanized: str
    metadata: dict


class BatchResponse(BaseModel):
    results: List[BatchItemResult]
    total: int
    cached_count: int
    processing_time_ms: int


def _romanize_single(text: str, style: str, cache) -> BatchItemResult:
    """Process a single text item (runs in thread pool)."""
    if not text or not text.strip():
        return BatchItemResult(
            original=text,
            romanized=text,
            metadata={"cached": False, "detected_lang": "und"},
        )

    # Check cache
    cached_result = cache.get(text, style) if cache.enabled else None
    if cached_result:
        return BatchItemResult(
            original=text,
            romanized=cached_result["romanized"],
            metadata={**cached_result["metadata"], "cached": True},
        )

    detection = detect_script(text)
    script_type = get_script_type(detection["language"], detection["script"])
    script_code = detection.get("script_code", "")

    romanized, engine_used = route_romanization(text, script_type, script_code, style)

    meta = {
        "detected_lang": detection["language"],
        "engine_used": engine_used,
        "cached": False,
    }

    if cache.enabled:
        cache.set(text, romanized, meta, style)

    return BatchItemResult(original=text, romanized=romanized, metadata=meta)


@router.post("/batch", response_model=BatchResponse)
async def romanize_batch(request: BatchRequest):
    """Romanize multiple texts in a single request (max 100)."""
    if not request.texts:
        raise HTTPException(status_code=400, detail="Texts list cannot be empty")

    if len(request.texts) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_BATCH_SIZE} texts per batch",
        )

    start_time = time.time()
    cache = get_cache()
    stats = get_stats()

    results: List[BatchItemResult] = [None] * len(request.texts)

    with ThreadPoolExecutor(max_workers=min(10, len(request.texts))) as executor:
        future_to_idx = {
            executor.submit(_romanize_single, text, request.style, cache): i
            for i, text in enumerate(request.texts)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                results[idx] = BatchItemResult(
                    original=request.texts[idx],
                    romanized=request.texts[idx],
                    metadata={"error": str(e), "cached": False},
                )

    cached_count = sum(1 for r in results if r.metadata.get("cached", False))
    stats.record_request()

    return BatchResponse(
        results=results,
        total=len(results),
        cached_count=cached_count,
        processing_time_ms=int((time.time() - start_time) * 1000),
    )
