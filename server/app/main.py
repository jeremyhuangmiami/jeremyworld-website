from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import secrets
import shutil
import subprocess
import mimetypes
import tempfile


app = FastAPI(title="Free File Converters API")

# CORS for local dev and simple deployments; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path("/tmp/freefileconverters")
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
for d in (UPLOAD_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

MAX_MB = 100


def ensure_size_limit(temp_path: Path, max_mb: int = MAX_MB) -> None:
    size_mb = temp_path.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        raise HTTPException(status_code=413, detail="File too large")


def run_command(cmd: list[str], timeout_seconds: int = 180) -> None:
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
    except subprocess.CalledProcessError as e:
        message = e.stderr.decode("utf-8", "ignore")[:600] or str(e)
        raise HTTPException(status_code=400, detail=f"Conversion failed: {message}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Conversion timed out")


@app.get("/healthz")
def health() -> JSONResponse:
    return JSONResponse({"ok": True})


@app.post("/convert")
async def convert(file: UploadFile = File(...), target: str = Form(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    safe_id = secrets.token_hex(8)
    input_suffix = Path(file.filename).suffix.lower()
    input_path = UPLOAD_DIR / f"{safe_id}{input_suffix}"

    # Normalize target like ".pdf" or "pdf" -> "pdf"
    target = target.strip().lstrip(".").lower()
    if not target:
        raise HTTPException(status_code=400, detail="Missing target format")
    output_path = OUTPUT_DIR / f"{safe_id}.{target}"

    # Persist upload to disk for scanning/conversion
    with input_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    ensure_size_limit(input_path)

    mime = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""

    # Route to appropriate converter
    if mime.startswith("image/") or input_suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tiff", ".bmp"}:
        # ImageMagick
        run_command(["convert", str(input_path), str(output_path)])
    elif mime.startswith("audio/") or input_suffix in {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"}:
        # ffmpeg (audio)
        run_command(["ffmpeg", "-y", "-i", str(input_path), str(output_path)])
    elif mime.startswith("video/") or input_suffix in {".mp4", ".mov", ".mkv", ".avi", ".webm"}:
        # ffmpeg (video)
        run_command(["ffmpeg", "-y", "-i", str(input_path), str(output_path)])
    elif input_suffix in {".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".odt", ".odp", ".ods"}:
        # LibreOffice headless -> PDF (demo)
        if output_path.suffix != ".pdf":
            raise HTTPException(status_code=400, detail="Docs supported -> pdf only in this demo")
        run_command([
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(OUTPUT_DIR),
            str(input_path),
        ])
        output_path = OUTPUT_DIR / (input_path.stem + ".pdf")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if not output_path.exists():
        raise HTTPException(status_code=500, detail="Output not produced")

    download_name = f"{Path(file.filename).stem}.{output_path.suffix.lstrip('.')}"
    return FileResponse(
        path=str(output_path),
        filename=download_name,
        media_type="application/octet-stream",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

