import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "AI English Video Caption Generator")

    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")  # tiny/base/small/medium
    DEVICE = os.getenv("DEVICE", "cpu")
    COMPUTE_TYPE = os.getenv("COMPUTE_TYPE", "int8")

    MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "1000"))

    SUPPORTED_VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi", ".webm")

    TEMP_DIR = os.getenv("TEMP_DIR", "temp")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")

    # Subtitle styling (used when burning captions with FFmpeg subtitles filter)
    SUBTITLE_FONT = os.getenv("SUBTITLE_FONT", "DejaVu Sans")
    SUBTITLE_FONT_SIZE = int(os.getenv("SUBTITLE_FONT_SIZE", "22"))
    SUBTITLE_COLOR = os.getenv("SUBTITLE_COLOR", "&H00FFFFFF")  # white
    SUBTITLE_OUTLINE_COLOR = os.getenv("SUBTITLE_OUTLINE_COLOR", "&H00000000")  # black
    SUBTITLE_BACK_COLOR = os.getenv("SUBTITLE_BACK_COLOR", "&H80000000")  # semi-transparent black

    # Caption line constraints
    MAX_CHARS_PER_LINE = int(os.getenv("MAX_CHARS_PER_LINE", "42"))
    MAX_LINES_PER_CAPTION = int(os.getenv("MAX_LINES_PER_CAPTION", "2"))


settings = Settings()