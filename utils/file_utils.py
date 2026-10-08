import os
import uuid
from config.settings import settings


def is_supported_video(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in settings.SUPPORTED_VIDEO_EXTENSIONS


def get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def is_within_size_limit(size_bytes: int) -> bool:
    size_mb = size_bytes / (1024 * 1024)
    return size_mb <= settings.MAX_VIDEO_SIZE_MB


def make_temp_path(suffix: str) -> str:
    """
    Build a unique path inside the temp directory.
    Example: make_temp_path(".wav") -> temp/8f3c1a2b.wav
    """
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    return os.path.join(settings.TEMP_DIR, filename)


def make_output_path(suffix: str, prefix: str = "captioned_video") -> str:
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    filename = f"{prefix}_{uuid.uuid4().hex[:8]}{suffix}"
    return os.path.join(settings.OUTPUT_DIR, filename)


def safe_remove(path: str) -> None:
    """
    Delete a file if it exists. Never raises.
    """
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
