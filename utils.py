import os
import sys


def resource_path(relative_path: str) -> str:
    """Return absolute path to resource, whether running as script or as PyInstaller bundle."""
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, relative_path)
