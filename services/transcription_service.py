from typing import List
from faster_whisper import WhisperModel

from config.settings import settings
from models.schemas import TranscriptSegment, TranscriptionResult


class TranscriptionError(Exception):
    pass


def load_whisper_model() -> WhisperModel:
    """
    Load and return a Faster-Whisper model based on settings.
    This is the function Streamlit should wrap with @st.cache_resource.
    """
    return WhisperModel(
        settings.WHISPER_MODEL,
        device=settings.DEVICE,
        compute_type=settings.COMPUTE_TYPE,
    )


def transcribe_audio(model: WhisperModel, audio_path: str) -> TranscriptionResult:
    """
    Transcribe English speech from audio_path into timestamped segments.
    """
    try:
        segments_iter, info = model.transcribe(
            audio_path,
            language="en",
            vad_filter=True,
            beam_size=5,
        )
    except Exception as exc:  # noqa: BLE001 - surface as domain error
        raise TranscriptionError(f"Speech transcription failed: {exc}") from exc

    segments: List[TranscriptSegment] = []
    full_text_parts: List[str] = []

    for seg in segments_iter:
        text = seg.text.strip()
        if not text:
            continue
        segments.append(TranscriptSegment(start=seg.start, end=seg.end, text=text))
        full_text_parts.append(text)

    if not segments:
        raise TranscriptionError("No speech was detected in the video.")

    return TranscriptionResult(
        segments=segments,
        language="en",
        full_text=" ".join(full_text_parts),
    )
