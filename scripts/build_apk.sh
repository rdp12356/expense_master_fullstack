#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../client"

python -m pip install --upgrade pip
python -m pip install --upgrade buildozer Cython

# Build debug APK
buildozer -v android debug

echo "\nAPK(s) located in: $(pwd)/bin"