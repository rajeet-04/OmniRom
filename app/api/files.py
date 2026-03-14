"""File romanization endpoint."""

import io
import os
import csv

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from app.core.detector import detect_script, get_script_type
from app.engines.router import route_romanization

router = APIRouter(prefix="/v1/romanize", tags=["files"])

ALLOWED_EXTENSIONS = {".txt", ".csv", ".srt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _romanize_line(text: str, style: str) -> str:
    """Romanize a single line of text."""
    if not text.strip():
        return text
    detection = detect_script(text)
    script_type = get_script_type(detection["language"], detection["script"])
    script_code = detection.get("script_code", "")
    romanized, _ = route_romanization(text, script_type, script_code, style)
    return romanized


async def _process_text_file(text: str, style: str) -> str:
    """Process plain text file line by line."""
    lines = text.split("\n")
    results = [_romanize_line(line, style) if line.strip() else line for line in lines]
    return "\n".join(results)


async def _process_csv_file(text: str, style: str) -> str:
    """Process CSV file - romanize cells with non-ASCII content."""
    reader = csv.reader(io.StringIO(text))
    output = io.StringIO()
    writer = csv.writer(output)

    for row in reader:
        new_row = []
        for cell in row:
            if cell.strip() and any(ord(c) > 127 for c in cell):
                new_row.append(_romanize_line(cell, style))
            else:
                new_row.append(cell)
        writer.writerow(new_row)

    return output.getvalue()


async def _process_srt_file(text: str, style: str) -> str:
    """Process SRT subtitle file - romanize subtitle text lines.

    Handles two formats:
    1. Standard SRT: subtitle number, timestamp, text (blank line between blocks)
    2. Simple timestamp format: each line is [timestamp] text (no blank lines)
    """
    import re

    # First, check if this is standard SRT format (has blank lines between blocks)
    # Standard SRT has blocks like: "1\n[00:00:01] Text\n\n2\n[00:00:02] Text"
    lines = text.strip().split("\n")

    # Pattern to detect timestamp line: [MM:SS.mmm] or [HH:MM:SS.mmm]
    timestamp_pattern = re.compile(r"^\[\d{1,2}:\d{2}\.\d{2,3}\]")

    # Check if lines look like they start with timestamps (simple format)
    has_timestamps = any(
        timestamp_pattern.match(line.strip()) for line in lines if line.strip()
    )

    if not has_timestamps:
        # Standard SRT format with blank lines
        result_lines = []
        blocks = text.strip().split("\n\n")

        for block in blocks:
            lines = block.split("\n")
            if len(lines) >= 3:
                result_lines.append(lines[0])  # Subtitle number
                result_lines.append(lines[1])  # Timestamp line
                subtitle_text = " ".join(lines[2:])
                result_lines.append(_romanize_line(subtitle_text, style))
                result_lines.append("")
            else:
                result_lines.append(block)

        return "\n".join(result_lines)

    # Simple timestamp format: each line is [timestamp] text
    # e.g., [00:31.98] من ڈھولے
    result_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line starts with timestamp
        match = timestamp_pattern.match(line)
        if match:
            # Extract timestamp and text
            timestamp_end = match.end()
            timestamp = line[:timestamp_end]
            subtitle_text = line[timestamp_end:].strip()

            # Romanize the subtitle text
            if subtitle_text:
                romanized = _romanize_line(subtitle_text, style)
                result_lines.append(f"{timestamp} {romanized}")
            else:
                result_lines.append(line)
        else:
            # Pass through non-timestamp lines as-is
            result_lines.append(line)

    return "\n".join(result_lines)


@router.post("/file")
async def romanize_file(
    file: UploadFile = File(...),
    style: str = Form("standard"),
):
    """
    Process a text file and return romanized content.

    Supported formats: .txt, .csv, .srt (max 10 MB).
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid UTF-8 encoding")

    if ext == ".txt":
        result = await _process_text_file(text, style)
    elif ext == ".csv":
        result = await _process_csv_file(text, style)
    elif ext == ".srt":
        result = await _process_srt_file(text, style)
    else:
        result = text

    output = io.BytesIO(result.encode("utf-8"))
    return StreamingResponse(
        output,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="romanized_{file.filename}"'
        },
    )
