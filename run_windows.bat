@echo off
REM One-click setup + run (Windows). Double-click, or run from the VS Code terminal.
cd /d "%~dp0"
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate
echo Installing requirements (first time takes a few minutes)...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
python check_setup.py
streamlit run app.py
pause
