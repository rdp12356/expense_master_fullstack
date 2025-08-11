# SuperApp (Kivy/KivyMD + FastAPI)

A polished, interactive Kivy/KivyMD application with a companion FastAPI backend. Build for Android (APK with Buildozer) and Desktop (EXE/onefile with PyInstaller).

## Project Structure

```
client/                   # Kivy/KivyMD mobile/desktop app
  main.py                 # App entrypoint
  app.kv                  # KivyMD UI layout/theme
  services/
    api_client.py         # Optional REST client to talk to backend
    storage.py            # Local SQLite storage
  requirements.txt        # Client Python dependencies
  buildozer.spec          # Android build configuration
server/                   # FastAPI backend (optional)
  main.py                 # API entrypoint
  requirements.txt        # Backend dependencies
  Dockerfile              # Containerized backend
scripts/
  build_apk.sh            # Build Android APK (debug)
  build_exe.sh            # Build desktop executable (Linux/Windows)
```

## 1) Setup (Local Dev)

- Create a virtual environment and install client deps

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r client/requirements.txt
```

- (Optional) Run the backend locally

```bash
python3 -m venv .venv-server
source .venv-server/bin/activate
pip install --upgrade pip
pip install -r server/requirements.txt
uvicorn server.main:app --reload --port 8000
```

- Run the client app

```bash
source .venv/bin/activate
python client/main.py
```

To use the backend, set the API Base URL in Settings to `http://127.0.0.1:8000`.

## 2) Build Android APK (on Linux)

- Install build tools

```bash
source .venv/bin/activate
pip install --upgrade buildozer Cython
sudo apt-get update && sudo apt-get install -y libffi-dev libssl-dev liblzo2-dev zlib1g-dev unzip openjdk-17-jdk
```

- Build the APK

```bash
cd client
buildozer -v android debug
# Outputs to bin/*.apk
```

Notes:
- First build downloads the Android SDK/NDK; it may take a while.
- In `buildozer.spec`, network permission is enabled for API usage.

## 3) Build Desktop Executable

PyInstaller doesn’t cross-compile. Build on the target OS.

- Linux onefile build

```bash
source .venv/bin/activate
pip install pyinstaller
bash scripts/build_exe.sh
# Outputs to dist/SuperApp
```

- Windows EXE

Run on Windows PowerShell/CMD with Python 3.10/3.11:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r client\requirements.txt
pip install pyinstaller kivy_deps.sdl2 kivy_deps.glew kivy_deps.angle
pyinstaller --name SuperApp --onefile --windowed client\main.py --add-data "client\app.kv;." --collect-all kivy --collect-all kivymd
# EXE at dist\SuperApp.exe
```

If icons or additional assets are added, include them via `--add-data`.

## 4) Configuration

- API Base URL can be set in the app’s Settings screen. Leave empty to work fully offline (local SQLite).
- Themes: toggle light/dark from the top bar.

## 5) Notes

- For charts, the app uses `kivy_garden.graph` (lightweight and Android-friendly).
- For Android, ensure Java 17 and sufficient disk space. If build fails due to recipes, try cleaning: `buildozer android clean`.
- For troubleshooting packaging, consult Kivy docs: `https://kivy.org/doc/stable/` and Buildozer docs: `https://buildozer.readthedocs.io/en/latest/`.
- If you see `MDNavigationLayout must contain only ScreenManager and MDNavigationDrawer`, ensure the root of `app.kv` is `MDNavigationLayout` with only those two direct children. Top bars should be inside each screen.
