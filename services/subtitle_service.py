from typing import List
from models.schemas import CaptionLine
from utils.time_utils import seconds_to_srt_timestamp, seconds_to_vtt_timestamp


def generate_srt(captions: List[CaptionLine]) -> str:
    """
    Build SRT-formatted text from caption lines.
    """
    if not captions:
        return ""

    blocks = []
    for index, cap in enumerate(captions, start=1):
        start_ts = seconds_to_srt_timestamp(cap.start)
        end_ts = seconds_to_srt_timestamp(cap.end)
        text = cap.text
        block = f"{index}\n{start_ts} --> {end_ts}\n{text}\n"
        blocks.append(block)

    return "\n".join(blocks).strip() + "\n"


def generate_vtt(captions: List[CaptionLine]) -> str:
    """
    Build WebVTT-formatted text from caption lines.
    """
    if not captions:
        return "WEBVTT\n"

    lines = ["WEBVTT", ""]
    for cap in captions:
        start_ts = seconds_to_vtt_timestamp(cap.start)
        end_ts = seconds_to_vtt_timestamp(cap.end)
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(cap.text)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def save_srt_file(srt_content: str, path: str) -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    return path
