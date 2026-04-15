# MCacheBox
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import win32event
import win32api
import winerror
import pywintypes

_mutex = None

def is_already_running(mutex_name: str = "HashedMazeAppMutex") -> bool:
    global _mutex

    try:
        _mutex = win32event.CreateMutex(None, False, mutex_name)
        error = win32api.GetLastError()
    except pywintypes.error as e:
        raise RuntimeError(f"Failed to create or open mutex: {e}") from e

    return error == winerror.ERROR_ALREADY_EXISTS