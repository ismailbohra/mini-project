import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config.settings import settings

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / settings.ASSETS_DIR.split("/", 1)[-1] if "/" in settings.ASSETS_DIR else BASE_DIR / settings.ASSETS_DIR
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(upload_file: UploadFile, subdir: str = "") -> str:
    """Save an UploadFile to backend/assets/<subdir>/ and return public path.

    Returns a path like `/assets/<subdir>/<filename>` which can be served
    by the static files mount.
    """
    if not upload_file:
        return ""

    target_dir = ASSETS_DIR / subdir if subdir else ASSETS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload_file.filename).suffix or ""
    filename = f"{uuid.uuid4().hex}{suffix}"
    dest = target_dir / filename
    # Use blocking IO; acceptable for moderate loads. Replace with aiofiles for async.
    with dest.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    sub = f"{subdir}/" if subdir else ""
    return f"/assets/{sub}{filename}"
