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

echo [1/3] Installing Python dependencies (Flask, pyodbc)...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Dependency installation failed.
  pause
  exit /b 1
)

echo.
echo [2/3] Creating library directory structure under program root...
set "LIBROOT=%~dp0"
for %%D in ("database" "schematic" "symbol\footprint" "symbol\pad" "symbol\flash" "symbol\mech" "3d" "doc") do (
  if not exist "%LIBROOT%%%~D\" (
    mkdir "%LIBROOT%%%~D"
    echo   + created: %%~D
  ) else (
    echo   = exists:  %%~D
  )
)

echo.
echo [3/3] Please make sure "Microsoft Access Database Engine (x64)"
echo        is installed, otherwise .accdb cannot be read/written.
echo.
echo Done! Double-click run.bat to start.
pause