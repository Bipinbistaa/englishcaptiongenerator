import json
import subprocess
from utils.file_utils import is_supported_video, is_within_size_limit


class VideoValidationError(Exception):
    pass


def validate_video_file(filename: str, size_bytes: int) -> None:
    """
    Validate extension and file size. Raises VideoValidationError on failure.
    """
    if not is_supported_video(filename):
        raise VideoValidationError(
            "Unable to process this video. Please upload a valid video file "
            "(.mp4, .mov, .mkv, .avi, .webm)."
        )

    if not is_within_size_limit(size_bytes):
        raise VideoValidationError(
            "The uploaded video exceeds the maximum allowed size."
        )


def has_audio_stream(video_path: str) -> bool:
    """
    Use ffprobe to check whether the video contains at least one audio stream.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "a",
                "-show_entries", "stream=codec_type",
                "-of", "json",
                video_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        data = json.loads(result.stdout or "{}")
        streams = data.get("streams", [])
        return len(streams) > 0
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        return False


def get_video_duration(video_path: str) -> float:
    """
    Return video duration in seconds using ffprobe. Returns 0.0 on failure.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                video_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        data = json.loads(result.stdout or "{}")
        return float(data.get("format", {}).get("duration", 0.0))
    except (subprocess.SubprocessError, json.JSONDecodeError, ValueError, FileNotFoundError):
        return 0.0
