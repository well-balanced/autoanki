#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# 0) check Python
if ! command -v python3 >/dev/null 2>&1; then
  osascript -e 'display alert "AutoAnki" message "Python 3 is required.\nInstall from python.org or via Homebrew."'
  exit 1
fi

# 1) venv + deps
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

# 2) create .env
if [ ! -f ".env" ] || ! grep -q '^OPENAI_API_KEY=' .env; then
  read -r -s -p "Enter your OPENAI_API_KEY: " KEY; echo
  {
    echo "OPENAI_API_KEY=$KEY"
    echo "OPENAI_MODEL=gpt-4o-mini"
  } >> .env
fi

# 3) check AnkiConnect
if ! curl -s --max-time 2 http://127.0.0.1:8765 >/dev/null; then
  osascript -e 'display alert "AutoAnki" message "Anki or AnkiConnect not reachable (http://127.0.0.1:8765).\nOpen Anki → Tools → Add-ons → Get Add-ons… → code 2055492159, then restart."'
  exit 1
fi

# 4) run
python main.py