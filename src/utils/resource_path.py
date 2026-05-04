# Hashed Maze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import os, sys
from pathlib import Path

# def resource_path(relative_path):
#     if hasattr(sys, "_MEIPASS"):
#         return os.path.join(sys._MEIPASS, relative_path)  # type: ignore
#     base = Path(__file__).parent.parent.parent
#     return str(base / relative_path)

def resource_path(relative_path: str) -> str:
    """Returns absolute path for dev and PyInstaller environments."""
    if getattr(sys, '_MEIPASS', None):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', relative_path)