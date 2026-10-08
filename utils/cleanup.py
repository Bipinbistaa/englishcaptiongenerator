from utils.file_utils import safe_remove


class TempFileTracker:
    """
    Tracks temp files created during one processing run so they
    can all be removed together once no longer needed.
    """

    def __init__(self):
        self._paths = []

    def track(self, path: str) -> str:
        self._paths.append(path)
        return path

    def cleanup_all(self):
        for path in self._paths:
            safe_remove(path)
        self._paths = []
