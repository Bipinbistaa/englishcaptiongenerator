import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.schemas import CaptionLine
from services.subtitle_service import generate_srt, generate_vtt


def make_caption(start, end, text):
    return CaptionLine(start=start, end=end, lines=[text])


def test_generate_srt_numbering():
    captions = [make_caption(0, 2, "Hello"), make_caption(2, 4, "World")]
    srt = generate_srt(captions)
    assert "1\n" in srt
    assert "2\n" in srt


def test_generate_srt_timestamps():
    captions = [make_caption(1.0, 4.0, "Artificial intelligence is changing the way we work.")]
    srt = generate_srt(captions)
    assert "00:00:01,000 --> 00:00:04,000" in srt


def test_generate_srt_text_present():
    captions = [make_caption(0, 2, "Hello world")]
    srt = generate_srt(captions)
    assert "Hello world" in srt


def test_generate_srt_empty_segments():
    assert generate_srt([]) == ""


def test_generate_srt_long_segment():
    long_text = "This is a fairly long caption line used for testing purposes only."
    captions = [make_caption(0, 5, long_text)]
    srt = generate_srt(captions)
    assert long_text in srt


def test_generate_srt_no_overlap_when_sequential():
    captions = [make_caption(0, 2, "A"), make_caption(2, 4, "B")]
    srt = generate_srt(captions)
    lines = srt.strip().split("\n\n")
    assert len(lines) == 2


def test_generate_vtt_header():
    captions = [make_caption(0, 2, "Hello")]
    vtt = generate_vtt(captions)
    assert vtt.startswith("WEBVTT")


def test_generate_vtt_empty():
    vtt = generate_vtt([])
    assert vtt.strip() == "WEBVTT"
