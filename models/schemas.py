from dataclasses import dataclass, field
from typing import List


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class TranscriptionResult:
    segments: List[TranscriptSegment] = field(default_factory=list)
    language: str = "en"
    full_text: str = ""


@dataclass
class CaptionLine:
    start: float
    end: float
    lines: List[str]  # up to MAX_LINES_PER_CAPTION strings

    @property
    def text(self) -> str:
        return "\n".join(self.lines)
