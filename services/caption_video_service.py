import os
import re
from moviepy import VideoFileClip, TextClip, CompositeVideoClip


class CaptionBurnError(Exception):
    pass


_SRT_BLOCK_RE = re.compile(
    r"\d+\s*\n"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n"
    r"(.*?)(?=\n\s*\n|\Z)",
    re.DOTALL,
)

# Common font file locations to try, per OS. First existing wins.
_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",          # macOS
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",                          # Windows
]


def _resolve_font() -> str:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    raise CaptionBurnError(
        "No usable font file found for captions. Install a TTF font "
        "(e.g. DejaVu Sans) or update _FONT_CANDIDATES with a valid path."
    )


def _srt_ts_to_seconds(ts: str) -> float:
    hms, millis = ts.split(",")
    h, m, s = hms.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(millis) / 1000.0


def _parse_srt(srt_path: str):
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    captions = []
    for match in _SRT_BLOCK_RE.finditer(content):
        start_ts, end_ts, text = match.groups()
        text = text.strip()
        if not text:
            continue
        captions.append(
            (_srt_ts_to_seconds(start_ts), _srt_ts_to_seconds(end_ts), text)
        )
    return captions


def burn_captions_into_video(input_video: str, subtitle_file: str, output_video: str) -> str:
    """
    Burn subtitle_file (.srt) into input_video and write output_video.
    Preserves original resolution, aspect ratio, duration, and audio.
    """
    if not os.path.exists(input_video):
        raise CaptionBurnError("Input video not found.")
    if not os.path.exists(subtitle_file):
        raise CaptionBurnError("Subtitle file not found.")

    captions = _parse_srt(subtitle_file)
    if not captions:
        raise CaptionBurnError("Subtitle file contained no valid captions.")

    font_path = _resolve_font()

    video = None
    final = None
    try:
        video = VideoFileClip(input_video)
        w, h = video.size
        font_size = max(int(h * 0.045), 18)

        text_clips = []
        for start, end, text in captions:
            end = min(end, video.duration)
            start = min(start, video.duration)
            if end <= start:
                continue

            txt_clip = (
                TextClip(
                    font=font_path,
                    text=text,
                    font_size=font_size,
                    color="white",
                    method="caption",
                    size=(int(w * 0.9), None),
                    stroke_color="black",
                    stroke_width=2,
                    text_align="center",
                )
                .with_start(start)
                .with_end(end)
                .with_position(("center", "bottom"))
            )
            text_clips.append(txt_clip)

        final = CompositeVideoClip([video, *text_clips])
        final = final.with_audio(video.audio)

        final.write_videofile(
            output_video,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            fps=video.fps,
            logger=None,
        )

    except Exception as exc:  # noqa: BLE001
        raise CaptionBurnError(f"MoviePy failed to burn captions: {exc}") from exc
    finally:
        if final is not None:
            final.close()
        if video is not None:
            video.close()

    if not os.path.exists(output_video):
        raise CaptionBurnError("Caption burning did not produce an output file.")

    return output_video