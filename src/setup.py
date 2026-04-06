import json
import winreg
from pathlib import Path

REGISTRY_KEY = r"Software\Microsoft\Edge\NativeMessagingHosts\com.hashed_maze"
REGISTRY_KEY_CHROME = r"Software\Google\Chrome\NativeMessagingHosts\com.hashed_maze"

def run_setup():
    base = Path(__file__).parent.parent  # raiz do projeto
    manifest_path = base / "host_manifest.json"
    bat_path = base / "run_bridge_python_host.bat"

    # Gera o host_manifest.json com caminho correto
    manifest = {
        "name": "com.hashed_maze",
        "description": "Ponte para o meu cofre HashedMaze",
        "path": str(bat_path),
        "type": "stdio",
        "allowed_origins": [
            "chrome-extension://gmagciijklmgdpmlibnaiapngnllpila/"
        ]
    }

    # "chrome-extension://gaoienohpdkolcghibinejpjmmdnkfcb/"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Registra no Edge
    _register(REGISTRY_KEY, str(manifest_path))

    # Registra no Chrome
    _register(REGISTRY_KEY_CHROME, str(manifest_path))


def _register(key_path: str, manifest_path: str):
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, manifest_path)
    except Exception as e:
        print(f"Erro ao registrar {key_path}: {e}")