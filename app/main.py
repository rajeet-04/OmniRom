from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.romanize import router as romanize_router
from app.api.batch import router as batch_router
from app.api.files import router as files_router
from app.api.languages import router as languages_router
from app.api.cache import router as cache_router
from app.api.stats import router as stats_router
from app.middleware.logging import LoggingMiddleware

app = FastAPI(
    title="OmniRom API",
    description="Universal Romanization Service - Convert any script to Latin",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(romanize_router)
app.include_router(batch_router)
app.include_router(files_router)
app.include_router(languages_router)
app.include_router(cache_router)
app.include_router(stats_router)


@app.get("/")
def root():
    return {"message": "OmniRom API", "version": "0.1.0"}


@app.get("/health")
def health():
    from app.core.cache import get_cache
    cache = get_cache()
    return {
        "status": "healthy",
        "cache_enabled": cache.enabled,
    }
