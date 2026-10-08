import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.time_utils import seconds_to_srt_timestamp, srt_timestamp_to_seconds


def test_seconds_to_srt_timestamp_basic():
    assert seconds_to_srt_timestamp(65.25) == "00:01:05,250"


def test_seconds_to_srt_timestamp_zero():
    assert seconds_to_srt_timestamp(0) == "00:00:00,000"


def test_seconds_to_srt_timestamp_hours():
    assert seconds_to_srt_timestamp(3661.5) == "01:01:01,500"


def test_seconds_to_srt_timestamp_negative_clamped():
    assert seconds_to_srt_timestamp(-5) == "00:00:00,000"


def test_srt_timestamp_roundtrip():
    original = 125.75
    ts = seconds_to_srt_timestamp(original)
    back = srt_timestamp_to_seconds(ts)
    assert abs(back - original) < 0.001
