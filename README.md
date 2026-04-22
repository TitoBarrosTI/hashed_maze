# 🔐 Hashed Maze
### A local password manager built with Python and PySide6

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/titobarrosti)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.10-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![AES-256](https://img.shields.io/badge/AES--256--GCM-Encrypted-red?style=for-the-badge&logo=letsencrypt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)

---

## 📖 About

**Hashed Maze** is a local-first password manager that stores all credentials encrypted on your own machine — no cloud, no third-party servers, no data leaving your device.

Built with Python and PySide6, it features a clean desktop interface, AES-256-GCM encryption, master password protection, and a browser extension integration for Chrome and Edge via Native Messaging.

---

## ✨ Features

- 🔒 **AES-256-GCM encryption** — industry-standard symmetric encryption for all stored credentials
- 🧠 **Master password protection** — single access point with bcrypt-based key derivation
- 🔍 **Search & manage** — find, add, edit, and delete credentials with ease
- 💡 **Password strength indicator** — real-time feedback powered by `zxcvbn`
- 🧩 **Browser extension** — Native Messaging integration for Chrome and Edge
- 🖥️ **100% local** — your data never leaves your machine
- 🪟 **Windows desktop app** — native look and feel via PySide6/Qt

---

## 🚧 Roadmap

- [ ] Settings tab — application preferences and configuration
- [ ] Auto-lock after inactivity
- [ ] Password generator

---

## 📸 Screenshots

| Autofill in action — Brasil Paralelo streaming site |
|---|
| ![Obtaining Password](docs/screenshots/hashed_maze_obtaining_password.png) |

| Master Password | Search & Delete |
|---|---|
| ![Master Password](docs/screenshots/hashed_maze_master_password_register.png) | ![Search and Delete](docs/screenshots/hashed_maze_search_delete_item.png) |

| Search Tab | Config Tab | About Tab |
|---|---|---|
| ![Search](docs/screenshots/hashed_maze_search_tab.png) | ![Config](docs/screenshots/hashed_maze_config_tab.png) | ![About](docs/screenshots/hashed_maze_about_tab.png) |

---

## 🗂️ Project Structure

```
hashed_maze/
├── docs/
│   └── screenshots/
├── extension/
│   ├── background.js
│   ├── content.js
│   └── manifest.json
├── src/
│   ├── core/
│   │   ├── single_instance.py
│   │   └── state.py
│   ├── native_messaging/
│   │   └── registry.py
│   ├── utils/
│   │   ├── mixins/
│   │   │   ├── crud_mixin.py
│   │   │   ├── helpers.py
│   │   │   ├── security.py
│   │   │   └── settings.py
│   │   ├── dialogs.py
│   │   ├── password_strength.py
│   │   └── resource_path.py
│   ├── bridge.py
│   ├── config.py
│   ├── crypt.py
│   ├── database.py
│   ├── login_window_hashed_maze.py
│   ├── main_window_hashed_maze.py
│   ├── master_pass_hashed_maze.py
│   ├── models.py
│   ├── password_server.py
│   ├── popup_hint.py
│   └── setup.py
├── static/
│   └── icons/
├── ui/
│   ├── forms/
│   │   ├── login_window_hashed_maze.ui
│   │   ├── main_window_hashed_maze.ui
│   │   └── master_pass_hashed_maze.ui
│   └── helpers/
│       └── animations.py
├── host_manifest.json
├── main.py
├── roundedframe.py
├── run_bridge_python_host.bat
├── requirements.txt
├── LICENCE
└── README.md
```
ArquivoDescriçãoextension/background.jsService worker (Chrome/Edge)extension/content.jsContent script for autofillextension/manifest.jsonExtension manifest (MV3)src/core/single_instance.pyEnsures single instance executionsrc/core/state.pyCentralized app statesrc/native_messaging/registry.pyWindows registry setup for Native Messagingsrc/utils/mixins/crud_mixin.pyQt-integrated CRUD for credentials with SQLite and CryptoVault encryptionsrc/utils/mixins/helpers.pyUI helpers: icon switching, pwd strength bar, show/hide toggle, status feedback & logsrc/utils/mixins/security.pyMaster password verification and atomic re-encryption of all credentialssrc/utils/mixins/settings.pySettings persistence: load, save and apply search field/order preferencessrc/bridge.pyNative Messaging host (Python ↔ Browser)src/crypt.pyAES-256-GCM encryption (CryptoVault)src/database.pySQLite layer (SQLiteDB)src/password_server.pyLocal password server for extensionsrc/popup_hint.pyHover hint popup widgethost_manifest.jsonNative Messaging host manifestroundedframe.pyCustom QFrame with rounded corners

## ⚙️ Installation

### Prerequisites

- Python 3.12+
- Windows 10 or later
- Google Chrome or Microsoft Edge (for browser extension)

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/TitoBarrosTI/hashed_maze.git C:\hashed_maze
cd hashed_maze
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

### Browser Extension

**4. Load the extension in Chrome/Edge**
- Open `chrome://extensions` or `edge://extensions`
- Enable **Developer mode**
- Click **Load unpacked** and select the `extension/` folder

**5. Run the application**
```bash
python main.py
```
---
## ⚠️ Troubleshooting

### Error: Specified native messaging host not found

The extension relies on its Chrome-generated ID to communicate with the native host.

This ID is derived from the extension's directory when loaded unpacked.
If the directory is moved or differs from the one used during installation (e.g. `C:\hashed_maze`), the ID will change and communication will fail.

**Solution:**
- Keep the extension in the same directory defined during installation
OR
- Update the "allowed_origins" field in the native host manifest with the current extension ID (chrome://extensions)

---

## 🔐 Security Notes

- All credentials are encrypted with **AES-256-GCM** before being stored in SQLite
- The master password is never stored — only its derived key is used at runtime
- The database file (`.db3`) is stored locally and is not tracked by version control
- No telemetry, no network calls, no external dependencies beyond the listed packages

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| GUI Framework | PySide6 / Qt 6.10 |
| Database | SQLite via `sqlite3` |
| Encryption | AES-256-GCM (`cryptography`) |
| Password Analysis | `zxcvbn` |
| Browser Integration | Native Messaging (Chrome/Edge) |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENCE](LICENCE) file for details.