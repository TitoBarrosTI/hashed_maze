# MCacheBox
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import os, sys
from pathlib import Path

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)  # type: ignore
    base = Path(__file__).parent.parent.parent
    return str(base / relative_path)