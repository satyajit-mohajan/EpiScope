@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv
  if errorlevel 1 (echo Python 3.10+ required & pause & exit /b 1)
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (echo Package installation failed & pause & exit /b 1)
echo Open http://127.0.0.1:8000 in your browser.
".venv\Scripts\python.exe" -m uvicorn sentinel.api:app --host 127.0.0.1 --port 8000
pause
