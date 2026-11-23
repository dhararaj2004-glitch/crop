#!/usr/bin/env bash
# One-click setup + run (Mac/Linux):  bash run_mac_linux.sh
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt
python check_setup.py
streamlit run app.py
