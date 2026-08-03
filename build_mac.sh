#!/usr/bin/env bash
# Builds a standalone macOS executable for yue.
# Run this once on your Mac. Requires Python 3 to build, but the
# resulting dist/yue binary does NOT need Python to run afterwards.
set -e

cd "$(dirname "$0")"

python3 -m venv .build-venv
source .build-venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --onefile --name yue --clean main.py

deactivate

echo ""
echo "Build complete: dist/yue"
echo ""
echo "First run only, macOS will likely block the unsigned binary. Either:"
echo "  - Finder: right-click dist/yue -> Open -> Open, or"
echo "  - Terminal: xattr -dr com.apple.quarantine dist/yue"
echo ""
echo "Then run it with:"
echo "  ./dist/yue sample_audios/sample.wav"