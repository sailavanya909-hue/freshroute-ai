#!/bin/bash
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install it from https://www.python.org/downloads/macos/ and run this launcher again."
  read -r -p "Press Return to close."
  exit 1
fi
if [ ! -f data/freshroute.sqlite ]; then
  python3 tools/build_data.py
fi
echo ""
echo "FreshRoute is starting on your Mac."
echo "Open http://127.0.0.1:8765 in your browser."
echo "Keep this window open. Press Control+C here to stop the app."
echo ""
python3 app/server.py
