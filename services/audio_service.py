import subprocess
from utils.file_utils import make_temp_path


class AudioExtractionError(Exception):
    pass


def extract_audio(video_path: str) -> str:
    """
    Extract audio from video_path as 16kHz mono WAV.
    Returns the path to the generated WAV file.
    """
    audio_path = make_temp_path(".wav")

    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",                 # no video
        "-acodec", "pcm_s16le",
        "-ar", "16000",        # 16 kHz
        "-ac", "1",            # mono
        audio_path,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        raise AudioExtractionError("Audio extraction timed out.")
    except FileNotFoundError:
        raise AudioExtractionError(
            "FFmpeg was not found. Please make sure FFmpeg is installed."
        )

    if result.returncode != 0:
        raise AudioExtractionError(
            "No usable audio track was found in this video."
        )

    return audio_path
