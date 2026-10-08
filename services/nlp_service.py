import re
from typing import List

from config.settings import settings
from models.schemas import TranscriptSegment, CaptionLine


def clean_text(text: str) -> str:
    """
    Normalize whitespace and remove stray artifacts while preserving
    punctuation and original wording.
    """
    text = text.strip()
    text = re.sub(r"\s+", " ", text)          # collapse multiple spaces
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)  # no space before punctuation
    return text


def split_into_caption_lines(text: str, max_chars: int = None, max_lines: int = None) -> List[str]:
    """
    Split a chunk of text into up to `max_lines` lines, each at most
    `max_chars` characters, breaking on word boundaries.
    """
    max_chars = max_chars or settings.MAX_CHARS_PER_LINE
    max_lines = max_lines or settings.MAX_LINES_PER_CAPTION

    words = text.split()
    lines: List[str] = []
    current_line = ""

    for word in words:
        candidate = f"{current_line} {word}".strip()
        if len(candidate) <= max_chars:
            current_line = candidate
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

        if len(lines) >= max_lines:
            break

    if current_line and len(lines) < max_lines:
        lines.append(current_line)

    return lines if lines else [text[:max_chars]]


def _split_long_segment_text(text: str, max_chars: int) -> List[str]:
    """
    Break a long sentence into caption-sized chunks (each chunk itself
    may later be wrapped into up to 2 lines). Splits preferentially at
    sentence or clause boundaries, falling back to word boundaries.
    """
    chunk_limit = max_chars * settings.MAX_LINES_PER_CAPTION
    if len(text) <= chunk_limit:
        return [text]

    # Try splitting on sentence boundaries first
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: List[str] = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= chunk_limit:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # sentence itself may still be too long -> word-wrap it
            if len(sentence) > chunk_limit:
                words = sentence.split()
                sub = ""
                for w in words:
                    cand = f"{sub} {w}".strip()
                    if len(cand) <= chunk_limit:
                        sub = cand
                    else:
                        chunks.append(sub)
                        sub = w
                current = sub
            else:
                current = sentence

    if current:
        chunks.append(current)

    return chunks


def process_segments(segments: List[TranscriptSegment]) -> List[CaptionLine]:
    """
    Convert raw transcript segments into caption-ready CaptionLine objects:
    - cleans text
    - splits overly long segments into multiple timed captions
      (timestamps distributed proportionally across the split)
    - wraps each caption's text into <= MAX_LINES_PER_CAPTION lines
    """
    captions: List[CaptionLine] = []

    for seg in segments:
        cleaned = clean_text(seg.text)
        if not cleaned:
            continue

        chunks = _split_long_segment_text(cleaned, settings.MAX_CHARS_PER_LINE)

        duration = max(seg.end - seg.start, 0.01)
        total_chars = sum(len(c) for c in chunks) or 1

        cursor = seg.start
        for chunk in chunks:
            proportion = len(chunk) / total_chars
            chunk_duration = max(duration * proportion, 0.8)  # minimum display time
            chunk_start = cursor
            chunk_end = min(chunk_start + chunk_duration, seg.end) if len(chunks) > 1 else seg.end
            cursor = chunk_end

            lines = split_into_caption_lines(chunk)
            captions.append(CaptionLine(start=chunk_start, end=chunk_end, lines=lines))

    # Guard against zero-length or overlapping captions
    for i in range(1, len(captions)):
        if captions[i].start < captions[i - 1].end:
            captions[i].start = captions[i - 1].end

    return captions
