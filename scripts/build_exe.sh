#!/usr/bin/env bash
set -euo pipefail

# Linux build (onefile)
python -m pip install --upgrade pip
python -m pip install pyinstaller

# Ensure we run from repo root
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Bundle KV file with the app
pyinstaller \
  --name SuperApp \
  --onefile \
  --windowed \
  --add-data "client/app.kv:." \
  --collect-all kivy \
  --collect-all kivymd \
  client/main.py

echo "\nExecutable located in: $(pwd)/dist"