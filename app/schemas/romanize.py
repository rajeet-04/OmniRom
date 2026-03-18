"""Request and response schemas for romanization endpoints."""

from pydantic import BaseModel, Field
from typing import Optional


class RomanizeRequest(BaseModel):
    text: str = Field(..., description="Text to romanize", min_length=1)
    source_lang: Optional[str] = Field(
        "auto", description="Source language (auto-detect if not specified)"
    )
    style: Optional[str] = Field(
        "standard",
        description="Romanization style: standard, academic, chat, phonetic",
    )


class RomanizeResponse(BaseModel):
    original: str
    romanized: str
    metadata: dict
