@echo off
chcp 65001 >nul
echo ========================================
echo   Allegro Lib Manager - Install Script
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found. Please install Python 3 and add it to PATH.
  pause
  exit /b 1
)

echo [1/2] Installing Python dependencies (Flask, pyodbc)...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Dependency installation failed.
  pause
  exit /b 1
)

echo.
echo [2/2] Please make sure "Microsoft Access Database Engine (x64)"
echo        is installed, otherwise .accdb cannot be read/written.
echo.
echo Done! Double-click run.bat to start.
pause