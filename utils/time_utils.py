def seconds_to_srt_timestamp(seconds: float) -> str:
    """
    

    Example:
        65.25 -> "00:01:05,250"
    """
    if seconds < 0:
        seconds = 0.0

    total_ms = round(seconds * 1000)
    hours, remainder_ms = divmod(total_ms, 3_600_000)
    minutes, remainder_ms = divmod(remainder_ms, 60_000)
    secs, millis = divmod(remainder_ms, 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def srt_timestamp_to_seconds(timestamp: str) -> float:
   
    hms, millis = timestamp.split(",")
    hours, minutes, secs = hms.split(":")
    total = (
        int(hours) * 3600
        + int(minutes) * 60
        + int(secs)
        + int(millis) / 1000.0
    )
    return total


def seconds_to_vtt_timestamp(seconds: float) -> str:
   
    return seconds_to_srt_timestamp(seconds).replace(",", ".")
