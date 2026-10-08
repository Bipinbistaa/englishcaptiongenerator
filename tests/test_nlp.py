import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.nlp_service import clean_text, split_into_caption_lines, process_segments
from models.schemas import TranscriptSegment


def test_clean_text_whitespace():
    assert clean_text("Hello    world") == "Hello world"


def test_clean_text_punctuation_spacing():
    assert clean_text("Hello ,world !") == "Hello,world!"


def test_clean_text_strips_ends():
    assert clean_text("   Hello world   ") == "Hello world"


def test_split_into_caption_lines_short_text():
    lines = split_into_caption_lines("Hello world", max_chars=42, max_lines=2)
    assert lines == ["Hello world"]


def test_split_into_caption_lines_respects_max_chars():
    text = "This is a fairly long sentence that should wrap onto multiple lines nicely"
    lines = split_into_caption_lines(text, max_chars=20, max_lines=2)
    assert len(lines) <= 2
    for line in lines:
        assert len(line) <= 20 + 15  # allow last word overflow tolerance


def test_process_segments_preserves_count_reasonable():
    segments = [
        TranscriptSegment(start=0.0, end=3.0, text="Hello there  friend."),
        TranscriptSegment(start=3.0, end=6.0, text="This is another segment."),
    ]
    captions = process_segments(segments)
    assert len(captions) >= 2


def test_process_segments_no_negative_overlap():
    segments = [
        TranscriptSegment(start=0.0, end=2.0, text="First segment text here."),
        TranscriptSegment(start=1.5, end=4.0, text="Second segment text here."),
    ]
    captions = process_segments(segments)
    for i in range(1, len(captions)):
        assert captions[i].start >= captions[i - 1].end
