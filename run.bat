@echo off
chcp 65001 >nul
cd /d %~dp0
cd src
python app.py
pause