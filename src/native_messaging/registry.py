# HashedMaze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License
import winreg
from src.utils.resource_path import resource_path

def register_native_messaging_host():
    manifest_path = resource_path("host_manifest.json")
    
    key_path = r"Software\Microsoft\Edge\NativeMessagingHosts\com.hashed_maze"
    
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, manifest_path)
        return True, "Registered successfully"
    except Exception as e:
        return False, f"Registration error: {e}"